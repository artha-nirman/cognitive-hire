import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2AuthorizationCodeBearer
from pathlib import Path
import os

from src.common.config import settings
from src.common.db.database import init_db
from src.common.events import init_event_system, close_event_system, register_event_handler
from src.domains.employer.router import router as employer_router
from src.domains.job.router import router as job_router
from src.domains.publishing.router import router as publishing_router
from src.domains.screening.router import router as screening_router
from src.domains.sourcing.router import router as sourcing_router
from src.common.middleware.logging import RequestLoggingMiddleware
from src.common.middleware.auth import AuthMiddleware
from src.common.middleware.tenant import TenantMiddleware
from src.common.websocket.handlers import handle_job_event, handle_screening_event, handle_sourcing_event
from src.websocket.routes import router as websocket_router

# Configure structured logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))

# Define processors based on format
processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

# Add the renderer based on configuration
if settings.LOG_FORMAT.lower() == "json":
    processors.append(structlog.processors.JSONRenderer())
else:
    processors.append(structlog.dev.ConsoleRenderer())

structlog.configure(
    processors=processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and cleanup application resources.
    This context manager runs at application startup and shutdown.
    It handles initializing and closing database connections and the event system.
    """
    # Startup
    logger.info("Application starting", 
                app_name=settings.APP_NAME, 
                environment=settings.ENVIRONMENT,
                log_level=settings.LOG_LEVEL)
    
    # Initialize database
    try:
        await init_db()
    except Exception as e:
        logger.error("Database initialization failed", exc_info=e)
        raise
    
    # Initialize event system
    try:
        await init_event_system()
        
        # Register WebSocket event handlers
        await register_event_handler("job.created", handle_job_event)
        await register_event_handler("job.updated", handle_job_event)
        await register_event_handler("job.published", handle_job_event)
        await register_event_handler("job.unpublished", handle_job_event)
        
        await register_event_handler("screening.resume.uploaded", handle_screening_event)
        await register_event_handler("screening.matching.started", handle_screening_event)
        await register_event_handler("screening.interest_check.sent", handle_screening_event)
        
        await register_event_handler("sourcing.process.started", handle_sourcing_event)
        await register_event_handler("sourcing.channel.registered", handle_sourcing_event)
        
    except Exception as e:
        logger.error("Event system initialization failed", exc_info=e)
        raise
    
    logger.info("Application started successfully")
    
    yield
    
    # Cleanup
    logger.info("Application shutting down")
    
    # Close event system connections
    try:
        await close_event_system()
    except Exception as e:
        logger.error("Error during event system shutdown", exc_info=e)
    
    logger.info("Application shutdown complete")

# Define OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
    tokenUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
    scopes={f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/api/user_impersonation": "Access API"}
)

# Create FastAPI application
app = FastAPI(
    title="Recruitment Service API",
    description="API for managing job postings, employers, and candidate interactions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # We'll create a custom docs endpoint
    redoc_url=None,  # We'll create a custom redoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(TenantMiddleware)

# Include routers from all domains
app.include_router(employer_router, prefix="/api/employer", tags=["Employer"])
app.include_router(job_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(publishing_router, prefix="/api/publishing", tags=["Publishing"])
app.include_router(screening_router, prefix="/api/screening", tags=["Screening"])
app.include_router(sourcing_router, prefix="/api/sourcing", tags=["Sourcing"])
app.include_router(websocket_router, prefix="/ws")

# Determine the path to static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    # Mount the static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files from {static_dir}")

# Custom OpenAPI to include security definitions
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
                    "tokenUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
                    "scopes": {
                        f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/api/user_impersonation": "Access API"
                    }
                }
            }
        }
    }
    
    # Apply security to all operations
    openapi_schema["security"] = [{"oauth2": [f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/api/user_impersonation"]}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom Swagger UI with Azure AD B2C configuration
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url="/static/oauth2-redirect.html",
        init_oauth={
            "clientId": settings.SWAGGER_UI_CLIENT_ID,
            "appName": "Cognitive Hire API Swagger UI",
            "scopeSeparator": " ",
            "additionalQueryStringParams": {
                "prompt": "login"  # Force login every time
            }
        }
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
    )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and log them appropriately."""
    logger.info("HTTP exception", 
                status_code=exc.status_code, 
                detail=exc.detail,
                path=request.url.path)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors and log them with details."""
    logger.warning("Validation error", 
                  errors=exc.errors(),
                  body=str(await request.body()),
                  path=request.url.path)
                  
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/health", include_in_schema=False)
async def health_check():
    """
    Health check endpoint.
    
    Returns a simple status response to indicate the service is running.
    Used by container orchestration and monitoring systems.
    """
    logger.debug("Health check requested")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

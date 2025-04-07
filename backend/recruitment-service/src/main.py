import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2AuthorizationCodeBearer
from pathlib import Path
import os
from jose import jwt

from src.common.config import settings
from src.common.db.database import init_db
from src.common.events import init_event_system, close_event_system, register_event_handler
from src.domains.employer.router import router as employer_router
from src.domains.job.router import router as job_router
from src.domains.publishing.router import router as publishing_router
from src.domains.screening.router import router as screening_router
from src.domains.sourcing.router import router as sourcing_router
# Removed middleware imports
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
    
    # Initialize Azure AD B2C authentication
    try:
        from src.common.auth.dependencies import init_azure_auth
        await init_azure_auth(app)
        logger.info("Azure AD B2C authentication initialized")
    except Exception as e:
        logger.error("Azure AD B2C initialization failed", exc_info=e)
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
    scopes={
        "openid": "OpenID Connect authentication",
        settings.azure_ad_b2c_scope: "Access API"
    }
)

# Create FastAPI application
app = FastAPI(
    title="Recruitment Service API",
    description="API for managing job postings, employers, and candidate interactions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Enable docs with default URL
    redoc_url="/redoc",  # Enable redoc with default URL
    # Use built-in OAuth2 redirect handling from settings
    swagger_ui_oauth2_redirect_url=settings.oauth2_redirect_path,
    # Configure OAuth2 initialization directly
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.effective_swagger_client_id,
        "appName": "Cognitive Hire API Swagger UI",
        "scopeSeparator": " ",
        "scopes": settings.azure_ad_b2c_scopes
    }
)

# Add development mode auth bypass info to description if in development
if settings.ENVIRONMENT in ["development", "testing"]:
    app.description += """

## Development Authentication Bypass

In development environments, you can bypass authentication by clicking the "Authorize" button and entering a token in the "authBypass" section, or by adding these headers to your requests:
```
X-Auth-Bypass: {token}
X-Test-Tenant-ID: test-tenant-id  # Optional
```

This feature is disabled in production.
"""

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # Mount the static files at /static
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files from {static_dir}")
    
    # Don't mount the /docs path directly with StaticFiles
    # Instead, use our explicit routes below
    oauth2_redirect_path = static_dir / "oauth2-redirect.html"
    if not oauth2_redirect_path.exists():
        logger.warning("OAuth2 redirect file not found at expected location", path=str(oauth2_redirect_path))

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

# Enhanced token debugging endpoint
@app.get("/debug/token-info", include_in_schema=False)
async def token_info(request: Request):
    """
    Debug endpoint to check token information.
    Only available in development mode.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")
    
    from src.debug.token_debug import get_auth_debug_info
    
    # Get detailed token debugging info
    debug_info = get_auth_debug_info(request)
    
    return debug_info

# Add an auth test endpoint for development
@app.get("/debug/auth-test", include_in_schema=False)
async def auth_test(request: Request):
    """
    Debug endpoint that requires authentication.
    Only available in development mode.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")
        
    # Should only reach here if authentication succeeded
    return {
        "authenticated": True,
        "user": request.state.user if hasattr(request.state, "user") else None,
        "user_id": request.state.user_id if hasattr(request.state, "user_id") else None,
        "roles": request.state.roles if hasattr(request.state, "roles") else None,
    }

# Add authentication help endpoint for development
@app.get("/debug/auth-help", include_in_schema=False)
async def auth_help_endpoint():
    """
    Debug endpoint providing authentication help.
    Only available in development mode.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")
        
    from src.debug.token_debug import get_auth_help_info
    
    return get_auth_help_info()

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
    
    # Ensure OpenAPI version is explicitly set
    openapi_schema["openapi"] = "3.0.2"
    
    # Add security schemes
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
                    "tokenUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
                    "scopes": {
                        "openid": "OpenID Connect authentication",
                        settings.azure_ad_b2c_scope: "Access API"
                    }
                }
            }
        },
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add development auth bypass info if in development mode
    if settings.ENVIRONMENT in ["development", "testing"]:
        openapi_schema["components"]["securitySchemes"]["authBypass"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-Auth-Bypass",
            "description": f"Development authentication bypass token. Use value: '{settings.AUTH_BYPASS_TOKEN}'"
        }
        
        # Allow either oauth2 OR authBypass OR bearerAuth (not all required)
        openapi_schema["security"] = [
            {"oauth2": settings.azure_ad_b2c_scopes},
            {"bearerAuth": []},
            {"authBypass": []}
        ]
    else:
        # In non-development environments, only use OAuth2 and Bearer
        openapi_schema["security"] = [
            {"oauth2": settings.azure_ad_b2c_scopes},
            {"bearerAuth": []}
        ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
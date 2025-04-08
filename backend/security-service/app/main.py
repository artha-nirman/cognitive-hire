from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.api.router import api_router
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.correlation_id import CorrelationIdMiddleware

# Set up logging first
setup_logging()

app = FastAPI(
    title="Cognitive Hire Security Service",
    description="Authentication and authorization for the Cognitive Hire platform",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "security-service"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.ENVIRONMENT == "development"
    )

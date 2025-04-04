import time
from typing import Callable
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs information about incoming requests and outgoing responses including:
    - Request method, URL, and client IP
    - Response status code and processing time
    - Request ID for request tracing
    """
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Extract basic request info
        method = request.method
        url = str(request.url)
        client = request.client.host if request.client else None
        
        request_id = request.headers.get("X-Request-ID", "-")
        
        # Attach request_id to context for all logs in this request
        logger_with_context = logger.bind(request_id=request_id)
        
        # Log request with appropriate level based on endpoint
        # Health checks are logged at debug level to reduce noise
        if request.url.path == "/health":
            logger_with_context.debug("Request received", method=method, url=url, client=client)
        else:
            logger_with_context.info("Request received", method=method, url=url, client=client)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response with level depending on status code
            log_method = logger_with_context.info
            if response.status_code >= 400 and response.status_code < 500:
                log_method = logger_with_context.warning
            elif response.status_code >= 500:
                log_method = logger_with_context.error
                
            log_method(
                "Request completed",
                method=method,
                url=url,
                status_code=response.status_code,
                process_time=f"{process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            logger_with_context.error(
                "Request failed",
                method=method,
                url=url,
                error=str(e),
                process_time=f"{process_time:.3f}s",
                exc_info=e
            )
            
            # Re-raise the exception
            raise

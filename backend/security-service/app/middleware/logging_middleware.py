from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time
from app.core.logging import logger, user_id

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response information
    """
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Extract request information
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # Log the request
        logger.info(
            f"Request started: {method} {url}",
            extra={
                "http.method": method,
                "http.url": url,
                "http.client_ip": client_host,
                "event": "request_started"
            }
        )
        
        # Process the request and catch any exceptions
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Extract user ID from request state if available
            request_user_id = getattr(request.state, "user_id", None)
            if request_user_id:
                user_id.set(request_user_id)
            
            # Log the response
            logger.info(
                f"Request completed: {method} {url} - {response.status_code}",
                extra={
                    "http.method": method,
                    "http.url": url,
                    "http.status_code": response.status_code,
                    "http.duration": process_time,
                    "event": "request_completed"
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate processing time in case of exception
            process_time = time.time() - start_time
            
            # Log the exception
            logger.error(
                f"Request failed: {method} {url} - {str(e)}",
                extra={
                    "http.method": method,
                    "http.url": url,
                    "http.duration": process_time,
                    "error": str(e),
                    "event": "request_failed"
                },
                exc_info=True
            )
            
            # Re-raise the exception to be handled by the error handler middleware
            raise

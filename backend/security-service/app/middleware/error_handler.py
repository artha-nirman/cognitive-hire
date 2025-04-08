from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.core.logging import logger

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling exceptions and returning standardized error responses
    """
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request
            return await call_next(request)
            
        except Exception as e:
            # Log the exception with full traceback
            logger.exception(
                f"Unhandled exception: {str(e)}",
                extra={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "error": str(e),
                    "error.type": e.__class__.__name__,
                    "event": "unhandled_exception"
                }
            )
            
            # Return a standardized error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "correlation_id": getattr(request.state, "correlation_id", "unknown")
                }
            )

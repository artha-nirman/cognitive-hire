from fastapi import Request
import time
import structlog
from typing import Callable

logger = structlog.get_logger(__name__)

async def request_logging_middleware(request: Request, call_next: Callable):
    """
    Middleware to log all incoming requests and their responses.
    
    Args:
        request: The FastAPI request
        call_next: The next middleware or route handler
        
    Returns:
        The response from the next handler
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        client=request.client.host if request.client else "unknown",
        request_id=request.headers.get("X-Request-ID", "none"),
        auth_header_present="authorization" in [k.lower() for k in request.headers.keys()],
        auth_bypass_present="x-auth-bypass" in [k.lower() for k in request.headers.keys()]
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response
        process_time = (time.time() - start_time) * 1000
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=round(process_time, 2)
        )
        
        return response
    except Exception as e:
        # Log exceptions that weren't caught by exception handlers
        process_time = (time.time() - start_time) * 1000
        logger.error(
            "Request failed with unhandled error",
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time_ms=round(process_time, 2),
            exc_info=e
        )
        raise

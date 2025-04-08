import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.logging import correlation_id

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a correlation ID to the request and response
    """
    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from header or generate a new one
        request_id = request.headers.get("X-Correlation-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Set correlation ID in context variable
        correlation_id.set(request_id)
        
        # Add correlation ID to request state for access in route handlers
        request.state.correlation_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = request_id
        
        return response

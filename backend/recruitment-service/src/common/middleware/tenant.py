import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware for multi-tenancy support.
    
    Extracts tenant information from the authenticated user's token
    or from X-Tenant-ID header and adds it to the request state.
    This ensures proper data isolation between tenants.
    """
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        logger.info("Tenant middleware initialized")
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process each request to add tenant context.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from downstream handlers
        """
        # Skip tenant handling for non-authenticated paths
        if not hasattr(request.state, "user"):
            logger.debug("Skipping tenant context for unauthenticated request")
            return await call_next(request)
            
        # Extract tenant ID from token or header
        tenant_id = None
        
        # First try token
        if hasattr(request.state, "user"):
            tenant_id = request.state.user.get("tenant_id")
            if tenant_id:
                logger.debug("Tenant ID found in token", tenant_id=tenant_id)
        
        # Try header as fallback
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
            if tenant_id:
                logger.debug("Tenant ID found in header", tenant_id=tenant_id)
            else:
                logger.warning("No tenant ID found in token or header")
            
        # Store tenant ID in request state
        request.state.tenant_id = tenant_id
        
        if tenant_id:
            logger.info("Request tenant context set", tenant_id=tenant_id)
            
        # Continue with the request
        response = await call_next(request)
        
        # Add tenant to response headers for debugging
        if tenant_id and settings.ENVIRONMENT == "development":
            response.headers["X-Tenant-ID"] = tenant_id
            
        return response

from typing import Optional, Dict, List
import structlog
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.responses import Response

from src.common.config import settings

logger = structlog.get_logger(__name__)
security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT-based authentication.
    
    Validates JWT tokens in the Authorization header and adds user information
    to the request state for use in request handlers.
    """
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        # Define paths that don't need authentication
        self.public_paths = [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health", 
            "/metrics"
        ]
        logger.info("Auth middleware initialized", public_paths=self.public_paths)
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process each request, validating authentication when required.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from downstream handlers or an error response
        """
        # Skip auth for public paths
        for path in self.public_paths:
            if request.url.path.startswith(path):
                logger.debug("Skipping auth for public path", path=request.url.path)
                return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # No token provided, unauthenticated
            logger.warning(
                "Missing or invalid Authorization header", 
                path=request.url.path,
                client=request.client.host if request.client else None
            )
            return Response(
                content='{"detail":"Not authenticated"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode the token
            logger.debug("Validating JWT token")
            payload = jwt.decode(
                token,
                settings.AUTH_SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM]
            )
            
            # Add user info to request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.roles = payload.get("roles", [])
            
            logger.debug(
                "User authenticated successfully", 
                user_id=request.state.user_id,
                roles=request.state.roles
            )
            
            # Proceed with request
            return await call_next(request)
            
        except JWTError as e:
            # Invalid token
            logger.warning(
                "Invalid token", 
                error=str(e), 
                path=request.url.path
            )
            return Response(
                content='{"detail":"Invalid token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        except Exception as e:
            # Other errors
            logger.error(
                "Authentication error", 
                path=request.url.path,
                exc_info=e
            )
            return Response(
                content='{"detail":"Internal server error"}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json"
            )

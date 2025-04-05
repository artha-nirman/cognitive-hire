import time
import json
import httpx
import structlog
from typing import Optional, Dict, List, Tuple, Callable, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.responses import Response

from src.common.config import settings

logger = structlog.get_logger(__name__)

class AzureADB2CAuth:
    """
    Azure AD B2C authentication helper for validating tokens.
    
    This helper caches the signing keys from Azure AD B2C to reduce
    the number of outbound requests needed for token validation.
    """
    
    def __init__(self):
        self.jwks = None  # JSON Web Key Set
        self.jwks_last_updated = 0
        self.jwks_update_interval = 3600  # 1 hour
        
    async def get_jwks(self) -> Dict:
        """
        Get the JSON Web Key Set from Azure AD B2C.
        
        Fetches keys from the OpenID configuration endpoint and caches them
        to minimize external requests.
        
        Returns:
            Dict: The JSON Web Key Set
        """
        now = time.time()
        
        # If we have a cached JWKS that's not too old, use it
        if self.jwks and now - self.jwks_last_updated < self.jwks_update_interval:
            return self.jwks
            
        try:
            # Fetch the OpenID configuration
            async with httpx.AsyncClient() as client:
                openid_config_response = await client.get(settings.openid_config_url)
                openid_config_response.raise_for_status()
                openid_config = openid_config_response.json()
                
                # Get the JWKS URI from the config
                jwks_uri = openid_config["jwks_uri"]
                
                # Fetch the JWKS
                jwks_response = await client.get(jwks_uri)
                jwks_response.raise_for_status()
                self.jwks = jwks_response.json()
                self.jwks_last_updated = now
                
                logger.info("Fetched new JWKS from Azure AD B2C", 
                            keys_count=len(self.jwks.get("keys", [])))
                
                return self.jwks
        except Exception as e:
            logger.error("Failed to fetch JWKS", exc_info=e)
            if self.jwks:
                # Use stale JWKS if we have it rather than failing
                return self.jwks
            raise
            
    async def validate_token(self, token: str) -> Dict:
        """
        Validate a JWT token issued by Azure AD B2C.
        
        Args:
            token: The JWT token to validate
            
        Returns:
            Dict: The decoded JWT claims if valid
            
        Raises:
            HTTPException: If the token is invalid
        """
        try:
            # Get the JWKS
            jwks = await self.get_jwks()
            
            # Extract header data from token without verification
            header = jwt.get_unverified_header(token)
            
            # Find the key
            rsa_key = {}
            for key in jwks.get("keys", []):
                if key["kid"] == header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "n": key["n"],
                        "e": key["e"],
                        "use": key.get("use", "sig")
                    }
                    break
                    
            if not rsa_key:
                logger.warning("No matching key found in JWKS", kid=header.get("kid"))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature key"
                )
                
            # Validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.AZURE_AD_B2C_CLIENT_ID,
                options={"verify_exp": True}
            )
            
            # Validate tenant
            if "tfp" in payload:
                policy = payload["tfp"]
                if policy != settings.AZURE_AD_B2C_SIGNIN_POLICY:
                    logger.warning("Invalid policy in token", policy=policy, expected=settings.AZURE_AD_B2C_SIGNIN_POLICY)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token policy"
                    )
            
            return payload
            
        except JWTError as e:
            logger.warning("JWT validation failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error("Token validation error", exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )


# Singleton instance
azure_ad_b2c_auth = AzureADB2CAuth()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT-based authentication with Azure AD B2C.
    
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
            "/metrics",
            "/.well-known/",  # For discovery endpoints
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
            # Validate token
            logger.debug("Validating JWT token")
            payload = await azure_ad_b2c_auth.validate_token(token)
            
            # Extract claims
            user_id = payload.get("sub")
            tenant_id = payload.get("extension_TenantId")  # Assumes custom attribute in B2C
            roles = payload.get("roles", [])
            
            # Add user info to request state
            request.state.user = payload
            request.state.user_id = user_id
            request.state.tenant_id = tenant_id
            request.state.roles = roles
            
            logger.debug(
                "User authenticated successfully", 
                user_id=request.state.user_id,
                tenant_id=tenant_id,
                roles=roles
            )
            
            # Proceed with request
            return await call_next(request)
            
        except HTTPException as e:
            # Pass through HTTP exceptions
            return Response(
                content=json.dumps({"detail": e.detail}),
                status_code=e.status_code,
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

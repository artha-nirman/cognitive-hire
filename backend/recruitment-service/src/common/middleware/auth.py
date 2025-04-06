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
            
            try:
                # Extract header data from token without verification
                header = jwt.get_unverified_header(token)
                logger.debug("Token header decoded", kid=header.get("kid"), alg=header.get("alg"))
            except Exception as e:
                logger.warning("Failed to decode token header", error=str(e), token_prefix=token[:10] if len(token) > 10 else token)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token format: {str(e)}"
                )
                
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
                
            # Decode token with more verbose logging
            try:
                # First try with audience validation
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=["RS256"],
                        audience=settings.AZURE_AD_B2C_CLIENT_ID,
                        options={"verify_exp": True}
                    )
                except JWTError as e:
                    # If audience validation fails, try without it (for ID tokens)
                    logger.debug("Audience validation failed, trying without strict validation", error=str(e))
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=["RS256"],
                        options={"verify_exp": True, "verify_aud": False}
                    )
            except JWTError as jwt_error:
                logger.warning("JWT decode failed", 
                             error=str(jwt_error), 
                             token_prefix=token[:10] if len(token) > 10 else token)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {str(jwt_error)}"
                )
            
            # Log successful token validation
            logger.debug(
                "Token validated successfully",
                token_type=payload.get("token_type", "unknown"),
                scopes=payload.get("scp", "").split(" ") if payload.get("scp") else [],
                aud=payload.get("aud"),
                iss=payload.get("iss"),
                sub=payload.get("sub", "unknown")
            )
            
            # Check policy if present
            if "tfp" in payload:
                policy = payload["tfp"]
                if policy != settings.AZURE_AD_B2C_SIGNIN_POLICY:
                    logger.warning("Invalid policy in token", 
                                  policy=policy, 
                                  expected=settings.AZURE_AD_B2C_SIGNIN_POLICY)
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
            "/docs/",
            "/docs/oauth2-redirect.html",
            "/docs/swagger-ui",
            "/redoc", 
            "/openapi.json", 
            "/health", 
            "/metrics",
            "/.well-known/",  # For discovery endpoints
            "/static/",  # Static files
            "/debug/",   # Debug endpoints
        ]
        
        # Authentication bypass setting
        self.bypass_enabled = settings.AUTH_BYPASS_ENABLED
        self.bypass_header = "X-Auth-Bypass"
        self.bypass_token = settings.AUTH_BYPASS_TOKEN
        
        if self.bypass_enabled:
            logger.warning(
                "Authentication bypass is ENABLED by configuration",
                bypass_header=self.bypass_header
            )
        
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
        # Log the current path for debugging
        logger.debug("Processing request", path=request.url.path)
        
        # Skip auth for public paths
        for path in self.public_paths:
            if request.url.path.startswith(path):
                logger.debug("Skipping auth for public path", path=request.url.path, matched_pattern=path)
                return await call_next(request)
        
        logger.debug("Path requires authentication", path=request.url.path)

        # Check if auth bypass is enabled and if a valid bypass token is present
        bypass_active = False
        
        if self.bypass_enabled and settings.ENVIRONMENT in ["development", "testing"]:
            # Get bypass token from header
            bypass_header_value = request.headers.get(self.bypass_header)
            
            # Only bypass if the header contains the correct token
            if bypass_header_value and bypass_header_value == self.bypass_token:
                logger.warning(
                    "Authentication bypassed with valid token",
                    path=request.url.path
                )
                bypass_active = True
            elif bypass_header_value:
                logger.warning(
                    "Authentication bypass attempt with invalid token",
                    path=request.url.path
                )
        
        if bypass_active:
            # Add a mock user to request state
            request.state.user = {
                "sub": "test-user-id",
                "name": "Test User",
                "roles": ["admin"],
                "tenant_id": request.headers.get("X-Test-Tenant-ID", "default-tenant")
            }
            request.state.user_id = "test-user-id"
            request.state.tenant_id = request.headers.get("X-Test-Tenant-ID", "default-tenant")
            request.state.roles = ["admin"]
            
            return await call_next(request)
        
        # Get token from header for regular authentication
        auth_header = request.headers.get("Authorization")
        logger.debug("Authorization header", header_value=auth_header[:15] + "..." if auth_header else "None")
        
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
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Validate token
            payload = await azure_ad_b2c_auth.validate_token(token)
            
            # Add user info to request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.roles = payload.get("roles", [])
            
            # Continue with request
            return await call_next(request)
            
        except HTTPException as e:
            # Re-raise HTTP exceptions from the token validation
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error("Authentication error", exc_info=e)
            return Response(
                content='{"detail":"Authentication error"}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json"
            )

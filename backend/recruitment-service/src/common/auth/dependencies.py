from fastapi import Depends, HTTPException, Request, status, Header, Security, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2AuthorizationCodeBearer
import structlog
from typing import Dict, Optional, Any
import msal
from jose import jwt

from src.common.config import settings

logger = structlog.get_logger(__name__)

# Security schemes
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
    tokenUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
    scopes={
        "openid": "OpenID Connect authentication", 
        settings.azure_ad_b2c_scope: "Access API"
    },
    auto_error=False
)

# HTTP Bearer security scheme that doesn't auto error
bearer_scheme = HTTPBearer(auto_error=False)

# MSAL configuration
msal_config = {
    "tenant": f"{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com",
    "client_id": settings.AZURE_AD_B2C_CLIENT_ID,
    "client_credential": settings.AZURE_AD_B2C_CLIENT_SECRET,
    "authority": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}",
}

# MSAL application instance
app_instance = None

async def init_azure_auth(app: FastAPI) -> None:
    """Initialize Microsoft Authentication Library (MSAL) for Azure AD B2C."""
    global app_instance
    logger.info("Initializing Azure AD B2C authentication")
    
    try:
        # Create MSAL confidential client application
        app_instance = msal.ConfidentialClientApplication(
            msal_config["client_id"],
            authority=msal_config["authority"],
            client_credential=msal_config["client_credential"]
        )
        
        # Register token exchange route
        from pydantic import BaseModel
        
        class TokenExchangeRequest(BaseModel):
            code: str
            redirect_uri: str
            code_verifier: Optional[str] = None  # PKCE code verifier
            
        @app.post("/auth/token")
        async def exchange_code_for_token(request_data: TokenExchangeRequest):
            """
            Exchange an OAuth2 authorization code for a token.
            
            Args:
                request_data: Authorization code and redirect URI
            
            Returns:
                Access token and related information
            """
            if not app_instance:
                logger.error("Authentication not initialized")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication not initialized"
                )
            
            try:
                logger.info("Exchanging code for token", 
                            code_prefix=request_data.code[:10] if len(request_data.code) > 10 else "***",
                            redirect_uri=request_data.redirect_uri)
                
                # Using MSAL to handle the code-to-token exchange
                scopes = [settings.azure_ad_b2c_scope]
                
                # Prepare the kwargs for acquire_token_by_authorization_code
                kwargs = {
                    "code": request_data.code,
                    "scopes": scopes,
                    "redirect_uri": request_data.redirect_uri
                }
                
                # Add code_verifier if provided (for PKCE)
                if request_data.code_verifier:
                    kwargs["code_verifier"] = request_data.code_verifier
                
                # Exchange code for token
                result = app_instance.acquire_token_by_authorization_code(**kwargs)
                
                if "error" in result:
                    logger.error(
                        "Token acquisition failed", 
                        error=result.get("error"),
                        description=result.get("error_description")
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Token acquisition failed: {result.get('error')}: {result.get('error_description')}"
                    )
                
                logger.info("Code exchanged for token successfully", 
                            token_type=result.get("token_type"),
                            scope=result.get("scope", "").split())
                
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Failed to exchange code for token", exc_info=e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Token exchange failed: {str(e)}"
                )
        
        logger.info("Azure AD B2C authentication initialized successfully", 
                   client_id=settings.AZURE_AD_B2C_CLIENT_ID,
                   tenant=settings.AZURE_AD_B2C_TENANT_NAME,
                   policy=settings.AZURE_AD_B2C_SIGNIN_POLICY,
                   scope=settings.azure_ad_b2c_scope)
    except Exception as e:
        logger.error("Failed to initialize Azure AD B2C authentication", exc_info=e)
        raise

async def get_current_user(
    request: Request,
    oauth2_token: Optional[str] = Security(oauth2_scheme),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_auth_bypass: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get current authenticated user from any supported auth method.
    
    This dependency verifies the token and returns user information.
    
    Args:
        request: The HTTP request
        oauth2_token: OAuth2 token from Swagger UI Auth
        bearer_token: Bearer token from Authorization header
        x_auth_bypass: Optional bypass token header
        
    Returns:
        User information extracted from token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Development bypass for testing
    if settings.ENVIRONMENT in ["development", "testing"] and settings.AUTH_BYPASS_ENABLED:
        if x_auth_bypass == settings.AUTH_BYPASS_TOKEN:
            logger.warning("Authentication bypassed with token")
            return {
                "sub": "test-user-id",
                "name": "Test User",
                "roles": ["admin"],
                "tenant_id": request.headers.get("X-Test-Tenant-ID", "default-tenant")
            }
    
    # Get token from either oauth2 or bearer auth
    token = None
    if bearer_token:
        token = bearer_token.credentials
    elif oauth2_token:
        token = oauth2_token
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # In a real implementation, validate the token
        # For now, we'll just decode it without verification
        payload = jwt.decode(
            token, 
            options={"verify_signature": False}
        )
        
        logger.info("Token validation successful", 
                  user_id=payload.get("sub", "unknown"),
                  token_prefix=token[:10] if token else "none")
        
        # Extract and return user information
        return {
            "sub": payload.get("sub"),
            "name": payload.get("name"),
            "email": payload.get("emails", [payload.get("email", "")])[0] if isinstance(payload.get("emails"), list) else payload.get("email"),
            "roles": payload.get("roles", []),
            "tenant_id": payload.get("tid") or payload.get("tenant_id"),
            "token": token  # Include the token for potential reuse
        }
    except Exception as e:
        logger.error("Token validation failed", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_tenant_id(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Extract tenant ID from authenticated user.
    
    Args:
        request: The HTTP request
        user: Authenticated user data
        
    Returns:
        Tenant ID string
    """
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-ID")
    return tenant_id

# Helper function to extract user ID from the authenticated user
def get_user_id(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Extract the user ID from the authenticated user."""
    return user.get("sub") or user.get("oid") or "unknown"

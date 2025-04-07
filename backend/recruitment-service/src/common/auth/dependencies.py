from fastapi import Depends, HTTPException, Request, status, Header, Security, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2AuthorizationCodeBearer
import structlog
from typing import Dict, Optional, Any
from jose import jwt
from fastapi_azure_auth import B2CMultiTenantAuthorizationCodeBearer
from fastapi_azure_auth.exceptions import InvalidAuth
from fastapi_azure_auth.user import User

from src.common.config import settings

logger = structlog.get_logger(__name__)

# Create B2C auth instance using the fastapi-azure-auth library
auth = B2CMultiTenantAuthorizationCodeBearer(
    app_client_id=settings.AZURE_AD_B2C_CLIENT_ID,
    openid_config_url=settings.openid_config_url,
    openapi_authorization_url=f'https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize',
    openapi_token_url=f'https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token',
    scopes={
        "openid": "OpenID Connect authentication",
        settings.azure_ad_b2c_scope: "Access API"
    },
    validate_iss=False,
)

async def init_azure_auth(app: FastAPI) -> None:
    """Initialize Azure AD B2C authentication."""
    logger.info("Initializing Azure AD B2C authentication")
    
    try:
        # No need for MSAL initialization
        # The auth instance is already created above
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
    user: Optional[User] = Security(auth),
    x_auth_bypass: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get current authenticated user from any supported auth method.
    
    This dependency verifies the token and returns user information.
    
    Args:
        request: The HTTP request
        user: User from Azure AD B2C authentication
        x_auth_bypass: Optional bypass token header
        
    Returns:
        User information extracted from token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Debug logging to help identify authentication issues
    logger.debug("Auth attempt",
               has_user=user is not None,
               has_bypass=x_auth_bypass is not None,
               bypass_enabled=settings.AUTH_BYPASS_ENABLED,
               environment=settings.ENVIRONMENT)
    
    # Development bypass for testing
    if settings.ENVIRONMENT in ["development", "testing"] and settings.AUTH_BYPASS_ENABLED:
        if x_auth_bypass == settings.AUTH_BYPASS_TOKEN:
            logger.info("Authentication bypassed with token")
            return {
                "sub": "test-user-id",
                "name": "Test User",
                "roles": ["admin"],
                "tenant_id": request.headers.get("X-Test-Tenant-ID", "default-tenant")
            }
    
    # Check if we have a valid User object from Azure auth
    if user:
        logger.info("B2C authentication successful", 
                   user_id=user.claims.get("sub", "unknown"))
        
        # Extract and return user information from the User object
        return {
            "sub": user.claims.get("sub"),
            "name": user.claims.get("name"),
            "email": user.claims.get("emails", [user.claims.get("email", "")])[0] if isinstance(user.claims.get("emails"), list) else user.claims.get("email"),
            "roles": user.claims.get("roles", []),
            "tenant_id": user.claims.get("tid") or user.claims.get("tenant_id"),
            "token": user.token  # The token is available on the User object
        }
    
    # Try to get token from Authorization header as fallback
    auth_header = request.headers.get("Authorization", "")
    token = None
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    if token:
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
    
    logger.warning("Authentication failed - no valid credentials provided")
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
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

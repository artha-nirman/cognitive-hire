from fastapi import Depends, HTTPException, Request, status, Header
from typing import Dict, Optional, Any
from fastapi_azure_auth import B2CMultiTenantAuthorizationCodeBearer
from fastapi_azure_auth.user import User

from src.common.config import settings
from src.common.logging import get_logger

# Get a structured logger
logger = get_logger(__name__)

# Create B2C auth instance as per the library specs
azure_scheme = B2CMultiTenantAuthorizationCodeBearer(
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

async def get_current_user(
    request: Request,
    user: Optional[User] = Depends(azure_scheme),
    x_auth_bypass: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get current authenticated user from Azure AD B2C or development bypass.
    """
    logger.debug("Auth attempt", 
               path=request.url.path,
               has_auth_bypass=bool(x_auth_bypass))
    
    # Development bypass for testing
    if settings.ENVIRONMENT in ["development", "testing"] and settings.AUTH_BYPASS_ENABLED:
        if x_auth_bypass == settings.AUTH_BYPASS_TOKEN:
            logger.info("Auth bypass successful", path=request.url.path)
            return {
                "sub": "test-user-id",
                "name": "Test User",
                "roles": ["admin"],
                "tenant_id": request.headers.get("X-Test-Tenant-ID", "default-tenant")
            }
        elif x_auth_bypass:
            logger.warning("Invalid auth bypass token", path=request.url.path)
    
    # Azure AD B2C authentication
    if user:
        logger.info("B2C auth successful", user_id=user.claims.get("sub", "unknown"), path=request.url.path)
        return {
            "sub": user.claims.get("sub"),
            "name": user.claims.get("name"),
            "email": user.claims.get("emails", [user.claims.get("email", "")])[0] if isinstance(user.claims.get("emails"), list) else user.claims.get("email"),
            "roles": user.claims.get("roles", []),
            "tenant_id": user.claims.get("tid") or user.claims.get("tenant_id"),
            "token": user.token
        }
    
    # Authentication failed
    logger.warning("Authentication failed - no valid credentials", path=request.url.path)
    
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

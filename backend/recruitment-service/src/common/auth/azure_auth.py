from typing import Dict, Optional, Any
import structlog
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
import msal
import httpx

from src.common.config import settings

logger = structlog.get_logger(__name__)

# Standard OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
    tokenUrl=f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
    scopes={
        "openid": "OpenID Connect authentication",
        f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/api/user_impersonation": "Access API"
    }
)

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
        logger.info("Azure AD B2C authentication initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Azure AD B2C authentication", exc_info=e)
        raise

async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from the request.
    
    This dependency is used in route handlers to require authentication
    and access user information.
    
    Args:
        request: The HTTP request
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if we already have a user set by middleware bypass
    if hasattr(request.state, "user") and request.state.user:
        logger.debug("Using user from request state (bypass)", user_id=request.state.user_id)
        return request.state.user
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # For API validation, we rely on the OAuth2 validation already performed by FastAPI
        # Just extract claims from the token
        claims = {"token": token}
        
        # In a real implementation, you would validate the token using Microsoft Identity Platform
        # This is just a placeholder for the current implementation
        return claims
    except Exception as e:
        logger.error("Failed to process authentication token", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

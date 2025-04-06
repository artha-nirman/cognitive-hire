from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from src.common.auth.azure_auth import validate_token
from src.common.config import settings

logger = structlog.get_logger(__name__)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate token and return user info."""
    try:
        payload = await validate_token(credentials.credentials)
        return payload
    except Exception as e:
        logger.warning("Authentication failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_tenant_id(request: Request, user = Depends(get_current_user)):
    """Extract tenant ID from authenticated user."""
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-ID")
    return tenant_id

from fastapi import Depends, HTTPException, Request, Header
from typing import Optional
from jose import jwt  # Use jose.jwt instead of importing jwt directly

from app.core.config import settings
from app.core.logging import logger
from app.services.auth_service import AuthService

def get_auth_service() -> AuthService:
    """Dependency to get auth service"""
    return AuthService()

async def get_current_user(request: Request):
    """Get current user from request"""
    # Check if we're in development mode with bypass enabled
    if settings.ENVIRONMENT in ["development", "test"] and settings.AUTH_BYPASS:
        x_bypass_auth = request.headers.get("X-Bypass-Auth")
        if x_bypass_auth == settings.AUTH_BYPASS_SECRET:
            x_test_user = request.headers.get("X-Test-User") or "admin"
            test_users = {
                "admin": {"id": "test-admin", "roles": ["admin"], "permissions": ["*"]},
                "recruiter": {"id": "test-recruiter", "roles": ["recruiter"], "permissions": ["jobs:read", "candidates:read"]},
                "candidate": {"id": "test-candidate", "roles": ["candidate"], "permissions": ["profile:read", "profile:write"]},
            }
            return test_users.get(x_test_user, test_users["admin"])
    
    # Otherwise, validate the token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user info
        user_id = payload.get("sub")
        email = payload.get("email")
        roles = payload.get("roles", [])
        
        logger.info(f"Retrieved user from token: {user_id}", extra={"event": "get_current_user_success", "user_id": user_id})
        
        return {
            "id": user_id,
            "email": email,
            "roles": roles,
            "permissions": []  # Would be populated from database
        }
    except jwt.PyJWTError as e:
        logger.warning(f"Invalid token: {str(e)}", extra={"event": "get_current_user_failure"})
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    """Dependency to require a specific permission"""
    async def _require_permission(user = Depends(get_current_user)):
        # Admin role always has all permissions
        if "admin" in user.get("roles", []):
            return user
            
        # Check for wildcard permission
        if "*" in user.get("permissions", []):
            return user
            
        # Check for specific permission
        if permission in user.get("permissions", []):
            return user
            
        # If we have a colon, check for wildcard domain permission
        if ":" in permission:
            domain = permission.split(":")[0]
            domain_wildcard = f"{domain}:*"
            if domain_wildcard in user.get("permissions", []):
                return user
        
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return _require_permission

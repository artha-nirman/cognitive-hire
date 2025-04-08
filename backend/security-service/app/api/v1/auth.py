from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
from app.schemas.auth import TokenResponse, LoginRequest, RegisterRequest
from app.core.logging import logger
from app.core.config import settings
from app.services.auth_service import AuthService
from app.dependencies.auth import get_auth_service

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handle user login through Azure AD B2C or development bypass
    """
    logger.info(f"Login attempt for user: {request.username}", extra={"event": "login_attempt"})
    
    try:
        token_data = await auth_service.authenticate_user(request.username, request.password)
        logger.info(f"Login successful for user: {request.username}", extra={"event": "login_success"})
        return token_data
    except Exception as e:
        logger.warning(
            f"Login failed for user: {request.username}", 
            extra={"event": "login_failure", "error": str(e)}
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    """
    logger.info(f"Registration attempt for user: {request.email}", extra={"event": "registration_attempt"})
    
    try:
        token_data = await auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            user_type=request.user_type
        )
        logger.info(f"Registration successful for user: {request.email}", extra={"event": "registration_success"})
        return token_data
    except Exception as e:
        logger.warning(
            f"Registration failed for user: {request.email}", 
            extra={"event": "registration_failure", "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    refresh_token: str = Header(...)
):
    """
    Refresh an access token using a refresh token
    """
    logger.info("Token refresh requested", extra={"event": "token_refresh_attempt"})
    
    try:
        token_data = await auth_service.refresh_token(refresh_token)
        logger.info("Token refresh successful", extra={"event": "token_refresh_success"})
        return token_data
    except Exception as e:
        logger.warning(
            "Token refresh failed", 
            extra={"event": "token_refresh_failure", "error": str(e)}
        )
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    access_token: str = Header(...)
):
    """
    Logout a user by invalidating their token
    """
    logger.info("Logout requested", extra={"event": "logout_attempt"})
    
    try:
        await auth_service.logout(access_token)
        logger.info("Logout successful", extra={"event": "logout_success"})
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.warning(
            "Logout failed", 
            extra={"event": "logout_failure", "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    x_bypass_auth: Optional[str] = Header(None),
    x_test_user: Optional[str] = Header(None)
):
    """
    Get current user information
    """
    # Development bypass for testing
    if settings.ENVIRONMENT in ["development", "test"] and settings.AUTH_BYPASS and x_bypass_auth == settings.AUTH_BYPASS_SECRET:
        test_user = x_test_user or "admin"
        test_users = {
            "admin": {"id": "test-admin", "roles": ["admin"], "name": "Test Admin"},
            "recruiter": {"id": "test-recruiter", "roles": ["recruiter"], "name": "Test Recruiter"},
            "candidate": {"id": "test-candidate", "roles": ["candidate"], "name": "Test Candidate"},
        }
        return test_users.get(test_user, test_users["admin"])
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        user_data = await auth_service.get_current_user(token)
        return user_data
    except Exception as e:
        logger.warning(
            "Failed to get current user", 
            extra={"event": "get_current_user_failure", "error": str(e)}
        )
        raise HTTPException(status_code=401, detail="Invalid token")

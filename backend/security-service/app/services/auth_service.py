from typing import Dict, Optional
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
import uuid
from jose import jwt  # Use jose.jwt instead of importing jwt directly

from app.core.config import settings
from app.core.logging import logger
from app.schemas.auth import TokenResponse

class AuthService:
    """Service for authentication and authorization"""
    
    async def authenticate_user(self, username: str, password: str) -> TokenResponse:
        """Authenticate a user with username and password"""
        logger.info(f"Authenticating user: {username}", extra={"event": "user_auth_attempt"})
        
        # Mock implementation until database is set up
        # In a real implementation, we would:
        # 1. Look up user in database
        # 2. Verify password
        # 3. Generate tokens
        
        # For now, allow a test login
        if username == "admin@example.com" and password == "adminpassword":
            token = self._generate_token(
                {"sub": "test-admin", "email": username, "roles": ["admin"]}
            )
            
            logger.info(f"User authenticated: {username}", extra={"event": "user_auth_success"})
            
            return TokenResponse(
                access_token=token,
                token_type="Bearer",
                expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
                refresh_token="mock_refresh_token",
                user_id="test-admin",
                email=username
            )
        
        logger.warning(f"Authentication failed for user: {username}", extra={"event": "user_auth_failure"})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    async def register_user(self, email: str, password: str, full_name: str, user_type: str) -> TokenResponse:
        """Register a new user"""
        logger.info(f"Registering new user: {email}", extra={"event": "user_register_attempt"})
        
        # Mock implementation until database is set up
        # In a real implementation, we would:
        # 1. Validate email is not taken
        # 2. Hash password
        # 3. Create user record
        # 4. Generate tokens
        
        user_id = str(uuid.uuid4())
        token = self._generate_token(
            {"sub": user_id, "email": email, "roles": [user_type]}
        )
        
        logger.info(f"User registered: {email}", extra={"event": "user_register_success", "user_id": user_id})
        
        return TokenResponse(
            access_token=token,
            token_type="Bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
            refresh_token="mock_refresh_token",
            user_id=user_id,
            email=email
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh an access token"""
        logger.info("Token refresh requested", extra={"event": "token_refresh_attempt"})
        
        # Mock implementation until database is set up
        # In a real implementation, we would:
        # 1. Validate refresh token
        # 2. Look up user
        # 3. Generate new tokens
        
        # For demo, assume it's a valid token and generate a new one
        if refresh_token == "mock_refresh_token":
            token = self._generate_token(
                {"sub": "test-admin", "email": "admin@example.com", "roles": ["admin"]}
            )
            
            logger.info("Token refresh successful", extra={"event": "token_refresh_success"})
            
            return TokenResponse(
                access_token=token,
                token_type="Bearer",
                expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
                refresh_token="mock_refresh_token",
                user_id="test-admin",
                email="admin@example.com"
            )
        
        logger.warning("Token refresh failed: invalid token", extra={"event": "token_refresh_failure"})
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    async def logout(self, access_token: str) -> bool:
        """Logout a user"""
        logger.info("Logout requested", extra={"event": "logout_attempt"})
        
        # Mock implementation until database is set up
        # In a real implementation, we would:
        # 1. Add token to blacklist
        # 2. Revoke refresh tokens
        
        logger.info("Logout successful", extra={"event": "logout_success"})
        return True
    
    async def get_current_user(self, token: str) -> Dict:
        """Get current user from token"""
        logger.debug("Getting current user from token", extra={"event": "get_current_user"})
        
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
                "roles": roles
            }
        except jwt.PyJWTError as e:
            logger.warning(f"Invalid token: {str(e)}", extra={"event": "get_current_user_failure"})
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def _generate_token(self, data: dict) -> str:
        """Generate a JWT token"""
        # Create token expiration
        expires = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        
        # Create token payload
        payload = data.copy()
        payload.update({"exp": expires})
        
        # Generate token
        token = jwt.encode(
            payload, 
            settings.JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token

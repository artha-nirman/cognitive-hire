from pydantic import BaseModel, EmailStr, Field, AnyHttpUrl
from typing import Optional, Dict, Any, List

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    user_id: str
    email: EmailStr

class LoginRequest(BaseModel):
    username: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    user_type: str = Field(..., description="User type (candidate, recruiter, admin)")

class OAuthLoginRequest(BaseModel):
    """Request to initiate OAuth login flow"""
    redirect_uri: AnyHttpUrl
    state: Optional[str] = None
    prompt: Optional[str] = None

class OAuthLoginResponse(BaseModel):
    """Response with OAuth authorization URL"""
    authorization_url: AnyHttpUrl

class OAuthCallbackRequest(BaseModel):
    """Request parameters for OAuth callback"""
    code: str
    state: Optional[str] = None
    redirect_uri: AnyHttpUrl

class UserInfo(BaseModel):
    """User information returned by /me endpoint"""
    id: str
    email: EmailStr
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    user_type: str
    picture: Optional[str] = None
    identity_provider: Optional[str] = None

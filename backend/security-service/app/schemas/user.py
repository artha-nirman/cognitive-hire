from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    user_type: str = Field(..., description="User type (candidate, recruiter, admin)")

class UserCreate(UserBase):
    # For AD B2C users, password may not be directly managed by our system
    password: Optional[str] = Field(None, min_length=8)
    external_id: Optional[str] = None
    identity_provider: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    user_type: Optional[str] = None
    password: Optional[str] = None
    
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[str] = []
    external_auth: bool = False  # Indicates if user authenticates via external provider
    identity_provider: Optional[str] = None
    
    class Config:
        orm_mode = True

class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int

class ExternalUserCreate(BaseModel):
    """Create a new user from external auth provider"""
    external_id: str
    identity_provider: str  
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str
    picture_url: Optional[str] = None
    claims: Optional[Dict[str, Any]] = None

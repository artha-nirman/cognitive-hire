from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime

class AzureADUserInfo(BaseModel):
    """Schema for user information from Azure AD B2C token"""
    sub: str = Field(..., description="Subject identifier, unique for each user")
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    roles: List[str] = []
    tid: Optional[str] = None  # Tenant ID
    oid: Optional[str] = None  # Object ID
    identities: Optional[List[Dict[str, Any]]] = None
    iss: Optional[str] = None  # Issuer
    exp: Optional[int] = None  # Expiration time

class OAuthConfig(BaseModel):
    """Configuration for OAuth endpoints"""
    tenant_id: str
    client_id: str 
    client_secret: Optional[str] = None
    policy_name: str = "B2C_1_signupsignin"
    scope: str = "openid profile email"
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    
    def get_authorization_endpoint(self) -> str:
        if self.authorization_endpoint:
            return self.authorization_endpoint
        return f"https://{self.tenant_id}.b2clogin.com/{self.tenant_id}.onmicrosoft.com/{self.policy_name}/oauth2/v2.0/authorize"
    
    def get_token_endpoint(self) -> str:
        if self.token_endpoint:
            return self.token_endpoint
        return f"https://{self.tenant_id}.b2clogin.com/{self.tenant_id}.onmicrosoft.com/{self.policy_name}/oauth2/v2.0/token"
    
    def get_jwks_uri(self) -> str:
        if self.jwks_uri:
            return self.jwks_uri
        return f"https://{self.tenant_id}.b2clogin.com/{self.tenant_id}.onmicrosoft.com/{self.policy_name}/discovery/v2.0/keys"

class OAuthTokenRequest(BaseModel):
    """OAuth token request parameters"""
    grant_type: str = "authorization_code"
    client_id: str
    scope: str
    code: Optional[str] = None
    redirect_uri: str
    code_verifier: Optional[str] = None
    client_secret: Optional[str] = None

class OAuthTokenResponse(BaseModel):
    """OAuth token response from Azure AD B2C"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None

class UserExternalMapping(BaseModel):
    """Maps external identity to internal user record"""
    id: str
    user_id: str
    provider: str = "azure_ad_b2c" 
    external_id: str
    email: EmailStr
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

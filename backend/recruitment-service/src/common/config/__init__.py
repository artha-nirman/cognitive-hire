from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    
    All configuration values can be set through environment variables.
    For local development, values can be defined in a .env file.
    
    Configuration hierarchy:
    1. Environment variables
    2. .env file values (if present)
    3. Default values defined here
    """
    
    # Application settings
    APP_NAME: str = "recruitment-service"
    ENVIRONMENT: str = "development"  # development, testing, production
    LOG_LEVEL: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "json"  # json or console
    
    # Security
    AUTH_SECRET_KEY: str = "default-dev-key-replace-in-production"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth bypass config for development/testing
    AUTH_BYPASS_ENABLED: bool = True
    AUTH_BYPASS_TOKEN: str = "cog-hire-dev-bypass-token-apr-2025"
    
    # Azure AD B2C Settings
    AZURE_AD_B2C_TENANT_NAME: str = "cognitivehire"
    AZURE_AD_B2C_CLIENT_ID: str = ""  # No default, must be provided
    AZURE_AD_B2C_CLIENT_SECRET: str = ""  # No default, must be provided
    AZURE_AD_B2C_SIGNIN_POLICY: str = "B2C_1_signupsignin1"
    AZURE_AD_B2C_RESPONSE_MODE: str = "query"
    AZURE_AD_B2C_RESPONSE_TYPE: str = "code"
    
    # Scope configuration
    AZURE_AD_B2C_SCOPE_RESOURCE: str = "api"
    AZURE_AD_B2C_SCOPE_PERMISSION: str = "user_impersonation"
    
    # API Documentation
    SWAGGER_UI_CLIENT_ID: Optional[str] = None  # Falls back to AZURE_AD_B2C_CLIENT_ID if None
    
    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "*"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/recruitment"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Event system
    EVENT_BUS_URL: Optional[str] = None
    
    # External services
    CANDIDATE_SERVICE_URL: Optional[str] = None
    WORKFLOW_SERVICE_URL: Optional[str] = None
    
    @property
    def authority_url(self) -> str:
        """Return the complete authority URL for Azure AD B2C."""
        return f"https://{self.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{self.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{self.AZURE_AD_B2C_SIGNIN_POLICY}"
        
    @property
    def openid_config_url(self) -> str:
        """Return the OpenID configuration URL for Azure AD B2C."""
        return f"{self.authority_url}/v2.0/.well-known/openid-configuration"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list, handling both string and list inputs."""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS
    
    @property
    def async_database_url(self) -> str:
        """
        Convert standard PostgreSQL URL to use the asyncpg driver.
        
        Returns:
            Properly formatted database URL for asyncio use
        """
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL
    
    @property
    def azure_ad_b2c_scope(self) -> str:
        """
        Return the properly formatted scope for Azure AD B2C.
        
        Constructs the scope using the recommended format:
        https://{tenant}.onmicrosoft.com/{client_id}/{permission}
        
        The specific format may vary based on how the API is registered in Azure AD B2C.
        """
        # Standard format used by most Azure AD B2C setups
        return f"https://{self.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{self.AZURE_AD_B2C_CLIENT_ID}/{self.AZURE_AD_B2C_SCOPE_PERMISSION}"
        
    @property
    def azure_ad_b2c_scopes(self) -> list[str]:
        """Return a list of scopes required for authentication."""
        return ["openid", self.azure_ad_b2c_scope]
    
    @property
    def effective_swagger_client_id(self) -> str:
        """Return the client ID to use for Swagger UI."""
        return self.SWAGGER_UI_CLIENT_ID or self.AZURE_AD_B2C_CLIENT_ID
    
    @property
    def oauth2_redirect_path(self) -> str:
        """Return the OAuth2 redirect path for Swagger UI."""
        return "/docs/oauth2-redirect"
    
    @property
    def oauth2_redirect_url(self) -> str:
        """
        Return the full OAuth2 redirect URL including hostname.
        This should match the redirect URL registered in Azure AD B2C.
        """
        # For local development, use localhost
        if self.ENVIRONMENT == "development":
            return f"http://localhost:8000{self.oauth2_redirect_path}"
        # For production, use a configured domain or default
        return f"https://api.cognitivehire.com{self.oauth2_redirect_path}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

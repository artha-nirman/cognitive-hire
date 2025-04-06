from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    
    All configuration values can be set through environment variables.
    For local development, values can be defined in a .env file.
    """
    
    # Application settings
    APP_NAME: str = "recruitment-service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "json"  # json or console
    
    # Security
    AUTH_SECRET_KEY: str
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth bypass config for development/testing
    AUTH_BYPASS_ENABLED: bool = True
    AUTH_BYPASS_TOKEN: Optional[str] = "cog-hire-dev-bypass-token-apr-2025"
    
    # Azure AD B2C Settings
    AZURE_AD_B2C_TENANT_NAME: str
    AZURE_AD_B2C_CLIENT_ID: str
    AZURE_AD_B2C_CLIENT_SECRET: str
    AZURE_AD_B2C_SIGNIN_POLICY: str = "B2C_1_signupsignin1"
    AZURE_AD_B2C_AUTHORITY: str = "{tenant_name}.b2clogin.com"
    AZURE_AD_B2C_SCOPE: str = "https://{tenant_name}.onmicrosoft.com/api/user_impersonation"
    
    # Swagger UI OAuth Settings
    SWAGGER_UI_CLIENT_ID: str  # Same as AZURE_AD_B2C_CLIENT_ID or specific client for Swagger
    SWAGGER_UI_OAUTH_REDIRECT_URL: str = "http://localhost:8000/docs/oauth2-redirect.html"
    
    # CORS - Fix to parse comma-separated string from .env
    CORS_ORIGINS: Union[str, List[str]] = "*"
    
    # Database
    DATABASE_URL: str
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

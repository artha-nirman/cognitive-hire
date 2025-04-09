from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Dynamically load the correct .env file based on the ENVIRONMENT variable
environment = os.getenv("ENVIRONMENT", "development")
if environment == "test":
    load_dotenv(".env.test-integration")
else:
    load_dotenv(".env")

class Settings(BaseSettings):
    # General settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = ENVIRONMENT == "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database settings
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Auth settings
    AZURE_AD_B2C_TENANT_ID: Optional[str] = None
    AZURE_AD_B2C_CLIENT_ID: Optional[str] = None
    AZURE_AD_B2C_CLIENT_SECRET: Optional[str] = None
    AZURE_AD_B2C_POLICY_NAME: Optional[str] = None
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Auth bypass for development
    AUTH_BYPASS: bool = False
    AUTH_BYPASS_SECRET: Optional[str] = "dev-bypass-secret"  # Set a default for tests
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "security-service"
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

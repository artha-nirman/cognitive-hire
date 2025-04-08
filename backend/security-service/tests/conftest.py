import pytest
from fastapi.testclient import TestClient
import os
import sys
from typing import Generator

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.core.config import settings

# Ensure AUTH_BYPASS is enabled for tests
settings.ENVIRONMENT = "test"
settings.AUTH_BYPASS = True
settings.AUTH_BYPASS_SECRET = "dev-bypass-secret"

@pytest.fixture
def test_client() -> Generator:
    """
    Create a test client for FastAPI app
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture
def user_service() -> UserService:
    """
    Get a user service instance for testing
    """
    return UserService()

@pytest.fixture
def auth_service() -> AuthService:
    """
    Get an auth service instance for testing
    """
    return AuthService()

@pytest.fixture
def role_service() -> RoleService:
    """
    Get a role service instance for testing
    """
    return RoleService()

@pytest.fixture
def permission_service() -> PermissionService:
    """
    Get a permission service instance for testing
    """
    return PermissionService()

@pytest.fixture
def auth_header() -> dict:
    """
    Create a mock authorization header for testing
    """
    # For testing with bypass
    return {
        "X-Bypass-Auth": "dev-bypass-secret",
        "X-Test-User": "admin"
    }

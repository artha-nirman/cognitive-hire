import os
import pytest
import requests
import logging
from urllib.parse import urlparse, parse_qs
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.auth import OAuthLoginRequest, OAuthCallbackRequest

# Skip tests if integration testing is not enabled
pytestmark = pytest.mark.skipif(
    os.environ.get('RUN_INTEGRATION_TESTS') != 'true',
    reason="Integration tests only run when RUN_INTEGRATION_TESTS=true"
)

# Test client
client = TestClient(app)

# Configure logger
logger = logging.getLogger("test_logger")
logging.basicConfig(level=logging.INFO)

def test_oauth_login_generates_valid_url():
    """Test that the OAuth login endpoint generates a valid Azure AD B2C authorization URL"""
    request_data = {
        "redirect_uri": "http://localhost:8000/docs/oauth2-redirect",
        "state": "test_state"
    }
    
    response = client.post("/api/v1/auth/oauth/login", json=request_data)
    
    assert response.status_code == 200
    result = response.json()
    assert "authorization_url" in result
    
    # Log the authorization URL
    logger.info(f"Generated Authorization URL: {result['authorization_url']}")
    
    # Parse URL to verify it has the correct structure
    url = urlparse(result["authorization_url"])
    query = parse_qs(url.query)
    
    assert url.netloc.endswith("b2clogin.com")
    assert "client_id" in query
    assert query.get("redirect_uri")[0] == request_data["redirect_uri"]
    assert query.get("state")[0] == request_data["state"]

def test_oauth_callback_with_valid_code():
    """Test the OAuth callback endpoint with a valid authorization code"""
    callback_data = {
        "code": "mock_authorization_code",
        "state": "test_state"
    }
    
    response = client.post("/api/v1/auth/oauth/callback", json=callback_data)
    
    assert response.status_code == 200
    result = response.json()
    assert "access_token" in result
    assert "refresh_token" in result
    assert "expires_in" in result
    logger.info(f"OAuth Callback Response: {result}")


def test_oauth_callback_with_invalid_code():
    """Test the OAuth callback endpoint with an invalid authorization code"""
    callback_data = {
        "code": "invalid_code",
        "state": "test_state"
    }
    
    response = client.post("/api/v1/auth/oauth/callback", json=callback_data)
    
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    logger.info(f"OAuth Callback Error Response: {result}")


def test_oauth_login_with_missing_redirect_uri():
    """Test the OAuth login endpoint with a missing redirect URI"""
    request_data = {
        "state": "test_state"
    }
    
    response = client.post("/api/v1/auth/oauth/login", json=request_data)
    
    assert response.status_code == 422  # Unprocessable Entity
    result = response.json()
    assert "detail" in result
    logger.info(f"OAuth Login Error Response: {result}")


def test_oauth_login_with_invalid_state():
    """Test the OAuth login endpoint with an invalid state"""
    request_data = {
        "redirect_uri": "http://localhost:8000/docs/oauth2-redirect",
        "state": None  # Invalid state
    }
    
    response = client.post("/api/v1/auth/oauth/login", json=request_data)
    
    assert response.status_code == 422  # Unprocessable Entity
    result = response.json()
    assert "detail" in result
    logger.info(f"OAuth Login Error Response: {result}")

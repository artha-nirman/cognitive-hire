from fastapi.testclient import TestClient
import pytest

def test_login_success(test_client: TestClient):
    """Test successful login"""
    # Arrange
    login_data = {
        "username": "admin@example.com",
        "password": "adminpassword"
    }
    
    # Act
    response = test_client.post("/api/v1/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"
    assert "user_id" in data
    assert "email" in data
    assert data["email"] == login_data["username"]

def test_login_failure(test_client: TestClient):
    """Test failed login"""
    # Arrange
    login_data = {
        "username": "admin@example.com",
        "password": "wrongpassword"
    }
    
    # Act
    response = test_client.post("/api/v1/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 401

def test_get_current_user(test_client: TestClient, auth_header: dict):
    """Test getting the current user profile"""
    # Act
    response = test_client.get("/api/v1/auth/me", headers=auth_header)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "roles" in data
    assert "admin" in data["roles"]

def test_register_user(test_client: TestClient):
    """Test user registration"""
    # Arrange
    register_data = {
        "email": "newuser@example.com",
        "password": "securepassword",
        "full_name": "New User",
        "user_type": "candidate"
    }
    
    # Act
    response = test_client.post("/api/v1/auth/register", json=register_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert "user_id" in data
    assert "email" in data
    assert data["email"] == register_data["email"]

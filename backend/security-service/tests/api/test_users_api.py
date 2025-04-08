from fastapi.testclient import TestClient
import pytest
import json

def test_list_users(test_client: TestClient, auth_header: dict):
    """Test the users list endpoint"""
    # Act
    response = test_client.get("/api/v1/users", headers=auth_header)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

def test_get_user(test_client: TestClient, auth_header: dict):
    """Test getting a specific user"""
    # Arrange
    user_id = "test-admin"
    
    # Act
    response = test_client.get(f"/api/v1/users/{user_id}", headers=auth_header)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "admin@example.com"

def test_create_user(test_client: TestClient, auth_header: dict):
    """Test creating a user"""
    # Arrange
    user_data = {
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "is_active": True,
        "user_type": "recruiter",
        "password": "securepassword"
    }
    
    # Act
    response = test_client.post(
        "/api/v1/users", 
        json=user_data,
        headers=auth_header
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data

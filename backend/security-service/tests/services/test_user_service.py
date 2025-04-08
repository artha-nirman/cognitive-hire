import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate

@pytest.mark.asyncio
async def test_create_user(user_service: UserService):
    """Test creating a user"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        user_type="admin"
    )
    
    # Act
    result = await user_service.create_user(user_data)
    
    # Assert
    assert result is not None
    assert result.email == user_data.email
    assert result.first_name == user_data.first_name
    assert result.last_name == user_data.last_name
    assert result.is_active == user_data.is_active
    assert result.user_type == user_data.user_type
    assert result.id is not None

@pytest.mark.asyncio
async def test_get_user(user_service: UserService):
    """Test getting a user"""
    # Arrange - using a known test ID that returns a mock user
    user_id = "test-admin"
    
    # Act
    result = await user_service.get_user(user_id)
    
    # Assert
    assert result is not None
    assert result.id == user_id
    assert result.email == "admin@example.com"

@pytest.mark.asyncio
async def test_get_nonexistent_user(user_service: UserService):
    """Test getting a user that doesn't exist"""
    # Arrange
    user_id = "nonexistent-user"
    
    # Act
    result = await user_service.get_user(user_id)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_update_user(user_service: UserService):
    """Test updating a user"""
    # Arrange
    user_id = "test-admin"
    update_data = UserUpdate(
        first_name="Updated",
        last_name="Name"
    )
    
    # Act
    result = await user_service.update_user(user_id, update_data)
    
    # Assert
    assert result is not None
    assert result.id == user_id
    assert result.first_name == "Updated"
    assert result.last_name == "Name"

@pytest.mark.asyncio
async def test_list_users(user_service: UserService):
    """Test listing users"""
    # Act
    users, total = await user_service.list_users()
    
    # Assert
    assert users is not None
    assert len(users) > 0
    assert total >= len(users)
    assert isinstance(users[0].id, str)

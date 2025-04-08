from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Optional
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.logging import logger
from app.services.user_service import UserService
from app.dependencies.user import get_user_service
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new user (Admin only)
    """
    logger.info(f"Creating new user: {user.email}", extra={"event": "user_create_attempt"})
    
    try:
        # Check if user has admin role
        if "admin" not in current_user.get("roles", []):
            logger.warning(
                f"Unauthorized attempt to create user by: {current_user.get('id')}", 
                extra={"event": "unauthorized_user_create"}
            )
            raise HTTPException(status_code=403, detail="Not authorized to create users")
        
        created_user = await user_service.create_user(user)
        logger.info(f"User created: {user.email}", extra={"event": "user_create_success"})
        return created_user
    except Exception as e:
        logger.error(
            f"Failed to create user: {user.email}", 
            extra={"event": "user_create_failure", "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """
    List users (Admin only)
    """
    logger.info("Listing users", extra={"event": "user_list_attempt"})
    
    try:
        # Check if user has admin role
        if "admin" not in current_user.get("roles", []):
            logger.warning(
                f"Unauthorized attempt to list users by: {current_user.get('id')}", 
                extra={"event": "unauthorized_user_list"}
            )
            raise HTTPException(status_code=403, detail="Not authorized to list users")
        
        users, total = await user_service.list_users(skip, limit)
        logger.info(f"Listed {len(users)} users", extra={"event": "user_list_success"})
        return {"items": users, "total": total}
    except Exception as e:
        logger.error(
            "Failed to list users", 
            extra={"event": "user_list_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a user by ID
    """
    logger.info(f"Getting user: {user_id}", extra={"event": "user_get_attempt"})
    
    try:
        # Check if user is requesting their own record or is an admin
        if current_user.get("id") != user_id and "admin" not in current_user.get("roles", []):
            logger.warning(
                f"Unauthorized attempt to get user {user_id} by: {current_user.get('id')}", 
                extra={"event": "unauthorized_user_get"}
            )
            raise HTTPException(status_code=403, detail="Not authorized to access this user")
        
        user = await user_service.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}", extra={"event": "user_get_not_found"})
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User found: {user_id}", extra={"event": "user_get_success"})
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get user: {user_id}", 
            extra={"event": "user_get_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user: UserUpdate,
    user_id: str = Path(...),
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a user
    """
    logger.info(f"Updating user: {user_id}", extra={"event": "user_update_attempt"})
    
    try:
        # Check if user is updating their own record or is an admin
        if current_user.get("id") != user_id and "admin" not in current_user.get("roles", []):
            logger.warning(
                f"Unauthorized attempt to update user {user_id} by: {current_user.get('id')}", 
                extra={"event": "unauthorized_user_update"}
            )
            raise HTTPException(status_code=403, detail="Not authorized to update this user")
        
        updated_user = await user_service.update_user(user_id, user)
        if not updated_user:
            logger.warning(f"User not found for update: {user_id}", extra={"event": "user_update_not_found"})
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User updated: {user_id}", extra={"event": "user_update_success"})
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update user: {user_id}", 
            extra={"event": "user_update_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a user (Admin only)
    """
    logger.info(f"Deleting user: {user_id}", extra={"event": "user_delete_attempt"})
    
    try:
        # Check if user has admin role
        if "admin" not in current_user.get("roles", []):
            logger.warning(
                f"Unauthorized attempt to delete user {user_id} by: {current_user.get('id')}", 
                extra={"event": "unauthorized_user_delete"}
            )
            raise HTTPException(status_code=403, detail="Not authorized to delete users")
        
        success = await user_service.delete_user(user_id)
        if not success:
            logger.warning(f"User not found for deletion: {user_id}", extra={"event": "user_delete_not_found"})
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User deleted: {user_id}", extra={"event": "user_delete_success"})
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete user: {user_id}", 
            extra={"event": "user_delete_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

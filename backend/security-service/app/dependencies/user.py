from fastapi import Depends
from app.services.user_service import UserService

def get_user_service() -> UserService:
    """Dependency to get user service"""
    return UserService()

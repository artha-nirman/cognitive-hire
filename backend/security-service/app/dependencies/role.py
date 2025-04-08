from fastapi import Depends
from app.services.role_service import RoleService

def get_role_service() -> RoleService:
    """Dependency to get role service"""
    return RoleService()

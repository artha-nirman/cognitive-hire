from fastapi import Depends
from app.services.permission_service import PermissionService

def get_permission_service() -> PermissionService:
    """Dependency to get permission service"""
    return PermissionService()

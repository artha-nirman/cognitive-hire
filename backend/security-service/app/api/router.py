from fastapi import APIRouter
from app.api.v1 import users, auth, roles, permissions

# Create API router
api_router = APIRouter(prefix="/api")

# Include routers for each API group
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/v1/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/v1/permissions", tags=["Permissions"])

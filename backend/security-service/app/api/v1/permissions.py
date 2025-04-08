from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
from app.schemas.permission import PermissionCreate, PermissionResponse, PermissionListResponse
from app.core.logging import logger
from app.services.permission_service import PermissionService
from app.dependencies.permission import get_permission_service
from app.dependencies.auth import get_current_user, require_permission

router = APIRouter()

@router.get("", response_model=PermissionListResponse)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    permission_service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(require_permission("permissions:read"))
):
    """
    List permissions
    """
    logger.info("Listing permissions", extra={"event": "permission_list_attempt"})
    
    try:
        permissions, total = await permission_service.list_permissions(skip, limit)
        logger.info(f"Listed {len(permissions)} permissions", extra={"event": "permission_list_success"})
        return {"items": permissions, "total": total}
    except Exception as e:
        logger.error(
            "Failed to list permissions", 
            extra={"event": "permission_list_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=PermissionResponse)
async def create_permission(
    permission: PermissionCreate,
    permission_service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(require_permission("permissions:create"))
):
    """
    Create a new permission
    """
    logger.info(f"Creating new permission: {permission.name}", extra={"event": "permission_create_attempt"})
    
    try:
        created_permission = await permission_service.create_permission(permission)
        logger.info(f"Permission created: {permission.name}", extra={"event": "permission_create_success"})
        return created_permission
    except Exception as e:
        logger.error(
            f"Failed to create permission: {permission.name}", 
            extra={"event": "permission_create_failure", "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str = Path(...),
    permission_service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(require_permission("permissions:read"))
):
    """
    Get a permission by ID
    """
    logger.info(f"Getting permission: {permission_id}", extra={"event": "permission_get_attempt"})
    
    try:
        permission = await permission_service.get_permission(permission_id)
        if not permission:
            logger.warning(f"Permission not found: {permission_id}", extra={"event": "permission_get_not_found"})
            raise HTTPException(status_code=404, detail="Permission not found")
        
        logger.info(f"Permission found: {permission_id}", extra={"event": "permission_get_success"})
        return permission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get permission: {permission_id}", 
            extra={"event": "permission_get_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign/{role_id}/{permission_id}")
async def assign_permission_to_role(
    role_id: str = Path(...),
    permission_id: str = Path(...),
    permission_service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(require_permission("roles:update"))
):
    """
    Assign a permission to a role
    """
    logger.info(
        f"Assigning permission {permission_id} to role {role_id}", 
        extra={"event": "permission_assign_attempt"}
    )
    
    try:
        success = await permission_service.assign_permission_to_role(role_id, permission_id)
        if not success:
            logger.warning(
                f"Failed to assign permission {permission_id} to role {role_id}", 
                extra={"event": "permission_assign_not_found"}
            )
            raise HTTPException(status_code=404, detail="Role or permission not found")
        
        logger.info(
            f"Permission {permission_id} assigned to role {role_id}", 
            extra={"event": "permission_assign_success"}
        )
        return {"message": "Permission assigned to role successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to assign permission {permission_id} to role {role_id}", 
            extra={"event": "permission_assign_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/revoke/{role_id}/{permission_id}")
async def revoke_permission_from_role(
    role_id: str = Path(...),
    permission_id: str = Path(...),
    permission_service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(require_permission("roles:update"))
):
    """
    Revoke a permission from a role
    """
    logger.info(
        f"Revoking permission {permission_id} from role {role_id}", 
        extra={"event": "permission_revoke_attempt"}
    )
    
    try:
        success = await permission_service.revoke_permission_from_role(role_id, permission_id)
        if not success:
            logger.warning(
                f"Failed to revoke permission {permission_id} from role {role_id}", 
                extra={"event": "permission_revoke_not_found"}
            )
            raise HTTPException(status_code=404, detail="Role or permission not found")
        
        logger.info(
            f"Permission {permission_id} revoked from role {role_id}", 
            extra={"event": "permission_revoke_success"}
        )
        return {"message": "Permission revoked from role successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to revoke permission {permission_id} from role {role_id}", 
            extra={"event": "permission_revoke_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

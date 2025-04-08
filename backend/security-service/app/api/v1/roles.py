from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
from app.core.logging import logger
from app.services.role_service import RoleService
from app.dependencies.role import get_role_service
from app.dependencies.auth import get_current_user, require_permission

router = APIRouter()

@router.get("", response_model=RoleListResponse)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role_service: RoleService = Depends(get_role_service),
    _: dict = Depends(require_permission("roles:read"))
):
    """
    List roles
    """
    logger.info("Listing roles", extra={"event": "role_list_attempt"})
    
    try:
        roles, total = await role_service.list_roles(skip, limit)
        logger.info(f"Listed {len(roles)} roles", extra={"event": "role_list_success"})
        return {"items": roles, "total": total}
    except Exception as e:
        logger.error(
            "Failed to list roles", 
            extra={"event": "role_list_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    _: dict = Depends(require_permission("roles:create"))
):
    """
    Create a new role
    """
    logger.info(f"Creating new role: {role.name}", extra={"event": "role_create_attempt"})
    
    try:
        created_role = await role_service.create_role(role)
        logger.info(f"Role created: {role.name}", extra={"event": "role_create_success"})
        return created_role
    except Exception as e:
        logger.error(
            f"Failed to create role: {role.name}", 
            extra={"event": "role_create_failure", "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str = Path(...),
    role_service: RoleService = Depends(get_role_service),
    _: dict = Depends(require_permission("roles:read"))
):
    """
    Get a role by ID
    """
    logger.info(f"Getting role: {role_id}", extra={"event": "role_get_attempt"})
    
    try:
        role = await role_service.get_role(role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}", extra={"event": "role_get_not_found"})
            raise HTTPException(status_code=404, detail="Role not found")
        
        logger.info(f"Role found: {role_id}", extra={"event": "role_get_success"})
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get role: {role_id}", 
            extra={"event": "role_get_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role: RoleUpdate,
    role_id: str = Path(...),
    role_service: RoleService = Depends(get_role_service),
    _: dict = Depends(require_permission("roles:update"))
):
    """
    Update a role
    """
    logger.info(f"Updating role: {role_id}", extra={"event": "role_update_attempt"})
    
    try:
        updated_role = await role_service.update_role(role_id, role)
        if not updated_role:
            logger.warning(f"Role not found for update: {role_id}", extra={"event": "role_update_not_found"})
            raise HTTPException(status_code=404, detail="Role not found")
        
        logger.info(f"Role updated: {role_id}", extra={"event": "role_update_success"})
        return updated_role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update role: {role_id}", 
            extra={"event": "role_update_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{role_id}")
async def delete_role(
    role_id: str = Path(...),
    role_service: RoleService = Depends(get_role_service),
    _: dict = Depends(require_permission("roles:delete"))
):
    """
    Delete a role
    """
    logger.info(f"Deleting role: {role_id}", extra={"event": "role_delete_attempt"})
    
    try:
        success = await role_service.delete_role(role_id)
        if not success:
            logger.warning(f"Role not found for deletion: {role_id}", extra={"event": "role_delete_not_found"})
            raise HTTPException(status_code=404, detail="Role not found")
        
        logger.info(f"Role deleted: {role_id}", extra={"event": "role_delete_success"})
        return {"message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete role: {role_id}", 
            extra={"event": "role_delete_failure", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

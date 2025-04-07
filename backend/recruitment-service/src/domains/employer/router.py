from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.common.db.database import get_db
from src.domains.employer.models import EmployerCreate, EmployerRead, EmployerUpdate
from src.domains.employer.service import EmployerService
from src.common.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=EmployerRead, status_code=status.HTTP_201_CREATED)
async def create_employer(
    employer: EmployerCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new employer (organization)."""
    service = EmployerService(db)
    return await service.create_employer(employer)


@router.get("/{employer_id}", response_model=EmployerRead)
async def get_employer(
    employer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get employer by ID."""
    service = EmployerService(db)
    employer = await service.get_employer(employer_id)
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    return employer


@router.get("/", response_model=List[EmployerRead])
async def list_employers(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List employers with pagination."""
    service = EmployerService(db)
    return await service.list_employers(skip=skip, limit=limit)


@router.put("/{employer_id}", response_model=EmployerRead)
async def update_employer(
    employer_id: str,
    employer: EmployerUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an employer."""
    service = EmployerService(db)
    updated_employer = await service.update_employer(employer_id, employer)
    if not updated_employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    return updated_employer


@router.delete("/{employer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employer(
    employer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an employer."""
    service = EmployerService(db)
    result = await service.delete_employer(employer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employer not found")
    return None

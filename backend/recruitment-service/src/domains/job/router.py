from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.common.db.database import get_db
from src.domains.job.models import JobCreate, JobRead, JobUpdate
from src.domains.job.service import JobService

router = APIRouter()


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting."""
    service = JobService(db)
    return await service.create_job(job)


@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job by ID."""
    service = JobService(db)
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/", response_model=List[JobRead])
async def list_jobs(
    employer_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering and pagination."""
    service = JobService(db)
    return await service.list_jobs(
        employer_id=employer_id, 
        status=status,
        skip=skip, 
        limit=limit
    )


@router.put("/{job_id}", response_model=JobRead)
async def update_job(
    job_id: str,
    job: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a job."""
    service = JobService(db)
    updated_job = await service.update_job(job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job."""
    service = JobService(db)
    result = await service.delete_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return None


@router.post("/{job_id}/publish", response_model=JobRead)
async def publish_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Publish a job to make it visible to candidates."""
    service = JobService(db)
    job = await service.publish_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/unpublish", response_model=JobRead)
async def unpublish_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Unpublish a job to hide it from candidates."""
    service = JobService(db)
    job = await service.unpublish_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

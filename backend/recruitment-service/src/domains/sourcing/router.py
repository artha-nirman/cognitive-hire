from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from src.common.db.database import get_db
from src.domains.sourcing.service import SourcingService

router = APIRouter()


@router.post("/jobs/{job_id}/source-candidates", status_code=status.HTTP_202_ACCEPTED)
async def source_candidates_for_job(
    job_id: str,
    search_criteria: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Start a candidate sourcing process for a job."""
    service = SourcingService(db)
    try:
        return await service.start_candidate_sourcing(job_id, search_criteria)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start sourcing process: {str(e)}"
        )


@router.get("/jobs/{job_id}/sourcing-status")
async def get_sourcing_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of a sourcing process for a job."""
    service = SourcingService(db)
    try:
        return await service.get_sourcing_status(job_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sourcing status: {str(e)}"
        )


@router.post("/sourcing-channels")
async def register_sourcing_channel(
    channel_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Register a new sourcing channel (e.g., LinkedIn, Indeed)."""
    service = SourcingService(db)
    try:
        return await service.register_sourcing_channel(channel_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register sourcing channel: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.common.db.database import get_db
from src.domains.screening.service import ScreeningService

router = APIRouter()


@router.post("/resumes", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload a resume for screening."""
    service = ScreeningService(db)
    try:
        return await service.upload_resume(file, candidate_id, job_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.post("/jobs/{job_id}/match", status_code=status.HTTP_202_ACCEPTED)
async def match_candidates_to_job(
    job_id: str,
    candidate_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Match candidates to a job based on their profiles and resumes."""
    service = ScreeningService(db)
    try:
        return await service.match_candidates_to_job(job_id, candidate_ids)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start matching process: {str(e)}"
        )


@router.post("/interest-check", status_code=status.HTTP_202_ACCEPTED)
async def send_interest_check(
    candidate_id: str,
    job_id: str,
    channel: str,  # email, sms, phone
    db: AsyncSession = Depends(get_db)
):
    """Send an interest check to a candidate for a job."""
    service = ScreeningService(db)
    try:
        return await service.send_interest_check(candidate_id, job_id, channel)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send interest check: {str(e)}"
        )

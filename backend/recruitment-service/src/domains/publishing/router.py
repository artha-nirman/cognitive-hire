from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.common.db.database import get_db
from src.domains.job.models import JobPublishingChannel, PublishingChannelRead, PublishingChannelCreate
from src.domains.publishing.service import PublishingService

router = APIRouter()


@router.post("/jobs/{job_id}/channels", response_model=PublishingChannelRead)
async def add_publishing_channel(
    job_id: str,
    channel_data: PublishingChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a publishing channel to a job."""
    service = PublishingService(db)
    try:
        return await service.add_channel(job_id, channel_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add publishing channel: {str(e)}"
        )


@router.get("/jobs/{job_id}/channels", response_model=List[PublishingChannelRead])
async def list_publishing_channels(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all publishing channels for a job."""
    service = PublishingService(db)
    return await service.list_channels(job_id)


@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_publishing_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a publishing channel."""
    service = PublishingService(db)
    result = await service.remove_channel(channel_id)
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")
    return None

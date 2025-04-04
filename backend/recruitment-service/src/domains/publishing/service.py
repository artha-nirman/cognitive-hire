import datetime
import structlog
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.domains.job.models import (
    Job, JobPublishingChannel, PublishingChannelCreate, PublishingChannelRead
)
from src.common.events import publish_event


class PublishingService:
    """
    Service for publishing-related operations.
    
    Manages job publishing channels and handles distribution of job postings
    to various external platforms.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
        self.logger = structlog.get_logger(__name__)
        
    async def add_channel(self, job_id: str, channel_data: PublishingChannelCreate) -> JobPublishingChannel:
        """
        Add a publishing channel to a job.
        
        Args:
            job_id: ID of the job to add the channel to
            channel_data: Publishing channel data
            
        Returns:
            The created channel entity
            
        Raises:
            HTTPException: If job not found
            Exception: If database operations fail
        """
        self.logger.info(
            "Adding publishing channel",
            job_id=job_id,
            channel=channel_data.channel_name
        )
        
        try:
            # Check if job exists
            job_query = select(Job).where(Job.id == job_id)
            result = await self.db.execute(job_query)
            job = result.scalars().first()
            
            if not job:
                self.logger.warning("Job not found for channel addition", job_id=job_id)
                raise HTTPException(status_code=404, detail="Job not found")
                
            # Create channel
            channel = JobPublishingChannel(
                job_id=job_id,
                **channel_data.dict()
            )
            
            self.db.add(channel)
            await self.db.commit()
            await self.db.refresh(channel)
            
            self.logger.info(
                "Publishing channel added successfully",
                job_id=job_id,
                channel_id=str(channel.id),
                channel_name=channel.channel_name
            )
            
            # Publish event
            await publish_event("publishing.channel.added", {
                "job_id": job_id,
                "channel_id": str(channel.id),
                "channel_name": channel.channel_name
            })
            
            return channel
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to add publishing channel", 
                job_id=job_id,
                channel=channel_data.channel_name,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
            
    async def list_channels(self, job_id: str) -> List[JobPublishingChannel]:
        """
        List all publishing channels for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            List of publishing channel entities
            
        Raises:
            Exception: If database query fails
        """
        self.logger.debug("Listing publishing channels", job_id=job_id)
        
        try:
            query = select(JobPublishingChannel).where(JobPublishingChannel.job_id == job_id)
            result = await self.db.execute(query)
            channels = result.scalars().all()
            
            self.logger.debug(
                "Publishing channels listed", 
                job_id=job_id, 
                count=len(channels)
            )
            return channels
        except Exception as e:
            self.logger.error(
                "Error listing publishing channels", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            raise
            
    async def remove_channel(self, channel_id: str) -> bool:
        """
        Remove a publishing channel.
        
        Args:
            channel_id: ID of the channel to remove
            
        Returns:
            True if removed, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        self.logger.info("Removing publishing channel", channel_id=channel_id)
        
        try:
            # Get channel first for event data
            query = select(JobPublishingChannel).where(JobPublishingChannel.id == channel_id)
            result = await self.db.execute(query)
            channel = result.scalars().first()
            
            if not channel:
                self.logger.warning("Channel not found for removal", channel_id=channel_id)
                return False
                
            # Store data for event
            job_id = str(channel.job_id)
            channel_name = channel.channel_name
                
            # Delete channel
            delete_query = delete(JobPublishingChannel).where(JobPublishingChannel.id == channel_id)
            delete_result = await self.db.execute(delete_query)
            await self.db.commit()
            
            if delete_result.rowcount > 0:
                self.logger.info(
                    "Publishing channel removed successfully", 
                    channel_id=channel_id,
                    job_id=job_id
                )
                
                # Publish event
                await publish_event("publishing.channel.removed", {
                    "channel_id": channel_id,
                    "job_id": job_id,
                    "channel_name": channel_name
                })
                
                return True
                
            return False
        except Exception as e:
            self.logger.error(
                "Error removing publishing channel", 
                channel_id=channel_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise

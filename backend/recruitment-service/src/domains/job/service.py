import datetime
import uuid
from typing import List, Optional, Dict, Any
import structlog
from fastapi import HTTPException
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domains.job.models import (
    Job, JobCreate, JobUpdate, JobRead,
    JobPublishingChannel, PublishingChannelCreate
)
from src.common.events import publish_event


class JobService:
    """
    Service for job-related operations.
    
    Handles all business logic related to job postings including
    creation, updates, publishing, and deletion.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
        self.logger = structlog.get_logger(__name__)
        
    async def create_job(self, job_data: JobCreate) -> Job:
        """
        Create a new job.
        
        Args:
            job_data: The job data for creation
            
        Returns:
            The created job entity
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info(
            "Creating new job", 
            title=job_data.title,
            employer_id=job_data.employer_id,
            tenant_id=job_data.tenant_id
        )
        
        try:
            job = Job(**job_data.dict())
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
            
            self.logger.info(
                "Job created successfully", 
                job_id=str(job.id),
                title=job.title
            )
            
            # Publish event
            await publish_event("job.created", {
                "job_id": str(job.id),
                "tenant_id": str(job.tenant_id),
                "employer_id": str(job.employer_id),
                "title": job.title,
                "created_at": job.created_at.isoformat()
            })
            
            return job
        except Exception as e:
            self.logger.error(
                "Failed to create job", 
                title=job_data.title,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            The job entity or None if not found
            
        Raises:
            Exception: If database query fails
        """
        self.logger.debug("Fetching job", job_id=job_id)
        
        try:
            query = select(Job).options(
                selectinload(Job.publishing_channels)
            ).where(Job.id == job_id)
            result = await self.db.execute(query)
            job = result.scalars().first()
            
            if job:
                self.logger.debug(
                    "Job found", 
                    job_id=job_id,
                    title=job.title
                )
            else:
                self.logger.info("Job not found", job_id=job_id)
                
            return job
        except Exception as e:
            self.logger.error(
                "Error fetching job", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            raise
        
    async def list_jobs(
        self,
        employer_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """
        List jobs with filtering and pagination.
        
        Args:
            employer_id: Optional employer ID filter
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of job entities
            
        Raises:
            Exception: If database query fails
        """
        self.logger.debug(
            "Listing jobs", 
            employer_id=employer_id, 
            status=status,
            skip=skip,
            limit=limit
        )
        
        try:
            query = select(Job)
            
            # Apply filters
            filters = []
            if employer_id:
                filters.append(Job.employer_id == employer_id)
            if status:
                filters.append(Job.status == status)
                
            if filters:
                query = query.where(and_(*filters))
                
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            jobs = result.scalars().all()
            
            self.logger.debug(
                "Jobs listed", 
                count=len(jobs),
                employer_id=employer_id,
                status=status
            )
            return jobs
        except Exception as e:
            self.logger.error(
                "Error listing jobs", 
                employer_id=employer_id,
                status=status,
                error=str(e),
                exc_info=e
            )
            raise
        
    async def update_job(self, job_id: str, job_data: JobUpdate) -> Optional[Job]:
        """
        Update a job.
        
        Args:
            job_id: ID of the job to update
            job_data: The data to update
            
        Returns:
            The updated job entity or None if not found
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info("Updating job", job_id=job_id)
        
        # Remove None values to allow partial updates
        update_data = {k: v for k, v in job_data.dict().items() if v is not None}
        
        if not update_data:
            self.logger.debug("No update needed, all fields are None")
            return await self.get_job(job_id)
            
        try:
            query = (
                update(Job)
                .where(Job.id == job_id)
                .values(**update_data)
                .returning(Job)
            )
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_job = result.scalars().first()
            
            if updated_job:
                self.logger.info(
                    "Job updated successfully", 
                    job_id=job_id,
                    title=updated_job.title,
                    fields=list(update_data.keys())
                )
                
                # Publish event
                await publish_event("job.updated", {
                    "job_id": str(updated_job.id),
                    "tenant_id": str(updated_job.tenant_id),
                    "employer_id": str(updated_job.employer_id),
                    "title": updated_job.title,
                    "status": updated_job.status,
                    "updated_at": updated_job.updated_at.isoformat()
                })
            else:
                self.logger.warning("Job not found for update", job_id=job_id)
            
            return updated_job
        except Exception as e:
            self.logger.error(
                "Error updating job", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info("Deleting job", job_id=job_id)
        
        try:
            # Get job first to collect data for event
            job = await self.get_job(job_id)
            if not job:
                self.logger.warning("Job not found for deletion", job_id=job_id)
                return False
                
            query = delete(Job).where(Job.id == job_id)
            result = await self.db.execute(query)
            await self.db.commit()
            
            if result.rowcount > 0:
                self.logger.info("Job deleted successfully", job_id=job_id, title=job.title)
                
                # Publish event
                await publish_event("job.deleted", {
                    "job_id": str(job.id),
                    "tenant_id": str(job.tenant_id),
                    "employer_id": str(job.employer_id),
                    "title": job.title
                })
                return True
                
            return False
        except Exception as e:
            self.logger.error(
                "Error deleting job", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def publish_job(self, job_id: str) -> Optional[Job]:
        """
        Publish a job, making it visible to candidates.
        
        Args:
            job_id: ID of the job to publish
            
        Returns:
            The updated job entity or None if not found
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info("Publishing job", job_id=job_id)
        
        try:
            job = await self.get_job(job_id)
            
            if not job:
                self.logger.warning("Job not found for publishing", job_id=job_id)
                return None
                
            if job.status == "PUBLISHED":
                self.logger.info("Job is already published", job_id=job_id)
                return job
                
            # Update status and published_at timestamp
            query = (
                update(Job)
                .where(Job.id == job_id)
                .values(
                    status="PUBLISHED",
                    published_at=datetime.datetime.utcnow()
                )
                .returning(Job)
            )
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_job = result.scalars().first()
            
            if updated_job:
                self.logger.info(
                    "Job published successfully", 
                    job_id=job_id,
                    title=updated_job.title
                )
                
                # Publish event
                await publish_event("job.published", {
                    "job_id": str(updated_job.id),
                    "tenant_id": str(updated_job.tenant_id),
                    "employer_id": str(updated_job.employer_id),
                    "title": updated_job.title,
                    "published_at": updated_job.published_at.isoformat()
                })
                
            return updated_job
        except Exception as e:
            self.logger.error(
                "Error publishing job", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def unpublish_job(self, job_id: str) -> Optional[Job]:
        """
        Unpublish a job, hiding it from candidates.
        
        Args:
            job_id: ID of the job to unpublish
            
        Returns:
            The updated job entity or None if not found
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info("Unpublishing job", job_id=job_id)
        
        try:
            job = await self.get_job(job_id)
            
            if not job:
                self.logger.warning("Job not found for unpublishing", job_id=job_id)
                return None
                
            if job.status != "PUBLISHED":
                self.logger.info(
                    "Job is not currently published", 
                    job_id=job_id,
                    current_status=job.status
                )
                return job
                
            # Update status
            query = (
                update(Job)
                .where(Job.id == job_id)
                .values(status="DRAFT")
                .returning(Job)
            )
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_job = result.scalars().first()
            
            if updated_job:
                self.logger.info(
                    "Job unpublished successfully", 
                    job_id=job_id,
                    title=updated_job.title
                )
                
                # Publish event
                await publish_event("job.unpublished", {
                    "job_id": str(updated_job.id),
                    "tenant_id": str(updated_job.tenant_id),
                    "employer_id": str(updated_job.employer_id),
                    "title": updated_job.title
                })
                
            return updated_job
        except Exception as e:
            self.logger.error(
                "Error unpublishing job", 
                job_id=job_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise

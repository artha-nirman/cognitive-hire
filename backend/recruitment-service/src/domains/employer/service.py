import uuid
from typing import List, Optional
import structlog
from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.employer.models import (
    Employer, EmployerCreate, EmployerUpdate, EmployerRead,
    Department, DepartmentCreate, DepartmentUpdate, DepartmentRead,
    Team, TeamCreate, TeamUpdate, TeamRead
)


class EmployerService:
    """
    Service for employer-related operations.
    
    Handles all business logic related to employers, departments, and teams.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
        self.logger = structlog.get_logger(__name__)
        
    async def create_employer(self, employer_data: EmployerCreate) -> Employer:
        """
        Create a new employer.
        
        Args:
            employer_data: The employer data for creation
            
        Returns:
            The created employer entity
            
        Raises:
            Exception: If database operations fail
        """
        self.logger.info(
            "Creating new employer", 
            name=employer_data.name,
            tenant_id=employer_data.tenant_id
        )
        
        try:
            employer = Employer(**employer_data.dict())
            self.db.add(employer)
            await self.db.commit()
            await self.db.refresh(employer)
            
            self.logger.info(
                "Employer created successfully", 
                employer_id=str(employer.id),
                name=employer.name
            )
            
            return employer
        except Exception as e:
            self.logger.error(
                "Failed to create employer", 
                name=employer_data.name,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def get_employer(self, employer_id: str) -> Optional[Employer]:
        """
        Get employer by ID.
        
        Args:
            employer_id: The ID of the employer to retrieve
            
        Returns:
            The employer entity or None if not found
        """
        self.logger.debug("Fetching employer", employer_id=employer_id)
        
        try:
            query = select(Employer).where(Employer.id == employer_id)
            result = await self.db.execute(query)
            employer = result.scalars().first()
            
            if employer:
                self.logger.debug(
                    "Employer found", 
                    employer_id=employer_id,
                    name=employer.name
                )
            else:
                self.logger.info("Employer not found", employer_id=employer_id)
                
            return employer
        except Exception as e:
            self.logger.error(
                "Error fetching employer", 
                employer_id=employer_id,
                error=str(e),
                exc_info=e
            )
            raise
        
    async def list_employers(self, skip: int = 0, limit: int = 100) -> List[Employer]:
        """
        List employers with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of employer entities
        """
        self.logger.debug("Listing employers", skip=skip, limit=limit)
        
        try:
            query = select(Employer).offset(skip).limit(limit)
            result = await self.db.execute(query)
            employers = result.scalars().all()
            
            self.logger.debug("Employers listed", count=len(employers))
            return employers
        except Exception as e:
            self.logger.error(
                "Error listing employers", 
                skip=skip,
                limit=limit,
                error=str(e),
                exc_info=e
            )
            raise
        
    async def update_employer(self, employer_id: str, employer_data: EmployerUpdate) -> Optional[Employer]:
        """
        Update an employer.
        
        Args:
            employer_id: ID of the employer to update
            employer_data: The data to update
            
        Returns:
            The updated employer entity or None if not found
        """
        self.logger.info("Updating employer", employer_id=employer_id)
        
        # Remove None values to allow partial updates
        update_data = {k: v for k, v in employer_data.dict().items() if v is not None}
        
        if not update_data:
            self.logger.debug("No update needed, all fields are None")
            return await self.get_employer(employer_id)
        
        try:
            query = (
                update(Employer)
                .where(Employer.id == employer_id)
                .values(**update_data)
                .returning(Employer)
            )
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_employer = result.scalars().first()
            
            if updated_employer:
                self.logger.info(
                    "Employer updated successfully", 
                    employer_id=employer_id,
                    fields=list(update_data.keys())
                )
            else:
                self.logger.warning("Employer not found for update", employer_id=employer_id)
                
            return updated_employer
        except Exception as e:
            self.logger.error(
                "Error updating employer", 
                employer_id=employer_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
        
    async def delete_employer(self, employer_id: str) -> bool:
        """
        Delete an employer.
        
        Args:
            employer_id: ID of the employer to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        self.logger.info("Deleting employer", employer_id=employer_id)
        
        try:
            query = delete(Employer).where(Employer.id == employer_id)
            result = await self.db.execute(query)
            await self.db.commit()
            
            deleted = result.rowcount > 0
            
            if deleted:
                self.logger.info("Employer deleted successfully", employer_id=employer_id)
            else:
                self.logger.warning("Employer not found for deletion", employer_id=employer_id)
                
            return deleted
        except Exception as e:
            self.logger.error(
                "Error deleting employer", 
                employer_id=employer_id, 
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
    
    # Department-related methods
    async def create_department(self, employer_id: str, department_data: DepartmentCreate) -> Department:
        """
        Create a new department for an employer.
        
        Args:
            employer_id: ID of the parent employer
            department_data: Department data for creation
            
        Returns:
            Created department entity
            
        Raises:
            HTTPException: If employer not found
            Exception: If database operation fails
        """
        self.logger.info(
            "Creating department", 
            employer_id=employer_id, 
            name=department_data.name
        )
        
        try:
            # Check if employer exists
            employer = await self.get_employer(employer_id)
            if not employer:
                self.logger.warning("Employer not found for department creation", employer_id=employer_id)
                raise HTTPException(status_code=404, detail="Employer not found")
                
            department = Department(employer_id=employer_id, **department_data.dict())
            self.db.add(department)
            await self.db.commit()
            await self.db.refresh(department)
            
            self.logger.info(
                "Department created successfully", 
                department_id=str(department.id),
                name=department.name,
                employer_id=employer_id
            )
            
            return department
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Error creating department", 
                employer_id=employer_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise
    
    # Team-related methods
    async def create_team(self, employer_id: str, team_data: TeamCreate) -> Team:
        """
        Create a new team for an employer.
        
        Args:
            employer_id: ID of the parent employer
            team_data: Team data for creation
            
        Returns:
            Created team entity
            
        Raises:
            HTTPException: If employer or department not found
            Exception: If database operation fails
        """
        self.logger.info(
            "Creating team", 
            employer_id=employer_id, 
            name=team_data.name,
            department_id=team_data.department_id
        )
        
        try:
            # Check if employer exists
            employer = await self.get_employer(employer_id)
            if not employer:
                self.logger.warning("Employer not found for team creation", employer_id=employer_id)
                raise HTTPException(status_code=404, detail="Employer not found")
                
            # Check department if provided
            if team_data.department_id:
                department_query = select(Department).where(
                    Department.id == team_data.department_id,
                    Department.employer_id == employer_id
                )
                department_result = await self.db.execute(department_query)
                department = department_result.scalars().first()
                
                if not department:
                    self.logger.warning(
                        "Department not found for team creation", 
                        department_id=team_data.department_id
                    )
                    raise HTTPException(status_code=404, detail="Department not found")
                    
            team = Team(employer_id=employer_id, **team_data.dict())
            self.db.add(team)
            await self.db.commit()
            await self.db.refresh(team)
            
            self.logger.info(
                "Team created successfully", 
                team_id=str(team.id),
                name=team.name,
                employer_id=employer_id,
                department_id=team_data.department_id
            )
            
            return team
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Error creating team", 
                employer_id=employer_id,
                error=str(e),
                exc_info=e
            )
            await self.db.rollback()
            raise

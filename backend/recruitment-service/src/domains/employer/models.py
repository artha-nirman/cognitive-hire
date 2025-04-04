from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.common.db.database import Base


# SQLAlchemy Models

class Employer(Base):
    """Employer (organization) table."""
    __tablename__ = "employers"

    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)  # Small, Medium, Large, Enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    departments = relationship("Department", back_populates="employer", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="employer", cascade="all, delete-orphan")
    
    
class Department(Base):
    """Department within an employer organization."""
    __tablename__ = "departments"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    employer_id = Column(UUID, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employer = relationship("Employer", back_populates="departments")
    teams = relationship("Team", back_populates="department")
    
    
class Team(Base):
    """Team within a department."""
    __tablename__ = "teams"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    employer_id = Column(UUID, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employer = relationship("Employer", back_populates="teams")
    department = relationship("Department", back_populates="teams")


# Pydantic Models for API

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: str
    employer_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamUpdate(TeamBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: str
    employer_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    teams: List[TeamRead] = []
    
    class Config:
        from_attributes = True


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class EmployerBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None


class EmployerCreate(EmployerBase):
    tenant_id: str


class EmployerRead(EmployerBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployerReadWithDepartments(EmployerRead):
    departments: List[DepartmentRead] = []


class EmployerUpdate(EmployerBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

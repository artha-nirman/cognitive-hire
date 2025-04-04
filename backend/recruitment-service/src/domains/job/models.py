from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from src.common.db.database import Base


# SQLAlchemy Models

class Job(Base):
    """Job posting table."""
    __tablename__ = "jobs"

    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(UUID, nullable=False, index=True)
    employer_id = Column(UUID, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    job_type = Column(String, nullable=False)  # Full-time, Part-time, Contract, etc.
    location = Column(String, nullable=True)
    is_remote = Column(Boolean, default=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, nullable=True, default="USD")
    required_skills = Column(ARRAY(String), nullable=True)
    preferred_skills = Column(ARRAY(String), nullable=True)
    experience_level = Column(String, nullable=True)  # Entry, Mid, Senior, etc.
    education_level = Column(String, nullable=True)
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    status = Column(String, default="DRAFT")  # DRAFT, PUBLISHED, CLOSED, FILLED
    application_url = Column(String, nullable=True)
    application_email = Column(String, nullable=True)
    application_instructions = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False)
    meta_data = Column(JSON, nullable=True)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # employer = relationship("Employer", back_populates="jobs")
    publishing_channels = relationship("JobPublishingChannel", back_populates="job", cascade="all, delete-orphan")


class JobPublishingChannel(Base):
    """Job publishing channel mapping."""
    __tablename__ = "job_publishing_channels"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    job_id = Column(UUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    channel_name = Column(String, nullable=False)  # LinkedIn, Indeed, etc.
    channel_id = Column(String, nullable=True)  # ID in the external system
    status = Column(String, default="PENDING")  # PENDING, PUBLISHED, FAILED
    external_url = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="publishing_channels")


# Pydantic Models for API

class PublishingChannelBase(BaseModel):
    channel_name: str
    channel_id: Optional[str] = None
    external_url: Optional[str] = None
    status: str = "PENDING"


class PublishingChannelCreate(PublishingChannelBase):
    pass


class PublishingChannelRead(PublishingChannelBase):
    id: str
    job_id: str
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    job_type: str
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    application_instructions: Optional[str] = None
    is_featured: bool = False
    meta_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class JobCreate(JobBase):
    tenant_id: str
    employer_id: str


class JobRead(JobBase):
    id: str
    tenant_id: str
    employer_id: str
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobReadWithChannels(JobRead):
    publishing_channels: List[PublishingChannelRead] = []
    
    class Config:
        from_attributes = True


class JobUpdate(JobBase):
    title: Optional[str] = None
    job_type: Optional[str] = None
    status: Optional[str] = None

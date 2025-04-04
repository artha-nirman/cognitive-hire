import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

import structlog

from src.common.config import settings

logger = structlog.get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Create async session
AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession,
)

# Base class for models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def init_db() -> None:
    """
    Initialize database connection and create tables if needed.
    
    This function is called during application startup.
    In development mode, it also creates missing tables based on model definitions.
    
    Raises:
        Exception: If database connection fails
    """
    logger.info(
        "Initializing database connection", 
        db_url=settings.DATABASE_URL.split("@")[-1],
        environment=settings.ENVIRONMENT
    )
    
    try:
        async with engine.begin() as conn:
            # For development - create tables if needed
            if settings.ENVIRONMENT == "development":
                logger.info("Creating database tables in development mode")
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created")
                
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error("Failed to initialize database", exc_info=e)
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for dependency injection.
    
    Creates and yields a new async SQLAlchemy session for each request,
    ensuring proper session cleanup after request completion.
    
    Yields:
        AsyncSession: Database session
        
    Raises:
        Exception: If session operations fail
    """
    session = AsyncSessionLocal()
    try:
        logger.debug("Creating new database session")
        yield session
        await session.commit()
        logger.debug("Database session committed")
    except Exception as e:
        logger.error("Database session error, rolling back", exc_info=e)
        await session.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        await session.close()

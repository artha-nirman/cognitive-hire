import logging
import sys
from typing import List, Dict, Any

import structlog
from structlog.types import Processor

from src.common.config import settings

def configure_logging() -> None:
    """
    Configure structured logging for the application.
    This sets up both standard logging and structlog with proper
    integration between them.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Remove existing handlers
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL)
    root_logger.setLevel(log_level)
    
    # Create handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Define log format and add handler
    if settings.LOG_FORMAT.lower() == "json":
        # JSON formatter for structured logs
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.format_exc_info,
            ]
        )
    else:
        # Console formatter for development
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.format_exc_info,
            ]
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure structlog
    shared_processors: List[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Disable uvicorn and fastapi logs in production for cleaner output
    if settings.ENVIRONMENT != "development":
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)

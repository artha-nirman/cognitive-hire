import logging
import json
import sys
import os
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

from app.core.config import settings

# Context variables
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')
user_id: ContextVar[str] = ContextVar('user_id', default='')


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for consistent log formatting
    """
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['service'] = settings.OTEL_SERVICE_NAME
        log_record['environment'] = settings.ENVIRONMENT
        
        # Add context variables if available
        corr_id = correlation_id.get()
        if corr_id:
            log_record['correlation_id'] = corr_id
            
        uid = user_id.get()
        if uid:
            log_record['user_id'] = uid


def setup_logging():
    """
    Set up logging configuration
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Configure JSON handler for output
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter in all environments
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Create logger
logger = logging.getLogger("security-service")

# Don't propagate to root handler to avoid duplicate logs
logger.propagate = True

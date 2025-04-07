import logging
import os
import structlog
from typing import Optional, List, Dict, Any

from src.common.config import settings

# Map string log levels to integer values
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

def configure_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure both standard logging and structlog with consistent settings.
    
    Args:
        log_level: Override log level (defaults to settings.LOG_LEVEL)
        log_format: Override log format (defaults to settings.LOG_FORMAT)
    """
    # Use parameters or fall back to settings
    level = log_level or settings.LOG_LEVEL
    format_type = log_format or settings.LOG_FORMAT
    
    # Convert string level to int if needed
    level_int = LOG_LEVEL_MAP.get(level.upper(), logging.INFO)
    
    # Configure standard logging
    root_logger = logging.getLogger()
    root_logger.setLevel(level_int)
    
    # Remove existing handlers to avoid duplicates
    while root_logger.handlers:
        root_logger.removeHandler(root_logger.handlers[0])
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_int)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set levels for key loggers
    configure_module_loggers(level_int)
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add the renderer based on format type
    if format_type.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Log the configuration
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured",
        log_level=level,
        log_format=format_type,
        environment=settings.ENVIRONMENT
    )

def configure_module_loggers(level_int: int) -> None:
    """
    Configure log levels for specific modules.
    
    Args:
        level_int: Base log level to use
    """
    # Key modules to configure
    modules = [
        # Our application modules
        "src",
        "src.common",
        "src.common.auth",
        "src.common.auth.dependencies",
        "src.common.db",
        "src.common.events",
        "src.domains.employer",
        "src.domains.employer.router",
        "src.domains.job",
        "src.domains.publishing",
        "src.domains.screening",
        "src.domains.sourcing",
        "src.websocket",
        
        # Third-party modules we may want to adjust
        "fastapi_azure_auth",
        "uvicorn",
        "sqlalchemy",
    ]
    
    # Set specific log levels based on requirements
    override_levels = {
        # Always show auth logs for troubleshooting
        "src.common.auth": logging.DEBUG,
        "src.common.auth.dependencies": logging.DEBUG,
        "fastapi_azure_auth": logging.DEBUG,
        
        # Database logs can be noisy at DEBUG level
        "sqlalchemy.engine.base.Engine": (
            logging.DEBUG if settings.DB_ECHO and level_int <= logging.DEBUG else logging.INFO
        ),
    }
    
    # Configure all modules
    for module in modules:
        module_level = override_levels.get(module, level_int)
        logging.getLogger(module).setLevel(module_level)
        
        # Make sure propagation is enabled
        logging.getLogger(module).propagate = True

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)

# Automatically configure logging when the module is imported
configure_logging()

from typing import Dict, Any
import structlog
import json

# Updated import path to avoid circular dependency
from src.websocket.routes import broadcast_to_channel

logger = structlog.get_logger(__name__)

async def handle_job_event(event_data: Dict[str, Any]) -> None:
    """
    Handle job-related events and broadcast to WebSockets.
    
    Args:
        event_data: The event payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Job event missing job_id", event_data=event_data)
        return
    
    channel = f"job:{job_id}"
    message = {
        "type": "job_update",
        "job_id": job_id,
        "event_type": event_data.get("type", "unknown"),
        "data": event_data
    }
    
    logger.debug("Broadcasting job event to WebSocket", channel=channel, event_type=message["event_type"])
    await broadcast_to_channel(channel, message)

async def handle_screening_event(event_data: Dict[str, Any]) -> None:
    """
    Handle screening-related events and broadcast to WebSockets.
    
    Args:
        event_data: The event payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Screening event missing job_id", event_data=event_data)
        return
    
    channel = f"screening:{job_id}"
    message = {
        "type": "screening_update",
        "job_id": job_id,
        "event_type": event_data.get("type", "unknown"),
        "data": event_data
    }
    
    logger.debug("Broadcasting screening event to WebSocket", channel=channel, event_type=message["event_type"])
    await broadcast_to_channel(channel, message)

async def handle_sourcing_event(event_data: Dict[str, Any]) -> None:
    """
    Handle sourcing-related events and broadcast to WebSockets.
    
    Args:
        event_data: The event payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Sourcing event missing job_id", event_data=event_data)
        return
    
    channel = f"sourcing:{job_id}"
    message = {
        "type": "sourcing_update",
        "job_id": job_id,
        "event_type": event_data.get("type", "unknown"),
        "data": event_data
    }
    
    logger.debug("Broadcasting sourcing event to WebSocket", channel=channel, event_type=message["event_type"])
    await broadcast_to_channel(channel, message)

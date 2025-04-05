import structlog
from typing import Dict, Any

from src.websocket.routes import broadcast_to_channel

logger = structlog.get_logger(__name__)

async def handle_job_event(event_data: Dict[str, Any]) -> None:
    """
    Handle job-related events and broadcast to WebSocket clients.
    
    Args:
        event_data: The event data payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Job event missing job_id", event_data=event_data)
        return
        
    # Broadcast to job updates channel
    channel = f"job-updates:{job_id}"
    await broadcast_to_channel(channel, event_data)
    
    logger.info(
        "Broadcast job event to WebSocket clients", 
        job_id=job_id,
        event_type=event_data.get("type", "unknown")
    )


async def handle_screening_event(event_data: Dict[str, Any]) -> None:
    """
    Handle screening-related events and broadcast to WebSocket clients.
    
    Args:
        event_data: The event data payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Screening event missing job_id", event_data=event_data)
        return
        
    # Broadcast to screening channel
    channel = f"screening:{job_id}"
    await broadcast_to_channel(channel, event_data)
    
    logger.info(
        "Broadcast screening event to WebSocket clients", 
        job_id=job_id,
        event_type=event_data.get("type", "unknown")
    )


async def handle_sourcing_event(event_data: Dict[str, Any]) -> None:
    """
    Handle sourcing-related events and broadcast to WebSocket clients.
    
    Args:
        event_data: The event data payload
    """
    job_id = event_data.get("job_id")
    if not job_id:
        logger.warning("Sourcing event missing job_id", event_data=event_data)
        return
        
    # Broadcast to sourcing channel
    channel = f"sourcing:{job_id}"
    await broadcast_to_channel(channel, event_data)
    
    logger.info(
        "Broadcast sourcing event to WebSocket clients", 
        job_id=job_id,
        event_type=event_data.get("type", "unknown")
    )

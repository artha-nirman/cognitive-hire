import asyncio
from typing import Dict, Set, List, Any, Optional
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from jose import jwt, JWTError

# Updated import - use auth module directly instead of middleware
from src.common.auth.azure_auth import get_current_user
from src.common.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)

# Store active connections
active_connections: Dict[str, Set[WebSocket]] = {}

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify the authentication token for WebSocket connections."""
    try:
        # Simple validation for development mode bypass
        if (settings.ENVIRONMENT in ["development", "testing"] and 
            settings.AUTH_BYPASS_ENABLED and 
            token == settings.AUTH_BYPASS_TOKEN):
            logger.warning("WebSocket authentication bypassed with token")
            return {
                "sub": "test-user-id",
                "name": "Test User",
                "roles": ["admin"]
            }
            
        # For production, perform actual token validation here
        # This is a simplified implementation
        # In a real app, you'd use proper token validation
        payload = jwt.decode(token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("WebSocket auth failed", error=str(e))
        return None
    except Exception as e:
        logger.error("Error validating WebSocket token", exc_info=e)
        return None

async def broadcast_to_channel(channel: str, message: Dict[str, Any]) -> None:
    """Broadcast a message to all connections in a channel."""
    if channel not in active_connections:
        logger.debug("No active connections for channel", channel=channel)
        return
        
    connections = active_connections[channel]
    if not connections:
        logger.debug("Channel exists but has no connections", channel=channel)
        return
        
    logger.info(
        "Broadcasting message to channel", 
        channel=channel, 
        connection_count=len(connections),
        message_type=message.get("type")
    )
    
    # Use gather with exception handling to avoid one failed send affecting others
    send_tasks = []
    for connection in connections:
        send_tasks.append(asyncio.create_task(
            send_message_safe(connection, message)
        ))
    
    if send_tasks:
        await asyncio.gather(*send_tasks, return_exceptions=True)

async def send_message_safe(websocket: WebSocket, message: Dict[str, Any]) -> None:
    """Send a message with exception handling."""
    try:
        await websocket.send_json(message)
    except Exception as e:
        logger.warning("Failed to send message to WebSocket", error=str(e))

@router.websocket("/job/{job_id}")
async def websocket_job_endpoint(
    websocket: WebSocket, 
    job_id: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time job updates."""
    # Verify token
    user = await verify_token(token)
    if not user:
        logger.warning("WebSocket connection rejected - invalid token", job_id=job_id)
        await websocket.close(code=1008)  # Policy violation
        return
        
    # Accept the connection
    await websocket.accept()
    
    # Register connection
    channel = f"job:{job_id}"
    if channel not in active_connections:
        active_connections[channel] = set()
    active_connections[channel].add(websocket)
    
    logger.info(
        "WebSocket connection established", 
        channel=channel, 
        connection_count=len(active_connections[channel])
    )
    
    try:
        # Send initial status message
        await websocket.send_json({
            "type": "connection_established",
            "job_id": job_id,
            "message": "Connected to job updates"
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            # Process client messages if needed
            await websocket.send_json({
                "type": "echo",
                "data": data
            })
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", channel=channel)
    except Exception as e:
        logger.error("WebSocket error", channel=channel, error=str(e), exc_info=e)
    finally:
        # Remove connection
        if channel in active_connections:
            active_connections[channel].discard(websocket)
            # Clean up empty channel
            if not active_connections[channel]:
                del active_connections[channel]

# Similar endpoints for other WebSocket channels
@router.websocket("/screening/{job_id}")
async def websocket_screening_endpoint(
    websocket: WebSocket, 
    job_id: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time screening updates."""
    # Similar implementation as websocket_job_endpoint
    # ...
    # Simplified for brevity
    user = await verify_token(token)
    if not user:
        await websocket.close(code=1008)
        return
        
    await websocket.accept()
    channel = f"screening:{job_id}"
    # ...rest of implementation

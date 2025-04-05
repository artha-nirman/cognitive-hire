import json
from typing import Dict, Any, List
import asyncio
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from starlette.websockets import WebSocketState

from src.common.middleware.auth import azure_ad_b2c_auth

logger = structlog.get_logger(__name__)

router = APIRouter()

# Store active connections by channel and user ID
active_connections: Dict[str, Dict[str, WebSocket]] = {}

async def authenticate_websocket(websocket: WebSocket, token: str = Query(...)) -> Dict[str, Any]:
    """
    Authenticate a WebSocket connection.
    
    Args:
        websocket: The WebSocket connection
        token: The authentication token
        
    Returns:
        Dict containing user claims
        
    Raises:
        WebSocketDisconnect: If authentication fails
    """
    try:
        # Validate token
        payload = await azure_ad_b2c_auth.validate_token(token)
        return payload
    except Exception as e:
        logger.warning("WebSocket authentication failed", error=str(e))
        await websocket.close(code=1008, reason="Authentication failed")
        raise WebSocketDisconnect(code=1008)

@router.websocket("/job-updates/{job_id}")
async def job_updates(websocket: WebSocket, job_id: str, token: str = Query(...)):
    """WebSocket endpoint for real-time job updates."""
    try:
        # Authenticate
        user_claims = await authenticate_websocket(websocket, token)
        user_id = user_claims.get("sub")
        
        # Accept connection
        await websocket.accept()
        logger.info("WebSocket connection accepted", channel="job-updates", job_id=job_id, user_id=user_id)
        
        # Register connection
        channel = f"job-updates:{job_id}"
        if channel not in active_connections:
            active_connections[channel] = {}
        active_connections[channel][user_id] = websocket
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to job updates stream",
            "job_id": job_id
        })
        
        # Keep connection open until client disconnects
        try:
            while True:
                # Ping to keep connection alive and check for disconnect
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", channel="job-updates", job_id=job_id, user_id=user_id)
            if channel in active_connections and user_id in active_connections[channel]:
                del active_connections[channel][user_id]
                if not active_connections[channel]:
                    del active_connections[channel]
                    
    except WebSocketDisconnect:
        # Authentication failed or connection closed before accept
        logger.info("WebSocket connection failed", channel="job-updates", job_id=job_id)
    except Exception as e:
        logger.error("WebSocket error", channel="job-updates", job_id=job_id, exc_info=e)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1011, reason="Server error")

@router.websocket("/screening/{job_id}")
async def screening_updates(websocket: WebSocket, job_id: str, token: str = Query(...)):
    """WebSocket endpoint for real-time screening updates."""
    try:
        # Authenticate
        user_claims = await authenticate_websocket(websocket, token)
        user_id = user_claims.get("sub")
        
        # Accept connection
        await websocket.accept()
        logger.info("WebSocket connection accepted", channel="screening", job_id=job_id, user_id=user_id)
        
        # Register connection
        channel = f"screening:{job_id}"
        if channel not in active_connections:
            active_connections[channel] = {}
        active_connections[channel][user_id] = websocket
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to screening updates stream",
            "job_id": job_id
        })
        
        # Keep connection open until client disconnects
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", channel="screening", job_id=job_id, user_id=user_id)
            if channel in active_connections and user_id in active_connections[channel]:
                del active_connections[channel][user_id]
                if not active_connections[channel]:
                    del active_connections[channel]
                    
    except WebSocketDisconnect:
        # Authentication failed or connection closed before accept
        logger.info("WebSocket connection failed", channel="screening", job_id=job_id)
    except Exception as e:
        logger.error("WebSocket error", channel="screening", job_id=job_id, exc_info=e)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1011, reason="Server error")

@router.websocket("/sourcing/{job_id}")
async def sourcing_updates(websocket: WebSocket, job_id: str, token: str = Query(...)):
    """WebSocket endpoint for real-time sourcing updates."""
    try:
        # Authenticate
        user_claims = await authenticate_websocket(websocket, token)
        user_id = user_claims.get("sub")
        
        # Accept connection
        await websocket.accept()
        logger.info("WebSocket connection accepted", channel="sourcing", job_id=job_id, user_id=user_id)
        
        # Register connection
        channel = f"sourcing:{job_id}"
        if channel not in active_connections:
            active_connections[channel] = {}
        active_connections[channel][user_id] = websocket
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to sourcing updates stream",
            "job_id": job_id
        })
        
        # Keep connection open until client disconnects
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", channel="sourcing", job_id=job_id, user_id=user_id)
            if channel in active_connections and user_id in active_connections[channel]:
                del active_connections[channel][user_id]
                if not active_connections[channel]:
                    del active_connections[channel]
                    
    except WebSocketDisconnect:
        # Authentication failed or connection closed before accept
        logger.info("WebSocket connection failed", channel="sourcing", job_id=job_id)
    except Exception as e:
        logger.error("WebSocket error", channel="sourcing", job_id=job_id, exc_info=e)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1011, reason="Server error")

async def broadcast_to_channel(channel: str, message: Dict[str, Any]):
    """
    Broadcast a message to all connections in a channel.
    
    Args:
        channel: The channel to broadcast to
        message: The message to send
    """
    if channel not in active_connections:
        logger.debug("No active connections for channel", channel=channel)
        return
        
    disconnected_users = []
    for user_id, websocket in active_connections[channel].items():
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning("Failed to send message", channel=channel, user_id=user_id, error=str(e))
            disconnected_users.append(user_id)
            
    # Clean up disconnected users
    for user_id in disconnected_users:
        if user_id in active_connections[channel]:
            del active_connections[channel][user_id]
            
    if not active_connections[channel]:
        del active_connections[channel]

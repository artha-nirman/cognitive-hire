import json
import datetime
from typing import Any, Dict, List, Optional, Callable, Awaitable
import aio_pika
import structlog
import uuid
import redis.asyncio as redis

from src.common.config import settings

logger = structlog.get_logger(__name__)

# Global connection objects
connection = None
channel = None

# Event handler type
EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

# Map of event types to handlers
event_handlers: Dict[str, List[EventHandler]] = {}


async def init_event_system() -> None:
    """
    Initialize the event system.
    
    Sets up connections to the event bus (RabbitMQ) or falls back to Redis.
    Binds queues to the relevant event patterns.
    
    Raises:
        Exception: If connection to the event system fails
    """
    global connection, channel
    
    if not settings.EVENT_BUS_URL:
        logger.warning("No event bus URL configured, using Redis as fallback")
        await init_redis_events()
        return
        
    try:
        # Connect to RabbitMQ
        logger.info("Connecting to event bus", url=settings.EVENT_BUS_URL.split("@")[-1])
        connection = await aio_pika.connect_robust(settings.EVENT_BUS_URL)
        channel = await connection.channel()
        
        # Declare exchange
        exchange = await channel.declare_exchange(
            "recruitment_events", 
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Declare and bind queue for this service
        queue_name = f"recruitment-service-{settings.ENVIRONMENT}"
        logger.debug("Creating queue", queue_name=queue_name)
        queue = await channel.declare_queue(
            queue_name,
            durable=True
        )
        
        # Bind to relevant event patterns
        event_patterns = [
            "employer.*",
            "job.*",
            "publishing.*",
            "screening.*", 
            "sourcing.*",
            "candidate.*",  # External events we care about
            "workflow.*"    # External events we care about
        ]
        
        for pattern in event_patterns:
            logger.debug("Binding to event pattern", pattern=pattern)
            await queue.bind(exchange, routing_key=pattern)
        
        # Start consuming events
        await queue.consume(process_event)
        
        logger.info("Event system initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize event system", exc_info=e)
        connection = None
        channel = None
        raise


async def close_event_system() -> None:
    """
    Close event system connections.
    
    Properly closes RabbitMQ connections when the application is shutting down.
    """
    global connection, channel
    
    if connection:
        try:
            logger.info("Closing event system connection")
            await connection.close()
            logger.info("Event system connection closed")
        except Exception as e:
            logger.error("Error closing event system connection", exc_info=e)
    
    connection = None
    channel = None


async def publish_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Publish an event to the event bus.
    
    Args:
        event_type: Type of the event (e.g., "job.created")
        data: Event payload data
        
    Raises:
        Exception: If publishing fails and fallback also fails
    """
    if not connection or not channel:
        logger.warning(
            "Event system not initialized, using fallback", 
            event_type=event_type
        )
        await publish_redis_event(event_type, data)
        return
    
    try:
        # Create the event message
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        # Get exchange
        exchange = await channel.get_exchange("recruitment_events")
        
        # Publish message
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json"
            ),
            routing_key=event_type
        )
        
        logger.debug("Published event", event_type=event_type, data=data)
    except Exception as e:
        logger.error("Failed to publish event", event_type=event_type, exc_info=e)
        # Try fallback
        await publish_redis_event(event_type, data)


async def register_event_handler(event_type: str, handler: EventHandler) -> None:
    """
    Register a handler for an event type.
    
    Args:
        event_type: Type of event to handle
        handler: Async function to handle the event
    """
    if event_type not in event_handlers:
        event_handlers[event_type] = []
    
    event_handlers[event_type].append(handler)
    logger.debug("Registered event handler", 
                 event_type=event_type, 
                 handler=handler.__name__)


async def process_event(message: aio_pika.IncomingMessage) -> None:
    """
    Process an incoming event message.
    
    Args:
        message: The incoming RabbitMQ message
    """
    async with message.process():
        try:
            # Parse message
            body = json.loads(message.body.decode())
            event_type = body["type"]
            data = body["data"]
            
            logger.debug("Received event", 
                         event_type=event_type, 
                         routing_key=message.routing_key)
            
            # Find handlers and call them
            handlers = event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(
                        "Error in event handler", 
                        event_type=event_type, 
                        handler=handler.__name__, 
                        exc_info=e
                    )
        except Exception as e:
            logger.error("Failed to process event", exc_info=e)


# Redis fallback for local development or when RabbitMQ is not available
redis_client = None

async def init_redis_events() -> None:
    """
    Initialize Redis for event publishing (fallback).
    
    Used when the primary event system (RabbitMQ) is not available.
    """
    global redis_client
    try:
        logger.info("Initializing Redis event system", url=settings.REDIS_URL)
        redis_client = redis.from_url(settings.REDIS_URL)
        # Start a background task to subscribe to events
        import asyncio
        asyncio.create_task(redis_subscription_listener())
        logger.info("Redis event system initialized")
    except Exception as e:
        logger.error("Failed to initialize Redis event system", exc_info=e)
        redis_client = None


async def redis_subscription_listener() -> None:
    """
    Listen for Redis published events.
    
    Subscribes to all relevant event channels and processes messages.
    """
    if not redis_client:
        logger.error("Redis client not initialized, cannot start listener")
        return
        
    try:
        logger.info("Starting Redis subscription listener")
        # Create a new connection for the subscription
        sub_client = redis.from_url(settings.REDIS_URL)
        pubsub = sub_client.pubsub()
        
        # Subscribe to all event channels we care about
        await pubsub.psubscribe("event:*")
        
        # Listen for messages
        logger.info("Listening for Redis events")
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                try:
                    # Parse the message
                    logger.debug("Received Redis message", channel=message["channel"])
                    data = json.loads(message["data"])
                    event_type = data["type"]
                    event_data = data["data"]
                    
                    # Process with handlers
                    handlers = event_handlers.get(event_type, [])
                    for handler in handlers:
                        try:
                            await handler(event_data)
                        except Exception as e:
                            logger.error(
                                "Error in Redis event handler", 
                                event_type=event_type,
                                exc_info=e
                            )
                except Exception as e:
                    logger.error("Failed to process Redis event", exc_info=e)
    except Exception as e:
        logger.error("Redis subscription error", exc_info=e)
    finally:
        # Try to clean up
        try:
            logger.info("Cleaning up Redis subscription")
            await pubsub.unsubscribe()
            await sub_client.close()
        except Exception as e:
            logger.error("Error during Redis cleanup", exc_info=e)


async def publish_redis_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Publish an event to Redis.
    
    Args:
        event_type: Type of the event
        data: Event payload data
        
    Raises:
        Warning: If Redis client is not initialized
    """
    if not redis_client:
        logger.warning(
            "Redis client not initialized, event will be lost",
            event_type=event_type
        )
        return
        
    try:
        # Create the message
        message = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "data": data,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        # Publish to Redis
        await redis_client.publish(f"event:{event_type}", json.dumps(message))
        logger.debug("Published event to Redis", event_type=event_type)
    except Exception as e:
        logger.error(
            "Failed to publish event to Redis", 
            event_type=event_type, 
            exc_info=e
        )

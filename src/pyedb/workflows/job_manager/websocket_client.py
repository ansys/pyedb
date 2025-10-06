"""
WebSocket client for real-time job updates
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict

from config import JobManagerConfig
import socketio

logger = logging.getLogger(__name__)


class JobManagerWebSocketClient:
    """WebSocket client for real-time job updates"""

    def __init__(self, url: str = None):
        self.url = url or JobManagerConfig.WEBSOCKET_URL
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.callbacks = {}
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup Socket.IO event handlers"""

        @self.sio.event
        async def connect():
            self.connected = True
            logger.info(f"Connected to WebSocket server at {self.url}")
            await self.sio.emit("client_connected", {"client_type": "streamlit_ui"})

        @self.sio.event
        async def disconnect():
            self.connected = False
            logger.info("Disconnected from WebSocket server")

        @self.sio.event
        async def connect_error(data):
            logger.error(f"WebSocket connection error: {data}")

        # Job-specific events
        @self.sio.on("job_queued")
        async def on_job_queued(data):
            logger.info(f"Job queued: {data}")
            await self._trigger_callback("job_queued", data)

        @self.sio.on("job_started")
        async def on_job_started(data):
            logger.info(f"Job started: {data}")
            await self._trigger_callback("job_started", data)

        @self.sio.on("job_scheduled")
        async def on_job_scheduled(data):
            logger.info(f"Job scheduled: {data}")
            await self._trigger_callback("job_scheduled", data)

        @self.sio.on("job_completed")
        async def on_job_completed(data):
            logger.info(f"Job completed: {data}")
            await self._trigger_callback("job_completed", data)

        @self.sio.on("job_failed")
        async def on_job_failed(data):
            logger.error(f"Job failed: {data}")
            await self._trigger_callback("job_failed", data)

        @self.sio.on("job_cancelled")
        async def on_job_cancelled(data):
            logger.info(f"Job cancelled: {data}")
            await self._trigger_callback("job_cancelled", data)

        @self.sio.on("resource_update")
        async def on_resource_update(data):
            logger.debug(f"Resource update: {data}")
            await self._trigger_callback("resource_update", data)

        @self.sio.on("queue_update")
        async def on_queue_update(data):
            logger.debug(f"Queue update: {data}")
            await self._trigger_callback("queue_update", data)

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            await self.sio.connect(self.url)
            logger.info("WebSocket client initialized")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.connected:
            await self.sio.disconnect()
            self.connected = False

    def register_callback(self, event: str, callback: Callable):
        """Register a callback for a specific event"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
        logger.debug(f"Registered callback for event: {event}")

    def unregister_callback(self, event: str, callback: Callable):
        """Unregister a callback"""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
            logger.debug(f"Unregistered callback for event: {event}")

    async def _trigger_callback(self, event: str, data: Dict[str, Any]):
        """Trigger all callbacks for an event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error in callback for event {event}: {e}")

    def is_connected(self) -> bool:
        """Check if WebSocket client is connected"""
        return self.connected and self.sio.connected

    async def request_job_status(self, job_id: str):
        """Request status update for a specific job"""
        if self.connected:
            await self.sio.emit("request_job_status", {"job_id": job_id})

    async def subscribe_to_job_updates(self, job_id: str):
        """Subscribe to updates for a specific job"""
        if self.connected:
            await self.sio.emit("subscribe_job", {"job_id": job_id})


class StreamlitWebSocketManager:
    """WebSocket manager specifically for Streamlit integration"""

    def __init__(self):
        self.client = JobManagerWebSocketClient()
        self.auto_refresh = False
        self.refresh_callback = None
        self.last_update = None

    async def initialize(self, refresh_callback: Callable = None):
        """Initialize WebSocket manager"""
        self.refresh_callback = refresh_callback

        # Register callbacks for automatic UI updates
        self.client.register_callback("job_queued", self._on_job_update)
        self.client.register_callback("job_started", self._on_job_update)
        self.client.register_callback("job_completed", self._on_job_update)
        self.client.register_callback("job_failed", self._on_job_update)
        self.client.register_callback("job_cancelled", self._on_job_update)

        try:
            await self.client.connect()
        except Exception as e:
            logger.warning(f"WebSocket connection failed, falling back to polling: {e}")

    async def _on_job_update(self, data: Dict[str, Any]):
        """Handle job update events"""
        logger.info(f"Job update received: {data}")
        self.last_update = asyncio.get_event_loop().time()

        # Trigger Streamlit refresh if callback is provided
        if self.refresh_callback:
            try:
                if asyncio.iscoroutinefunction(self.refresh_callback):
                    await self.refresh_callback()
                else:
                    self.refresh_callback()
            except Exception as e:
                logger.error(f"Error in refresh callback: {e}")

    def enable_auto_refresh(self, enabled: bool = True):
        """Enable or disable auto-refresh"""
        self.auto_refresh = enabled
        logger.info(f"Auto-refresh {'enabled' if enabled else 'disabled'}")

    async def close(self):
        """Close WebSocket manager"""
        await self.client.disconnect()

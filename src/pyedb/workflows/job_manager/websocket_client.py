"""
Backend client for communicating with the Job Manager service.
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class EnhancedBackendClient:
    """Backend client that communicates with the Job Manager API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._connected = False
        self.scheduler_info: Optional[Dict[str, Any]] = None
        self.is_local_mode = True

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establish a connection to the backend."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
            self._connected = True
            logger.info(f"Connected to backend at {self.base_url}")

    async def disconnect(self):
        """Close the connection to the backend."""
        if self.session:
            await self.session.close()
            self.session = None
            self._connected = False
            logger.info("Disconnected from backend")

    async def initialize(self):
        """Initialize and detect scheduler by fetching system status from the backend."""
        await self.connect()
        try:
            status = await self.get_system_status()
            self.scheduler_info = status.get("scheduler_detection")
            self.is_local_mode = status.get("mode") == "local"
            logger.info(f"System status synchronized with backend: mode='{self.get_current_mode()}'")
        except Exception as e:
            logger.error(f"Failed to initialize from backend: {e}. Assuming local mode as a fallback.")
            self.scheduler_info = {
                "active_scheduler": "none",
                "detected_by": "fallback (connection failed)",
                "backend_available": False,
            }
            self.is_local_mode = True

    async def get_system_status(self) -> Dict[str, Any]:
        """Get the complete system status from the backend."""
        if not self._connected or not self.session:
            raise ConnectionError("Client not connected")
        try:
            async with self.session.get(f"{self.base_url}/system/status") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error getting system status: {e}")
            raise

    async def submit_job_auto(self, **kwargs) -> Optional[str]:
        """Submit a job using the backend's automatic scheduler detection."""
        if not self._connected or not self.session:
            raise ConnectionError("Client not connected")
        try:
            job_config = {
                "project_path": kwargs.get("project_path"),
                "jobid": f"{kwargs.get('job_name')}_{int(datetime.now().timestamp())}",
                "simulation_type": kwargs.get("simulation_type"),
                "resources": {"nodes": kwargs.get("num_nodes", 1), "cpus_per_node": kwargs.get("cpus_per_node", 16)},
            }
            priority_map = {"low": -1, "normal": 0, "high": 5, "critical": 10}
            priority_num = priority_map.get(kwargs.get("priority", "normal"), 0)

            payload = {"config": job_config, "priority": priority_num}
            async with self.session.post(f"{self.base_url}/jobs/submit", json=payload) as response:
                result = await response.json()
                if response.status == 200 and result.get("success"):
                    job_id = result.get("job_id")
                    logger.info(f"Job submitted successfully: {job_id}")
                    return job_id
                else:
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Job submission failed: {error_msg}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Error submitting job: {e}")
            return None

    def get_current_mode(self) -> str:
        """Get the current execution mode (local or scheduler)."""
        return "local" if self.is_local_mode else "scheduler"

    def is_connected(self) -> bool:
        return self._connected and self.session and not self.session.closed

"""
Development-mode backend client with proper PYTHONPATH handling
"""

import asyncio
from datetime import datetime
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import aiohttp

# Add the src directory to Python path for development mode
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

# Add to Python path for development
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Now we can import from pyedb
try:
    from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler

    BACKEND_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info(f"Backend modules loaded successfully from {SRC_PATH}")
except ImportError as e:
    BACKEND_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"Could not import backend modules: {e}")
    logger.info(f"PYTHONPATH: {sys.path}")


class EnhancedBackendClient:
    """Backend client that works in development mode"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = None
        self._connected = False
        self.scheduler_info = None
        self.is_local_mode = True

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establish connection to backend"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
            self._connected = True
            logger.info(f"Connected to backend at {self.base_url}")

    async def disconnect(self):
        """Close connection to backend"""
        if self.session:
            await self.session.close()
            self.session = None
            self._connected = False
            logger.info("Disconnected from backend")

    async def initialize(self):
        """Initialize and detect scheduler using backend"""
        await self.connect()

        # Use existing JobManagerHandler detection if available
        if BACKEND_AVAILABLE:
            try:
                detected_scheduler = JobManagerHandler._detect_scheduler()
                self.scheduler_info = {
                    "active_scheduler": detected_scheduler.value,
                    "detected_by": "JobManagerHandler._detect_scheduler()",
                    "backend_available": True,
                }
                self.is_local_mode = detected_scheduler.value == "none"
                logger.info(f"Scheduler detection complete: {self.scheduler_info}")

            except Exception as e:
                logger.error(f"Scheduler detection failed: {e}")
                self.scheduler_info = {"active_scheduler": "none", "error": str(e), "backend_available": False}
                self.is_local_mode = True
        else:
            # Fallback - assume local mode if backend not available
            logger.warning("Backend not available, assuming local mode")
            self.scheduler_info = {
                "active_scheduler": "none",
                "detected_by": "fallback (backend unavailable)",
                "backend_available": False,
            }
            self.is_local_mode = True

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status from backend"""
        if not self.scheduler_info:
            await self.initialize()

        status = {
            "scheduler_detection": self.scheduler_info,
            "mode": "local" if self.is_local_mode else "scheduler",
            "backend_status": "connected" if self._connected else "disconnected",
            "project_path": SRC_PATH,
        }

        # Add local pool info if available
        try:
            pool_stats = await self.get_queue_stats()
            if pool_stats:
                status["local_pool"] = {
                    "running_jobs": pool_stats.get("running_jobs", 0),
                    "queued_jobs": pool_stats.get("total_queued", 0),
                    "max_concurrent": pool_stats.get("max_concurrent", 2),
                }
        except Exception as e:
            logger.warning(f"Could not get pool stats: {e}")

        return status

    async def get_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs from backend"""
        try:
            async with self.session.get(f"{self.base_url}/jobs") as response:
                if response.status == 200:
                    jobs = await response.json()
                    logger.info(f"Retrieved {len(jobs)} jobs from backend")
                    return jobs
                else:
                    logger.error(f"Failed to get jobs: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
            return []

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            async with self.session.get(f"{self.base_url}/queue") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {}

    async def submit_job_auto(self, **kwargs) -> Optional[str]:
        """Submit job - backend handles local vs scheduler"""
        try:
            job_config = {
                "project_path": kwargs.get("project_path"),
                "jobid": f"{kwargs.get('job_name')}_{int(datetime.now().timestamp())}",
                "solver": "Hfss3DLayout",
                "simulation_type": kwargs.get("simulation_type"),
                "resources": {"nodes": kwargs.get("num_nodes", 1), "cpus_per_node": kwargs.get("cpus_per_node", 16)},
                "batch_system": "auto",  # Let backend decide
                "priority": kwargs.get("priority", "normal"),
            }

            # Map priority to numbers
            priority_map = {"low": -1, "normal": 0, "high": 5, "critical": 10}
            priority_num = priority_map.get(kwargs.get("priority", "normal"), 0)

            async with self.session.post(
                f"{self.base_url}/jobs/submit", json={"config": job_config, "priority": priority_num}
            ) as response:
                result = await response.json()

                if response.status == 200 and result.get("success"):
                    job_id = result.get("job_id")
                    logger.info(f"Job submitted successfully: {job_id}")
                    return job_id
                else:
                    logger.error(f"Job submission failed: {result.get('error', 'Unknown error')}")
                    return None

        except Exception as e:
            logger.error(f"Error submitting job: {e}")
            return None

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        try:
            async with self.session.post(f"{self.base_url}/jobs/{job_id}/cancel") as response:
                result = await response.json()
                return response.status == 200 and result.get("success", False)
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {e}")
            return False

    def get_current_mode(self) -> str:
        """Get current execution mode"""
        return "local" if self.is_local_mode else "scheduler"

    def is_connected(self) -> bool:
        return self._connected and self.session and not self.session.closed


# Development helper function
def check_backend_access():
    """Check if backend modules are accessible"""
    try:
        from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler

        detected = JobManagerHandler._detect_scheduler()
        print(f"✅ Backend accessible! Detected scheduler: {detected.value}")
        return True
    except ImportError as e:
        print(f"❌ Backend not accessible: {e}")
        print(f"PYTHONPATH: {sys.path}")
        return False


if __name__ == "__main__":
    check_backend_access()

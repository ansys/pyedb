"""
Backend client for connecting to Job Manager service
"""

from typing import Any, Dict, Optional, Union

import aiohttp


class BackendClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status from backend"""
        try:
            async with self.session.get(f"{self.base_url}/system/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e), "mode": "offline"}

    async def submit_job(self, config: Union[Dict[str, Any], str], priority: int = 0) -> Optional[str]:
        """Submit a job to the backend"""
        try:
            payload = {"config": config, "priority": priority}

            async with self.session.post(f"{self.base_url}/jobs/submit", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("job_id") if result.get("success") else None
        except Exception as e:
            print(f"Error submitting job: {e}")
            return None

    async def get_all_jobs(self) -> list:
        """Get all jobs from backend"""
        try:
            async with self.session.get(f"{self.base_url}/jobs") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception:
            return []

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            async with self.session.get(f"{self.base_url}/queue") as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception:
            return {}

    async def edit_concurrent_limits(self, limits_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Edit concurrent job limits in the backend pool"""
        try:
            async with self.session.put(f"{self.base_url}/pool/limits", json=limits_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("limits") if result.get("success") else None
                else:
                    print(f"Failed to edit concurrent limits: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error editing concurrent limits: {e}")
            return None

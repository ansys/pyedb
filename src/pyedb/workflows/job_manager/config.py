"""
Configuration settings for PyEDB Job Manager integration
"""

import os
from typing import Any, Dict


class JobManagerConfig:
    """Configuration settings for the job manager integration"""

    # Backend service settings
    BACKEND_HOST = os.getenv("PYEDB_JOB_MANAGER_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("PYEDB_JOB_MANAGER_PORT", "8080"))
    BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

    # WebSocket settings
    WEBSOCKET_URL = f"ws://{BACKEND_HOST}:{BACKEND_PORT}"

    # API endpoints
    API_ENDPOINTS = {
        "jobs": "/jobs",
        "submit": "/jobs/submit",
        "cancel": "/jobs/{job_id}/cancel",
        "resources": "/resources",
        "queue": "/queue",
        "priority": "/jobs/{job_id}/priority",
    }

    # Timeout settings
    REQUEST_TIMEOUT = 30  # seconds
    CONNECTION_TIMEOUT = 10  # seconds

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    # Auto-refresh settings
    AUTO_REFRESH_INTERVAL = 5  # seconds

    # File upload settings
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = "uploads"

    # Logging settings
    LOG_LEVEL = os.getenv("PYEDB_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Resource limits
    DEFAULT_MAX_CONCURRENT_JOBS = 4
    DEFAULT_MAX_CPU_PERCENT = 80.0
    DEFAULT_MIN_MEMORY_GB = 2.0
    DEFAULT_MIN_DISK_GB = 10.0

    @classmethod
    def get_backend_url(cls, endpoint: str) -> str:
        """Get full backend URL for an endpoint"""
        return f"{cls.BACKEND_URL}{endpoint}"

    @classmethod
    def get_job_status_colors(cls) -> Dict[str, str]:
        """Get color mapping for job statuses"""
        return {
            "pending": "#ed6c02",
            "queued": "#7b1fa2",
            "running": "#0066cc",
            "completed": "#2e7d32",
            "failed": "#d32f2f",
            "cancelled": "#9e9e9e",
            "scheduled": "#ff9800",
        }

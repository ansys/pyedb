"""
Setup script for PyEDB Job Manager backend service
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_backend_service():
    """Setup and start the backend service"""

    # Check if PyEDB is available
    try:
        import pyedb

        logger.info("✅ PyEDB found")
    except ImportError:
        logger.error("❌ PyEDB not found. Please install: pip install pyedb")
        return False

    # Create directories
    directories = ["uploads", "logs", "temp"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

    # Start backend service
    logger.info("🚀 Starting PyEDB Job Manager backend service...")

    try:
        # Import and start the service
        import asyncio

        from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits

        async def start_service():
            manager = JobManager(ResourceLimits(max_concurrent_jobs=4))
            # The service will start automatically

            logger.info("✅ Backend service started successfully!")
            logger.info("🌐 Service available at: http://localhost:8080")

            # Keep the service running
            while True:
                await asyncio.sleep(1)

        asyncio.run(start_service())

    except Exception as e:
        logger.error(f"❌ Failed to start backend service: {e}")
        return False

    return True


if __name__ == "__main__":
    setup_backend_service()

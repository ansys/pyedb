"""
Windows-specific backend setup for PyEDB Job Manager
"""

import logging
import os
from pathlib import Path
import platform
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_windows_backend():
    """Setup Windows-specific backend configuration"""

    logger.info("🔧 Setting up PyEDB Job Manager for Windows...")

    # Check Windows version
    windows_version = platform.version()
    logger.info(f"Windows Version: {windows_version}")

    # Create Windows-specific directories
    directories = ["uploads", "logs", "temp", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

    # Set Windows-specific environment variables
    os.environ["PYEDB_PLATFORM"] = "windows"
    os.environ["ANSYS_EM_ROOT"] = r"C:\Program Files\AnsysEM"

    # Check for ANSYS installation
    ansys_paths = [
        r"C:\Program Files\AnsysEM",
        r"C:\Program Files\ANSYS Inc",
        r"D:\AnsysEM",
    ]

    ansys_found = False
    for path in ansys_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found ANSYS installation at: {path}")
            os.environ["ANSYS_PATH"] = path
            ansys_found = True
            break

    if not ansys_found:
        logger.warning("⚠️  ANSYS installation not found in standard locations")
        logger.info("Please set ANSYS_PATH environment variable manually")

    # Configure Windows Firewall (optional)
    logger.info("🔒 Note: You may need to allow Python through Windows Firewall")
    logger.info("   - Port 8080 for backend service")
    logger.info("   - Port 8501 for Streamlit UI")

    return True


if __name__ == "__main__":
    setup_windows_backend()

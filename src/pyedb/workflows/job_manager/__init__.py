"""
ANSYS EDB Job Manager
Professional job management interface for ANSYS Electronic Desktop simulations.
"""

__version__ = "3.0.0"
__author__ = "ANSYS, Inc."

from .app import JobManagerApp, main
from .job_manager import JobManager

__all__ = ["JobManagerApp", "JobManager", "main"]
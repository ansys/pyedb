# src/pyedb/workflows/job_manager/models/job_models.py
"""
Data models for job management
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class JobRequest(BaseModel):
    """Request model for submitting a new job"""
    name: str = Field(..., description="Name of the job")
    type: str = Field(..., description="Local or Cluster execution")
    solver: str = Field(..., description="ANSYS solver type")
    priority: str = Field("Medium", description="Job priority level")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Job-specific settings")


class Job(BaseModel):
    """Job model representing a simulation job"""
    id: str
    name: str
    type: str
    solver: str
    priority: str
    status: JobStatus
    submitted_date: str
    started_date: Optional[str] = None
    completed_date: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
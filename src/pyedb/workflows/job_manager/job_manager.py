# src/pyedb/workflows/job_manager/job_manager.py
"""
Core job management functionality for ANSYS EDB Job Manager
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from models.job_models import Job, JobRequest, JobStatus


class JobManager:
    """Manages job submission, tracking, and execution"""

    def __init__(self, data_file: str = "jobs.json"):
        self.data_file = data_file
        self.jobs: List[Job] = []
        self.load_jobs()

    def submit_job(self, job_request: JobRequest) -> str:
        """Submit a new job for execution"""
        job_id = f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

        job = Job(
            id=job_id,
            name=job_request.name,
            type=job_request.type,
            solver=job_request.solver,
            priority=job_request.priority,
            status=JobStatus.PENDING,
            submitted_date=datetime.now().isoformat(),
            settings=job_request.settings
        )

        self.jobs.append(job)
        self.save_jobs()

        # Simulate job execution (replace with actual execution logic)
        self._start_job_execution(job)

        return job_id

    def get_jobs(self, filters: Optional[Dict] = None) -> List[Job]:
        """Retrieve jobs with optional filtering"""
        jobs = self.jobs

        if filters:
            if 'status' in filters:
                jobs = [j for j in jobs if j.status == filters['status']]
            if 'type' in filters:
                jobs = [j for j in jobs if j.type == filters['type']]

        # Sort by submission date (newest first)
        return sorted(jobs, key=lambda x: x.submitted_date, reverse=True)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or pending job"""
        job = next((j for j in self.jobs if j.id == job_id), None)

        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            job.completed_date = datetime.now().isoformat()
            self.save_jobs()
            return True

        return False

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a specific job"""
        job = next((j for j in self.jobs if j.id == job_id), None)
        return job.status if job else None

    def _start_job_execution(self, job: Job):
        """Start job execution (simulated)"""
        # This would integrate with actual ANSYS solvers
        # For now, we simulate job progression

        if job.type == "Local":
            # Simulate local job execution
            job.status = JobStatus.RUNNING
            self.save_jobs()
        else:
            # Simulate cluster job submission
            job.status = JobStatus.PENDING
            self.save_jobs()

    def load_jobs(self):
        """Load jobs from persistent storage"""
        try:
            if Path(self.data_file).exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.jobs = [Job(**job_data) for job_data in data]
        except Exception as e:
            print(f"Error loading jobs: {e}")
            self.jobs = []

    def save_jobs(self):
        """Save jobs to persistent storage"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump([job.dict() for job in self.jobs], f, indent=2)
        except Exception as e:
            print(f"Error saving jobs: {e}")

    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "total_jobs": len(self.jobs),
            "running_jobs": len([j for j in self.jobs if j.status == JobStatus.RUNNING]),
            "completed_jobs": len([j for j in self.jobs if j.status == JobStatus.COMPLETED]),
            "pending_jobs": len([j for j in self.jobs if j.status == JobStatus.PENDING]),
        }
from typing import List
from job import Job


class JobManager:
    def get_jobs(self) -> List[Job]:
        # Should return list of Job objects
        pass

    def create_job(self, name, project, simulation_type, project_file=None,
                   batch_options=None, resources=None, batch_system="local",
                   priority="normal") -> Job:
        # Should create and return a Job object
        pass

    def submit_job(self, job: Job) -> bool:
        # Should submit job to batch system
        pass

    def get_job(self, job_id: str) -> Job:
        # Should return specific job
        pass
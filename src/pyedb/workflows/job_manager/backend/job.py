import datetime


class Job:
    def __init__(self):
        self.job_id: str
        self.name: str
        self.project: str
        self.status: str  # "pending", "running", "completed", "failed"
        self.simulation_type: str
        self.priority: str
        self.batch_system: str
        self.resources: dict  # {"nodes": 1, "cpus_per_node": 1}
        self.start_time: datetime
        self.submit_time: datetime
        self.completion_time: datetime
        self.project_file: str

from typing import List

from aiohttp import web

import pyedb
from pyedb.workflows.job_manager.job_submission import HFSSSimulationConfig
from pyedb.workflows.job_manager.service import (
    JobManager,
    ResourceLimits,
    submit_job_to_manager,
)


class JobManagerHandler:
    def __init__(self, edb: pyedb.Edb):
        self.ansys_path = edb.base_path
        self.manager = JobManager()
        self.manager.resource_limits = ResourceLimits(max_concurrent_jobs=2)
        self.runner = None

    async def start_service(self, host: str = "localhost", port: int = 8080):
        self.runner = web.AppRunner(self.manager.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()
        print(f"Job Manager service started at http://{host}:{port}")

    async def stop_service(self):
        if self.runner:
            await self.runner.cleanup()
            print("Job Manager service stopped.")

    async def submit_jobs(self, tasks: List[HFSSSimulationConfig]) -> List[str]:
        job_ids = []
        for task in tasks:
            print("Submitting job:", task.jobid)
            job_id = await submit_job_to_manager(task)
            job_ids.append(job_id)
            print("Submitted job ID:", job_id)
        return job_ids

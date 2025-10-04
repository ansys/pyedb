import os

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .service import JobService


class JobManagerHandler:
    def __init__(self):
        self.service = JobService()
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        # UI Routes - serve static files
        ui_path = os.path.join(os.path.dirname(__file__), "ui/dist")

        # Mount static files if they exist
        if os.path.exists(ui_path):
            self.router.mount("/ui/static", StaticFiles(directory=ui_path), name="ui-static")

        # Serve UI
        @self.router.get("/ui")
        @self.router.get("/ui/")
        async def serve_ui():
            return FileResponse(os.path.join(ui_path, "index.html"))

        @self.router.get("/ui/{full_path:path}")
        async def serve_ui_path(full_path: str):
            return FileResponse(os.path.join(ui_path, "index.html"))

        # API Routes
        @self.router.get("/jobs")
        async def get_jobs():
            return self.service.get_jobs()

        @self.router.get("/jobs/{job_id}")
        async def get_job(job_id: str):
            return self.service.get_job(job_id)

        @self.router.post("/jobs")
        async def create_job(job_data: dict):
            return self.service.create_job(job_data)

        @self.router.put("/jobs/{job_id}")
        async def update_job(job_id: str, job_data: dict):
            return self.service.update_job(job_id, job_data)

        @self.router.delete("/jobs/{job_id}")
        async def delete_job(job_id: str):
            return self.service.delete_job(job_id)

        @self.router.get("/cluster/partitions")
        async def get_partitions():
            return self.service.get_partitions()

        @self.router.get("/resources/local")
        async def get_local_resources():
            return self.service.get_local_resources()

        @self.router.get("/job-pool/status")
        async def get_job_pool_status():
            return self.service.get_job_pool_status()

    def get_router(self):
        return self.router

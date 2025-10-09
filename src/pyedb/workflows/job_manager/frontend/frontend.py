# job_manager_ui.py
import reflex as rx
import asyncio
from typing import List, Dict, Optional
import httpx
import json
from datetime import datetime


class JobManagerState(rx.State):
    """State for Job Manager UI connecting to running JobManagerHandler"""

    # UI State
    jobs: List[Dict] = []
    local_resources: Dict = {}
    cluster_partitions: List[Dict] = []
    show_submit_dialog: bool = False
    selected_file: str = ""

    # Job submission form
    project_file: str = ""
    num_cpus: int = 4
    num_nodes: int = 1
    cpus_per_node: int = 4
    tasks_per_node: int = 1
    selected_queue: str = "default"
    batch_options: str = ""

    # Connection settings
    backend_url: str = "http://localhost:8000"  # Adjust based on your JobManagerHandler

    # Auto-refresh interval
    _auto_refresh: bool = True

    def on_load(self):
        """Initialize when app loads"""
        self.refresh_all_data()
        return self.start_auto_refresh()

    async def start_auto_refresh(self):
        """Start automatic refresh of data"""
        while self._auto_refresh:
            await asyncio.sleep(5)  # Refresh every 5 seconds
            if self._auto_refresh:
                self.refresh_all_data()

    def stop_auto_refresh(self):
        """Stop automatic refresh"""
        self._auto_refresh = False

    def refresh_all_data(self):
        """Refresh all monitoring data from backend"""
        self.refresh_jobs()
        self.refresh_local_resources()
        self.refresh_cluster_resources()

    def refresh_jobs(self):
        """Get jobs from backend JobManagerHandler"""
        try:
            # This would call your actual JobManagerHandler endpoint
            # For now, using placeholder - replace with actual HTTP calls
            response = httpx.get(f"{self.backend_url}/jobs")
            if response.status_code == 200:
                self.jobs = response.json()
        except Exception as e:
            print(f"Error refreshing jobs: {e}")
            # Fallback to empty list
            self.jobs = []

    def refresh_local_resources(self):
        """Get local resources from backend"""
        try:
            response = httpx.get(f"{self.backend_url}/resources/local")
            if response.status_code == 200:
                self.local_resources = response.json()
        except Exception as e:
            print(f"Error refreshing local resources: {e}")
            self.local_resources = {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "total_cpus": 8,
                "total_memory": 16
            }

    def refresh_cluster_resources(self):
        """Get cluster partitions and resources"""
        try:
            response = httpx.get(f"{self.backend_url}/resources/cluster")
            if response.status_code == 200:
                self.cluster_partitions = response.json()
        except Exception as e:
            print(f"Error refreshing cluster resources: {e}")
            self.cluster_partitions = []

    def handle_file_upload(self, files: List[rx.UploadFile]):
        """Handle project file upload"""
        if files:
            self.selected_file = files[0].filename
            self.project_file = files[0].filename

    def submit_job(self):
        """Submit job to backend"""
        try:
            job_data = {
                "project_file": self.project_file,
                "num_cpus": self.num_cpus,
                "num_nodes": self.num_nodes,
                "cpus_per_node": self.cpus_per_node,
                "tasks_per_node": self.tasks_per_node,
                "queue": self.selected_queue,
                "batch_options": self.batch_options
            }

            # Submit to backend
            response = httpx.post(f"{self.backend_url}/jobs/submit", json=job_data)
            if response.status_code == 200:
                self.show_submit_dialog = False
                self.refresh_jobs()  # Refresh job list
                return rx.toast.success("Job submitted successfully!")
            else:
                return rx.toast.error("Failed to submit job")

        except Exception as e:
            return rx.toast.error(f"Error submitting job: {str(e)}")

    def cancel_job(self, job_id: str):
        """Cancel a running job"""
        try:
            response = httpx.post(f"{self.backend_url}/jobs/{job_id}/cancel")
            if response.status_code == 200:
                self.refresh_jobs()
                return rx.toast.success("Job cancelled successfully!")
        except Exception as e:
            return rx.toast.error(f"Error cancelling job: {str(e)}")


def job_card(job: Dict) -> rx.Component:
    """Individual job card component"""
    status_colors = {
        "running": "blue",
        "completed": "green",
        "failed": "red",
        "pending": "orange",
        "cancelled": "gray"
    }

    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(job.get("name", "Unnamed Job"), font_weight="bold", size="lg"),
                rx.text(f"ID: {job.get('id', 'N/A')}", size="sm", color="gray"),
                rx.text(f"Type: {job.get('type', 'local')}", size="sm", color="gray"),
                align_items="start",
                spacing="1"
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(
                    job.get("status", "unknown").upper(),
                    color_scheme=status_colors.get(job.get("status", "pending"), "gray")
                ),
                rx.text(
                    f"Progress: {job.get('progress', 0)}%",
                    size="sm"
                ),
                align_items="end",
                spacing="1"
            ),
            width="100%"
        ),
        rx.divider(margin_y="0.5em"),
        rx.hstack(
            rx.text(f"Submitted: {job.get('submit_time', 'N/A')}", size="sm"),
            rx.spacer(),
            rx.cond(
                job.get("status") == "running",
                rx.button(
                    "Cancel",
                    size="sm",
                    color_scheme="red",
                    on_click=lambda: JobManagerState.cancel_job(job.get("id"))
                ),
                None
            ),
            width="100%"
        ),
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        background="rgba(255, 255, 255, 0.8)",
        backdrop_filter="blur(10px)",
        border="1px solid rgba(255, 255, 255, 0.2)",
        width="100%"
    )


def jobs_panel() -> rx.Component:
    """Jobs listing panel"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Jobs", size="lg"),
                rx.spacer(),
                rx.button(
                    "Refresh",
                    on_click=JobManagerState.refresh_jobs
                ),
                rx.button(
                    "Submit New Job",
                    color_scheme="blue",
                    on_click=JobManagerState.show_submit_dialog.set(True)
                ),
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                JobManagerState.jobs,
                rx.vstack(
                    rx.foreach(JobManagerState.jobs, job_card),
                    spacing="3",
                    width="100%"
                ),
                rx.center(
                    rx.text("No jobs found", color="gray"),
                    padding_y="2em"
                )
            ),
            spacing="3",
            width="100%"
        ),
        box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        background="rgba(255, 255, 255, 0.9)",
        backdrop_filter="blur(10px)",
        border="1px solid rgba(255, 255, 255, 0.2)",
        width="100%"
    )


def resource_monitor() -> rx.Component:
    """Local resources monitor"""
    return rx.card(
        rx.vstack(
            rx.heading("Local Resources", size="lg"),
            rx.divider(),
            rx.hstack(
                rx.vstack(
                    rx.text("CPU Usage", font_weight="bold"),
                    rx.progress(
                        value=JobManagerState.local_resources.get("cpu_usage", 0),
                        width="100%"
                    ),
                    rx.text(f"{JobManagerState.local_resources.get('cpu_usage', 0)}%"),
                    align_items="start",
                    width="100%"
                ),
                rx.vstack(
                    rx.text("Memory Usage", font_weight="bold"),
                    rx.progress(
                        value=JobManagerState.local_resources.get("memory_usage", 0),
                        width="100%"
                    ),
                    rx.text(f"{JobManagerState.local_resources.get('memory_usage', 0)}%"),
                    align_items="start",
                    width="100%"
                ),
                spacing="4",
                width="100%"
            ),
            rx.grid(
                rx.stat(
                    rx.stat_label("Total CPUs"),
                    rx.stat_number(JobManagerState.local_resources.get("total_cpus", 0)),
                ),
                rx.stat(
                    rx.stat_label("Total Memory (GB)"),
                    rx.stat_number(JobManagerState.local_resources.get("total_memory", 0)),
                ),
                rx.stat(
                    rx.stat_label("Disk Usage"),
                    rx.stat_number(f"{JobManagerState.local_resources.get('disk_usage', 0)}%"),
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        background="rgba(255, 255, 255, 0.9)",
        backdrop_filter="blur(10px)",
        border="1px solid rgba(255, 255, 255, 0.2)",
        width="100%"
    )


def cluster_partitions_panel() -> rx.Component:
    """Cluster partitions monitor"""
    return rx.cond(
        JobManagerState.cluster_partitions,
        rx.card(
            rx.vstack(
                rx.heading("Cluster Partitions", size="lg"),
                rx.divider(),
                rx.foreach(
                    JobManagerState.cluster_partitions,
                    lambda partition: rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.text(partition.get("name", "Unknown"), font_weight="bold", size="lg"),
                                rx.badge(partition.get("state", "unknown")),
                                rx.spacer(),
                                rx.text(
                                    f"Nodes: {partition.get('nodes_available', 0)}/{partition.get('nodes_total', 0)}"),
                                width="100%"
                            ),
                            rx.progress(
                                value=partition.get("cpu_usage", 0),
                                label=f"CPU: {partition.get('cpu_usage', 0)}%"
                            ),
                            rx.progress(
                                value=partition.get("memory_usage", 0),
                                label=f"Memory: {partition.get('memory_usage', 0)}%"
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        width="100%"
                    )
                ),
                spacing="3",
                width="100%"
            ),
            box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            background="rgba(255, 255, 255, 0.9)",
            backdrop_filter="blur(10px)",
            border="1px solid rgba(255, 255, 255, 0.2)",
            width="100%"
        ),
        rx.box()  # Empty if no cluster partitions
    )


def job_submission_dialog() -> rx.Component:
    """Job submission dialog"""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header("Submit New Job"),
                rx.modal_body(
                    rx.vstack(
                        rx.upload(
                            rx.vstack(
                                rx.button(
                                    "Select Project File",
                                    color="blue",
                                    variant="outline"
                                ),
                                rx.text("Drag and drop files here or click to select files"),
                                spacing="2"
                            ),
                            border="1px dashed",
                            padding="5em",
                            on_drop=JobManagerState.handle_file_upload(rx.upload_files()),
                        ),
                        rx.cond(
                            JobManagerState.selected_file,
                            rx.text(JobManagerState.selected_file),
                            rx.text("No file selected")
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="Number of CPUs",
                                value=JobManagerState.num_cpus,
                                on_change=JobManagerState.set_num_cpus,
                                type="number"
                            ),
                            rx.input(
                                placeholder="Number of Nodes",
                                value=JobManagerState.num_nodes,
                                on_change=JobManagerState.set_num_nodes,
                                type="number"
                            ),
                            width="100%"
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="CPUs per Node",
                                value=JobManagerState.cpus_per_node,
                                on_change=JobManagerState.set_cpus_per_node,
                                type="number"
                            ),
                            rx.input(
                                placeholder="Tasks per Node",
                                value=JobManagerState.tasks_per_node,
                                on_change=JobManagerState.set_tasks_per_node,
                                type="number"
                            ),
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Queue",
                            value=JobManagerState.selected_queue,
                            on_change=JobManagerState.set_selected_queue
                        ),
                        rx.text_area(
                            placeholder="Batch Options (JSON)",
                            value=JobManagerState.batch_options,
                            on_change=JobManagerState.set_batch_options
                        ),
                        spacing="4",
                        width="100%"
                    )
                ),
                rx.modal_footer(
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=JobManagerState.show_submit_dialog.set(False)
                        ),
                        rx.button(
                            "Submit Job",
                            color_scheme="blue",
                            on_click=JobManagerState.submit_job
                        ),
                        spacing="3"
                    )
                ),
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                background="rgba(255, 255, 255, 0.95)",
                backdrop_filter="blur(16px)",
                border="1px solid rgba(255, 255, 255, 0.3)"
            )
        ),
        is_open=JobManagerState.show_submit_dialog
    )


def index() -> rx.Component:
    """Main application page"""
    return rx.box(
        rx.vstack(
            rx.heading("PyEDB Job Manager", size="2xl", margin_bottom="1em"),
            rx.grid(
                jobs_panel(),
                rx.vstack(
                    resource_monitor(),
                    cluster_partitions_panel(),
                    spacing="4"
                ),
                grid_template_columns="2fr 1fr",
                gap="6",
                width="100%"
            ),
            spacing="6",
            width="100%",
            max_width="1400px",
            padding="2em"
        ),
        job_submission_dialog(),
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        min_height="100vh",
        display="flex",
        justify_content="center",
        align_items="start"
    )


# Create app
app = rx.App(
    style={
        "font_family": "Inter, sans-serif",
    }
)
app.add_page(
    index,
    title="PyEDB Job Manager",
    on_load=JobManagerState.on_load
)
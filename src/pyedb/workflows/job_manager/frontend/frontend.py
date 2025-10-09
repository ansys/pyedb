"""
Reflex Frontend for ANSYS Job Manager
====================================

Modern, responsive UI with glass morphism design, dark theme, and real-time updates.
Integrates with the JobManager backend via REST API and WebSocket connections.
"""

from enum import Enum
import platform
from typing import Any, Dict, List

import httpx
import reflex as rx


class JobStatus(Enum):
    """Job status enumeration matching backend."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class State(rx.State):
    """Main application state with real-time job management."""

    # Connection state
    backend_url: str = "http://localhost:8080"
    connected: bool = False
    loading: bool = True

    # Job management
    jobs: List[Dict[str, Any]] = []
    selected_job_id: str = ""
    queue_stats: Dict[str, int] = {}

    # System monitoring
    system_status: Dict[str, Any] = {}
    resource_usage: Dict[str, Any] = {}
    partitions: List[Dict[str, Any]] = []

    # Job submission form
    project_path: str = ""
    job_priority: int = 0
    design_name: str = ""
    setup_name: str = ""
    num_cores: int = 1
    memory_limit: str = "4GB"
    scheduler_type: str = "none"
    hfss_batch_options: Dict[str, Any] = {
        "create_starting_mesh": False,
        "default_process_priority": "Normal",
        "enable_gpu": False,
        "mpi_vendor": "Intel" if platform.system() != "Linux" else "OpenMPI",
        "solve_adaptive_only": False,
    }

    # Settings
    max_concurrent_jobs: int = 2
    max_cpu_percent: float = 75.0
    min_memory_gb: float = 4.0
    min_disk_gb: float = 20.0

    # UI state
    show_job_details: bool = False
    show_settings: bool = False
    show_new_job_modal: bool = False
    notification_message: str = ""
    notification_type: str = "info"  # info, success, warning, error

    # Scheduler options
    node_number: int = 1
    cores_per_node: int = 1
    tasks_per_node: int = 1
    partition_name: str = ""

    # Add these setter methods here (they are NOT async)
    def set_max_concurrent_jobs(self, value: str):
        """Set max concurrent jobs from string input."""
        try:
            self.max_concurrent_jobs = int(value) if value else 1
        except ValueError:
            self.max_concurrent_jobs = 1

    def set_min_memory_gb(self, value: str):
        """Set min memory GB from string input."""
        try:
            self.min_memory_gb = float(value) if value else 1.0
        except ValueError:
            self.min_memory_gb = 1.0

    def set_min_disk_gb(self, value: str):
        """Set min disk GB from string input."""
        try:
            self.min_disk_gb = float(value) if value else 1.0
        except ValueError:
            self.min_disk_gb = 1.0

    def set_num_cores(self, value: str):
        """Set number of cores from string input."""
        try:
            self.num_cores = int(value) if value else 1
        except ValueError:
            self.num_cores = 1

    def set_max_cpu_percent(self, value: list[float]):
        """Set max CPU percent from slider."""
        if value and len(value) > 0:
            self.max_cpu_percent = float(value[0])

    def set_job_priority(self, value: str):
        """Set job priority from input."""
        try:
            self.job_priority = int(value)
        except (ValueError, TypeError):
            self.job_priority = 0

    def set_project_path(self, value: str):
        """Set project path from input."""
        self.project_path = value

    def set_design_name(self, value: str):
        """Set design name from input."""
        self.design_name = value

    def set_setup_name(self, value: str):
        """Set setup name from input."""
        self.setup_name = value

    def set_notification_message(self, value: str):
        """Set notification message."""
        self.notification_message = value

    def set_show_settings(self, value: bool):
        """Toggle settings modal."""
        self.show_settings = value

    def set_show_new_job_modal(self, value: bool):
        """Toggle new job modal."""
        self.show_new_job_modal = value

    def set_node_number(self, value: str):
        """Set node number from string input."""
        try:
            self.node_number = int(value) if value else 1
        except ValueError:
            self.node_number = 1

    def set_cores_per_node(self, value: str):
        """Set cores per node from string input."""
        try:
            self.cores_per_node = int(value) if value else 1
        except ValueError:
            self.cores_per_node = 1

    def set_tasks_per_node(self, value: str):
        """Set tasks per node from string input."""
        try:
            self.tasks_per_node = int(value) if value else 1
        except ValueError:
            self.tasks_per_node = 1

    def set_partition_name(self, value: str):
        """Set partition name from input."""
        self.partition_name = value

    def browse_project_file(self):
        """Trigger file browser (legacy method - now using rx.upload)."""
        self.notification_message = "Please use the Browse button to select a file"
        self.notification_type = "info"

    async def handle_file_upload(self, files: list[rx.UploadFile]):
        """Handle file uploads."""
        if files:
            upload_data = await files[0].read()
            outfile = f"uploaded_files/{files[0].filename}"
            with open(outfile, "wb") as f:
                f.write(upload_data)
            self.project_path = outfile
            self.notification_message = f"File {files[0].filename} uploaded."
            self.notification_type = "success"

    async def connect_to_backend(self):
        """Initialize connection to backend API and WebSocket."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/system/status")
                if response.status_code == 200:
                    self.system_status = response.json()
                    self.connected = True
                    await self.load_initial_data()
                else:
                    self.connected = False
        except Exception as e:
            self.connected = False
            self.notification_message = f"Failed to connect to backend: {str(e)}"
            self.notification_type = "error"
        finally:
            self.loading = False

    async def load_initial_data(self):
        """Load jobs, queue stats, and system status."""
        try:
            async with httpx.AsyncClient() as client:
                # Load jobs
                jobs_response = await client.get(f"{self.backend_url}/jobs")
                if jobs_response.status_code == 200:
                    self.jobs = jobs_response.json()

                # Load queue stats
                queue_response = await client.get(f"{self.backend_url}/queue")
                if queue_response.status_code == 200:
                    self.queue_stats = queue_response.json()

                # Load partitions
                partitions_response = await client.get(f"{self.backend_url}/scheduler/partitions")
                if partitions_response.status_code == 200:
                    self.partitions = partitions_response.json()

                # Load resource usage
                resource_response = await client.get(f"{self.backend_url}/resources")
                if resource_response.status_code == 200:
                    self.resource_usage = resource_response.json()

        except Exception as e:
            self.notification_message = f"Failed to load data: {str(e)}"
            self.notification_type = "error"

    async def submit_job(self):
        """Submit a new job to the backend."""
        if not self.project_path:
            self.notification_message = "Project path is required"
            self.notification_type = "warning"
            return

        job_data = {
            "project_path": self.project_path,
            "priority": self.job_priority,
            "design_name": self.design_name,
            "setup_name": self.setup_name,
            "num_cores": self.num_cores,
            "memory_limit_gb": int(self.memory_limit.replace("GB", "")),
            "scheduler_type": self.scheduler_type,
            "hfss_batch_options": self.hfss_batch_options,
        }
        if self.scheduler_type != "none":
            job_data.update(
                {
                    "node_number": self.node_number,
                    "cores_per_node": self.cores_per_node,
                    "tasks_per_node": self.tasks_per_node,
                    "partition_name": self.partition_name,
                }
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.backend_url}/jobs/submit", json=job_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.notification_message = f"Job {result['job_id']} submitted successfully"
                        self.notification_type = "success"
                        await self.load_initial_data()
                        # Clear form and close modal
                        self.project_path = ""
                        self.design_name = ""
                        self.setup_name = ""
                        self.show_new_job_modal = False
                    else:
                        self.notification_message = f"Job submission failed: {result.get('error')}"
                        self.notification_type = "error"
        except Exception as e:
            self.notification_message = f"Failed to submit job: {str(e)}"
            self.notification_type = "error"

    async def cancel_job(self, job_id: str):
        """Cancel a running or queued job."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.backend_url}/jobs/{job_id}/cancel")
                if response.status_code == 200:
                    self.notification_message = f"Job {job_id} cancelled"
                    self.notification_type = "success"
                    await self.load_initial_data()
        except Exception as e:
            self.notification_message = f"Failed to cancel job: {str(e)}"
            self.notification_type = "error"

    async def update_concurrent_limits(self):
        """Update concurrent job limits."""
        limits_data = {
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "max_cpu_percent": self.max_cpu_percent,
            "min_memory_gb": self.min_memory_gb,
            "min_disk_gb": self.min_disk_gb,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(f"{self.backend_url}/pool/limits", json=limits_data)
                if response.status_code == 200:
                    self.notification_message = "Resource limits updated successfully"
                    self.notification_type = "success"
                    self.show_settings = False
        except Exception as e:
            self.notification_message = f"Failed to update limits: {str(e)}"
            self.notification_type = "error"

    def toggle_job_details(self, job_id: str):
        """Toggle job details panel."""
        if self.selected_job_id == job_id:
            self.show_job_details = False
            self.selected_job_id = ""
        else:
            self.selected_job_id = job_id
            self.show_job_details = True

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle uploaded files."""
        if files:
            file = files[0]
            self.project_path = file.filename
            self.notification_message = f"File selected: {file.filename}"
            self.notification_type = "success"
        else:
            self.notification_message = "No file selected"
            self.notification_type = "warning"

    def set_hfss_batch_option(self, key: str, value: bool):
        """Set a single HFSS batch option."""
        self.hfss_batch_options[key] = value


# Design tokens and theme configuration
DESIGN_TOKENS = {
    "colors": {
        "background": "#0a0a0a",
        "background_secondary": "#111111",
        "surface": "#1a1a1a",
        "surface_secondary": "#222222",
        "primary": "#3b82f6",
        "primary_dark": "#2563eb",
        "secondary": "#64748b",
        "accent": "#06b6d4",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "text_primary": "#ffffff",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "border": "#334155",
        "border_secondary": "#475569",
    },
    "elevations": {
        "elev1": "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.24)",
        "elev2": "0 3px 6px rgba(0,0,0,0.32), 0 3px 6px rgba(0,0,0,0.28)",
        "elev3": "0 10px 20px rgba(0,0,0,0.38), 0 6px 6px rgba(0,0,0,0.32)",
        "elev4": "0 14px 28px rgba(0,0,0,0.42), 0 10px 10px rgba(0,0,0,0.36)",
    },
    "glass": {
        "background": "rgba(255, 255, 255, 0.05)",
        "backdrop_filter": "blur(20px)",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
    },
}

# Global styles
GLASS_STYLE = {
    "background": DESIGN_TOKENS["glass"]["background"],
    "backdrop_filter": DESIGN_TOKENS["glass"]["backdrop_filter"],
    "border": DESIGN_TOKENS["glass"]["border"],
    "border_radius": "16px",
    "box_shadow": DESIGN_TOKENS["elevations"]["elev2"],
}

CARD_STYLE = {
    **GLASS_STYLE,
    "padding": "24px",
    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": DESIGN_TOKENS["elevations"]["elev3"],
    },
}

BUTTON_STYLE = {
    "border_radius": "12px",
    "padding": "12px 24px",
    "font_weight": "600",
    "transition": "all 0.2s ease",
    "border": "none",
    "cursor": "pointer",
    "_hover": {
        "transform": "translateY(-1px)",
    },
}

PRIMARY_BUTTON_STYLE = {
    **BUTTON_STYLE,
    "background": DESIGN_TOKENS["colors"]["primary"],
    "color": "white",
    "_hover": {
        **BUTTON_STYLE["_hover"],
        "background": DESIGN_TOKENS["colors"]["primary_dark"],
    },
}


def status_badge(status: str) -> rx.Component:
    """Status badge with color coding."""
    return rx.badge(
        rx.cond(
            status == "queued",
            "QUEUED",
            rx.cond(
                status == "running",
                "RUNNING",
                rx.cond(
                    status == "completed",
                    "COMPLETED",
                    rx.cond(
                        status == "failed",
                        "FAILED",
                        rx.cond(
                            status == "cancelled", "CANCELLED", rx.cond(status == "scheduled", "SCHEDULED", "UNKNOWN")
                        ),
                    ),
                ),
            ),
        ),
        style={
            "background": rx.cond(
                status == "queued",
                DESIGN_TOKENS["colors"]["secondary"],
                rx.cond(
                    status == "running",
                    DESIGN_TOKENS["colors"]["primary"],
                    rx.cond(
                        status == "completed",
                        DESIGN_TOKENS["colors"]["success"],
                        rx.cond(
                            status == "failed",
                            DESIGN_TOKENS["colors"]["error"],
                            rx.cond(
                                status == "cancelled",
                                DESIGN_TOKENS["colors"]["warning"],
                                rx.cond(
                                    status == "scheduled",
                                    DESIGN_TOKENS["colors"]["accent"],
                                    DESIGN_TOKENS["colors"]["secondary"],
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            "color": "white",
            "padding": "4px 12px",
            "border_radius": "20px",
            "font_size": "12px",
            "font_weight": "600",
        },
    )


def shimmer_skeleton() -> rx.Component:
    """Animated shimmer skeleton loader."""
    return rx.skeleton(
        height="20px",
        width="100%",
        style={
            "background": "linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, "
            "rgba(255,255,255,0.1) 75%)",
            "background_size": "200% 100%",
            "animation": "shimmer 1.5s infinite",
            "border_radius": "4px",
        },
    )


def job_card(job: Dict[str, Any]) -> rx.Component:
    """Individual job card with glass morphism design."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        job.get("jobid", "Unknown"),
                        font_weight="700",
                        font_size="18px",
                        color=DESIGN_TOKENS["colors"]["text_primary"],
                    ),
                    status_badge(job.get("status", "unknown")),
                    justify_content="space_between",
                    width="100%",
                ),
                rx.text(
                    f"Priority: {job.get('priority', 0)}",
                    font_size="14px",
                    color=DESIGN_TOKENS["colors"]["text_secondary"],
                ),
                rx.text(
                    f"Created: {job.get('created_at', 'Unknown')}",
                    font_size="12px",
                    color=DESIGN_TOKENS["colors"]["text_muted"],
                ),
                align_items="start",
                spacing="2",
                flex="1",
            ),
            rx.vstack(
                rx.button(
                    rx.icon("eye"),
                    on_click=State.toggle_job_details(job.get("jobid", "")),
                    variant="ghost",
                    size="2",
                ),
                rx.cond(
                    (job.get("status") == "queued") | (job.get("status") == "running"),
                    rx.button(
                        rx.icon("x"),
                        on_click=State.cancel_job(job.get("jobid", "")),
                        variant="ghost",
                        size="2",
                        color_scheme="red",
                    ),
                ),
                spacing="2",
            ),
            justify_content="space-between",  # Changed from "space-between"
            align_items="start",
            width="100%",
        ),
        style=CARD_STYLE,
        on_click=State.toggle_job_details(job.get("jobid", "")),
    )


def active_jobs_grid(**props) -> rx.Component:
    """A grid to display active jobs."""
    return rx.box(
        rx.vstack(
            rx.text("Active Jobs", font_size="24px", font_weight="700", color=DESIGN_TOKENS["colors"]["text_primary"]),
            rx.cond(
                State.jobs,
                rx.foreach(
                    State.jobs,
                    job_card,
                ),
                rx.box(
                    rx.text("No active jobs.", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                    padding="20px",
                    width="100%",
                    align="center",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        style=CARD_STYLE,
        **props,
    )


def job_list_table(**props) -> rx.Component:
    """A table to display all jobs."""
    return rx.box(
        rx.vstack(
            rx.text("Job Queue", font_size="24px", font_weight="700", color=DESIGN_TOKENS["colors"]["text_primary"]),
            rx.data_table(
                data=State.jobs,
                columns=[
                    {"title": "Job ID", "key": "jobid"},
                    {"title": "Status", "key": "status"},
                    {"title": "Priority", "key": "priority"},
                    {"title": "Submitted", "key": "created_at"},
                    {"title": "Partitions", "key": "partitions"},
                ],
                style={"width": "100%"},
            ),
            spacing="4",
            width="100%",
        ),
        style=CARD_STYLE,
        **props,
    )


def job_details_panel(**props) -> rx.Component:
    """Expandable job details panel."""
    return rx.cond(
        State.show_job_details & (State.selected_job_id != ""),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "Job Details",
                        font_size="24px",
                        font_weight="700",
                        color=DESIGN_TOKENS["colors"]["text_primary"],
                    ),
                    rx.button(
                        rx.icon("x"),
                        on_click=State.toggle_job_details(""),
                        variant="ghost",
                        size="2",
                    ),
                    justify_content="space-between",
                    width="100%",
                ),
                rx.divider(color=DESIGN_TOKENS["colors"]["border"]),
                rx.grid(
                    rx.box(
                        rx.text("Job ID:", font_weight="600", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.text(State.selected_job_id, color=DESIGN_TOKENS["colors"]["text_primary"]),
                    ),
                    rx.box(
                        rx.text("Status:", font_weight="600", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                status_badge(job["status"]),
                            ),
                        ),
                    ),
                    rx.box(
                        rx.text("Priority:", font_weight="600", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                rx.text(str(job["priority"]), color=DESIGN_TOKENS["colors"]["text_primary"]),
                            ),
                        ),
                    ),
                    rx.box(
                        rx.text("Project:", font_weight="600", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                rx.text(job["project_path"], color=DESIGN_TOKENS["colors"]["text_primary"]),
                            ),
                        ),
                    ),
                    columns="2",
                    spacing="4",
                ),
                rx.foreach(
                    State.jobs,
                    lambda job: rx.cond(
                        (job["jobid"] == State.selected_job_id) & (job.get("error", "") != ""),
                        rx.box(
                            rx.text("Error:", font_weight="600", color=DESIGN_TOKENS["colors"]["error"]),
                            rx.text(job["error"], color=DESIGN_TOKENS["colors"]["text_primary"]),
                            style={
                                "background": "rgba(239, 68, 68, 0.1)",
                                "border": "1px solid rgba(239, 68, 68, 0.3)",
                                "border_radius": "8px",
                                "padding": "12px",
                            },
                        ),
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            style=CARD_STYLE,
            **props,
        ),
    )


def job_submission_form() -> rx.Component:
    """Job submission form modal."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Submit New Job"),
            rx.form(
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Project Path (.aedt/.aedb)",
                            font_size="14px",
                            color=DESIGN_TOKENS["colors"]["text_secondary"],
                        ),
                        rx.hstack(
                            rx.upload(
                                rx.button("Browse", variant="soft", size="2"),
                                id="upload_project",
                                on_drop=State.handle_file_upload,
                            ),
                            rx.input(
                                value=State.project_path,
                                on_change=State.set_project_path,
                                placeholder="or enter path here",
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["text_primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                },
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "Design Name (optional)",
                                font_size="14px",
                                color=DESIGN_TOKENS["colors"]["text_secondary"],
                            ),
                            rx.input(
                                placeholder="Enter design name...",
                                value=State.design_name,
                                on_change=State.set_design_name,
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["text_primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "_placeholder": {
                                        "color": DESIGN_TOKENS["colors"]["text_muted"],
                                    },
                                },
                            ),
                            spacing="2",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text(
                                "Setup Name (optional)",
                                font_size="14px",
                                color=DESIGN_TOKENS["colors"]["text_secondary"],
                            ),
                            rx.input(
                                placeholder="Enter setup name...",
                                value=State.setup_name,
                                on_change=State.set_setup_name,
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["text_primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "_placeholder": {
                                        "color": DESIGN_TOKENS["colors"]["text_muted"],
                                    },
                                },
                            ),
                            spacing="2",
                            flex="1",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Priority", font_size="14px", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                            rx.input(
                                type="number",
                                value=State.job_priority,
                                on_change=State.set_job_priority,
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["text_primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "width": "80px",
                                    "text_align": "center",
                                },
                            ),
                            spacing="2",
                        ),
                        rx.vstack(
                            rx.text("Cores", font_size="14px", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                            rx.input(
                                type="number",
                                value=State.num_cores,
                                on_change=State.set_num_cores,
                                min="1",
                                max="64",
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["text_primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "width": "80px",
                                    "text_align": "center",
                                },
                            ),
                            spacing="2",
                        ),
                        spacing="4",
                        width="100%",
                        align_items="end",
                    ),
                    rx.cond(
                        State.scheduler_type != "none",
                        rx.vstack(
                            rx.text("Scheduler Options", font_size="16px", font_weight="600"),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Nodes", font_size="14px"),
                                    rx.input(
                                        type="number",
                                        value=State.node_number,
                                        on_change=State.set_node_number,
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Cores/Node", font_size="14px"),
                                    rx.input(
                                        type="number",
                                        value=State.cores_per_node,
                                        on_change=State.set_cores_per_node,
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Tasks/Node", font_size="14px"),
                                    rx.input(
                                        type="number",
                                        value=State.tasks_per_node,
                                        on_change=State.set_tasks_per_node,
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Partition", font_size="14px"),
                                    rx.input(
                                        value=State.partition_name,
                                        on_change=State.set_partition_name,
                                    ),
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                    ),
                    rx.text("HFSS Batch Options", font_size="16px", font_weight="600"),
                    rx.hstack(
                        rx.checkbox(
                            "Create Starting Mesh",
                            is_checked=State.hfss_batch_options.get("create_starting_mesh", False),
                            on_change=lambda val: State.set_hfss_batch_option("create_starting_mesh", val),
                        ),
                        rx.checkbox(
                            "Enable GPU",
                            is_checked=State.hfss_batch_options.get("enable_gpu", False),
                            on_change=lambda val: State.set_hfss_batch_option("enable_gpu", val),
                        ),
                        rx.checkbox(
                            "Solve Adaptive Only",
                            is_checked=State.hfss_batch_options.get("solve_adaptive_only", False),
                            on_change=lambda val: State.set_hfss_batch_option("solve_adaptive_only", val),
                        ),
                        spacing="4",
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                on_click=State.set_show_new_job_modal(False),
                                variant="soft",
                                color_scheme="gray",
                            )
                        ),
                        rx.button(
                            "Submit Job",
                            on_click=State.submit_job,
                            style=PRIMARY_BUTTON_STYLE,
                            loading=State.loading,
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
            ),
            style={
                "background": DESIGN_TOKENS["colors"]["surface"],
                "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                "border_radius": "16px",
                "padding": "24px",
                "min_width": "600px",
            },
        ),
        open=State.show_new_job_modal,
    )


def local_resource_monitor(**props) -> rx.Component:
    """Local resource monitor."""
    return rx.box(
        rx.vstack(
            rx.text("Local Resource Monitor", font_size="20px", font_weight="700"),
            rx.cond(
                State.loading,
                shimmer_skeleton(),
                rx.cond(
                    State.resource_usage,
                    rx.hstack(
                        rx.vstack(
                            rx.text("CPU"),
                            rx.progress(value=State.resource_usage.get("cpu_percent", 0)),
                            rx.text(State.resource_usage.get("cpu_percent", 0), "%"),
                            align_items="center",
                        ),
                        rx.vstack(
                            rx.text("RAM"),
                            rx.progress(value=State.resource_usage.get("memory_percent", 0)),
                            rx.text(
                                State.resource_usage.get("memory_used_gb", 0),
                                "GB / ",
                                State.resource_usage.get("memory_total_gb", 0),
                                "GB",
                            ),
                            align_items="center",
                        ),
                        rx.vstack(
                            rx.text("Disk"),
                            rx.progress(value=State.resource_usage.get("disk_usage_percent", 0)),
                            rx.text(State.resource_usage.get("disk_free_gb", 0), "GB Free"),
                            align_items="center",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.text("No resource data available.", color="gray"),
                ),
            ),
            spacing="4",
            width="100%",
        ),
        style=CARD_STYLE,
        **props,
    )


def cluster_partitions(**props) -> rx.Component:
    """Cluster partitions monitor."""

    def render_partition(p: rx.Var) -> rx.Component:
        """Render a single partition."""
        cores_total_var = p["cores_total"]
        cores_used_var = p["cores_used"]
        mem_total_var = p["memory_total_gb"]
        mem_used_var = p["memory_used_gb"]

        return rx.vstack(
            rx.text(p["name"], font_weight="600"),
            rx.hstack(
                rx.text("Cores:"),
                rx.text(cores_used_var, "/", cores_total_var),
            ),
            rx.hstack(
                rx.text("Memory:"),
                rx.text(mem_used_var, " / ", mem_total_var, " GB"),
            ),
            spacing="2",
        )

    return rx.box(
        rx.vstack(
            rx.text("Cluster Partitions", font_size="20px", font_weight="700"),
            rx.cond(
                State.partitions,
                rx.foreach(
                    State.partitions,
                    render_partition,
                ),
                rx.text("No partition data available", color="gray"),
            ),
            spacing="4",
            width="100%",
        ),
        style=CARD_STYLE,
        **props,
    )


def system_status_card(**props) -> rx.Component:
    """System status overview card."""
    return rx.box(
        rx.vstack(
            rx.text(
                "System Status",
                font_size="20px",
                font_weight="700",
                color=DESIGN_TOKENS["colors"]["text_primary"],
            ),
            rx.cond(
                State.loading,
                rx.vstack(
                    shimmer_skeleton(),
                    shimmer_skeleton(),
                    shimmer_skeleton(),
                    spacing="2",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="12px",
                            height="12px",
                            border_radius="50%",
                            background=rx.cond(
                                State.connected,
                                DESIGN_TOKENS["colors"]["success"],
                                DESIGN_TOKENS["colors"]["error"],
                            ),
                        ),
                        rx.text(
                            rx.cond(
                                State.connected,
                                "Connected",
                                "Disconnected",
                            ),
                            color=DESIGN_TOKENS["colors"]["text_primary"],
                        ),
                        spacing="2",
                    ),
                    rx.text(
                        f"Running Jobs: {State.queue_stats.get('running_jobs', 0)} / "
                        f"{State.queue_stats.get('max_concurrent', 0)}",
                        color=DESIGN_TOKENS["colors"]["text_secondary"],
                    ),
                    rx.text(
                        f"Queued Jobs: {State.queue_stats.get('total_queued', 0)}",
                        color=DESIGN_TOKENS["colors"]["text_secondary"],
                    ),
                    spacing="2",
                ),
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        style=CARD_STYLE,
        **props,
    )


def settings_modal() -> rx.Component:
    """Settings modal for resource limits."""
    return rx.cond(
        State.show_settings,
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    "Resource Limits",
                    color=DESIGN_TOKENS["colors"]["text_primary"],
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Max Concurrent Jobs",
                            font_size="14px",
                            color=DESIGN_TOKENS["colors"]["text_secondary"],
                        ),
                        rx.input(
                            type="number",
                            value=State.max_concurrent_jobs,
                            on_change=State.set_max_concurrent_jobs,
                            min="1",
                            max="20",
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["text_primary"],
                                "padding": "8px 12px",
                                "font_size": "14px",
                                "height": "40px",
                                "width": "100px",
                                "text_align": "center",
                            },
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Max CPU %", font_size="14px", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.slider(
                            default_value=[75],
                            value=[State.max_cpu_percent],
                            on_change=State.set_max_cpu_percent,
                            min_=10,
                            max_=100,
                            step=5,
                            width="100%",
                            style={
                                "height": "20px",
                            },
                        ),
                        rx.text(
                            f"Value: {State.max_cpu_percent}%",
                            font_size="12px",
                            color=DESIGN_TOKENS["colors"]["text_muted"],
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Min Memory (GB)", font_size="14px", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                        rx.input(
                            type="number",
                            value=State.min_memory_gb,
                            on_change=State.set_min_memory_gb,
                            min="1",
                            max="128",
                            step="0.5",
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["text_primary"],
                                "padding": "8px 12px",
                                "font_size": "14px",
                                "height": "40px",
                                "width": "100px",
                                "text_align": "center",
                            },
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text(
                            "Min Disk Space (GB)",
                            font_size="14px",
                            color=DESIGN_TOKENS["colors"]["text_secondary"],
                        ),
                        rx.input(
                            type="number",
                            value=State.min_disk_gb,
                            on_change=State.set_min_disk_gb,
                            min="1",
                            max="1000",
                            step="1",
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["text_primary"],
                                "padding": "8px 12px",
                                "font_size": "14px",
                                "height": "40px",
                                "width": "100px",
                                "text_align": "center",
                            },
                        ),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=State.set_show_settings(False),
                            variant="ghost",
                            size="3",
                        ),
                        rx.button(
                            "Save Changes",
                            on_click=State.update_concurrent_limits,
                            style=PRIMARY_BUTTON_STYLE,
                            size="3",
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    spacing="6",
                    width="100%",
                ),
                style={
                    "background": DESIGN_TOKENS["colors"]["surface"],
                    "border": f"1px solid {DESIGN_TOKENS['colors']['border']}",
                    "border_radius": "16px",
                    "padding": "24px",
                    "min_width": "500px",
                    "max_width": "600px",
                },
            ),
            open=True,
        ),
    )


def notification_toast() -> rx.Component:
    """Notification toast system."""
    color_map = {
        "info": DESIGN_TOKENS["colors"]["primary"],
        "success": DESIGN_TOKENS["colors"]["success"],
        "warning": DESIGN_TOKENS["colors"]["warning"],
        "error": DESIGN_TOKENS["colors"]["error"],
    }

    return rx.cond(
        State.notification_message != "",
        rx.box(
            rx.hstack(
                rx.cond(
                    State.notification_type == "success",
                    rx.icon("check-circle", color=color_map["success"]),
                    rx.cond(
                        State.notification_type == "warning",
                        rx.icon("alert-triangle", color=color_map["warning"]),
                        rx.cond(
                            State.notification_type == "error",
                            rx.icon("x-circle", color=color_map["error"]),
                            rx.icon("info", color=color_map["info"]),
                        ),
                    ),
                ),
                rx.text(
                    State.notification_message,
                    color=DESIGN_TOKENS["colors"]["text_primary"],
                    font_weight="500",
                ),
                rx.button(
                    rx.icon("x"),
                    on_click=State.set_notification_message(""),
                    variant="ghost",
                    size="1",
                ),
                justify_content="space-between",
                align_items="center",
                width="100%",
            ),
            style={
                **GLASS_STYLE,
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "z_index": "1000",
                "max_width": "400px",
                "padding": "16px",
                "border_left": f"4px solid {color_map.get('success', DESIGN_TOKENS['colors']['primary'])}",
            },
        ),
    )


def header() -> rx.Component:
    """Application header with navigation."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("zap", size=32, color=DESIGN_TOKENS["colors"]["primary"]),
                rx.text(
                    "ANSYS Job Manager",
                    font_size="24px",
                    font_weight="700",
                    color=DESIGN_TOKENS["colors"]["text_primary"],
                ),
                spacing="3",
                align_items="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.text(
                    f"Scheduler: {State.system_status.get('mode', 'local')}",
                    color=DESIGN_TOKENS["colors"]["text_secondary"],
                ),
                rx.button(
                    rx.icon("settings"),
                    on_click=State.set_show_settings(True),
                    variant="ghost",
                    size="3",
                ),
                spacing="4",
                align_items="center",
            ),
        ),
        style={
            **GLASS_STYLE,
            "padding": "16px 32px",
            "position": "sticky",
            "top": "0",
            "z_index": "100",
        },
    )


def index() -> rx.Component:
    """Main dashboard page with responsive 3x2 grid (stacks on small screens)."""
    return rx.box(
        rx.vstack(
            # Header (unchanged structure / slight text change)
            rx.hstack(
                rx.hstack(
                    rx.image(src="/ansys-logo.png", height="40px"),
                    rx.heading("Ansys Job Manager", size="8", color=DESIGN_TOKENS["colors"]["text_primary"]),
                    spacing="4",
                    align_items="center",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.text("Scheduler:", color=DESIGN_TOKENS["colors"]["text_secondary"]),
                    rx.badge(
                        State.scheduler_type,
                        color_scheme="blue",
                        variant="soft",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("settings"),
                        on_click=State.set_show_settings(True),
                        variant="ghost",
                        size="2",
                    ),
                    spacing="4",
                    align_items="center",
                ),
                width="100%",
                padding="16px 0",
                border_bottom=f"1px solid {DESIGN_TOKENS['colors']['border']}",
                align_items="center",
            ),
            # Responsive 3-column layout using hstack and vstack
            rx.hstack(
                # Left Column
                rx.vstack(
                    system_status_card(),
                    active_jobs_grid(),
                    spacing="6",
                    width="20%",
                    align_items="stretch",
                ),
                # Middle Column
                rx.vstack(
                    rx.hstack(
                        rx.heading("Job Queue", size="8"),
                        rx.spacer(),
                        rx.button(
                            "Create New Job",
                            on_click=State.set_show_new_job_modal(True),
                            style=PRIMARY_BUTTON_STYLE,
                            size="3",
                        ),
                        width="100%",
                        align_items="center",
                    ),
                    job_list_table(),
                    spacing="6",
                    width="60%",
                    align_items="stretch",
                ),
                # Right Column
                rx.vstack(
                    local_resource_monitor(),
                    cluster_partitions(),
                    spacing="6",
                    width="20%",
                    align_items="stretch",
                ),
                spacing="6",
                width="100%",
                align_items="start",  # Align columns to the top
            ),
            # Job details panel appears full-width below grid when toggled.
            job_details_panel(width="100%"),
            settings_modal(),
            job_submission_form(),
            notification_toast(),
            spacing="6",
            width="100%",
            padding="0 24px",
        ),
        on_mount=State.connect_to_backend,
        style={
            "background": DESIGN_TOKENS["colors"]["background"],
            "color": DESIGN_TOKENS["colors"]["text_primary"],
            "font_family": "'Inter', sans-serif",
            "width": "100%",
        },
    )


# App configuration
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        gray_color="slate",
        panel_background="solid",
        radius="large",
    ),
    style={
        "font_family": "'Inter', sans-serif",
        "background": DESIGN_TOKENS["colors"]["background"],
    },
)
app.add_page(index, title="Ansys Job Manager")

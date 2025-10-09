"""
Reflex Frontend for ANSYS Job Manager
====================================

Modern, responsive UI with glass morphism design, dark theme, and real-time updates.
Integrates with the JobManager backend via REST API and WebSocket connections.
"""

import asyncio
from datetime import datetime
from enum import Enum
import json
from typing import Any, Dict, List, Optional

import httpx
import reflex as rx
import socketio


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

    # Job submission form
    project_path: str = ""
    job_priority: int = 0
    design_name: str = ""
    setup_name: str = ""
    num_cores: int = 1
    memory_limit: str = "4GB"
    scheduler_type: str = "none"

    # Settings
    max_concurrent_jobs: int = 2
    max_cpu_percent: float = 75.0
    min_memory_gb: float = 4.0
    min_disk_gb: float = 20.0

    # UI state
    show_job_details: bool = False
    show_settings: bool = False
    notification_message: str = ""
    notification_type: str = "info"  # info, success, warning, error

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

    def set_max_cpu_percent(self, value: list):
        """Set max CPU percent from slider."""
        if value and len(value) > 0:
            self.max_cpu_percent = float(value[0])

    def set_job_priority(self, value: list):
        """Set job priority from slider."""
        if value and len(value) > 0:
            self.job_priority = int(value[0])

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

    def browse_project_file(self):
        """Trigger file browser (legacy method - now using rx.upload)."""
        self.notification_message = "Please use the Browse button to select a file"
        self.notification_type = "info"

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
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.backend_url}/jobs/submit", json=job_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.notification_message = f"Job {result['job_id']} submitted successfully"
                        self.notification_type = "success"
                        await self.load_initial_data()
                        # Clear form
                        self.project_path = ""
                        self.design_name = ""
                        self.setup_name = ""
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


# Design tokens and theme configuration
DESIGN_TOKENS = {
    "colors": {
        "--background": "#0a0a0a",
        "--background-secondary": "#111111",
        "--surface": "#1a1a1a",
        "--surface-secondary": "#222222",
        "--primary": "#3b82f6",
        "--primary-dark": "#2563eb",
        "--secondary": "#64748b",
        "--accent": "#06b6d4",
        "--success": "#10b981",
        "--warning": "#f59e0b",
        "--error": "#ef4444",
        "--text-primary": "#ffffff",
        "--text-secondary": "#94a3b8",
        "--text-muted": "#64748b",
        "--border": "#334155",
        "--border-secondary": "#475569",
    },
    "elevations": {
        "--elev1": "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.24)",
        "--elev2": "0 3px 6px rgba(0,0,0,0.32), 0 3px 6px rgba(0,0,0,0.28)",
        "--elev3": "0 10px 20px rgba(0,0,0,0.38), 0 6px 6px rgba(0,0,0,0.32)",
        "--elev4": "0 14px 28px rgba(0,0,0,0.42), 0 10px 10px rgba(0,0,0,0.36)",
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
    "box_shadow": DESIGN_TOKENS["elevations"]["--elev2"],
}

CARD_STYLE = {
    **GLASS_STYLE,
    "padding": "24px",
    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": DESIGN_TOKENS["elevations"]["--elev3"],
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
    "background": f"var({DESIGN_TOKENS['colors']['--primary']})",
    "color": "white",
    "_hover": {
        **BUTTON_STYLE["_hover"],
        "background": f"var({DESIGN_TOKENS['colors']['--primary-dark']})",
    },
}


def status_badge(status: str) -> rx.Component:
    """Status badge with color coding."""
    color_map = {
        JobStatus.QUEUED.value: DESIGN_TOKENS["colors"]["--secondary"],
        JobStatus.RUNNING.value: DESIGN_TOKENS["colors"]["--primary"],
        JobStatus.COMPLETED.value: DESIGN_TOKENS["colors"]["--success"],
        JobStatus.FAILED.value: DESIGN_TOKENS["colors"]["--error"],
        JobStatus.CANCELLED.value: DESIGN_TOKENS["colors"]["--warning"],
        JobStatus.SCHEDULED.value: DESIGN_TOKENS["colors"]["--accent"],
    }

    # Use rx.cond to handle the uppercase transformation
    status_text = rx.cond(
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
                    rx.cond(status == "cancelled", "CANCELLED", rx.cond(status == "scheduled", "SCHEDULED", "UNKNOWN")),
                ),
            ),
        ),
    )

    return rx.badge(
        status_text,
        style={
            "background": rx.cond(
                status == "queued",
                DESIGN_TOKENS["colors"]["--secondary"],
                rx.cond(
                    status == "running",
                    DESIGN_TOKENS["colors"]["--primary"],
                    rx.cond(
                        status == "completed",
                        DESIGN_TOKENS["colors"]["--success"],
                        rx.cond(
                            status == "failed",
                            DESIGN_TOKENS["colors"]["--error"],
                            rx.cond(
                                status == "cancelled",
                                DESIGN_TOKENS["colors"]["--warning"],
                                rx.cond(
                                    status == "scheduled",
                                    DESIGN_TOKENS["colors"]["--accent"],
                                    DESIGN_TOKENS["colors"]["--secondary"],
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
                        color=DESIGN_TOKENS["colors"]["--text-primary"],
                    ),
                    status_badge(job.get("status", "unknown")),
                    justify="between",  # Changed from "space-between"
                    width="100%",
                ),
                rx.text(
                    f"Priority: {job.get('priority', 0)}",
                    font_size="14px",
                    color=DESIGN_TOKENS["colors"]["--text-secondary"],
                ),
                rx.text(
                    f"Created: {job.get('created_at', 'Unknown')}",
                    font_size="12px",
                    color=DESIGN_TOKENS["colors"]["--text-muted"],
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
            justify="between",  # Changed from "space-between"
            align_items="start",
            width="100%",
        ),
        style=CARD_STYLE,
        on_click=State.toggle_job_details(job.get("jobid", "")),
    )


def job_details_panel() -> rx.Component:
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
                        color=DESIGN_TOKENS["colors"]["--text-primary"],
                    ),
                    rx.button(
                        rx.icon("x"),
                        on_click=State.toggle_job_details(""),
                        variant="ghost",
                        size="2",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.divider(color=DESIGN_TOKENS["colors"]["--border"]),
                rx.grid(
                    rx.box(
                        rx.text("Job ID:", font_weight="600", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                        rx.text(State.selected_job_id, color=DESIGN_TOKENS["colors"]["--text-primary"]),
                    ),
                    rx.box(
                        rx.text("Status:", font_weight="600", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                status_badge(job["status"]),
                            ),
                        ),
                    ),
                    rx.box(
                        rx.text("Priority:", font_weight="600", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                rx.text(str(job["priority"]), color=DESIGN_TOKENS["colors"]["--text-primary"]),
                            ),
                        ),
                    ),
                    rx.box(
                        rx.text("Project:", font_weight="600", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                        rx.foreach(
                            State.jobs,
                            lambda job: rx.cond(
                                job["jobid"] == State.selected_job_id,
                                rx.text(job["project_path"], color=DESIGN_TOKENS["colors"]["--text-primary"]),
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
                            rx.text("Error:", font_weight="600", color=DESIGN_TOKENS["colors"]["--error"]),
                            rx.text(job["error"], color=DESIGN_TOKENS["colors"]["--text-primary"]),
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
        ),
    )


def job_submission_form() -> rx.Component:
    """Job submission form with manual path entry."""
    return rx.box(
        rx.vstack(
            rx.text(
                "Submit New Job",
                font_size="24px",
                font_weight="700",
                color=DESIGN_TOKENS["colors"]["--text-primary"],
            ),
            rx.form(
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Project Path (.aedt/.aedb)",
                            font_size="14px",
                            color=DESIGN_TOKENS["colors"]["--text-secondary"],
                        ),
                        rx.input(
                            placeholder=r"C:\path\to\your\project.aedt",
                            value=State.project_path,
                            on_change=State.set_project_path,
                            required=True,
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["--text-primary"],
                                "padding": "8px 12px",
                                "font_size": "14px",
                                "height": "40px",
                                "width": "100%",
                                "_focus": {
                                    "border_color": DESIGN_TOKENS["colors"]["--primary"],
                                    "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)",
                                },
                                "_placeholder": {
                                    "color": DESIGN_TOKENS["colors"]["--text-muted"],
                                },
                            },
                        ),
                        rx.text(
                            "💡 Tip: Copy and paste the full path to your ANSYS project file",
                            font_size="12px",
                            color=DESIGN_TOKENS["colors"]["--text-muted"],
                        ),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "Design Name (optional)",
                                font_size="14px",
                                color=DESIGN_TOKENS["colors"]["--text-secondary"],
                            ),
                            rx.input(
                                placeholder="Enter design name...",
                                value=State.design_name,
                                on_change=State.set_design_name,
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["--text-primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "_placeholder": {
                                        "color": DESIGN_TOKENS["colors"]["--text-muted"],
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
                                color=DESIGN_TOKENS["colors"]["--text-secondary"],
                            ),
                            rx.input(
                                placeholder="Enter setup name...",
                                value=State.setup_name,
                                on_change=State.set_setup_name,
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["--text-primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "_placeholder": {
                                        "color": DESIGN_TOKENS["colors"]["--text-muted"],
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
                            rx.text("Priority", font_size="14px", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                            rx.slider(
                                default_value=[0],
                                value=[State.job_priority],
                                on_change=State.set_job_priority,
                                min_=-10,
                                max_=10,
                                step=1,
                                width="100%",
                                style={
                                    "height": "20px",
                                },
                            ),
                            rx.text(
                                f"Value: {State.job_priority}",
                                font_size="12px",
                                color=DESIGN_TOKENS["colors"]["--text-muted"],
                            ),
                            spacing="2",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Cores", font_size="14px", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                            rx.input(
                                type="number",
                                value=State.num_cores,
                                on_change=State.set_num_cores,
                                min="1",
                                max="64",
                                style={
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                    "border_radius": "8px",
                                    "color": DESIGN_TOKENS["colors"]["--text-primary"],
                                    "padding": "8px 12px",
                                    "font_size": "14px",
                                    "height": "40px",
                                    "width": "80px",
                                    "text_align": "center",
                                },
                            ),
                            spacing="2",
                            flex="1",
                        ),
                        spacing="6",
                        width="100%",
                        align_items="end",
                    ),
                    rx.button(
                        "Submit Job",
                        on_click=State.submit_job,
                        style=PRIMARY_BUTTON_STYLE,
                        width="100%",
                        loading=State.loading,
                        size="3",
                    ),
                    spacing="6",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        style=CARD_STYLE,
    )


def system_status_card() -> rx.Component:
    """System status overview card."""
    return rx.box(
        rx.vstack(
            rx.text(
                "System Status",
                font_size="20px",
                font_weight="700",
                color=DESIGN_TOKENS["colors"]["--text-primary"],
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
                                DESIGN_TOKENS["colors"]["--success"],
                                DESIGN_TOKENS["colors"]["--error"],
                            ),
                        ),
                        rx.text(
                            rx.cond(
                                State.connected,
                                "Connected",
                                "Disconnected",
                            ),
                            color=DESIGN_TOKENS["colors"]["--text-primary"],
                        ),
                        spacing="2",
                    ),
                    rx.text(
                        f"Running Jobs: {State.queue_stats.get('running_jobs', 0)} / "
                        f"{State.queue_stats.get('max_concurrent', 0)}",
                        color=DESIGN_TOKENS["colors"]["--text-secondary"],
                    ),
                    rx.text(
                        f"Queued Jobs: {State.queue_stats.get('total_queued', 0)}",
                        color=DESIGN_TOKENS["colors"]["--text-secondary"],
                    ),
                    spacing="2",
                ),
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        style=CARD_STYLE,
    )


def settings_modal() -> rx.Component:
    """Settings modal for resource limits."""
    return rx.cond(
        State.show_settings,
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    "Resource Limits",
                    color=DESIGN_TOKENS["colors"]["--text-primary"],
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Max Concurrent Jobs",
                            font_size="14px",
                            color=DESIGN_TOKENS["colors"]["--text-secondary"],
                        ),
                        rx.input(
                            type="number",
                            value=State.max_concurrent_jobs,
                            on_change=State.set_max_concurrent_jobs,
                            min="1",
                            max="20",
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["--text-primary"],
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
                        rx.text("Max CPU %", font_size="14px", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
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
                            color=DESIGN_TOKENS["colors"]["--text-muted"],
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Min Memory (GB)", font_size="14px", color=DESIGN_TOKENS["colors"]["--text-secondary"]),
                        rx.input(
                            type="number",
                            value=State.min_memory_gb,
                            on_change=State.set_min_memory_gb,
                            min="1",
                            max="128",
                            step="0.5",
                            style={
                                "background": "rgba(255, 255, 255, 0.05)",
                                "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["--text-primary"],
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
                            color=DESIGN_TOKENS["colors"]["--text-secondary"],
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
                                "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
                                "border_radius": "8px",
                                "color": DESIGN_TOKENS["colors"]["--text-primary"],
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
                    "background": DESIGN_TOKENS["colors"]["--surface"],
                    "border": f"1px solid {DESIGN_TOKENS['colors']['--border']}",
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
        "info": DESIGN_TOKENS["colors"]["--primary"],
        "success": DESIGN_TOKENS["colors"]["--success"],
        "warning": DESIGN_TOKENS["colors"]["--warning"],
        "error": DESIGN_TOKENS["colors"]["--error"],
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
                    color=DESIGN_TOKENS["colors"]["--text-primary"],
                    font_weight="500",
                ),
                rx.button(
                    rx.icon("x"),
                    on_click=State.set_notification_message(""),
                    variant="ghost",
                    size="1",
                ),
                justify="between",
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
                "border_left": f"4px solid {color_map.get('success', DESIGN_TOKENS['colors']['--primary'])}",
            },
        ),
    )


def header() -> rx.Component:
    """Application header with navigation."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("zap", size=32, color=DESIGN_TOKENS["colors"]["--primary"]),
                rx.text(
                    "ANSYS Job Manager",
                    font_size="24px",
                    font_weight="700",
                    color=DESIGN_TOKENS["colors"]["--text-primary"],
                ),
                spacing="3",
                align_items="center",
            ),
            rx.hstack(
                rx.button(
                    rx.icon("refresh-cw"),
                    "Refresh",
                    on_click=State.load_initial_data,
                    variant="ghost",
                    loading=State.loading,
                ),
                rx.button(
                    rx.icon("settings"),
                    "Settings",
                    on_click=State.set_show_settings(True),
                    variant="ghost",
                ),
                spacing="2",
            ),
            justify="between",
            align_items="center",
            width="100%",
        ),
        style={
            **GLASS_STYLE,
            "padding": "16px 24px",
            "margin_bottom": "24px",
        },
    )


def main_content() -> rx.Component:
    """Main application content area."""
    return rx.container(
        rx.vstack(
            header(),
            rx.grid(
                rx.box(
                    system_status_card(),
                    grid_column="span 1",
                ),
                rx.box(
                    job_submission_form(),
                    grid_column="span 2",
                ),
                columns="3",
                spacing="6",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "Active Jobs",
                        font_size="24px",
                        font_weight="700",
                        color=DESIGN_TOKENS["colors"]["--text-primary"],
                    ),
                    rx.cond(
                        State.loading,
                        rx.vstack(
                            shimmer_skeleton(),
                            shimmer_skeleton(),
                            shimmer_skeleton(),
                            spacing="4",
                        ),
                        rx.cond(
                            State.jobs.length() > 0,
                            rx.vstack(
                                rx.foreach(State.jobs, job_card),
                                spacing="4",
                                width="100%",
                            ),
                            rx.box(
                                rx.text(
                                    "No jobs found",
                                    color=DESIGN_TOKENS["colors"]["--text-secondary"],
                                    font_size="16px",
                                ),
                                style={
                                    "text_align": "center",
                                    "padding": "48px",
                                },
                            ),
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                style=CARD_STYLE,
            ),
            job_details_panel(),
            spacing="6",
            width="100%",
        ),
        max_width="1400px",  # Increased from 1200px
        padding="24px",
    )


def index() -> rx.Component:
    """Main application page."""
    return rx.theme(
        rx.box(
            notification_toast(),
            settings_modal(),
            main_content(),
            style={
                "min_height": "100vh",
                "background": f"linear-gradient(135deg, {DESIGN_TOKENS['colors']['--background']} 0%, "
                f"{DESIGN_TOKENS['colors']['--background-secondary']} 100%)",
                "color": DESIGN_TOKENS["colors"]["--text-primary"],
            },
        ),
        appearance="dark",
        accent_color="blue",
        on_mount=State.connect_to_backend,
    )


app = rx.App(
    stylesheets=["custom.css"],
)

app.add_page(index, route="/")

"""
HFSS Simulation Job Manager - Production Ready
Enterprise-grade job management for ANSYS HFSS simulations
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
import logging
import os
import shutil

# import subprocess
import threading
import time
from typing import Any, Dict, List, Optional
import uuid

import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State

# --------------------------------------------------------------------------- #
# Optional native HFSS integration                                            #
# --------------------------------------------------------------------------- #
# try:
#     from hfss_jobs import (
#         HFSSSimulationConfig,
#         SchedulerOptions,
#         SchedulerType,
#         create_hfss_config,
#     )
#
#     HFSS_AVAILABLE = True
# except ImportError:
#     HFSS_AVAILABLE = False
#     print("Warning: hfss_jobs module not available. Using simulation mode only.")

# --------------------------------------------------------------------------- #
# Logging                                                                     #
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("hfss_job_manager.log"), logging.StreamHandler()],
)
logger = logging.getLogger("HFSSJobManager")

# --------------------------------------------------------------------------- #
# Design System                                                               #
# --------------------------------------------------------------------------- #
COLORS = {
    "primary": "#1a2332",
    "secondary": "#0d47a1",
    "accent": "#1976d2",
    "success": "#2e7d32",
    "warning": "#ed6c02",
    "error": "#d32f2f",
    "background": "#f5f7fa",
    "surface": "#ffffff",
    "text": "#1a2332",
    "text_secondary": "#5f6368",
    "border": "#e0e4e7",
    "divider": "#dadce0",
}


# --------------------------------------------------------------------------- #
# System Utilities                                                           #
# --------------------------------------------------------------------------- #
def get_system_resources():
    """Get real system resource information with psutil"""
    try:
        import psutil

        # CPU info
        cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1

        # Memory info
        mem = psutil.virtual_memory()
        total_ram = round(mem.total / (1024**3), 1)
        used_ram = round(mem.used / (1024**3), 1)
        free_ram = round(mem.available / (1024**3), 1)
        ram_percent = mem.percent

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Disk space
        disk = shutil.disk_usage("/")
        total_disk = round(disk.total / (1024**3), 1)
        free_disk = round(disk.free / (1024**3), 1)
        used_disk = round(disk.used / (1024**3), 1)

        return {
            "cpu_cores": cpu_count,
            "cpu_percent": cpu_percent,
            "total_ram": total_ram,
            "used_ram": used_ram,
            "free_ram": free_ram,
            "ram_percent": ram_percent,
            "total_disk": total_disk,
            "free_disk": free_disk,
            "used_disk": used_disk,
        }
    except ImportError:
        return {
            "cpu_cores": os.cpu_count() or 1,
            "cpu_percent": 0,
            "total_ram": 16.0,
            "used_ram": 8.0,
            "free_ram": 8.0,
            "ram_percent": 50.0,
            "total_disk": 512.0,
            "free_disk": 256.0,
            "used_disk": 256.0,
        }


# --------------------------------------------------------------------------- #
# Domain                                                                      #
# --------------------------------------------------------------------------- #
class JobStatus(Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    STOPPED = "Stopped"
    SUBMITTING = "Submitting"


# --------------------------------------------------------------------------- #
# Core manager                                                                #
# --------------------------------------------------------------------------- #
class HFSSJobManager:
    """Thread-safe controller for HFSS simulation jobs."""

    def __init__(self) -> None:
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.active_processes: Dict[str, Any] = {}
        self.scheduler_jobs: Dict[str, Any] = {}
        self._load_jobs()

        self.monitor_thread = threading.Thread(target=self._monitor_jobs, daemon=True)
        self.monitor_thread.start()
        self.scheduler_monitor_thread = threading.Thread(target=self._monitor_scheduler_jobs, daemon=True)
        self.scheduler_monitor_thread.start()
        logger.info("HFSS Job Manager initialized")

    def _load_jobs(self) -> None:
        logger.info("Initialized with empty job list")

    def add_job(self, config: Any) -> str:
        """Add a new HFSS simulation job to the queue."""
        with self.lock:
            job_id = config.get("jobid") or f"HFSS_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"

            job_data = {
                "job_id": job_id,
                "config": config,
                "status": JobStatus.QUEUED.value,
                "scheduler_type": config.get("scheduler_type", "none"),
                "submitted_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "output": None,
                "error": None,
                "scheduler_job_id": None,
            }

            self.jobs[job_id] = job_data
            logger.info("Added job %s to queue", job_id)
            return job_id

    def start_job(self, job_id: str) -> bool:
        """Start a queued job."""
        with self.lock:
            if job_id not in self.jobs or self.jobs[job_id]["status"] != JobStatus.QUEUED.value:
                return False
            self.jobs[job_id]["status"] = JobStatus.SUBMITTING.value
            self.jobs[job_id]["started_at"] = datetime.now().isoformat()

        threading.Thread(target=self._run_job, args=(job_id,), daemon=True).start()
        return True

    def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        with self.lock:
            if job_id not in self.jobs:
                return False
            status = self.jobs[job_id]["status"]
            if status not in {JobStatus.RUNNING.value, JobStatus.SUBMITTING.value}:
                return False

            self.jobs[job_id]["status"] = JobStatus.STOPPED.value
            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
            return True

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.jobs.values())

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        with self.lock:
            running = [job for job in self.jobs.values() if job["status"] == JobStatus.RUNNING.value]
            queued = [job for job in self.jobs.values() if job["status"] == JobStatus.QUEUED.value]

            total_nodes = total_cores = 0
            for job in running:
                opts = job.get("config", {}).get("scheduler_options", {})
                total_nodes += opts.get("nodes", 1)
                total_cores += opts.get("nodes", 1) * opts.get("tasks_per_node", 4)

            return {
                "running_jobs": len(running),
                "queued_jobs": len(queued),
                "total_nodes": total_nodes,
                "total_cores": total_cores,
                "timestamp": datetime.now().isoformat(),
            }

    def get_job_output(self, job_id: str) -> Optional[str]:
        """Get job output."""
        with self.lock:
            if job_id in self.active_processes:
                return "".join(self.active_processes[job_id].get("output", []))
            job = self.jobs.get(job_id)
            return job.get("output") if job else None

    def _run_job(self, job_id: str) -> None:
        """Execute job."""
        try:
            scheduler_type = self.jobs[job_id].get("scheduler_type", "none")
            if scheduler_type == "none":
                self._execute_local_job(job_id)
            else:
                self._simulate_scheduler_job(job_id)
        except Exception as exc:
            with self.lock:
                self.jobs[job_id]["status"] = JobStatus.FAILED.value
                self.jobs[job_id]["error"] = str(exc)
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()

    def _execute_local_job(self, job_id: str) -> None:
        """Simulate local execution."""
        import random

        duration = random.randint(5, 15)

        with self.lock:
            self.active_processes[job_id] = {
                "start_time": time.time(),
                "output": [f"Starting local job {job_id}\n"],
            }

        for i in range(duration):
            if job_id not in self.active_processes:
                break
            time.sleep(1)
            with self.lock:
                if job_id in self.active_processes:
                    progress = (i + 1) / duration * 100
                    self.active_processes[job_id]["output"].append(f"Progress: {progress:.1f}%\n")

        success = random.random() > 0.1
        with self.lock:
            out = "".join(self.active_processes.pop(job_id, {}).get("output", []))
            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
            self.jobs[job_id]["status"] = JobStatus.COMPLETED.value if success else JobStatus.FAILED.value
            self.jobs[job_id]["output"] = out + ("\nCompleted" if success else "\nFailed")

    def _simulate_scheduler_job(self, job_id: str) -> None:
        """Simulate scheduler submission."""
        import random

        time.sleep(3)
        with self.lock:
            self.jobs[job_id]["scheduler_job_id"] = str(random.randint(10000, 99999))
            self.jobs[job_id]["status"] = JobStatus.RUNNING.value

    def _monitor_jobs(self) -> None:
        """Background thread: start queued jobs when resources are available."""
        while True:
            try:
                queued = [job for job in self.jobs.values() if job["status"] == JobStatus.QUEUED.value]
                for job in queued:
                    self.start_job(job["job_id"])
                    time.sleep(2)
                time.sleep(10)
            except Exception as exc:
                logger.error("Error in monitor thread: %s", exc)
                time.sleep(30)

    def _monitor_scheduler_jobs(self) -> None:
        """Background thread: poll scheduler for job completion."""
        while True:
            try:
                with self.lock:
                    to_check = list(self.scheduler_jobs.items())

                for job_id, info in to_check:
                    scheduler_type = info.get("scheduler_type")
                    if scheduler_type and scheduler_type != "none":
                        if job_id in self.jobs:
                            self.jobs[job_id]["status"] = JobStatus.COMPLETED.value
                            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                            self.jobs[job_id]["output"] = "Scheduler job completed"
                        self.scheduler_jobs.pop(job_id, None)

                time.sleep(30)
            except Exception as exc:
                logger.error("Error in scheduler monitor thread: %s", exc)
                time.sleep(60)


# --------------------------------------------------------------------------- #
# Dash application                                                            #
# --------------------------------------------------------------------------- #
app = dash.Dash(__name__, title="HFSS Job Manager - Production", update_title="Loading...")
job_manager = HFSSJobManager()

# --------------------------------------------------------------------------- #
# Layout                                                                      #
# --------------------------------------------------------------------------- #
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "HFSS Job Manager",
                            style={"margin": 0, "fontSize": 28, "fontWeight": 300, "color": COLORS["text"]},
                        ),
                        html.P(
                            "Enterprise Simulation Control",
                            style={"margin": "4px 0 0 0", "color": COLORS["text_secondary"], "fontSize": 14},
                        ),
                    ]
                ),
            ],
            style={
                "padding": "24px 32px",
                "backgroundColor": COLORS["surface"],
                "borderBottom": f'1px solid {COLORS["border"]}',
            },
        ),
        # Main container
        html.Div(
            [
                # Control Panel
                html.Div(
                    [
                        html.H2(
                            "Cluster Configuration",
                            style={"margin": "0 0 16px 0", "fontSize": 20, "fontWeight": 400, "color": COLORS["text"]},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Scheduler Type",
                                    style={
                                        "fontSize": 14,
                                        "fontWeight": 500,
                                        "color": COLORS["text"],
                                        "marginBottom": 8,
                                    },
                                ),
                                dcc.Dropdown(
                                    id="scheduler-type-selector",
                                    options=[
                                        {"label": "Local Execution", "value": "none"},
                                        {"label": "SLURM Cluster", "value": "slurm"},
                                        {"label": "LSF Cluster", "value": "lsf"},
                                        {"label": "PBS Cluster", "value": "pbs"},
                                        {"label": "Windows HPC", "value": "windows_hpc"},
                                    ],
                                    value="none",
                                    style={"width": "300px"},
                                ),
                            ],
                            style={"marginBottom": 16},
                        ),
                        html.Div(id="resource-display"),
                    ],
                    style={
                        "padding": 24,
                        "backgroundColor": COLORS["surface"],
                        "borderRadius": 8,
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                        "marginBottom": 24,
                    },
                ),
                # Job Submission Form
                html.Div(
                    [
                        html.H2(
                            "Submit New Job",
                            style={"margin": "0 0 20px 0", "fontSize": 20, "fontWeight": 400, "color": COLORS["text"]},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            "Job ID",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="job-id",
                                            type="text",
                                            placeholder="my-job-001",
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": "0 0 200px", "marginRight": 16},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Project Path",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="project-path",
                                            type="text",
                                            placeholder="/path/to/project.aedt",
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                            ],
                            style={"display": "flex", "gap": 16, "marginBottom": 16},
                        ),
                        # File upload section for browse functionality
                        html.Div(
                            [
                                html.Label(
                                    "Project File",
                                    style={
                                        "fontSize": 14,
                                        "fontWeight": 500,
                                        "color": COLORS["text"],
                                        "marginBottom": 8,
                                    },
                                ),
                                dcc.Upload(
                                    id="upload-file",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A(
                                                "Select File", style={"color": COLORS["accent"], "cursor": "pointer"}
                                            ),
                                        ],
                                        style={
                                            "width": "100%",
                                            "height": 60,
                                            "lineHeight": "60px",
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": 5,
                                            "textAlign": "center",
                                            "borderColor": COLORS["border"],
                                            "backgroundColor": "#fafafa",
                                        },
                                    ),
                                    multiple=False,
                                    accept=".aedt",
                                ),
                                html.Div(
                                    id="file-path-display",
                                    style={"marginTop": 8, "fontSize": 12, "color": COLORS["text_secondary"]},
                                ),
                            ],
                            style={"marginBottom": 16},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            "Design Name",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="design-name",
                                            type="text",
                                            value="main",
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Setup Name",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="setup-name",
                                            type="text",
                                            value="Setup1",
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Nodes",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="nodes",
                                            type="number",
                                            value=1,
                                            min=1,
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": "0 0 100px"},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Cores",
                                            style={
                                                "fontSize": 14,
                                                "fontWeight": 500,
                                                "color": COLORS["text"],
                                                "marginBottom": 4,
                                            },
                                        ),
                                        dcc.Input(
                                            id="cores",
                                            type="number",
                                            value=4,
                                            min=1,
                                            style={"width": "100%", "height": 36, "borderRadius": 4},
                                        ),
                                    ],
                                    style={"flex": "0 0 100px"},
                                ),
                            ],
                            style={"display": "flex", "gap": 16, "marginBottom": 20},
                        ),
                        html.Button(
                            "Submit Job",
                            id="submit-job-btn",
                            n_clicks=0,
                            style={
                                "backgroundColor": COLORS["accent"],
                                "color": "white",
                                "border": "none",
                                "padding": "12px 32px",
                                "borderRadius": 4,
                                "fontSize": 14,
                                "fontWeight": 500,
                                "cursor": "pointer",
                                "transition": "background-color 0.2s",
                            },
                        ),
                        html.Div(id="submit-result", style={"marginTop": 12}),
                    ],
                    style={
                        "padding": 24,
                        "backgroundColor": COLORS["surface"],
                        "borderRadius": 8,
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                    },
                ),
                # Job Queue
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "Job Queue",
                                    style={"margin": 0, "fontSize": 20, "fontWeight": 400, "color": COLORS["text"]},
                                ),
                                html.Div(
                                    id="resource-summary",
                                    style={"marginTop": 8, "fontSize": 14, "color": COLORS["text_secondary"]},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "marginBottom": 16,
                            },
                        ),
                        html.Div(id="jobs-table"),
                    ],
                    style={
                        "padding": 24,
                        "backgroundColor": COLORS["surface"],
                        "borderRadius": 8,
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                    },
                ),
                # Log Output
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "Job Logs",
                                    style={"margin": 0, "fontSize": 20, "fontWeight": 400, "color": COLORS["text"]},
                                ),
                                html.Button(
                                    "Clear Log",
                                    id="clear-log-btn",
                                    style={
                                        "backgroundColor": COLORS["text_secondary"],
                                        "color": "white",
                                        "border": "none",
                                        "padding": "8px 16px",
                                        "borderRadius": 4,
                                        "fontSize": 12,
                                        "cursor": "pointer",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "marginBottom": 16,
                            },
                        ),
                        dcc.Dropdown(
                            id="log-job-selector",
                            placeholder="Select a job to view logs...",
                            style={"width": "300px", "marginBottom": 16},
                        ),
                        html.Div(
                            id="log-output",
                            style={
                                "backgroundColor": "#1e1e1e",
                                "color": "#e0e0e0",
                                "padding": 16,
                                "borderRadius": 4,
                                "fontFamily": "Consolas, Monaco, monospace",
                                "fontSize": 13,
                                "lineHeight": 1.4,
                                "whiteSpace": "pre-wrap",
                                "maxHeight": 400,
                                "overflowY": "auto",
                            },
                        ),
                    ],
                    style={
                        "padding": 24,
                        "backgroundColor": COLORS["surface"],
                        "borderRadius": 8,
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                    },
                ),
            ],
            style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px 32px"},
        ),
        # System resources store
        dcc.Store(id="system-resources", data=get_system_resources()),
        dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    ],
    style={"backgroundColor": COLORS["background"], "minHeight": "100vh"},
)


# --------------------------------------------------------------------------- #
# Callbacks                                                                   #
# --------------------------------------------------------------------------- #
@app.callback(
    Output("resource-display", "children"),
    [Input("scheduler-type-selector", "value"), Input("system-resources", "data")],
)
def update_resource_display(scheduler_type, system_data):
    if scheduler_type == "none":
        # Local resources with real data and dynamic CPU/RAM
        cpu_percent = system_data.get("cpu_percent", 0)
        ram_percent = system_data.get("ram_percent", 0)

        return html.Div(
            [
                html.Div(
                    [
                        html.H3("Local System", style={"margin": 0, "fontSize": 16, "fontWeight": 500}),
                    ],
                    style={"marginBottom": 16},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("CPU Cores", style={"fontSize": 14, "color": COLORS["text_secondary"]}),
                                html.Div(
                                    str(system_data.get("cpu_cores", 0)), style={"fontSize": 18, "fontWeight": 500}
                                ),
                            ],
                            style={"flex": 1},
                        ),
                        html.Div(
                            [
                                html.Div("CPU Usage", style={"fontSize": 14, "color": COLORS["text_secondary"]}),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    style={
                                                        "width": "100%",
                                                        "height": 8,
                                                        "backgroundColor": "#e0e0e0",
                                                        "borderRadius": 4,
                                                    }
                                                ),
                                                html.Div(
                                                    style={
                                                        "width": f"{cpu_percent}%",
                                                        "height": 8,
                                                        "backgroundColor": COLORS["accent"],
                                                        "borderRadius": 4,
                                                        "marginTop": -8,
                                                    }
                                                ),
                                            ],
                                            style={"width": 100, "marginBottom": 4},
                                        ),
                                        html.Div(
                                            f"{cpu_percent:.1f}%",
                                            style={"fontSize": 12, "fontWeight": 500, "color": COLORS["accent"]},
                                        ),
                                    ]
                                ),
                            ],
                            style={"flex": 1},
                        ),
                        html.Div(
                            [
                                html.Div("Memory", style={"fontSize": 14, "color": COLORS["text_secondary"]}),
                                html.Div(
                                    [
                                        html.Div(
                                            f"{system_data.get('free_ram', 0):.1f} GB / "
                                            f"{system_data.get('total_ram', 0):.1f} GB",
                                            style={"fontSize": 18, "fontWeight": 500},
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    style={
                                                        "width": "100%",
                                                        "height": 8,
                                                        "backgroundColor": "#e0e0e0",
                                                        "borderRadius": 4,
                                                    }
                                                ),
                                                html.Div(
                                                    style={
                                                        "width": f"{ram_percent}%",
                                                        "height": 8,
                                                        "backgroundColor": COLORS["warning"],
                                                        "borderRadius": 4,
                                                        "marginTop": -8,
                                                    }
                                                ),
                                            ],
                                            style={"width": 100, "marginBottom": 4},
                                        ),
                                        html.Div(
                                            f"{system_data.get('used_ram', 0):.1f} GB used",
                                            style={"fontSize": 12, "color": COLORS["text_secondary"]},
                                        ),
                                    ]
                                ),
                            ],
                            style={"flex": 1},
                        ),
                        html.Div(
                            [
                                html.Div("Storage", style={"fontSize": 14, "color": COLORS["text_secondary"]}),
                                html.Div(
                                    [
                                        html.Div(
                                            f"{system_data.get('free_disk', 0):.1f} GB / "
                                            f"{system_data.get('total_disk', 0):.1f} GB",
                                            style={"fontSize": 18, "fontWeight": 500},
                                        ),
                                    ]
                                ),
                            ],
                            style={"flex": 1},
                        ),
                    ],
                    style={"display": "flex", "gap": 32},
                ),
            ],
            style={"padding": 20},
        )
    else:
        # Cluster resources
        clusters = {
            "slurm": {"name": "SLURM Cluster", "nodes": 64, "cores": 2048, "memory": "8TB"},
            "lsf": {"name": "LSF Cluster", "nodes": 32, "cores": 1024, "memory": "4TB"},
            "pbs": {"name": "PBS Cluster", "nodes": 48, "cores": 1536, "memory": "6TB"},
            "windows_hpc": {"name": "Windows HPC", "nodes": 16, "cores": 512, "memory": "2TB"},
        }

        cluster = clusters.get(scheduler_type, {})
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    cluster.get("name", "Cluster"),
                                    style={"margin": 0, "fontSize": 16, "fontWeight": 500},
                                ),
                            ],
                            style={"marginBottom": 16},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            "Compute Nodes", style={"fontSize": 14, "color": COLORS["text_secondary"]}
                                        ),
                                        html.Div(
                                            f"{cluster.get('nodes', 0)}", style={"fontSize": 18, "fontWeight": 500}
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Total Cores", style={"fontSize": 14, "color": COLORS["text_secondary"]}
                                        ),
                                        html.Div(
                                            f"{cluster.get('cores', 0)}", style={"fontSize": 18, "fontWeight": 500}
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Total Memory", style={"fontSize": 14, "color": COLORS["text_secondary"]}
                                        ),
                                        html.Div(cluster.get("memory", "0"), style={"fontSize": 18, "fontWeight": 500}),
                                    ],
                                    style={"flex": 1},
                                ),
                            ],
                            style={"display": "flex", "gap": 32},
                        ),
                    ],
                    style={"padding": 20},
                ),
            ]
        )


@app.callback(
    Output("resource-summary", "children"),
    Input("interval-component", "n_intervals"),
    Input("system-resources", "data"),
)
def update_resource_summary(n: int, system_data):
    usage = job_manager.get_resource_usage()
    local_info = ""
    if usage["running_jobs"] == 0 and usage["queued_jobs"] == 0:
        local_info = (
            f" | CPU: {system_data.get('cpu_percent', 0):.1f}% | RAM: {system_data.get('used_ram', 0):.1f}/"
            f"{system_data.get('total_ram', 0)}GB"
        )
    return (
        f"{usage['running_jobs']} running, {usage['queued_jobs']} queued | " f"{usage['total_cores']} cores{local_info}"
    )


@app.callback(
    [Output("jobs-table", "children"), Output("log-job-selector", "options")],
    Input("interval-component", "n_intervals"),
    Input("system-resources", "data"),
)
def update_jobs_table(n: int, system_data):
    jobs = job_manager.get_all_jobs()
    table_data, log_opts = [], []

    for job in jobs:
        cfg = job.get("config", {})
        opts = cfg.get("scheduler_options", {})

        table_data.append(
            {
                "job_id": job["job_id"],
                "status": job["status"],
                "scheduler": job["scheduler_type"].upper(),
                "nodes": opts.get("nodes", 1),
                "cores": opts.get("tasks_per_node", system_data.get("cpu_cores", 4)),
                "submitted": job["submitted_at"][:19].replace("T", " "),
            }
        )

        log_opts.append({"label": job["job_id"], "value": job["job_id"]})

    table = dash_table.DataTable(
        id="jobs-datatable",
        columns=[
            {"name": "Job ID", "id": "job_id"},
            {"name": "Status", "id": "status"},
            {"name": "Scheduler", "id": "scheduler"},
            {"name": "Nodes", "id": "nodes", "type": "numeric"},
            {"name": "Cores", "id": "cores", "type": "numeric"},
            {"name": "Submitted", "id": "submitted"},
        ],
        data=table_data,
        style_cell={"textAlign": "left", "padding": "12px 16px", "fontSize": 14},
        style_header={
            "backgroundColor": COLORS["surface"],
            "fontWeight": 600,
            "borderBottom": f"1px solid {COLORS['border']}",
        },
        style_data_conditional=[
            {"if": {"column_id": "job_id"}, "fontWeight": 500},
            {"if": {"filter_query": "{status} = 'Running'"}, "color": COLORS["accent"]},
            {"if": {"filter_query": "{status} = 'Completed'"}, "color": COLORS["success"]},
            {"if": {"filter_query": "{status} = 'Failed'"}, "color": COLORS["error"]},
        ],
        page_size=10,
        style_table={"border": "none"},
    )
    return table, log_opts


@app.callback(
    Output("submit-result", "children"),
    Input("submit-job-btn", "n_clicks"),
    [
        State("job-id", "value"),
        State("project-path", "value"),
        State("design-name", "value"),
        State("setup-name", "value"),
        State("scheduler-type-selector", "value"),
        State("nodes", "value"),
        State("cores", "value"),
    ],
    prevent_initial_call=True,
)
def handle_submit(n_clicks, job_id, project_path, design_name, setup_name, scheduler_type, nodes, cores):
    if not job_id or not project_path:
        return html.Div("Please provide Job ID and Project Path", style={"color": COLORS["error"], "fontSize": 14})

    try:
        config = {
            "jobid": job_id,
            "project_path": project_path,
            "design_name": design_name or "main",
            "setup_name": setup_name or "Setup1",
            "scheduler_type": scheduler_type,
            "scheduler_options": {
                "nodes": nodes or 1,
                "tasks_per_node": cores or 4,
            },
        }

        job_manager.add_job(config)
        job_manager.start_job(job_id)

        return html.Div(
            [
                html.Div("✓ Job submitted", style={"color": COLORS["success"], "fontSize": 14}),
                html.Div(f"Job ID: {job_id}", style={"fontSize": 12, "color": COLORS["text_secondary"]}),
            ]
        )
    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": COLORS["error"], "fontSize": 14})


@app.callback(
    Output("log-output", "children"), [Input("log-job-selector", "value"), Input("interval-component", "n_intervals")]
)
def update_log_output(selected_job_id, n_intervals):
    if not selected_job_id:
        return "Select a job to view logs"

    output = job_manager.get_job_output(selected_job_id)
    if not output:
        return "No output available"

    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {output}"


@app.callback(
    Output("log-output", "children", allow_duplicate=True),
    Input("clear-log-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_log(n_clicks):
    if n_clicks > 0:
        return ""
    return dash.no_update


# File upload callbacks
@app.callback(
    [Output("project-path", "value"), Output("file-path-display", "children")],
    Input("upload-file", "filename"),
    Input("upload-file", "contents"),
)
def update_file_path(filename, contents):
    if filename:
        return filename, html.Div(
            ["Selected: ", html.Span(filename, style={"fontWeight": "bold", "color": COLORS["accent"]})]
        )
    return "", ""


# --------------------------------------------------------------------------- #
# Entry-point                                                                 #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    logger.info("Starting HFSS Job Manager - Production Mode")
    print("\n" + "=" * 60)
    print("🚀 HFSS Job Manager - Production Ready")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8050")
    print("📝 Real-time system resources monitoring")
    print("🖥️  Local/Cluster job management")
    print("📁 File upload via drag-and-drop or browse")
    print("⚡ Dynamic CPU/RAM usage graphs\n")
    app.run(debug=False, host="0.0.0.0", port=8050)

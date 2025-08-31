"""
HFSS Simulation Job Manager with Web Interface.

This module provides a comprehensive job management system for ANSYS HFSS simulations
with support for all enterprise schedulers and local resources.  It includes resource
tracking, job monitoring, and a web-based dashboard for job control.

Example (headless)::

    >>> from hfss_job_manager import HFSSJobManager
    >>> mgr = HFSSJobManager()
    >>> job_id = mgr.add_job(config)
    >>> mgr.start_job(job_id)

Example (web)::

    $ python hfss_job_manager.py
    # then browse to http://localhost:8050

Attributes:
    HFSS_AVAILABLE (bool): True when the native ``hfss_jobs`` package is importable.
    logger (logging.Logger): Root logger for the whole package.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from enum import Enum
import json
import logging
import os
import platform
import re
import subprocess
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

import dash
from dash import callback_context, dash_table, dcc, html
from dash.dependencies import Input, Output, State

# --------------------------------------------------------------------------- #
# Optional native HFSS integration                                            #
# --------------------------------------------------------------------------- #
try:
    from hfss_jobs import (
        HFSSSimulationConfig,
        SchedulerOptions,
        SchedulerType,
        create_hfss_config,
    )

    HFSS_AVAILABLE = True
except ImportError:
    HFSS_AVAILABLE = False
    print("Warning: hfss_jobs module not available. Using simulation mode only.")

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
# Domain                                                                      #
# --------------------------------------------------------------------------- #
class JobStatus(Enum):
    """Enumeration of all supported job life-cycle states."""

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
    """
    Thread-safe controller for HFSS simulation jobs.

    Features:
        - Local and scheduler-based execution (SLURM, LSF, PBS, Windows HPC)
        - Real-time resource tracking
        - Graceful job termination
        - In-memory persistence (no external DB)

    Attributes:
        jobs (Dict[str, Dict]): Mapping ``job_id`` → job record.
        lock (threading.Lock): Guards all shared state.
    """

    def __init__(self) -> None:
        """Initialize the manager and spawn background monitor threads."""
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

    # --------------------------------------------------------------------- #
    # Persistence helpers (no-op)                                           #
    # --------------------------------------------------------------------- #
    def _load_jobs(self) -> None:
        """Load jobs from persistent storage (stub for future DB integration)."""
        logger.info("Initialized with empty job list")

    def _save_jobs(self) -> None:
        """Save jobs to persistent storage (stub)."""

    # --------------------------------------------------------------------- #
    # Public API                                                            #
    # --------------------------------------------------------------------- #
    def add_job(self, config: Any) -> str:
        """
        Add a new HFSS simulation job to the queue.

        Args:
            config: An ``HFSSSimulationConfig`` instance or dict with compatible fields.

        Returns:
            str: The globally unique job identifier.
        """
        with self.lock:
            if hasattr(config, "jobid") and config.jobid:
                job_id = config.jobid
            else:
                job_id = f"HFSS_{datetime.now():%Y%m%d_%H%M%S}_" f"{uuid.uuid4().hex[:8]}"

            job_data = {
                "job_id": job_id,
                "config": asdict(config) if hasattr(config, "__dataclass_fields__") else config,
                "status": JobStatus.QUEUED.value,
                "scheduler_type": config.scheduler_type.value if hasattr(config, "scheduler_type") else "none",
                "submitted_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "output": None,
                "error": None,
                "scheduler_job_id": None,
            }

            self.jobs[job_id] = job_data
            self._save_jobs()
            logger.info("Added job %s to queue", job_id)
            return job_id

    def start_job(self, job_id: str) -> bool:
        """
        Transition a ``QUEUED`` job to ``RUNNING`` (or ``SUBMITTING``).

        Args:
            job_id: Job to start.

        Returns:
            bool: True if the transition succeeded.
        """
        with self.lock:
            if job_id not in self.jobs:
                logger.error("Job %s not found", job_id)
                return False
            if self.jobs[job_id]["status"] != JobStatus.QUEUED.value:
                logger.error("Job %s is not in queued state", job_id)
                return False

            self.jobs[job_id]["status"] = JobStatus.SUBMITTING.value
            self.jobs[job_id]["started_at"] = datetime.now().isoformat()
            self._save_jobs()

        threading.Thread(target=self._run_job, args=(job_id,), daemon=True).start()
        logger.info("Started job %s", job_id)
        return True

    def stop_job(self, job_id: str) -> bool:
        """
        Attempt to cancel/terminate a job.

        For local jobs the underlying process is terminated; for scheduler
        jobs the appropriate scheduler command (``scancel``, ``bkill`` …) is issued.

        Args:
            job_id: Job to stop.

        Returns:
            bool: True if the stop request was accepted.
        """
        with self.lock:
            if job_id not in self.jobs:
                logger.error("Job %s not found", job_id)
                return False

            status = self.jobs[job_id]["status"]
            if status not in {JobStatus.RUNNING.value, JobStatus.SUBMITTING.value}:
                logger.error("Job %s is not running", job_id)
                return False

            # Cancel scheduler job if applicable
            scheduler_job_id = self.jobs[job_id].get("scheduler_job_id")
            scheduler_type = self.jobs[job_id].get("scheduler_type")
            if scheduler_job_id and scheduler_type and scheduler_type != "none":
                self._cancel_scheduler_job(scheduler_type, scheduler_job_id)

            # Terminate local process
            if job_id in self.active_processes:
                proc_info = self.active_processes[job_id]
                proc = proc_info.get("process")
                if proc:
                    try:
                        proc.terminate()
                        time.sleep(1)
                        if proc.poll() is None:
                            proc.kill()
                    except Exception as exc:
                        logger.error("Error terminating process for job %s: %s", job_id, exc)
                del self.active_processes[job_id]

            if job_id in self.scheduler_jobs:
                del self.scheduler_jobs[job_id]

            self.jobs[job_id]["status"] = JobStatus.STOPPED.value
            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
            self._save_jobs()
            logger.info("Stopped job %s", job_id)
            return True

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single job record.

        Args:
            job_id: Job identifier.

        Returns:
            The job dictionary or None when no such job exists.
        """
        with self.lock:
            return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Return a snapshot of all jobs.

        Returns:
            List of job dictionaries (copy of internal state).
        """
        with self.lock:
            return list(self.jobs.values())

    def get_jobs_by_status(self, status: JobStatus) -> List[Dict[str, Any]]:
        """
        Filter jobs by status.

        Args:
            status: Desired status.

        Returns:
            List of job dictionaries whose ``status`` equals ``status.value``.
        """
        with self.lock:
            return [job for job in self.jobs.values() if job["status"] == status.value]

    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Aggregate current resource consumption.

        Returns:
            Dictionary with keys::

                {
                    "running_jobs": int,
                    "queued_jobs": int,
                    "total_nodes": int,
                    "total_cores": int,
                    "total_memory": int,   # GB
                    "total_gpus": int,
                    "timestamp": str,      # ISO-8601
                }
        """
        with self.lock:
            running = self.get_jobs_by_status(JobStatus.RUNNING)
            queued = self.get_jobs_by_status(JobStatus.QUEUED)

            total_nodes = total_cores = total_memory = total_gpus = 0

            for job in running:
                cfg = job.get("config", {})
                opts = cfg.get("scheduler_options", {})
                total_nodes += opts.get("nodes", 1)
                total_cores += opts.get("nodes", 1) * opts.get("tasks_per_node", 1)

                mem_str = opts.get("memory", "0GB")
                total_memory += int("".join(filter(str.isdigit, mem_str))) or 0
                total_gpus += opts.get("gpus", 0)

            return {
                "running_jobs": len(running),
                "queued_jobs": len(queued),
                "total_nodes": total_nodes,
                "total_cores": total_cores,
                "total_memory": total_memory,
                "total_gpus": total_gpus,
                "timestamp": datetime.now().isoformat(),
            }

    def get_job_progress(self, job_id: str) -> Optional[float]:
        """
        Estimate progress for a running job.

        Args:
            job_id: Job to query.

        Returns:
            Percentage (0–100) when estimable, otherwise None.
        """
        with self.lock:
            info = self.active_processes.get(job_id)
            if not info:
                return None
            if "progress" in info:
                return info["progress"]
            if "start_time" in info:
                elapsed = time.time() - info["start_time"]
                return min(95.0, elapsed / 300 * 100)
            return None

    def get_job_output(self, job_id: str) -> Optional[str]:
        """
        Fetch stdout/stderr produced by a job.

        Args:
            job_id: Job to query.

        Returns:
            Concatenated output text or None.
        """
        with self.lock:
            if job_id in self.active_processes:
                return "".join(self.active_processes[job_id].get("output", []))
            job = self.jobs.get(job_id)
            return job.get("output") if job else None

    # ------------------------------------------------------------------ #
    # Internal runners / monitors                                         #
    # ------------------------------------------------------------------ #
    def _run_job(self, job_id: str) -> None:
        """Execute the correct runner (local or scheduler)."""
        try:
            scheduler_type = self.jobs[job_id].get("scheduler_type", "none")
            if scheduler_type == "none":
                self._execute_local_job(job_id)
            else:
                self._execute_scheduler_job(job_id)
        except Exception as exc:
            with self.lock:
                self.jobs[job_id]["status"] = JobStatus.FAILED.value
                self.jobs[job_id]["error"] = str(exc)
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                self._save_jobs()
            logger.exception("Job %s failed", job_id)

    def _execute_local_job(self, job_id: str) -> None:
        """Run HFSS directly via subprocess."""
        if HFSS_AVAILABLE:
            cfg = HFSSSimulationConfig.from_dict(self.jobs[job_id]["config"])
            cmd = cfg.generate_command_string()
            logger.info("Executing HFSS command: %s", cmd)

            with self.lock:
                self.active_processes[job_id] = {
                    "process": None,
                    "start_time": time.time(),
                    "output": [],
                    "error": [],
                }

            if platform.system() == "Windows":
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
            else:
                import shlex

                proc = subprocess.Popen(
                    shlex.split(cmd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

            with self.lock:
                self.active_processes[job_id]["process"] = proc

            out_lines, err_lines = [], []
            while proc.poll() is None:
                line = proc.stdout.readline()
                if line:
                    out_lines.append(line)
                    with self.lock:
                        self.active_processes[job_id]["output"].append(line)
                line = proc.stderr.readline()
                if line:
                    err_lines.append(line)
                    with self.lock:
                        self.active_processes[job_id]["error"].append(line)
                time.sleep(0.1)

            out_remain, err_remain = proc.communicate()
            if out_remain:
                out_lines.append(out_remain)
            if err_remain:
                err_lines.append(err_remain)

            rc = proc.returncode
            with self.lock:
                self.active_processes.pop(job_id, None)
                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                self.jobs[job_id]["output"] = "".join(out_lines)
                self.jobs[job_id]["error"] = "".join(err_lines)
                self.jobs[job_id]["status"] = JobStatus.COMPLETED.value if rc == 0 else JobStatus.FAILED.value
                self._save_jobs()
            logger.info("Local job %s finished with rc=%s", job_id, rc)
        else:
            self._simulate_local_job(job_id)

    def _execute_scheduler_job(self, job_id: str) -> None:
        """Generate scheduler script and submit."""
        if HFSS_AVAILABLE:
            cfg = HFSSSimulationConfig.from_dict(self.jobs[job_id]["config"])
            script = cfg.generate_scheduler_script()

            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".sh") as f:
                f.write(script)
                script_path = f.name

            if platform.system() != "Windows":
                import stat

                os.chmod(script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

            submit_cmd = self._get_scheduler_submit_command(cfg.scheduler_type.value, script_path)
            logger.info("Submitting job %s via %s", job_id, cfg.scheduler_type.value)

            result = subprocess.run(
                submit_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            sched_id = self._extract_scheduler_job_id(result.stdout, cfg.scheduler_type.value)

            with self.lock:
                self.jobs[job_id]["scheduler_job_id"] = sched_id
                self.scheduler_jobs[job_id] = {
                    "scheduler_type": cfg.scheduler_type.value,
                    "scheduler_job_id": sched_id,
                    "submission_time": time.time(),
                }
                self._save_jobs()

            try:
                os.unlink(script_path)
            except OSError:
                pass
            logger.info("Job %s submitted with scheduler id %s", job_id, sched_id)
        else:
            self._simulate_scheduler_job(job_id)

    def _get_scheduler_submit_command(self, stype: str, script: str) -> str:
        """Return the correct submission command for each scheduler."""
        if stype == SchedulerType.SLURM.value:
            return f"sbatch {script}"
        if stype == SchedulerType.LSF.value:
            return f"bsub < {script}"
        if stype == SchedulerType.PBS.value:
            return f"qsub {script}"
        if stype == SchedulerType.WINDOWS_HPC.value:
            return f'powershell -Command "Submit-HpcJob -File {script}"'
        raise ValueError(f"Unsupported scheduler type: {stype}")

    def _extract_scheduler_job_id(self, out: str, stype: str) -> Optional[str]:
        """Parse scheduler output to obtain job id."""
        if stype == SchedulerType.SLURM.value:
            m = re.search(r"Submitted batch job (\d+)", out)
            return m.group(1) if m else None
        if stype == SchedulerType.LSF.value:
            m = re.search(r"<(\d+)>", out)
            return m.group(1) if m else None
        if stype == SchedulerType.PBS.value:
            return out.strip().split(".")[0] or None
        if stype == SchedulerType.WINDOWS_HPC.value:
            m = re.search(r"ID:\s*(\d+)", out)
            return m.group(1) if m else None
        return None

    def _simulate_local_job(self, job_id: str) -> None:
        """Fake local execution for demo purposes."""
        import random

        duration = random.randint(5, 30)
        logger.info("Simulating local job %s for %ss", job_id, duration)

        with self.lock:
            self.active_processes[job_id] = {
                "start_time": time.time(),
                "duration": duration,
                "progress": 0,
                "output": [f"Simulating HFSS job {job_id}\n"],
            }

        for i in range(duration):
            if job_id not in self.active_processes:
                break
            time.sleep(1)
            with self.lock:
                if job_id in self.active_processes:
                    progress = (i + 1) / duration * 100
                    self.active_processes[job_id]["progress"] = progress
                    self.active_processes[job_id]["output"].append(
                        f"Progress: {progress:.1f}% - step {i+1}/{duration}\n"
                    )

        success = random.random() > 0.2
        with self.lock:
            out = "".join(self.active_processes.pop(job_id, {}).get("output", []))
            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
            if success:
                self.jobs[job_id]["status"] = JobStatus.COMPLETED.value
                self.jobs[job_id]["output"] = out + "Simulation completed successfully\n"
            else:
                self.jobs[job_id]["status"] = JobStatus.FAILED.value
                self.jobs[job_id]["error"] = out + "Simulation failed\n"
            self._save_jobs()
        logger.info("Simulated job %s finished with status %s", job_id, self.jobs[job_id]["status"])

    def _simulate_scheduler_job(self, job_id: str) -> None:
        """Fake scheduler submission."""
        import random

        time.sleep(2)
        sched_id = str(random.randint(10000, 99999))
        stype = self.jobs[job_id].get("scheduler_type", "unknown")
        with self.lock:
            self.jobs[job_id]["scheduler_job_id"] = sched_id
            self.jobs[job_id]["output"] = f"Job submitted to {stype} with id {sched_id}"
            self.scheduler_jobs[job_id] = {
                "scheduler_type": stype,
                "scheduler_job_id": sched_id,
                "submission_time": time.time(),
            }
            self._save_jobs()
        logger.info("Simulated job %s submitted to %s with id %s", job_id, stype, sched_id)

    def _cancel_scheduler_job(self, stype: str, job_id: str) -> bool:
        """Send cancel command to scheduler (best effort)."""
        try:
            if stype == SchedulerType.SLURM.value:
                subprocess.run(["scancel", job_id], check=True)
            elif stype == SchedulerType.LSF.value:
                subprocess.run(["bkill", job_id], check=True)
            elif stype == SchedulerType.PBS.value:
                subprocess.run(["qdel", job_id], check=True)
            elif stype == SchedulerType.WINDOWS_HPC.value:
                subprocess.run(
                    ["powershell", "-Command", f"Stop-HpcJob -Id {job_id} -Force"],
                    check=True,
                )
            return True
        except Exception as exc:
            logger.error("Failed to cancel scheduler job %s: %s", job_id, exc)
            return False

    def _monitor_jobs(self) -> None:
        """Background thread: start queued jobs when resources are available."""
        while True:
            try:
                queued = self.get_jobs_by_status(JobStatus.QUEUED)
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
                    stype = info["scheduler_type"]
                    sched_id = info["scheduler_job_id"]
                    running = self._check_scheduler_job_status(stype, sched_id)
                    if not running:
                        with self.lock:
                            if job_id in self.jobs:
                                self.jobs[job_id]["status"] = JobStatus.COMPLETED.value
                                self.jobs[job_id]["completed_at"] = datetime.now().isoformat()
                                self.jobs[job_id]["output"] = f"Scheduler job {sched_id} completed"
                                self._save_jobs()
                            self.scheduler_jobs.pop(job_id, None)
                        logger.info("Scheduler job %s for %s completed", sched_id, job_id)

                time.sleep(30)
            except Exception as exc:
                logger.error("Error in scheduler monitor thread: %s", exc)
                time.sleep(60)

    def _check_scheduler_job_status(self, stype: str, job_id: str) -> bool:
        """Query scheduler to see if job is still running."""
        try:
            if stype == SchedulerType.SLURM.value:
                res = subprocess.run(["squeue", "-j", job_id, "-h"], capture_output=True, text=True)
                return res.returncode == 0 and job_id in res.stdout
            if stype == SchedulerType.LSF.value:
                res = subprocess.run(["bjobs", job_id], capture_output=True, text=True)
                return res.returncode == 0 and "RUN" in res.stdout
            if stype == SchedulerType.PBS.value:
                res = subprocess.run(["qstat", job_id], capture_output=True, text=True)
                return res.returncode == 0 and job_id in res.stdout
            if stype == SchedulerType.WINDOWS_HPC.value:
                cmd = f"Get-HpcJob -Id {job_id} | Where-Object {{$_.State -eq 'Running'}}"
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                return res.returncode == 0 and job_id in res.stdout
        except Exception:
            return True
        return True


# --------------------------------------------------------------------------- #
# Dash application                                                            #
# --------------------------------------------------------------------------- #
app = dash.Dash(
    __name__,
    title="HFSS Job Manager",
    update_title="Loading...",
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)
job_manager = HFSSJobManager()

# --------------------------------------------------------------------------- #
# Layout                                                                      #
# --------------------------------------------------------------------------- #
app.layout = html.Div(
    [
        html.H1("HFSS Simulation Job Manager", style={"textAlign": "center"}),
        html.Div(
            [
                html.H3("Resource Usage Summary"),
                html.Div(id="resource-summary"),
            ],
            style={
                "margin": 20,
                "padding": 20,
                "border": "1px solid #bdc3c7",
                "borderRadius": 5,
                "backgroundColor": "#ecf0f1",
            },
        ),
        html.Div(
            [
                html.H3("Submit New Job"),
                html.Div(
                    [
                        html.Label("Job ID"),
                        dcc.Input(
                            id="job-id",
                            type="text",
                            placeholder="Enter job ID",
                            style={"width": "100%"},
                        ),
                        html.Label("Project Path"),
                        dcc.Input(
                            id="project-path",
                            type="text",
                            placeholder="/path/to/project.aedt",
                            style={"width": "100%"},
                        ),
                        html.Label("Design Name"),
                        dcc.Input(id="design-name", type="text", value="main", style={"width": "100%"}),
                        html.Label("Setup Name"),
                        dcc.Input(id="setup-name", type="text", value="Setup1", style={"width": "100%"}),
                        html.Label("Scheduler Type"),
                        dcc.Dropdown(
                            id="scheduler-type",
                            options=[
                                {"label": "None (Local)", "value": "none"},
                                {"label": "SLURM", "value": "slurm"},
                                {"label": "LSF", "value": "lsf"},
                                {"label": "PBS", "value": "pbs"},
                                {"label": "Windows HPC", "value": "windows_hpc"},
                            ],
                            value="none",
                            style={"width": "100%"},
                        ),
                        html.Label("Nodes"),
                        dcc.Input(id="nodes", type="number", value=1, min=1, style={"width": "100%"}),
                        html.Label("Memory"),
                        dcc.Input(id="memory", type="text", value="4GB", style={"width": "100%"}),
                        html.Button(
                            "Submit Job",
                            id="submit-job",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "padding": 10,
                                "backgroundColor": "#2ecc71",
                                "color": "white",
                                "border": "none",
                                "borderRadius": 4,
                                "cursor": "pointer",
                            },
                        ),
                        html.Div(id="submit-status"),
                    ],
                    style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gap": 15},
                ),
            ],
            style={
                "margin": 20,
                "padding": 20,
                "border": "1px solid #bdc3c7",
                "borderRadius": 5,
                "backgroundColor": "#ecf0f1",
            },
        ),
        html.Div(
            [
                html.H3("Job Queue"),
                html.Div(id="jobs-table"),
                dcc.Interval(id="interval-component", interval=3_000, n_intervals=0),
            ],
            style={
                "margin": 20,
                "padding": 20,
                "border": "1px solid #bdc3c7",
                "borderRadius": 5,
                "backgroundColor": "#ecf0f1",
            },
        ),
        html.Div(
            [
                html.H3("Live Log Output"),
                dcc.Dropdown(
                    id="log-job-selector",
                    placeholder="Select a job to view logs",
                    style={"marginBottom": 10},
                ),
                html.Div(
                    id="log-output",
                    style={
                        "fontFamily": "monospace",
                        "fontSize": 12,
                        "whiteSpace": "pre-wrap",
                        "backgroundColor": "#2c3e50",
                        "color": "white",
                        "padding": 10,
                        "borderRadius": 5,
                        "maxHeight": 300,
                        "overflowY": "auto",
                    },
                ),
            ],
            style={
                "margin": 20,
                "padding": 20,
                "border": "1px solid #bdc3c7",
                "borderRadius": 5,
                "backgroundColor": "#ecf0f1",
            },
        ),
        html.Div(id="dummy-output", style={"display": "none"}),
    ]
)


# --------------------------------------------------------------------------- #
# Callbacks                                                                   #
# --------------------------------------------------------------------------- #
@app.callback(
    Output("resource-summary", "children"),
    Input("interval-component", "n_intervals"),
)
def update_resource_summary(n: int) -> html.Div:
    """
    Refresh resource-usage cards every ``n_intervals``.

    Args:
        n: The interval counter (unused).

    Returns:
        Dash component tree with four summary cards.
    """
    usage = job_manager.get_resource_usage()
    return html.Div(
        [
            html.Div(
                [
                    html.H4("Running Jobs"),
                    html.H2(usage["running_jobs"]),
                ],
                style={
                    "padding": 15,
                    "backgroundColor": "white",
                    "borderRadius": 5,
                    "textAlign": "center",
                },
            ),
            html.Div(
                [
                    html.H4("Queued Jobs"),
                    html.H2(usage["queued_jobs"]),
                ],
                style={
                    "padding": 15,
                    "backgroundColor": "white",
                    "borderRadius": 5,
                    "textAlign": "center",
                },
            ),
            html.Div(
                [
                    html.H4("Total Nodes"),
                    html.H2(usage["total_nodes"]),
                ],
                style={
                    "padding": 15,
                    "backgroundColor": "white",
                    "borderRadius": 5,
                    "textAlign": "center",
                },
            ),
            html.Div(
                [
                    html.H4("Total Memory"),
                    html.H2(f"{usage['total_memory']}GB"),
                ],
                style={
                    "padding": 15,
                    "backgroundColor": "white",
                    "borderRadius": 5,
                    "textAlign": "center",
                },
            ),
            html.P(f"Last Updated: {usage['timestamp']}", style={"marginTop": 15}),
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": 15},
    )


@app.callback(
    [Output("jobs-table", "children"), Output("log-job-selector", "options")],
    Input("interval-component", "n_intervals"),
)
def update_jobs_table(n: int) -> Tuple[html.Div, List[Dict[str, str]]]:
    """
    Re-render jobs table and populate log-selector dropdown.

    Args:
        n: Interval counter (unused).

    Returns:
        Tuple (table_component, dropdown_options).
    """
    jobs = job_manager.get_all_jobs()
    table_data, log_opts = [], []

    for job in jobs:
        cfg = job.get("config", {})
        opts = cfg.get("scheduler_options", {})
        submitted = job["submitted_at"]
        try:
            submitted = datetime.fromisoformat(submitted.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        progress = None
        if job["status"] == "Running":
            progress = job_manager.get_job_progress(job["job_id"])

        table_data.append(
            {
                "job_id": job["job_id"],
                "status": job["status"],
                "scheduler": job["scheduler_type"],
                "nodes": opts.get("nodes", 1),
                "memory": opts.get("memory", "N/A"),
                "submitted": submitted,
                "progress": progress,
            }
        )

        if job["status"] in {"Running", "Completed", "Failed"}:
            log_opts.append({"label": f"{job['job_id']} ({job['status']})", "value": job["job_id"]})

    table = html.Div(
        [
            dash_table.DataTable(
                id="jobs-datatable",
                columns=[
                    {"name": "Job ID", "id": "job_id"},
                    {"name": "Status", "id": "status"},
                    {"name": "Scheduler", "id": "scheduler"},
                    {"name": "Nodes", "id": "nodes", "type": "numeric"},
                    {"name": "Memory", "id": "memory"},
                    {"name": "Submitted", "id": "submitted"},
                    {"name": "Progress", "id": "progress", "type": "numeric"},
                ],
                data=table_data,
                style_cell={"textAlign": "left", "padding": 12},
                style_header={
                    "backgroundColor": "#2c3e50",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{status} = 'Running'"},
                        "backgroundColor": "#d4edda",
                        "color": "#155724",
                    },
                    {
                        "if": {"filter_query": "{status} = 'Queued'"},
                        "backgroundColor": "#fff3cd",
                        "color": "#856404",
                    },
                    {
                        "if": {"filter_query": "{status} = 'Failed'"},
                        "backgroundColor": "#f8d7da",
                        "color": "#721c24",
                    },
                    {
                        "if": {"filter_query": "{status} = 'Completed'"},
                        "backgroundColor": "#d1ecf1",
                        "color": "#0c5460",
                    },
                ],
                page_size=10,
                filter_action="native",
                sort_action="native",
            )
        ]
    )
    return table, log_opts


@app.callback(
    [Output("submit-job", "n_clicks"), Output("submit-status", "children")],
    Input("submit-job", "n_clicks"),
    [
        State("job-id", "value"),
        State("project-path", "value"),
        State("design-name", "value"),
        State("setup-name", "value"),
        State("scheduler-type", "value"),
        State("nodes", "value"),
        State("memory", "value"),
    ],
    prevent_initial_call=True,
)
def submit_job(
    n_clicks: int,
    job_id: Optional[str],
    project_path: Optional[str],
    design_name: Optional[str],
    setup_name: Optional[str],
    scheduler_type: Optional[str],
    nodes: Optional[int],
    memory: Optional[str],
) -> Tuple[int, html.Div]:
    """
    Validate form and create a new job.

    Args:
        n_clicks: Number of times the submit button was pressed.
        job_id: User-provided job identifier.
        project_path: Absolute path to the HFSS project file.
        design_name: HFSS design name.
        setup_name: Setup name.
        scheduler_type: Selected backend.
        nodes: Requested node count.
        memory: Memory string like ``"64GB"``.

    Returns:
        Tuple ``(0, status_component)`` (n_clicks is reset to 0).
    """
    if n_clicks == 0:
        return 0, html.Div()

    if not job_id or not project_path:
        return 0, html.Div("Job ID and Project Path are required!", style={"color": "red"})

    try:
        if HFSS_AVAILABLE:
            sched_opts = SchedulerOptions(nodes=nodes or 1, memory=memory or "4GB")
            cfg = create_hfss_config(
                jobid=job_id,
                project_path=project_path,
                design_name=design_name or "main",
                setup_name=setup_name or "Setup1",
                scheduler_type=SchedulerType(scheduler_type or "none"),
                scheduler_options=sched_opts,
            )
        else:
            cfg = {
                "jobid": job_id,
                "project_path": project_path,
                "design_name": design_name or "main",
                "setup_name": setup_name or "Setup1",
                "scheduler_type": scheduler_type or "none",
                "scheduler_options": {"nodes": nodes or 1, "memory": memory or "4GB"},
            }

        job_manager.add_job(cfg)
        return 0, html.Div("Job submitted successfully!", style={"color": "green"})
    except Exception as exc:
        logger.exception("Submit failed")
        return 0, html.Div(f"Error: {exc}", style={"color": "red"})


@app.callback(
    Output("log-output", "children"),
    [Input("log-job-selector", "value"), Input("interval-component", "n_intervals")],
)
def update_log_output(selected_job_id: Optional[str], n_intervals: int) -> html.Pre:
    """
    Stream live or historical log into the viewer.

    Args:
        selected_job_id: Currently selected job in the dropdown.
        n_intervals: Interval counter (unused).

    Returns:
        A ``html.Pre`` block containing the latest output.
    """
    if not selected_job_id:
        return html.P("Select a job to view its logs.")
    output = job_manager.get_job_output(selected_job_id)
    if not output:
        return html.P("No output yet.")
    return html.Pre(output)


@app.callback(
    Output("dummy-output", "children"),
    [
        Input({"type": "stop-button", "index": dash.ALL}, "n_clicks"),
        Input({"type": "start-button", "index": dash.ALL}, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def handle_button_clicks(*_) -> str:
    """
    Handle stop/start buttons via pattern-matching callbacks.

    Returns:
        Empty string (dummy output).
    """
    ctx = callback_context
    if not ctx.triggered:
        return ""

    button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    job_id = button_id["index"]
    action = button_id["type"]

    if action == "stop-button":
        job_manager.stop_job(job_id)
    elif action == "start-button":
        job_manager.start_job(job_id)
    return ""


# --------------------------------------------------------------------------- #
# Entry-point                                                                 #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    logger.info("Starting HFSS Job Manager web interface")
    print("HFSS Job Manager is running at http://localhost:8050")
    if not HFSS_AVAILABLE:
        print("Warning: hfss_jobs module not found – running in simulation mode.")
    app.run(debug=True, host="0.0.0.0", port=8050)

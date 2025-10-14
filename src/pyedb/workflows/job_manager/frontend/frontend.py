# frontend.py
from datetime import datetime
from typing import Dict, Optional

import aiohttp
from nicegui import ui

# ------------------------------------------------------------------
#  Badge helpers for job monitoring
# ------------------------------------------------------------------


def _refresh_badges(job: dict, w: dict):
    """Update text/classes on the *existing* widgets."""
    data = job.get("_cache") or {}
    if not data:  # nothing yet – keep old values
        return

    # Project
    prj = data.get("project", {})
    w["prj"].set_text(prj.get("name", "—"))

    # Init mesh
    init = data.get("init_mesh", {})
    w["init"].set_text(f"{init.get('tetrahedra', 0):,}")

    # Adaptive passes
    ads = data.get("adaptive", [])
    w["pass"].set_text(str(len(ads)))

    if ads:
        latest = ads[-1]
        w["ds"].set_text(f"{latest.get('delta_s', '—'):.4f}" if latest.get("delta_s") else "—")
        w["mem"].set_text(f"{latest.get('memory_mb', 0):.0f} MB")
        w["tet"].set_text(f"{latest.get('tetrahedra', 0):,}")

        conv = data.get("log_parser", {}).get("is_converged", False)
        print("BADGE uses", conv, "from", data.get("log_parser"))  # <-- temporary
        w["conv_bdg"].set_text("Converged" if conv else "Not converged")
        w["conv_bdg"].classes(remove="status-queued status-completed")
        w["conv_bdg"].classes("status-completed" if conv else "status-queued")

    # Sweep
    sw = data.get("sweep", {})
    if sw:
        total = sw.get("frequencies", 0)
        solved = len(sw.get("solved", []))
        w["swp"].set_text(f"{solved}/{total} pts")
    else:
        w["swp"].set_text("—")


def _build_or_refresh_badges(job: dict, frontend: "JobManagerFrontend") -> None:
    """
    Build the badge row INSIDE the current card and start a timer
    that updates the TEXT only – no permanent row reference is kept.
    The timer cancels itself when the job disappears or finishes.
    """

    # ---------- 1.  build row (every rebuild) ----------
    with ui.row().classes("items-center gap-3 mt-2"):
        widgets = {}
        for key, lbl in (
            ("prj", "Project"),
            ("init", "Init tet"),
            ("pass", "Passes"),
            ("ds", "ΔS"),
            ("mem", "Memory"),
            ("tet", "Tetra"),
            ("swp", "Sweep"),
            ("conv", "Status"),
        ):
            with ui.column().classes("items-center"):
                ui.label(lbl).classes("text-2xs text-gray-500")
                widgets[key] = ui.label("—").classes("text-xs font-bold" if key == "prj" else "text-xs")
                if key == "conv":
                    widgets["conv_bdg"] = widgets[key]

    job["_badge_widgets"] = widgets  # keep only the **text** objects
    if "_cache" not in job:
        job["_cache"] = {}

    # 2.  fill with **last known data** immediately
    _refresh_badges(job, widgets)

    # 3.  start/update timer
    _ensure_badge_timer(job, frontend)


def _ensure_badge_timer(job: dict, frontend: "JobManagerFrontend") -> None:
    """Timer refreshes LABELS; cancels itself when card/job vanishes."""
    timer_name = "_badge_timer"

    # cancel previous timer if still running
    old_timer = job.pop(timer_name, None)
    if old_timer:
        old_timer.cancel()

    # ----------  NEW:  one-shot fetch for finished jobs  ----------
    if job.get("status") in ("completed", "failed", "cancelled"):
        # cache still empty?  try to load final log **once**
        if not job.get("_cache"):

            async def _once():
                data = await frontend.fetch_job_log(job["id"])
                if data:
                    job["_cache"] = data
                    _refresh_badges(job, job["_badge_widgets"])

            # schedule it **now** – NiceGUI will run it in the event-loop
            ui.timer(0.1, _once, once=True)
        return

    async def refresh():
        # fetch new log data
        data = await frontend.fetch_job_log(job["id"])
        if data:
            job["_cache"].clear()
            job["_cache"].update(data)

        # update the **text** objects (still alive while card exists)
        _refresh_badges(job, job["_badge_widgets"])

    # NiceGUI timer – automatically dies when the client (tab) is closed
    job[timer_name] = ui.timer(frontend.refresh_period, refresh, active=True)


class JobManagerFrontend:
    def __init__(self, backend_url: str = "http://localhost:8080"):
        self.backend_url = backend_url
        self.jobs = []
        self.resources = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_usage_percent": 0,
            "memory_used_gb": 0,
            "memory_total_gb": 0,
            "disk_free_gb": 0,
            "disk_used_gb": 0,
            "disk_total_gb": 0,
        }
        self.queue_stats = {"total_queued": 0, "running_jobs": 0, "max_concurrent": 2}
        self.partitions = []
        self.system_status = {}
        self.scheduler_type = "none"
        self.auto_refresh = True
        self.refresh_period = 5
        self.job_filter: str = ""  # username or "" (=all)
        self.status_filter: str = "running"
        self.jobs_container = None  # will hold the NiceGUI element
        self.update_jobs_display = None  # will hold the callable

    async def fetch_login(self) -> str:
        """Return the login name of the current session."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/me") as resp:
                    if resp.status == 200:
                        return (await resp.json()).get("username", "unknown")
        except Exception as e:
            print("cannot fetch user:", e)
        return "unknown"

    async def fetch_all_data(self):
        """Fetch all data from backend"""
        await self.fetch_system_status()
        await self.fetch_jobs()
        await self.fetch_resources()
        await self.fetch_queue_stats()
        if self.scheduler_type != "none":
            await self.fetch_partitions()
        else:
            self.partitions = []

    async def fetch_system_status(self):
        """Fetch system status and scheduler type"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/system/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.system_status = data
                        self.scheduler_type = data.get("mode", "local")
        except Exception as e:
            print(f"Error fetching system status: {e}")

    async def fetch_jobs(self):
        """Fetch job list"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/jobs") as response:
                    if response.status == 200:
                        self.jobs = await response.json()
        except Exception as e:
            print(f"Error fetching jobs: {e}")

    async def fetch_resources(self):
        """Fetch resource usage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/resources") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.resources.update(data)
        except Exception as e:
            print(f"Error fetching resources: {e}")

    async def fetch_queue_stats(self):
        """Fetch queue statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/queue") as response:
                    if response.status == 200:
                        new = await response.json()
                        self.queue_stats.update(new)
        except Exception as e:
            print(f"Error fetching queue stats: {e}")

    async def fetch_partitions(self):
        """Fetch cluster partitions"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/scheduler/partitions") as response:
                    if response.status == 200:
                        self.partitions = await response.json()
        except Exception as e:
            print(f"Error fetching partitions: {e}")

    async def submit_job(self, job_data: Dict) -> bool:
        """Submit a new job"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.backend_url}/jobs/submit", json=job_data) as response:
                    if response.status == 200:
                        return True
                    else:
                        return False
        except Exception as e:
            print(f"Error submitting job: {e}")
            return False

    async def cancel_job(self, job_id: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.backend_url}/api/cancel/{job_id}") as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Error cancelling job: {e}")
            return False

    async def fetch_job_log(self, job_id: str) -> Optional[dict]:
        """Return the log dictionary for a single job."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/jobs/{job_id}/log") as resp:
                    if resp.status == 204:  # backend has no content yet
                        return None
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            print(f"Error fetching log for {job_id}: {e}")
            return None


# Setup auto-refresh with robust client validation
def _is_client_valid(container=None) -> bool:
    """Check if the UI client is valid and optionally check container validity."""
    try:
        if not (hasattr(ui, "context") and ui.context.client is not None):
            return False
        if container:
            return (
                hasattr(container, "client") and container.client is not None and container.client == ui.context.client
            )
        return True
    except Exception:
        return False


def safe_fetch_all_data():
    if _is_client_valid():
        return frontend.fetch_all_data()


def safe_update_jobs():
    if _is_client_valid() and hasattr(frontend, "update_jobs_display") and hasattr(frontend, "jobs_container"):
        container = getattr(frontend, "jobs_container", None)
        if _is_client_valid(container):
            frontend.update_jobs_display()


# Create frontend instance
frontend = JobManagerFrontend()


def setup_ui():
    # Custom CSS for modern styling
    modern_css = """
    <style>
    :root {
        --primary: #6366f1;
        --primary-dark: #4338ca;
        --secondary: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --card-border: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }

    body {
        background: linear-gradient(135deg, var(--dark-bg) 0%, #1e1b4b 100%);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    .custom-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        box-shadow:
            0 4px 6px -1px rgba(0, 0, 0, 0.3),
            0 2px 4px -1px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .custom-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 20px 25px -5px rgba(0, 0, 0, 0.4),
            0 10px 10px -5px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }

    .progress-bar {
        background: #334155;
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 8px 0;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
    }

    .stat-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }

    .job-item {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }

    .job-item:hover {
        border-color: var(--primary);
        transform: translateX(4px);
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-queued { background: var(--warning); color: white; }
    .status-running { background: var(--primary); color: white; }
    .status-completed { background: var(--success); color: white; }
    .status-failed { background: var(--error); color: white; }
    .status-cancelled { background: var(--secondary); color: white; }

    .btn-modern {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    .btn-modern:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.4);
    }

    .input-modern {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #334155;
        border-radius: 12px;
        color: var(--text-primary);
        padding: 12px 16px;
        transition: all 0.3s ease;
    }

    .input-modern:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        outline: none;
    }
    </style>
    """

    def create_resource_card(title: str, usage_percent: float, used: str, total: str, color: str = "primary"):
        """Create a modern resource-usage card with auto-refresh controls."""
        with ui.card().classes("custom-card w-full"):
            # ---------- title & gauge ----------
            with ui.row().classes("items-center justify-between w-full"):
                ui.label(title).classes("text-lg font-semibold text-gray-200")
                ui.label(f"{usage_percent:.1f}%").classes("font-mono text-sm text-gray-300")

            with ui.element("div").classes("progress-bar"):
                with ui.element("div").classes("progress-fill") as progress_fill:
                    progress_fill.style(f"width: {usage_percent}%; background: {color};")

            with ui.row().classes("justify-between text-sm w-full"):
                ui.label(f"Used: {used}").classes("text-gray-400")
                ui.label(f"Total: {total}").classes("text-gray-400")

            # Auto-refresh controls
            with ui.row().classes("items-center gap-3 mt-3 w-full"):
                toggle = (
                    ui.button(
                        icon="pause" if frontend.auto_refresh else "play_arrow", on_click=lambda: toggle_refresh()
                    )
                    .props("round dense")
                    .classes("btn-modern")
                    .style("min-width: 32px; min-height: 32px")
                )

                ui.label("Period (s)").classes("text-xs text-gray-400")
                period_inp = ui.number(
                    value=frontend.refresh_period, min=1, max=60, step=1, on_change=lambda: set_period()
                ).classes("input-modern w-16")

                # manual refresh
                ui.button("Refresh", icon="refresh", on_click=frontend.fetch_all_data).classes("btn-modern")

        # ---------- local helpers ----------
        def toggle_refresh():
            frontend.auto_refresh = not frontend.auto_refresh
            toggle.props(f"icon={'pause' if frontend.auto_refresh else 'play_arrow'}")
            _restart_timers()

        def set_period():
            frontend.refresh_period = period_inp.value
            _restart_timers()

        def _restart_timers():
            # cancel old timers
            for timer_attr in ["_fetch_timer", "_update_timer"]:
                if hasattr(frontend, timer_attr):
                    getattr(frontend, timer_attr).cancel()
            # create new ones with new period / state
            if frontend.auto_refresh:
                frontend._fetch_timer = ui.timer(frontend.refresh_period, safe_fetch_all_data)
                frontend._update_timer = ui.timer(frontend.refresh_period, safe_update_jobs)

        return

    def create_job_dialog():
        """Create job submission dialog"""
        with ui.dialog() as dialog, ui.card().classes("custom-card w-full max-w-2xl p-6"):
            ui.label("Submit New Job").classes("text-2xl font-bold mb-6 text-center")

            with ui.column().classes("w-full gap-4"):
                # Project file selection
                with ui.column().classes("w-full"):
                    ui.label("Project File").classes("font-semibold")
                    project_path = ui.input(
                        placeholder="Select project file...",
                        validation={"Please select a valid file": lambda value: len(value) > 0},
                    ).classes("input-modern w-full")

                    def handle_file_selection():
                        """Handle file selection with proper path updating"""
                        ui.run_javascript(f"""
                        const input = document.createElement("input");
                        input.type = "file";
                        input.accept = ".aedt,.aedb";
                        input.onchange = e => {{
                            const file = e.target.files[0];
                            if (file) {{
                                // Update the project path field
                                const pathInput = document.querySelector('input[placeholder="Select project file..."]');
                                if (pathInput) {{
                                    pathInput.value = file.name;
                                    pathInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}

                                // Also dispatch custom event for additional handling
                                const event = new CustomEvent("file-selected", {{
                                    detail: {{ name: file.name, path: file.name }}
                                }});
                                document.dispatchEvent(event);
                            }}
                        }};
                        input.click();
                        """)

                    with ui.row():
                        ui.button("Browse", on_click=handle_file_selection).classes("btn-modern")

                # Scheduler-specific options
                with ui.column().classes("w-full"):
                    ui.label("Compute Resources").classes("font-semibold")

                    if frontend.scheduler_type in ["none", "local"]:
                        # Local execution options
                        with ui.grid(columns=2).classes("w-full gap-4"):
                            cpus = ui.number(label="CPU Cores", value=1, min=1, max=64).classes("input-modern w-full")
                        # Set unused variables to None for consistency
                        nodes = cpus_per_node = tasks_per_node = queue = None
                    else:
                        # Cluster execution options
                        with ui.grid(columns=2).classes("w-full gap-4"):
                            nodes = ui.number(label="Nodes", value=1, min=1, max=100).classes("input-modern w-full")

                            cpus_per_node = ui.number(label="CPUs per Node", value=1, min=1, max=64).classes(
                                "input-modern w-full"
                            )

                            tasks_per_node = ui.number(label="Tasks per Node", value=1, min=1, max=64).classes(
                                "input-modern w-full"
                            )

                            queue = ui.select(
                                label="Queue", options=[p["name"] for p in frontend.partitions], value=None
                            ).classes("input-modern w-full")
                        # Set unused variable to None
                        cpus = None

                # Batch options section
                with ui.expansion("Advanced Batch Options", icon="settings").classes("w-full"):
                    with ui.grid(columns=2).classes("w-full gap-4"):
                        create_starting_mesh = ui.checkbox("Create Starting Mesh").classes("w-full")
                        enable_gpu = ui.checkbox("Enable GPU Acceleration").classes("w-full")
                        solve_adaptive_only = ui.checkbox("Solve Adaptive Only").classes("w-full")
                        validate_only = ui.checkbox("Validate Only").classes("w-full")

                        process_priority = ui.select(
                            label="Process Priority", options=["Normal", "Low", "High", "Idle"], value="Normal"
                        ).classes("input-modern w-full")

                        mpi_vendor = ui.select(
                            label="MPI Vendor", options=["Intel", "Microsoft", "Open MPI"], value="Intel"
                        ).classes("input-modern w-full")

                # Submit button
                async def submit_job_handler():
                    # Generate a unique job ID
                    job_id = f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    # Determine scheduler type
                    scheduler_type_lower = str(frontend.scheduler_type).lower().strip()
                    is_local_mode = scheduler_type_lower in ["none", "local"]

                    # Build the config in HFSSSimulationConfig format
                    job_config = {
                        "config": {
                            "user": frontend.job_filter.lower(),
                            "project_path": project_path.value,
                            "jobid": job_id,
                            "solver": "Hfss3DLayout",
                            "distributed": True,
                            "auto": True,
                            "non_graphical": True,
                            "monitor": True,
                            "design_name": "",
                            "design_mode": "",
                            "setup_name": "",
                            "scheduler_type": "none" if is_local_mode else frontend.scheduler_type.upper(),
                            "layout_options": {
                                "create_starting_mesh": create_starting_mesh.value,
                                "enable_gpu": enable_gpu.value,
                                "solve_adaptive_only": solve_adaptive_only.value,
                                "validate_only": validate_only.value,
                                "default_process_priority": process_priority.value,
                                "mpi_vendor": mpi_vendor.value,
                            },
                        }
                    }

                    if is_local_mode:
                        # Local execution - use machine_nodes only, let backend create default scheduler_options
                        if cpus is not None:
                            job_config["config"]["machine_nodes"] = [
                                {
                                    "hostname": "localhost",
                                    "cores": int(cpus.value),
                                    "max_cores": int(cpus.value),
                                    "utilization": 90,
                                }
                            ]

                            # Don't include scheduler_options for local execution - let backend use defaults
                            # This avoids the Pydantic compatibility issue
                        else:
                            ui.notify("CPU cores field is required for local execution", type="negative")
                            return
                    else:
                        # Cluster execution - use scheduler_options
                        if all(field is not None for field in [nodes, tasks_per_node, cpus_per_node, queue]):
                            job_config["config"]["scheduler_options"] = {
                                "queue": queue.value,
                                "time": "24:00:00",
                                "nodes": int(nodes.value),
                                "tasks_per_node": int(tasks_per_node.value),
                                "cores_per_node": int(cpus_per_node.value),
                                "memory": "4GB",
                                "account": None,
                                "reservation": None,
                                "qos": None,
                                "constraints": None,
                                "exclusive": False,
                                "gpus": 0,
                                "gpu_type": None,
                                "priority": "Normal",
                                "email_notification": None,
                                "run_as_administrator": False,
                            }
                        else:
                            ui.notify("All cluster fields are required for cluster execution", type="negative")
                            return

                    success = await frontend.submit_job(job_config)
                    if success:
                        # 1. optimistic local insert for instant feedback
                        new_job = {
                            "id": job_id,
                            "status": "queued",
                            "config": job_config["config"],
                            "start_time": None,
                            "end_time": None,
                            "_cache": {},
                            "user": frontend.job_filter.lower(),
                        }
                        frontend.jobs.insert(0, new_job)

                        # 2. draw it NOW
                        safe_update_jobs()

                        # 3. ----------  NEW  ----------  authoritative list from server
                        await frontend.fetch_jobs()  # re-fetch /api/jobs
                        safe_update_jobs()  # re-draw (keeps UI identical to server)
                        # ----------------------------------------------

                        ui.notify("Job submitted successfully!", type="positive")
                        dialog.close()
                    else:
                        ui.notify("Failed to submit job", type="negative")

                ui.button("Submit Job", on_click=submit_job_handler).classes("btn-modern w-full mt-4")

        return dialog

    def create_header(job_dialog):
        """Create application header with stats and controls"""
        with ui.header().classes(
            "bg-gradient-to-r from-blue-900/80 to-purple-900/80 backdrop-blur-md border-b border-white/10"
        ):
            with ui.row().classes("items-center justify-between w-full p-4"):
                # Left side - Logo and Submit Job button
                with ui.row().classes("items-center gap-4"):
                    ui.icon("work", size="2rem").classes("text-blue-400")
                    ui.label("ANSYS Job Manager").classes("text-2xl font-bold text-white")

                    # Submit Job button
                    ui.button("Submit New Job", icon="add_circle", on_click=lambda: job_dialog.open()).classes(
                        "btn-modern ml-4"
                    )

                # Center - Stats with improved styling
                with ui.row().classes("items-center gap-8"):
                    # Jobs in Queue
                    with ui.card().classes("bg-blue-900/30 border-blue-500/20 px-4 py-2 rounded-lg"):
                        with ui.column().classes("items-center gap-1"):
                            ui.label().bind_text_from(frontend.queue_stats, "total_queued").classes(
                                "text-2xl font-bold text-blue-400"
                            )
                            ui.label("In Queue").classes("text-xs text-blue-300 font-medium")

                    # Running Jobs
                    with ui.card().classes("bg-green-900/30 border-green-500/20 px-4 py-2 rounded-lg"):
                        with ui.column().classes("items-center gap-1"):
                            ui.label().bind_text_from(frontend.queue_stats, "running_jobs").classes(
                                "text-2xl font-bold text-green-400"
                            )
                            ui.label("Running").classes("text-xs text-green-300 font-medium")

                    # Max Concurrent with edit button
                    with ui.card().classes("bg-orange-900/30 border-orange-500/20 px-4 py-2 rounded-lg"):
                        with ui.column().classes("items-center gap-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.label().bind_text_from(frontend.queue_stats, "max_concurrent").classes(
                                    "text-2xl font-bold text-orange-400"
                                )
                                ui.button(icon="edit", on_click=lambda: edit_max_concurrent()).classes(
                                    "bg-orange-500/20 hover:bg-orange-500/40 text-orange-300 rounded-full p-1 "
                                    "transition-all"
                                ).style("min-width: 28px; min-height: 28px")
                            ui.label("Max Concurrent").classes("text-xs text-orange-300 font-medium")

                # Right side - Scheduler status and refresh
                with ui.row().classes("items-center gap-4"):
                    # Scheduler status badge
                    scheduler_color = {"none": "bg-green-500", "slurm": "bg-blue-500", "lsf": "bg-orange-500"}.get(
                        frontend.scheduler_type, "bg-gray-500"
                    )

                    with ui.badge(color=scheduler_color).classes("px-3 py-1"):
                        ui.label(f"Scheduler: {frontend.scheduler_type.upper()}").classes(
                            "text-white text-sm font-semibold"
                        )

                    # Refresh button
                    ui.button("Refresh", icon="refresh", on_click=frontend.fetch_all_data).classes("btn-modern")

        def edit_max_concurrent():
            """Dialog to edit max concurrent jobs"""
            with ui.dialog() as dialog, ui.card().classes("custom-card p-6"):
                ui.label("Edit Max Concurrent Jobs").classes("text-xl font-bold mb-4")

                current_value = frontend.queue_stats.get("max_concurrent", 1)
                new_value = ui.number(label="Max Concurrent Jobs", value=current_value, min=1, max=100).classes(
                    "input-modern w-full"
                )

                with ui.row().classes("gap-4 mt-4"):
                    ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white")

                    async def save_max_concurrent():
                        new_limit = int(new_value.value)
                        async with aiohttp.ClientSession() as session:
                            resp = await session.put(
                                f"{frontend.backend_url}/pool/limits", json={"max_concurrent_jobs": new_limit}
                            )
                            if resp.status == 200:
                                ui.notify(f"Max concurrent set to {new_limit}", type="positive")
                                dialog.close()
                            else:
                                text = await resp.text()
                                ui.notify(f"Failed to update limit: {text}", type="negative")

                    ui.button("Save", on_click=save_max_concurrent).classes("btn-modern")

            dialog.open()

    def create_main_dashboard(job_dialog):
        """Create main dashboard with exact ASCII layout:

        Local resources      |      job filter       |   cluster Partitions
                             |      job queue        |
        """
        with ui.column().classes("w-full p-4"):
            # 20-unit grid → 4  |  12  |  4
            with ui.grid(columns=20).classes("w-full gap-4"):
                # ------------------------------------------------------------------
                # Column 1 : Local Resources  (4 units)
                # ------------------------------------------------------------------
                with ui.column().classes("col-span-4"):
                    with ui.card().classes("custom-card w-full"):
                        ui.label("Local Resources").classes("text-base font-bold mb-3")
                        # CPU
                        with ui.card().classes("stat-card"):
                            with ui.row().classes("justify-between items-center"):
                                ui.label("CPU").classes("font-semibold text-sm")
                                ui.label().bind_text_from(
                                    frontend.resources, "cpu_percent", lambda x: f"{x:.1f}%" if x else "0%"
                                ).classes("text-sm")
                            ui.linear_progress(show_value=False).bind_value_from(
                                frontend.resources, "cpu_percent", lambda x: x / 100 if x else 0
                            ).classes("w-full")

                        # Memory
                        with ui.card().classes("stat-card"):
                            with ui.row().classes("justify-between items-center"):
                                ui.label("Memory").classes("font-semibold text-sm")
                                ui.label().bind_text_from(
                                    frontend.resources, "memory_used_gb", lambda x: f"{x} GB" if x else "0 GB"
                                ).classes("text-sm")
                            ui.linear_progress(show_value=False).bind_value_from(
                                frontend.resources, "memory_percent", lambda x: x / 100 if x else 0
                            ).classes("w-full")

                        # Disk
                        with ui.card().classes("stat-card"):
                            with ui.row().classes("justify-between items-center"):
                                ui.label("Disk").classes("font-semibold text-sm")
                                ui.label().bind_text_from(
                                    frontend.resources, "disk_free_gb", lambda x: f"{x} GB free" if x else "0 GB free"
                                ).classes("text-sm")
                            ui.linear_progress(show_value=False).bind_value_from(
                                frontend.resources, "disk_usage_percent", lambda x: x / 100 if x else 0
                            ).classes("w-full")

                        # Auto-refresh mini-card
                        with ui.card().classes("stat-card mt-2"):
                            with ui.row().classes("items-center gap-4"):
                                with ui.column().classes("items-center"):
                                    ui.label("Auto Update").classes("text-2xs text-gray-400 mb-1 mt-3")
                                    toggle = (
                                        ui.button(
                                            icon="play_arrow" if not frontend.auto_refresh else "pause",
                                            on_click=lambda: toggle_refresh(),
                                        )
                                        .props("round dense")
                                        .classes("btn-modern")
                                        .style(
                                            "width:28px; height:28px; min-width:28px; min-height:28px; "
                                            "display:flex; align-items:center; justify-content:center"
                                        )
                                    )

                                with ui.column().classes("items-center mt-6"):
                                    ui.label("Period (s)").classes("text-2xs text-gray-400 leading-none")
                                    ui.label().bind_text_from(frontend, "refresh_period").classes(
                                        "text-xs text-gray-200 leading-none"
                                    )
                                    period_slider = (
                                        ui.slider(
                                            value=frontend.refresh_period,
                                            min=1,
                                            max=30,
                                            step=1,
                                            on_change=lambda: setattr(frontend, "refresh_period", period_slider.value),
                                        )
                                        .classes("w-24 -mt-4")
                                        .style("height:28px")
                                    )

                # ------------------------------------------------------------------
                # Column 2 : Job Filter + Job Queue  (12 units)
                # ------------------------------------------------------------------
                with ui.column().classes("col-span-12"):
                    # Filter card
                    with ui.card().classes("custom-card w-full mb-4"):
                        ui.label("Filter Jobs").classes("text-base font-bold mb-2")
                        with ui.row().classes("items-center gap-3"):
                            ui.label("User:").classes("text-sm text-gray-300")
                            user_select = (
                                ui.select(options=["*"], value="*")
                                .props("dense outlined hide-bottom-space")
                                .classes("w-40")
                            )

                            async def refresh_user_list():
                                # ensure login name is in the list even when 0 jobs
                                login = await frontend.fetch_login()
                                users = sorted({j.get("user") or "" for j in frontend.jobs if j.get("user")})
                                all_users = ["*"] + [u for u in users if u != login] + [login]
                                user_select.set_options(all_users)
                                # pick default only once
                                if not frontend.job_filter:
                                    frontend.job_filter = login
                                user_select.value = frontend.job_filter

                            user_select.on(
                                "update:model-value",
                                lambda e: setattr(frontend, "job_filter", e.args.lower() if e.args else ""),
                            )
                            ui.button("⟳", on_click=refresh_user_list).props("round dense flat size=lm").classes(
                                "bg-primary/20 text-primary"
                            ).style("height: 28px; width: 28px; min-height: 28px; min-width: 28px")

                        # fire once immediately so the queue is filtered on first paint
                        ui.timer(0.1, refresh_user_list, once=True)

                    # Job Queue card (inline version)
                    create_jobs_section_inline()

                # ------------------------------------------------------------------
                # Column 3 : Cluster Partitions  (4 units)
                # ------------------------------------------------------------------
                with ui.column().classes("col-span-4"):
                    with ui.card().classes("custom-card w-full"):
                        ui.label("Cluster Partitions").classes("text-base font-bold mb-3")
                        with ui.column().classes("w-full gap-2"):
                            if frontend.partitions:
                                for partition in frontend.partitions:
                                    with ui.card().classes("stat-card"):
                                        with ui.row().classes("justify-between items-center"):
                                            ui.label(partition.get("name", "Unknown")).classes("font-semibold text-sm")
                                            ui.label(
                                                f"{partition.get('cores_used', 0)}/{partition.get('cores_total', 1)}"
                                            ).classes("text-xs")

                                        ui.linear_progress().bind_value_from(
                                            partition,
                                            lambda p=partition: p.get("cores_used", 0)
                                            / max(p.get("cores_total", 1), 1),
                                        ).classes("w-full mb-1")

                                        with ui.row().classes("justify-between text-xs"):
                                            ui.label("Mem:")
                                            ui.label().bind_text_from(
                                                partition,
                                                lambda p=partition: f"{p.get('memory_used_gb', 0):.0f}/"
                                                f"{p.get('memory_total_gb', 0):.0f} GB",
                                            )
                            else:
                                ui.label("No partitions available").classes("text-gray-500 text-center p-2 text-sm")

    def create_jobs_section_inline():
        with ui.card().classes("custom-card h-full w-full"):
            ui.label("Job Queue").classes("text-lg font-bold mb-3")

            with ui.element("div").classes("w-full overflow-y-auto") as jobs_container:

                def update_jobs_display():
                    try:
                        if not _is_client_valid(jobs_container):
                            return

                        jobs_container.clear()
                        visible_jobs = [
                            j
                            for j in frontend.jobs
                            if not frontend.job_filter
                            or frontend.job_filter == "*"
                            or (j.get("user") or "").lower() == frontend.job_filter.lower()
                        ]
                        with jobs_container:
                            if visible_jobs:
                                for job in visible_jobs:
                                    with ui.card().classes("job-item w-full mb-2"):
                                        # ----------  header row  ----------
                                        with ui.row().classes("items-center justify-between w-full"):
                                            with ui.column().classes("gap-1 flex-1"):
                                                ui.label(job.get("id", "Unknown")).classes("font-semibold text-sm")
                                                ui.label(
                                                    f"Design: {job.get('config', {}).get('design_name', 'N/A')}"
                                                ).classes("text-xs text-gray-400")

                                            status = job.get("status", "unknown")
                                            status_color = {
                                                "queued": "status-queued",
                                                "running": "status-running",
                                                "completed": "status-completed",
                                                "failed": "status-failed",
                                                "cancelled": "status-cancelled",
                                            }.get(status, "status-queued")

                                            with ui.row().classes("items-center gap-2"):
                                                ui.label(status).classes(f"status-badge {status_color}")

                                                if status in ["queued", "running"]:
                                                    ui.button(
                                                        icon="cancel",
                                                        on_click=lambda j=job: frontend.cancel_job(j["id"]),
                                                    ).classes("bg-red-500 hover:bg-red-600 text-white p-1").style(
                                                        "min-width: 28px; min-height: 28px"
                                                    )

                                        # ----------  badge row (kept inside this card)  ----------
                                        _build_or_refresh_badges(job, frontend)

                                        # ----------  optional timings  ----------
                                        if job.get("start_time") or job.get("end_time"):
                                            with ui.column().classes("text-right text-xs text-gray-400 mt-2"):
                                                if job.get("start_time"):
                                                    ui.label(f"Started: {job['start_time'][:10]}")
                            else:
                                with ui.column().classes("w-full h-full items-center justify-center"):
                                    ui.icon("inbox", size="3rem").classes("text-gray-400 mb-4")
                                    ui.label("No jobs in queue").classes("text-gray-500 text-center text-lg")
                                    ui.label("Submit a new job to get started").classes(
                                        "text-gray-400 text-center text-sm"
                                    )
                    except Exception as e:
                        if "client this element belongs to has been deleted" in str(e):
                            return
                        else:
                            print(f"Error in update_jobs_display: {e}")

                frontend.jobs_container = jobs_container
                frontend.update_jobs_display = update_jobs_display

    # Main application
    @ui.page("/")
    def main_page():
        # JavaScript for file selection
        file_selection_js = """
        document.addEventListener("file-selected", (e) => {
            // This would need to be connected to a specific input element
            // For now, it's a placeholder for file selection functionality
            console.log("File selected:", e.detail);
        });
        """
        # Add custom CSS
        ui.add_head_html(modern_css)
        ui.add_body_html(f"<script>{file_selection_js}</script>")

        # Create job dialog
        job_dialog = create_job_dialog()

        # Main layout
        create_header(job_dialog)
        create_main_dashboard(job_dialog)

        with ui.footer().classes("bg-gray-800 h-8"):
            ui.label("Footer")

        # Per-client -> browser tab closed, reload
        client = ui.context.client
        # 1. create timers RIGHT NOW for this client
        ui.timer(frontend.refresh_period, safe_fetch_all_data)
        ui.timer(frontend.refresh_period, safe_update_jobs)
        # 2. still register the callback so *new* clients get timers as well
        client.on_connect(
            lambda: (
                ui.timer(frontend.refresh_period, safe_fetch_all_data),
                ui.timer(frontend.refresh_period, safe_update_jobs),
            )
        )

        # ----------  NEW – one-shot fetch of real login  ----------
        async def init_login():
            frontend.job_filter = (await frontend.fetch_login()).lower()

        ui.timer(0.1, init_login, once=True)


if __name__ in {"__main__", "__mp_main__"}:
    setup_ui()
    ui.run(
        title="ANSYS Job Manager",
        favicon="💼",
        dark=True,
        reload=False,
        port=8082,
        native=False,  # Set to True for desktop app feel
    )

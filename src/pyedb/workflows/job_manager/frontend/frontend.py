# frontend.py
from nicegui import ui, app
from nicegui.elements.mixins.value_element import ValueElement
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import time


class JobManagerFrontend:
    def __init__(self, backend_url: str = "http://localhost:8080"):
        self.backend_url = backend_url
        self.jobs = []
        self.resources = {}
        self.queue_stats = {}
        self.partitions = []
        self.system_status = {}
        self.scheduler_type = "none"

        # Setup auto-refresh
        self.setup_auto_refresh()

    def setup_auto_refresh(self):
        """Setup periodic data refresh"""

        async def refresh_data():
            while True:
                try:
                    await self.fetch_all_data()
                except Exception as e:
                    print(f"Error refreshing data: {e}")
                await asyncio.sleep(2)  # Refresh every 2 seconds

        # Start background task
        asyncio.create_task(refresh_data())

    async def fetch_all_data(self):
        """Fetch all data from backend"""
        await self.fetch_system_status()
        await self.fetch_jobs()
        await self.fetch_resources()
        await self.fetch_queue_stats()
        if self.scheduler_type != "none":
            await self.fetch_partitions()

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
                async with session.get(f"{self.backend_url}/jobs") as response:
                    if response.status == 200:
                        self.jobs = await response.json()
        except Exception as e:
            print(f"Error fetching jobs: {e}")

    async def fetch_resources(self):
        """Fetch resource usage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/resources") as response:
                    if response.status == 200:
                        self.resources = await response.json()
        except Exception as e:
            print(f"Error fetching resources: {e}")

    async def fetch_queue_stats(self):
        """Fetch queue statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/queue") as response:
                    if response.status == 200:
                        self.queue_stats = await response.json()
        except Exception as e:
            print(f"Error fetching queue stats: {e}")

    async def fetch_partitions(self):
        """Fetch cluster partitions"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/scheduler/partitions") as response:
                    if response.status == 200:
                        self.partitions = await response.json()
        except Exception as e:
            print(f"Error fetching partitions: {e}")

    async def submit_job(self, job_data: Dict) -> bool:
        """Submit a new job"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.backend_url}/jobs/submit",
                        json=job_data
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error submitting job: {e}")
            return False

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.backend_url}/jobs/{job_id}/cancel"
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error cancelling job: {e}")
            return False


# Create frontend instance
frontend = JobManagerFrontend()

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
    """Create a modern resource usage card"""
    with ui.card().classes('custom-card w-full'):
        with ui.row().classes('items-center justify-between w-full'):
            ui.label(title).classes('text-lg font-semibold text-gray-200')
            ui.label(f"{usage_percent:.1f}%").classes('font-mono text-sm text-gray-300')

        # Progress bar
        with ui.element('div').classes('progress-bar'):
            with ui.element('div').classes('progress-fill') as progress_fill:
                progress_fill.style(f'width: {usage_percent}%; background: {color};')

        with ui.row().classes('justify-between text-sm w-full'):
            ui.label(f"Used: {used}").classes('text-gray-400')
            ui.label(f"Total: {total}").classes('text-gray-400')


def create_job_dialog():
    """Create job submission dialog"""
    with ui.dialog() as dialog, ui.card().classes('custom-card w-full max-w-2xl p-6'):
        ui.label('Submit New Job').classes('text-2xl font-bold mb-6 text-center')

        with ui.column().classes('w-full gap-4'):
            # Project file selection
            with ui.column().classes('w-full'):
                ui.label('Project File').classes('font-semibold')
                project_path = ui.input(
                    placeholder='Select project file...',
                    validation={'Please select a valid file': lambda value: len(value) > 0}
                ).classes('input-modern w-full')

                with ui.row():
                    ui.button('Browse', on_click=lambda: ui.run_javascript('''
                        const input = document.createElement("input");
                        input.type = "file";
                        input.accept = ".aedt,.aedb";
                        input.onchange = e => {
                            const file = e.target.files[0];
                            if (file) {
                                // In a real app, you'd upload this file
                                // For now, we'll just set the path
                                const event = new CustomEvent("file-selected", { 
                                    detail: file.name 
                                });
                                document.dispatchEvent(event);
                            }
                        };
                        input.click();
                    ''')).classes('btn-modern')

            # Scheduler-specific options
            with ui.column().classes('w-full'):
                ui.label('Compute Resources').classes('font-semibold')

                if frontend.scheduler_type == "none":
                    # Local execution options
                    with ui.grid(columns=2).classes('w-full gap-4'):
                        cpus = ui.number(
                            label='CPU Cores',
                            value=1,
                            min=1,
                            max=64
                        ).classes('input-modern w-full')
                else:
                    # Cluster execution options
                    with ui.grid(columns=2).classes('w-full gap-4'):
                        nodes = ui.number(
                            label='Nodes',
                            value=1,
                            min=1,
                            max=100
                        ).classes('input-modern w-full')

                        cpus_per_node = ui.number(
                            label='CPUs per Node',
                            value=1,
                            min=1,
                            max=64
                        ).classes('input-modern w-full')

                        tasks_per_node = ui.number(
                            label='Tasks per Node',
                            value=1,
                            min=1,
                            max=64
                        ).classes('input-modern w-full')

                        queue = ui.select(
                            label='Queue',
                            options=[p['name'] for p in frontend.partitions],
                            value=None
                        ).classes('input-modern w-full')

            # Batch options section
            with ui.expansion('Advanced Batch Options', icon='settings').classes('w-full'):
                with ui.grid(columns=2).classes('w-full gap-4'):
                    create_starting_mesh = ui.checkbox('Create Starting Mesh').classes('w-full')
                    enable_gpu = ui.checkbox('Enable GPU Acceleration').classes('w-full')
                    solve_adaptive_only = ui.checkbox('Solve Adaptive Only').classes('w-full')
                    validate_only = ui.checkbox('Validate Only').classes('w-full')

                    process_priority = ui.select(
                        label='Process Priority',
                        options=['Normal', 'Low', 'High', 'Idle'],
                        value='Normal'
                    ).classes('input-modern w-full')

                    mpi_vendor = ui.select(
                        label='MPI Vendor',
                        options=['Intel', 'OpenMPI', 'MPICH', 'Default'],
                        value='Default'
                    ).classes('input-modern w-full')

            # Submit button
            async def submit_job_handler():
                job_config = {
                    "config": {
                        "project_path": project_path.value,
                        "scheduler_type": frontend.scheduler_type,
                        "layout_options": {
                            "create_starting_mesh": create_starting_mesh.value,
                            "enable_gpu": enable_gpu.value,
                            "solve_adaptive_only": solve_adaptive_only.value,
                            "validate_only": validate_only.value,
                            "default_process_priority": process_priority.value,
                            "mpi_vendor": mpi_vendor.value
                        }
                    }
                }

                # Add scheduler-specific options
                if frontend.scheduler_type == "none":
                    job_config["config"]["machine_nodes"] = [{
                        "hostname": "localhost",
                        "cores": int(cpus.value),
                        "max_cores": int(cpus.value),
                        "utilization": 90
                    }]
                else:
                    job_config["config"]["scheduler_options"] = {
                        "nodes": int(nodes.value),
                        "tasks_per_node": int(tasks_per_node.value),
                        "cores_per_node": int(cpus_per_node.value),
                        "queue": queue.value
                    }

                success = await frontend.submit_job(job_config)
                if success:
                    ui.notify('Job submitted successfully!', type='positive')
                    dialog.close()
                else:
                    ui.notify('Failed to submit job', type='negative')

            ui.button('Submit Job', on_click=submit_job_handler).classes('btn-modern w-full mt-4')

    return dialog


def create_header():
    """Create application header"""
    with ui.header().classes(
            'bg-gradient-to-r from-blue-900/80 to-purple-900/80 backdrop-blur-md border-b border-white/10'):
        with ui.row().classes('items-center justify-between w-full p-4'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('work', size='2rem').classes('text-blue-400')
                ui.label('ANSYS Job Manager').classes('text-2xl font-bold text-white')

            with ui.row().classes('items-center gap-4'):
                # Scheduler status badge
                scheduler_color = {
                    'none': 'bg-green-500',
                    'slurm': 'bg-blue-500',
                    'lsf': 'bg-orange-500'
                }.get(frontend.scheduler_type, 'bg-gray-500')

                with ui.badge(color=scheduler_color).classes('px-3 py-1'):
                    ui.label(f"Scheduler: {frontend.scheduler_type.upper()}").classes(
                        'text-white text-sm font-semibold')

                # Refresh button
                ui.button('Refresh', icon='refresh', on_click=frontend.fetch_all_data).classes('btn-modern')


def create_main_dashboard():
    """Create main dashboard with resource monitoring"""
    with ui.column().classes('w-full p-6 gap-6'):
        # System Overview Cards
        with ui.grid(columns=4).classes('w-full gap-6'):
            # Queue Status Card
            with ui.card().classes('custom-card'):
                with ui.column().classes('items-center justify-center p-4 gap-2'):
                    ui.icon('queue', size='2rem').classes('text-blue-400')
                    ui.label('Jobs in Queue').classes('text-lg font-semibold')
                    ui.label().bind_text_from(frontend.queue_stats, 'total_queued').classes(
                        'text-3xl font-bold text-blue-400')

            # Running Jobs Card
            with ui.card().classes('custom-card'):
                with ui.column().classes('items-center justify-center p-4 gap-2'):
                    ui.icon('play_arrow', size='2rem').classes('text-green-400')
                    ui.label('Running Jobs').classes('text-lg font-semibold')
                    ui.label().bind_text_from(frontend.queue_stats, 'running_jobs').classes(
                        'text-3xl font-bold text-green-400')

            # Max Concurrent Card
            with ui.card().classes('custom-card'):
                with ui.column().classes('items-center justify-center p-4 gap-2'):
                    ui.icon('speed', size='2rem').classes('text-orange-400')
                    ui.label('Max Concurrent').classes('text-lg font-semibold')
                    ui.label().bind_text_from(frontend.queue_stats, 'max_concurrent').classes(
                        'text-3xl font-bold text-orange-400')

            # Submit Job Card
            with ui.card().classes('custom-card cursor-pointer') as card:
                card.on('click', lambda: job_dialog.open())
                with ui.column().classes('items-center justify-center p-4 gap-2'):
                    ui.icon('add_circle', size='2rem').classes('text-purple-400')
                    ui.label('Submit New Job').classes('text-lg font-semibold text-center')
                    ui.label('Click to open job submission form').classes('text-sm text-gray-400 text-center')

        # Resource Monitoring Section
        with ui.row().classes('w-full gap-6'):
            # Local Resources
            with ui.card().classes('custom-card flex-1'):
                ui.label('Local Resources').classes('text-xl font-bold mb-4')
                with ui.column().classes('w-full gap-4'):
                    # CPU Usage
                    with ui.card().classes('stat-card'):
                        with ui.row().classes('justify-between items-center'):
                            ui.label('CPU Usage').classes('font-semibold')
                            ui.label().bind_text_from(
                                frontend.resources,
                                'cpu_percent',
                                lambda x: f'{x:.1f}%' if x else '0%'
                            )
                        ui.linear_progress().bind_value_from(
                            frontend.resources,
                            'cpu_percent',
                            lambda x: x / 100 if x else 0
                        ).classes('w-full')

                    # Memory Usage
                    with ui.card().classes('stat-card'):
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Memory').classes('font-semibold')
                            ui.label().bind_text_from(
                                frontend.resources,
                                'memory_used_gb',
                                lambda x: f'{x} GB / {frontend.resources.get("memory_total_gb", 0)} GB' if x else '0 GB'
                            )
                        ui.linear_progress().bind_value_from(
                            frontend.resources,
                            'memory_percent',
                            lambda x: x / 100 if x else 0
                        ).classes('w-full')

                    # Disk Usage
                    with ui.card().classes('stat-card'):
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Disk Space').classes('font-semibold')
                            ui.label().bind_text_from(
                                frontend.resources,
                                'disk_free_gb',
                                lambda x: f'{x} GB free' if x else '0 GB free'
                            )
                        ui.linear_progress().bind_value_from(
                            frontend.resources,
                            'disk_usage_percent',
                            lambda x: x / 100 if x else 0
                        ).classes('w-full')

            # Cluster Partitions (if available)
            if frontend.scheduler_type != "none":
                with ui.card().classes('custom-card flex-1'):
                    ui.label('Cluster Partitions').classes('text-xl font-bold mb-4')
                    with ui.column().classes('w-full gap-4'):
                        if frontend.partitions:
                            for partition in frontend.partitions:
                                with ui.card().classes('stat-card'):
                                    with ui.row().classes('justify-between items-center'):
                                        ui.label(partition.get('name', 'Unknown')).classes('font-semibold')
                                        ui.label(
                                            f"{partition.get('cores_used', 0)} / {partition.get('cores_total', 1)} cores").classes(
                                            'text-sm')

                                    # CPU usage
                                    ui.linear_progress().bind_value_from(
                                        partition,
                                        lambda p=partition: p.get('cores_used', 0) / max(p.get('cores_total', 1), 1)
                                    ).classes('w-full mb-2')

                                    # Memory usage
                                    with ui.row().classes('justify-between text-sm'):
                                        ui.label('Memory:')
                                        ui.label().bind_text_from(
                                            partition,
                                            lambda
                                                p=partition: f"{p.get('memory_used_gb', 0):.1f} / {p.get('memory_total_gb', 0):.1f} GB"
                                        )
                        else:
                            ui.label('No partitions available').classes('text-gray-500 text-center p-4')


def create_jobs_section():
    """Create jobs monitoring section"""
    with ui.column().classes('w-full p-6'):
        with ui.card().classes('custom-card w-full'):
            ui.label('Job Queue').classes('text-xl font-bold mb-4')

            # Jobs table
            with ui.element('div').classes('w-full') as jobs_container:
                def update_jobs_display():
                    jobs_container.clear()
                    with jobs_container:
                        if frontend.jobs:
                            for job in frontend.jobs:
                                with ui.card().classes('job-item w-full'):
                                    with ui.row().classes('items-center justify-between w-full'):
                                        with ui.column().classes('gap-1'):
                                            ui.label(job.get('id', 'Unknown')).classes('font-semibold text-lg')
                                            ui.label(
                                                f"Design: {job.get('config', {}).get('design_name', 'N/A')}").classes(
                                                'text-sm text-gray-400')

                                        # Status badge
                                        status = job.get('status', 'unknown')
                                        status_color = {
                                            'queued': 'status-queued',
                                            'running': 'status-running',
                                            'completed': 'status-completed',
                                            'failed': 'status-failed',
                                            'cancelled': 'status-cancelled'
                                        }.get(status, 'status-queued')

                                        with ui.row().classes('items-center gap-4'):
                                            ui.element('span').classes(f'status-badge {status_color}').bind_text_from(
                                                job, 'status')

                                            # Cancel button for running/queued jobs
                                            if status in ['queued', 'running']:
                                                ui.button('Cancel', icon='cancel',
                                                          on_click=lambda j=job: frontend.cancel_job(j['id'])) \
                                                    .classes('bg-red-500 hover:bg-red-600 text-white')

                                        # Job timings
                                        with ui.column().classes('text-right text-sm text-gray-400'):
                                            if job.get('start_time'):
                                                ui.label(f"Started: {job['start_time']}")
                                            if job.get('end_time'):
                                                ui.label(f"Ended: {job['end_time']}")
                        else:
                            ui.label('No jobs in queue').classes('text-gray-500 text-center p-8')

                # Bind the update function to jobs changes
                frontend.jobs_container = jobs_container
                frontend.update_jobs_display = update_jobs_display


# Setup the main application
@ui.page('/')
def main_page():
    # Add custom CSS
    ui.add_head_html(modern_css)

    # Create job dialog
    job_dialog = create_job_dialog()

    # Main layout
    with ui.column().classes('w-full min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900'):
        create_header()

        # Main content area
        with ui.scroll_area().classes('w-full h-screen'):
            create_main_dashboard()
            create_jobs_section()

    # Setup auto-refresh for jobs display
    async def auto_refresh_jobs():
        while True:
            if hasattr(frontend, 'update_jobs_display'):
                frontend.update_jobs_display()
            await asyncio.sleep(2)

    asyncio.create_task(auto_refresh_jobs())


# JavaScript for file selection
file_selection_js = """
document.addEventListener("file-selected", (e) => {
    // This would need to be connected to a specific input element
    // For now, it's a placeholder for file selection functionality
    console.log("File selected:", e.detail);
});
"""

ui.add_body_html(f"<script>{file_selection_js}</script>")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="ANSYS Job Manager",
        favicon="work",
        dark=True,
        reload=False,
        port=8081,
        native=False  # Set to True for desktop app feel
    )
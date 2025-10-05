from datetime import datetime, timedelta
import os
import sys
import tempfile

from backend.job import Job
from backend.job_submission import HFSS3DLayoutBatchOptions
from backend.service import JobStatus
from job_manager import JobManager
import streamlit as st

# Add the backend path to import JobManager
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
# Create mock classes for demonstration
# class JobStatus:
#     PENDING = "pending"
#     RUNNING = "running"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     QUEUED = "queued"
#
#
# class SimulationType:
#     SI_ANALYSIS = "signal_integrity"
#     PI_ANALYSIS = "power_integrity"
#     THERMAL = "thermal"
#     EMI_EMC = "emi_emc"
#     LAYOUT_VERIFICATION = "layout_verification"

# Set page configuration
st.set_page_config(page_title="PyEDB Job Manager", page_icon="🔷", layout="wide", initial_sidebar_state="expanded")

# PREMIUM CORPORATE CSS WITH TRANSPARENCY AND HOVER EFFECTS
st.markdown(
    """
<style>
    :root {
        --synopsys-blue: #0033a0;
        --synopsys-light-blue: #00a3e0;
        --synopsys-orange: #ff6b00;
        --dark-gray: #2c3e50;
        --medium-gray: #546e7a;
        --light-gray: #f8f9fa;
        --border-gray: #e0e0e0;
        --card-bg: rgba(255, 255, 255, 0.95);
    }

    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        min-height: 100vh;
    }

    .header-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem 0;
        border-bottom: 1px solid rgba(0, 51, 160, 0.08);
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
        backdrop-filter: blur(15px);
        padding: 1.75rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        margin-bottom: 0.75rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0033a0, #00a3e0);
    }

    .metric-card:hover {
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
        border-color: rgba(0, 51, 160, 0.2);
    }

    .job-row {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(248, 250, 252, 0.97) 100%);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        margin-bottom: 0.75rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }

    .job-row::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #0033a0, #00a3e0);
        border-radius: 4px 0 0 4px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .job-row:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        border-color: rgba(0, 51, 160, 0.15);
        transform: translateX(4px);
    }

    .job-row:hover::before {
        opacity: 1;
    }

    .status-badge {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.75px;
        border: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .status-running {
        background: linear-gradient(135deg, rgba(0, 163, 224, 0.15) 0%, rgba(0, 123, 255, 0.1) 100%);
        color: #0066cc;
    }

    .status-completed {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.15) 0%, rgba(56, 142, 60, 0.1) 100%);
        color: #2e7d32;
    }

    .status-failed {
        background: linear-gradient(135deg, rgba(211, 47, 47, 0.15) 0%, rgba(198, 40, 40, 0.1) 100%);
        color: #d32f2f;
    }

    .status-pending {
        background: linear-gradient(135deg, rgba(237, 108, 2, 0.15) 0%, rgba(245, 124, 0, 0.1) 100%);
        color: #ed6c02;
    }

    .status-queued {
        background: linear-gradient(135deg, rgba(123, 31, 162, 0.15) 0%, rgba(106, 27, 154, 0.1) 100%);
        color: #7b1fa2;
    }

    .section-title {
        color: #1a202c;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid linear-gradient(90deg, #0033a0, transparent);
        background: linear-gradient(90deg, #0033a0, #00a3e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .job-id {
        font-family: 'SF Mono', 'Monaco', 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #1a202c;
        font-size: 14px;
        letter-spacing: -0.25px;
    }

    .compact-text {
        font-size: 13px;
        color: #718096;
        line-height: 1.5;
        font-weight: 500;
    }

    .priority-high {
        color: #e53e3e;
        font-weight: 700;
        background: rgba(229, 62, 62, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
    }

    .priority-critical {
        color: #c53030;
        font-weight: 800;
        background: rgba(197, 48, 48, 0.15);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
    }

    .priority-normal {
        color: #38a169;
        font-weight: 600;
        background: rgba(56, 161, 105, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
    }

    .form-section {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(248, 250, 252, 0.97) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        position: relative;
    }

    .form-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0033a0, #00a3e0, #ff6b00);
        border-radius: 16px 16px 0 0;
    }

    .batch-option-card {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(0, 51, 160, 0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }

    .batch-option-card:hover {
        background: rgba(255, 255, 255, 0.95);
        border-color: rgba(0, 51, 160, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    /* Hide only specific Streamlit elements */
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}

    /* Keep settings menu visible */
    #MainMenu {visibility: visible !important;}

    .stButton button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #0033a0, #00a3e0);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #00257a, #0080c0);
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize JobManager with error handling
@st.cache_resource
def initialize_job_manager():
    """Initialize the JobManager with proper error handling"""
    try:
        # Initialize database connection
        db_path = os.path.join(tempfile.gettempdir(), "pyedb_jobs.db")
        job_manager = JobManager(database_path=db_path)

        # Test connection
        jobs = job_manager.get_jobs()
        st.success("✅ Backend connected successfully")
        return job_manager
    except Exception as e:
        st.error(f"❌ Failed to initialize JobManager: {str(e)}")
        st.info("Running in demonstration mode with sample data")
        return None


# Initialize session state
if "show_new_job" not in st.session_state:
    st.session_state.show_new_job = False
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0
if "job_manager" not in st.session_state:
    st.session_state.job_manager = initialize_job_manager()


# Helper functions for backend integration
def get_jobs_from_backend():
    """Get jobs from backend with fallback to sample data"""
    if st.session_state.job_manager:
        try:
            jobs = st.session_state.job_manager.get_jobs()
            return jobs
        except Exception as e:
            st.error(f"Error fetching jobs: {e}")

    # Fallback to sample data
    return get_sample_jobs()


def get_sample_jobs():
    """Provide sample jobs when backend is not available"""
    return [
        {
            "job_id": "JOB-2841",
            "name": "Signal Integrity Analysis",
            "project": "Mobile SoC Design",
            "status": "running",
            "start_time": datetime.now() - timedelta(hours=2, minutes=15),
            "submit_time": datetime.now() - timedelta(hours=2, minutes=20),
            "resources": {"nodes": 8, "cpus_per_node": 16},
            "batch_system": "slurm",
            "priority": "high",
        },
        {
            "job_id": "JOB-2840",
            "name": "Power Distribution Network",
            "project": "Server Board Rev. B",
            "status": "completed",
            "start_time": datetime.now() - timedelta(hours=4),
            "completion_time": datetime.now() - timedelta(hours=2, minutes=18),
            "submit_time": datetime.now() - timedelta(hours=4, minutes=5),
            "resources": {"nodes": 12, "cpus_per_node": 8},
            "batch_system": "pbs",
            "priority": "normal",
        },
    ]


def submit_job_to_backend(job_config, project_file):
    """Submit job to backend with proper file handling"""
    if not st.session_state.job_manager:
        st.error("JobManager not initialized - running in demo mode")
        return False

    try:
        # Save uploaded file to temporary location
        if project_file is not None:
            temp_dir = tempfile.mkdtemp()
            project_file_path = os.path.join(temp_dir, project_file.name)
            with open(project_file_path, "wb") as f:
                f.write(project_file.getbuffer())
            job_config["project_file"] = project_file_path

        # Create and submit job
        job = st.session_state.job_manager.create_job(
            name=job_config["name"],
            project=job_config["project"],
            simulation_type=job_config["simulation_type"],
            project_file=job_config.get("project_file"),
            batch_options=job_config.get("hfss_3d_layout_options"),
            resources=job_config["resources"],
            batch_system=job_config["batch_system"],
            priority=job_config["priority"],
        )

        # Submit the job
        success = st.session_state.job_manager.submit_job(job)
        return success

    except Exception as e:
        st.error(f"Failed to submit job: {str(e)}")
        return False


def get_job_actions(job_id, job_status):
    """Get available actions for a job based on its status"""
    actions = []

    if job_status in [JobStatus.PENDING, JobStatus.QUEUED]:
        actions.extend(["start", "delete"])
    elif job_status == JobStatus.RUNNING:
        actions.extend(["stop", "pause", "view_logs"])
    elif job_status == JobStatus.COMPLETED:
        actions.extend(["view_results", "download", "rerun"])
    elif job_status == JobStatus.FAILED:
        actions.extend(["view_logs", "rerun", "delete"])

    return actions


# Header Section with Premium Styling
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown(
        """
    <div class="header-container">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #0033a0 0%, #00257a 100%);
                        border-radius: 12px; display: flex; align-items: center; justify-content: center;
                        color: white; font-weight: 800; font-size: 24px; box-shadow: 0 8px 24px rgba(0, 51, 160, 0.3);
                        border: 2px solid rgba(255, 255, 255, 0.9);">S</div>
            <div>
                <h1 style="color: #1a202c; margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.5px;">
                PyEDB Job Manager</h1>
                <p style="color: #718096; margin: 0; font-size: 1.1rem; font-weight: 500;">Enterprise EDA Workflow
                Management Platform</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown("<div style='text-align: right; padding-top: 2.5rem;'>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", key="header_refresh", use_container_width=True):
        st.session_state.refresh_key += 1
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Dashboard Metrics with Real Data and Premium Cards
jobs_data = get_jobs_from_backend()

# Calculate metrics
total_jobs = len(jobs_data)
completed_jobs = len(
    [j for j in jobs_data if getattr(j, "status", j.get("status")) in ["completed", JobStatus.COMPLETED]]
)
running_jobs = len([j for j in jobs_data if getattr(j, "status", j.get("status")) in ["running", JobStatus.RUNNING]])
failed_jobs = len([j for j in jobs_data if getattr(j, "status", j.get("status")) in ["failed", JobStatus.FAILED]])
pending_jobs = len(
    [
        j
        for j in jobs_data
        if getattr(j, "status", j.get("status")) in ["pending", "queued", JobStatus.PENDING, JobStatus.QUEUED]
    ]
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
    <div class="metric-card">
        <div style="color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 600; text-transform:
        uppercase; letter-spacing: 1px;">Total Jobs</div>
        <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">{total_jobs}</div>
        <div style="color: #38a169; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600;">↑ 12% from last
        week</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card">
        <div style="color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 600; text-transform:
        uppercase; letter-spacing: 1px;">Running</div>
        <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">{running_jobs}</div>
        <div style="color: #0066cc; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600;">Active simulations</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card">
        <div style="color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 600; text-transform:
        uppercase; letter-spacing: 1px;">Completed</div>
        <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">{completed_jobs}</div>
        <div style="color: #38a169; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600;">↑ 8% from last week</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="metric-card">
        <div style="color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 600; text-transform:
        uppercase; letter-spacing: 1px;">Pending</div>
        <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">{pending_jobs}</div>
        <div style="color: #ed6c02; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600;">In queue</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
    <div class="metric-card">
        <div style="color: #718096; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 600; text-transform:
        uppercase; letter-spacing: 1px;">Failed</div>
        <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">{failed_jobs}</div>
        <div style="color: #e53e3e; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600;">Requires attention</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Job Management Section
st.markdown('<div class="section-title">Job Management</div>', unsafe_allow_html=True)

# Search and Action Bar
search_col, filter_col, action_col = st.columns([2, 1, 1])

with search_col:
    search_term = st.text_input("", placeholder="Search jobs by name or ID...", label_visibility="collapsed")

with filter_col:
    status_filter = st.selectbox(
        "Status", ["All", "Running", "Completed", "Failed", "Pending", "Queued"], label_visibility="collapsed"
    )

with action_col:
    if st.button("Create New Job", use_container_width=True, type="primary"):
        st.session_state.show_new_job = True


# Display Jobs with Premium Styling
def format_job_duration(start_time, completion_time):
    """Calculate and format job duration"""
    if not start_time:
        return "--"

    if completion_time and isinstance(completion_time, datetime):
        duration = completion_time - start_time
    elif isinstance(start_time, datetime):
        duration = datetime.now() - start_time
    else:
        return "--"

    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"


# Filter and display jobs with premium styling
filtered_jobs = jobs_data
if search_term:
    filtered_jobs = [
        job
        for job in filtered_jobs
        if search_term.lower() in getattr(job, "name", job.get("name", "")).lower()
        or search_term.lower() in getattr(job, "job_id", job.get("job_id", "")).lower()
    ]

if status_filter != "All":
    filtered_jobs = [job for job in filtered_jobs if getattr(job, "status", job.get("status")) == status_filter.lower()]

if filtered_jobs:
    for job in filtered_jobs:
        # Extract job data with fallbacks for both object and dict types
        job_id = getattr(job, "job_id", job.get("job_id", "Unknown"))
        job_name = getattr(job, "name", job.get("name", "Unknown"))
        project = getattr(job, "project", job.get("project", "Unknown"))
        status = getattr(job, "status", job.get("status", "unknown"))
        priority = getattr(job, "priority", job.get("priority", "normal"))
        batch_system = getattr(job, "batch_system", job.get("batch_system", "local"))

        # Handle timestamps
        start_time = getattr(job, "start_time", job.get("start_time"))
        submit_time = getattr(job, "submit_time", job.get("submit_time"))
        completion_time = getattr(job, "completion_time", job.get("completion_time"))

        # Handle resources
        resources = getattr(job, "resources", job.get("resources", {}))
        nodes = resources.get("nodes", 1) if resources else 1
        cpus_per_node = resources.get("cpus_per_node", 1) if resources else 1

        status_class = f"status-{status}"
        priority_class = f"priority-{priority}"

        # Job row with premium styling
        with st.container():
            st.markdown('<div class="job-row">', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([1.2, 2, 1.5, 1])

            with col1:
                st.markdown(f"<div class='job-id'>{job_id}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>{project}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='{priority_class}'>Priority: {priority.upper()}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(
                    f"<div style='font-weight: 700; font-size: 15px; color: #1a202c; margin-bottom: 8px;'>{job_name}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if submit_time:
                    submit_str = (
                        submit_time.strftime("%Y-%m-%d %H:%M")
                        if isinstance(submit_time, datetime)
                        else str(submit_time)
                    )
                    st.markdown(f"<div class='compact-text'>📅 Submitted: {submit_str}</div>", unsafe_allow_html=True)
                if completion_time:
                    complete_str = (
                        completion_time.strftime("%Y-%m-%d %H:%M")
                        if isinstance(completion_time, datetime)
                        else str(completion_time)
                    )
                    st.markdown(f"<div class='compact-text'>✅ Completed: {complete_str}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>⚡ Batch: {batch_system.upper()}</div>", unsafe_allow_html=True)

            with col3:
                st.markdown(
                    f"<span class='status-badge {status_class}'>{status.upper()}</span>", unsafe_allow_html=True
                )
                if start_time:
                    start_str = (
                        start_time.strftime("%Y-%m-%d %H:%M") if isinstance(start_time, datetime) else str(start_time)
                    )
                    st.markdown(f"<div class='compact-text'>⏱️ Started: {start_str}</div>", unsafe_allow_html=True)

                duration = format_job_duration(start_time, completion_time)
                st.markdown(f"<div class='compact-text'>⏳ Duration: {duration}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='compact-text'>🖥️ {nodes} nodes × {cpus_per_node} CPUs</div>", unsafe_allow_html=True
                )

            with col4:
                # Dynamic actions based on job status
                actions = get_job_actions(job_id, status)

                if "view_logs" in actions:
                    if st.button("Logs", key=f"logs_{job_id}", use_container_width=True):
                        st.session_state.log_job = job_id
                if "view_results" in actions:
                    if st.button("Results", key=f"results_{job_id}", use_container_width=True):
                        st.session_state.results_job = job_id
                if "rerun" in actions:
                    if st.button("Rerun", key=f"rerun_{job_id}", use_container_width=True):
                        # Implement rerun logic
                        st.info(f"Rerunning job {job_id}")

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("No jobs found matching your criteria.")

# New Job Form with Premium Styling
if st.session_state.show_new_job:
    st.markdown("---")
    st.markdown('<div class="section-title">Create New Job</div>', unsafe_allow_html=True)

    with st.form("new_job_form", clear_on_submit=True):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Job Configuration")
            job_name = st.text_input("Job Name*", placeholder="Enter job name")
            project_name = st.text_input("Project Name*", placeholder="Enter project name")
            project_file = st.file_uploader(
                "Project File*",
                type=["aedt", "edb", "json", "py"],
                help="Upload your EDB project file or configuration",
            )

            simulation_type = st.selectbox(
                "Simulation Type*",
                [
                    "Signal Integrity Analysis",
                    "Power Integrity Analysis",
                    "Thermal Analysis",
                    "EMI/EMC Simulation",
                    "Layout Verification",
                    "Parasitic Extraction",
                    "Power Delivery Network",
                    "DC Analysis",
                ],
            )

        with col2:
            st.subheader("⚡ Compute Resources")
            batch_system = st.selectbox(
                "Batch System", ["local", "slurm", "pbs", "lsf", "sge"], help="Select batch system for job submission"
            )

            col2a, col2b = st.columns(2)
            with col2a:
                num_nodes = st.number_input("Number of Nodes", min_value=1, max_value=64, value=1)
            with col2b:
                cpus_per_node = st.number_input("CPUs per Node", min_value=1, max_value=128, value=16)

            walltime = st.text_input("Walltime", value="04:00:00", help="Format: HH:MM:SS")

            priority = st.selectbox("Priority", ["low", "normal", "high", "critical"])

        # HFSS 3D Layout Batch Options with Premium Cards
        st.subheader("🎛️ HFSS 3D Layout Batch Options")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="batch-option-card">', unsafe_allow_html=True)
            st.markdown("**🔄 Mesh & Solver Options**")
            create_starting_mesh = st.checkbox("Create Starting Mesh", value=True)
            solve_adaptive_only = st.checkbox("Solve Adaptive Only", value=False)
            validate_only = st.checkbox("Validate Only", value=False)
            st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="batch-option-card">', unsafe_allow_html=True)
            st.markdown("**🚀 Performance Options**")
            enable_gpu = st.checkbox("Enable GPU Acceleration", value=False)
            mpi_vendor = st.selectbox("MPI Vendor", ["intel", "openmpi", "mpich", "msmpi"])
            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("📝 Additional Configuration")
        additional_args = st.text_area(
            "Additional Arguments",
            placeholder="--option1 value1 --option2 value2",
            help="Additional command line arguments for the simulation",
            height=80,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("🚀 Submit Job", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_new_job = False
                st.rerun()

        if submit_btn:
            if job_name and project_name and project_file is not None:
                try:
                    # Create HFSS 3D Layout Batch Options
                    hfss_options = HFSS3DLayoutBatchOptions(
                        create_starting_mesh=create_starting_mesh,
                        enable_gpu=enable_gpu,
                        mpi_vendor=mpi_vendor,
                        solve_adaptive_only=solve_adaptive_only,
                        validate_only=validate_only,
                    )

                    # Create job configuration
                    job_config = {
                        "name": job_name,
                        "project": project_name,
                        "simulation_type": simulation_type,
                        "priority": priority,
                        "batch_system": batch_system,
                        "resources": {"nodes": num_nodes, "cpus_per_node": cpus_per_node},
                        "walltime": walltime,
                        "hfss_3d_layout_options": hfss_options,
                    }

                    # Submit to backend
                    success = submit_job_to_backend(job_config, project_file)

                    if success:
                        st.success(f"Job '{job_name}' submitted successfully!")
                        st.session_state.show_new_job = False
                        st.rerun()
                    else:
                        st.error("Failed to submit job to backend")

                except Exception as e:
                    st.error(f"Failed to submit job: {str(e)}")
            else:
                st.error("Please fill in all required fields (marked with *) and upload a project file")

# Sidebar with Premium Styling
with st.sidebar:
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 1.5rem; font-weight: 800; color: #1a202c; letter-spacing: 1px; margin-bottom:
        0.5rem;">SNPS</div>
        <div style="font-size: 0.875rem; color: #718096; font-weight: 600;">ENTERPRISE EDA PLATFORM</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### 📊 System Status")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU Usage", "42%", "-2%")
        st.metric("Active Jobs", f"{running_jobs}")
    with col2:
        st.metric("Memory", "68%", "+5%")
        st.metric("Queue", f"{pending_jobs}")

    st.markdown("---")

    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Refresh All", use_container_width=True):
        st.session_state.refresh_key += 1
        st.rerun()

    if st.button("📊 Export Report", use_container_width=True):
        st.success("Job report exported successfully")

    st.markdown("---")

    st.markdown("### ⚙️ Configuration")
    auto_refresh = st.checkbox("Enable auto-refresh", value=False)

    st.markdown("---")

    st.caption(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

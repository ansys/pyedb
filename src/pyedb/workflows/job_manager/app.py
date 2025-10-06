"""
Simplified Streamlit app using backend's scheduler detection
"""

import asyncio
import os
import platform
import time

from backend_client import EnhancedBackendClient
import streamlit as st
from websocket_client import EnhancedBackendClient


class SimplifiedSchedulerUI:
    """UI that simply uses backend's scheduler detection"""

    def __init__(self):
        self.client = EnhancedBackendClient()
        self.system_status = None
        self.ws_manager = None

    # Correct Code ✅
    async def initialize(self):
        """Initialize using backend detection"""
        # The client's initialize method takes no arguments
        await self.client.initialize()
        self.system_status = await self.client.get_system_status()

        # Setup WebSocket
        from websocket_client import EnhancedBackendClient

        self.ws_manager = EnhancedBackendClient()
        # The refresh_callback correctly goes here
        await self.ws_manager.initialize()

    async def refresh_callback(self):
        """Refresh on WebSocket events"""
        st.rerun()

    def render_mode_banner(self):
        """Simple mode indicator"""
        if not self.system_status:
            return

        mode = self.system_status.get("mode", "unknown")

        if mode == "local":
            st.info("🖥️ **Local Mode**: Using JobPoolManager for job execution")
        else:
            scheduler = self.system_status.get("scheduler_detection", {}).get("active_scheduler", "scheduler")
            st.success(f"⚡ **Scheduler Mode**: Using {scheduler.upper()} for job execution")

    def render_pool_status(self):
        """Show local pool status when in local mode"""
        if not self.system_status or "local_pool" not in self.system_status:
            return

        pool_info = self.system_status["local_pool"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Running", pool_info.get("running_jobs", 0))
        with col2:
            st.metric("Queued", pool_info.get("queued_jobs", 0))
        with col3:
            st.metric("Max Concurrent", pool_info.get("max_concurrent", 2))

    def render_job_form(self):
        """Job submission form"""
        st.markdown("### 🚀 Submit New Job")

        self.render_mode_banner()

        with st.form("job_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📋 Job Configuration")
                job_name = st.text_input("Job Name *", placeholder="Enter job name")
                project_name = st.text_input("Project Name *", placeholder="Enter project name")
                project_file = st.file_uploader("Project File *", type=["aedt", "edb", "json", "py"])
                simulation_type = st.selectbox(
                    "Simulation Type *",
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

                # Let backend handle the resource limits based on mode
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    num_nodes = st.number_input("Nodes", min_value=1, max_value=64, value=1)
                with col_res2:
                    cpus_per_node = st.number_input("CPUs per Node", min_value=1, max_value=128, value=16)

                priority = st.selectbox("Priority", ["low", "normal", "high", "critical"])
                walltime = st.text_input("Walltime", value="04:00:00", help="HH:MM:SS format")

            submitted = st.form_submit_button("🚀 Submit Job", type="primary", use_container_width=True)

            if submitted:
                if job_name and project_name and project_file:
                    # The backend will automatically handle local vs scheduler
                    asyncio.create_task(
                        self.submit_job(
                            job_name=job_name,
                            project_name=project_name,
                            project_file=project_file,
                            simulation_type=simulation_type,
                            num_nodes=num_nodes,
                            cpus_per_node=cpus_per_node,
                            priority=priority,
                            walltime=walltime,
                        )
                    )
                else:
                    st.error("Please fill in all required fields and upload a project file")

    async def submit_job(self, **kwargs):
        """Save uploaded file and submit job - this is the core connection logic."""
        try:
            uploaded_file = kwargs.get("project_file")

            # --- Start of Connection Logic ---
            # Create an 'uploads' directory, save the file from memory to the disk,
            # and then update the arguments to send the file's path to the backend.
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            kwargs["project_path"] = os.path.abspath(file_path)
            del kwargs["project_file"]
            # --- End of Connection Logic ---

            with st.spinner("Submitting job..."):
                job_id = await self.client.submit_job_auto(**kwargs)

                if job_id:
                    mode = self.client.get_current_mode()
                    st.success(f"""
                    ✅ Job submitted successfully!
                    **Job ID:** `{job_id}`
                    **Mode:** {mode.title()} Execution
                    """)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to submit job")

        except Exception as e:
            st.error(f"❌ Error submitting job: {e}")


# Main app
async def main():
    st.set_page_config(page_title="PyEDB Job Manager - Simplified", page_icon="🔧", layout="wide")

    st.markdown("# 🔧 PyEDB Job Manager - Scheduler Aware")

    if "ui_controller" not in st.session_state:
        st.session_state.ui_controller = SimplifiedSchedulerUI()
        st.session_state.initialized = False

    ui = st.session_state.ui_controller

    if not st.session_state.initialized:
        with st.spinner("Initializing system..."):
            await ui.initialize()
            st.session_state.initialized = True

    # Sidebar with system info
    with st.sidebar:
        st.markdown("### 🔧 System Info")

        if ui.system_status:
            mode = ui.system_status.get("mode", "unknown")
            scheduler_info = ui.system_status.get("scheduler_detection", {})

            st.metric("Platform", platform.system())
            st.metric("Mode", mode.title())

            if mode == "local":
                st.info("Running in local mode with JobPoolManager")
                ui.render_pool_status()
            else:
                scheduler = scheduler_info.get("active_scheduler", "unknown")
                st.success(f"Using {scheduler.upper()} scheduler")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        ui.render_job_form()

    with col2:
        st.markdown("### 📊 Quick Stats")
        # Add some quick stats here

    # Job list would go here
    st.markdown("### 📋 Job List")
    st.info("Job list implementation would go here")


if __name__ == "__main__":
    asyncio.run(main())

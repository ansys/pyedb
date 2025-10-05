# src/pyedb/workflows/job_manager/app.py
"""
ANSYS EDB Job Manager - Streamlit Application
Main entry point for the job management interface.
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_manager import JobManager
from components.forms import JobSubmissionForm
from components.job_card import JobCard
from components.resource_monitor import ResourceMonitor
from utils.styles import load_custom_css, apply_corporate_styling


class JobManagerApp:
    """Main application class for ANSYS EDB Job Manager"""

    def __init__(self):
        self.job_manager = JobManager()
        self.setup_page()

    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="ANSYS EDB Job Manager",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Load custom styles
        load_custom_css()
        apply_corporate_styling()

    def render_header(self):
        """Render the application header"""
        st.markdown("""
            <div class="main-header">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="font-size: 2.5rem;">⚡</span>
                    <div>
                        <h1 style="margin: 0; color: #002855;">ANSYS EDB Job Manager</h1>
                        <p style="margin: 0; color: #666; font-size: 1.1rem;">
                            Professional Simulation Job Management
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

    def render_sidebar(self):
        """Render the sidebar with quick actions and statistics"""
        with st.sidebar:
            # ANSYS Branding
            st.markdown("""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2 style="color: #002855; margin-bottom: 0;">ANSYS</h2>
                    <p style="color: #666; font-size: 0.9rem; margin: 0;">Engineering Simulation</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔧 Quick Actions")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("📊 Overview", use_container_width=True):
                    st.session_state.show_system_overview = True

            st.markdown("---")

            # Statistics
            st.markdown("### 📈 Statistics")
            jobs = self.job_manager.get_jobs()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Jobs", len(jobs))
                st.metric("Running", len([j for j in jobs if j.status == "Running"]))
            with col2:
                st.metric("Completed", len([j for j in jobs if j.status == "Completed"]))
                st.metric("Success Rate", "94%")

            st.markdown("---")

            # System Info
            st.markdown("### 💻 System Info")
            resources = ResourceMonitor.get_system_resources()
            st.caption(f"CPU: {resources['cpu_percent']}%")
            st.caption(f"Memory: {resources['memory_percent']}%")
            st.caption(f"Disk: {resources['disk_percent']}%")

    def render_job_submission(self):
        """Render the job submission form"""
        st.markdown("### 🚀 New Simulation Job")

        form = JobSubmissionForm()
        submitted_job = form.render()

        if submitted_job:
            job_id = self.job_manager.submit_job(submitted_job)
            st.success(f"✅ Job '{submitted_job.name}' submitted successfully! (ID: {job_id})")
            st.rerun()

    def render_job_list(self):
        """Render the list of jobs"""
        st.markdown("### 📋 Job Queue")

        jobs = self.job_manager.get_jobs()

        if not jobs:
            st.info("📭 No jobs in queue. Submit a new job to get started.")
            return

        # Filter options
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Running", "Pending", "Completed", "Failed"]
            )
        with col2:
            type_filter = st.selectbox(
                "Filter by Type",
                ["All", "Local", "Cluster"]
            )

        # Filter jobs
        filtered_jobs = jobs
        if status_filter != "All":
            filtered_jobs = [j for j in filtered_jobs if j.status == status_filter]
        if type_filter != "All":
            filtered_jobs = [j for j in filtered_jobs if j.type == type_filter]

        # Display jobs
        for job in filtered_jobs:
            job_card = JobCard(job)
            job_card.render()
            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

    def render_resource_monitoring(self):
        """Render the resource monitoring section"""
        st.markdown("### 📊 System Resources")

        # Create three columns for the gauges
        col1, col2, col3 = st.columns(3)

        with col1:
            ResourceMonitor.render_cpu_gauge()

        with col2:
            ResourceMonitor.render_memory_gauge()

        with col3:
            ResourceMonitor.render_disk_gauge()

    def render_main_content(self):
        """Render the main content area"""
        # Two-column layout
        left_col, right_col = st.columns([2, 1])

        with left_col:
            self.render_job_submission()
            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
            self.render_job_list()

        with right_col:
            self.render_resource_monitoring()

            # Recent activity
            st.markdown("### 📝 Recent Activity")
            recent_jobs = self.job_manager.get_jobs()[:5]
            for job in recent_jobs:
                st.caption(f"• {job.name} - {job.status}")

    def run(self):
        """Main application runner"""
        self.render_header()
        self.render_sidebar()
        self.render_main_content()


def main():
    """Application entry point"""
    app = JobManagerApp()
    app.run()


if __name__ == "__main__":
    main()
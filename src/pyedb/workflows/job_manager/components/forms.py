# src/pyedb/workflows/job_manager/components/forms.py
"""
Job submission form components
"""

import streamlit as st
import psutil
from models.job_models import JobRequest


class JobSubmissionForm:
    """Unified form for submitting both local and cluster jobs"""

    def render(self):
        """Render the job submission form"""
        with st.form(key="job_submission_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                job_name = st.text_input(
                    "Job Name *",
                    placeholder="Enter descriptive job name",
                    help="Provide a meaningful name for your simulation job"
                )

                project_file = st.file_uploader(
                    "Project File *",
                    type=['aedt', 'edb', 'zip'],
                    help="Upload your ANSYS project file"
                )

                job_type = st.radio(
                    "Execution Type *",
                    ["Local", "Cluster"],
                    horizontal=True,
                    help="Choose between local machine or cluster execution"
                )

            with col2:
                solver = st.selectbox(
                    "Solver Type *",
                    ["HFSS", "Mechanical", "Icepak", "Maxwell", "Q3D", "SIwave"],
                    help="Select the ANSYS solver"
                )

                priority = st.select_slider(
                    "Priority",
                    options=["Low", "Medium", "High"],
                    value="Medium",
                    help="Set job execution priority"
                )

            # Dynamic form section based on job type
            st.markdown("### ⚙️ Execution Settings")

            if job_type == "Local":
                settings = self._render_local_settings()
            else:
                settings = self._render_cluster_settings()

            # Advanced settings (collapsible)
            with st.expander("Advanced Settings"):
                advanced_col1, advanced_col2 = st.columns(2)
                with advanced_col1:
                    timeout = st.number_input(
                        "Timeout (hours)",
                        min_value=1,
                        max_value=720,
                        value=24,
                        help="Maximum execution time"
                    )
                    retry_attempts = st.number_input(
                        "Retry Attempts",
                        min_value=0,
                        max_value=5,
                        value=0
                    )

                with advanced_col2:
                    email_notifications = st.checkbox("Email Notifications")
                    if email_notifications:
                        email_address = st.text_input("Email Address")

            # Submit button
            submit_col = st.columns([1, 2, 1])[1]
            with submit_col:
                submitted = st.form_submit_button(
                    "🚀 Submit Job",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if self._validate_input(job_name, project_file):
                    job_request = JobRequest(
                        name=job_name,
                        type=job_type,
                        solver=solver,
                        priority=priority,
                        settings=settings
                    )
                    return job_request
                else:
                    return None

            return None

    def _render_local_settings(self):
        """Render settings specific to local jobs"""
        st.info("💻 Local execution will use this machine's resources")

        col1, col2 = st.columns(2)

        with col1:
            max_cores = psutil.cpu_count()
            cores = st.slider(
                "CPU Cores",
                min_value=1,
                max_value=max_cores,
                value=min(4, max_cores),
                help=f"Available cores: {max_cores}"
            )

        with col2:
            st.number_input(
                "Memory Limit (GB)",
                min_value=1,
                max_value=128,
                value=8,
                disabled=True,  # Memory options removed per requirements
                help="Memory management handled automatically"
            )

        return {
            "cores": cores,
            "execution_type": "local"
        }

    def _render_cluster_settings(self):
        """Render settings specific to cluster jobs"""
        st.info("🏢 Cluster execution will use HPC resources")

        col1, col2 = st.columns(2)

        with col1:
            queue = st.selectbox(
                "Queue",
                ["default", "high_mem", "gpu", "express"],
                help="Select cluster queue"
            )

            nodes = st.number_input(
                "Nodes",
                min_value=1,
                max_value=64,
                value=1,
                help="Number of compute nodes"
            )

        with col2:
            cores_per_node = st.number_input(
                "Cores per Node",
                min_value=1,
                max_value=32,
                value=8,
                help="CPU cores per node"
            )

            walltime = st.text_input(
                "Wall Time",
                value="01:00:00",
                help="Maximum execution time (HH:MM:SS)"
            )

        return {
            "queue": queue,
            "nodes": nodes,
            "cores_per_node": cores_per_node,
            "walltime": walltime,
            "execution_type": "cluster"
        }

    def _validate_input(self, job_name, project_file):
        """Validate form input"""
        if not job_name.strip():
            st.error("❌ Please enter a job name")
            return False

        if not project_file:
            st.error("❌ Please upload a project file")
            return False

        return True
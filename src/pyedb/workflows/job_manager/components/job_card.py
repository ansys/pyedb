# src/pyedb/workflows/job_manager/components/job_card.py
"""
Job card component for displaying job information
"""

import streamlit as st
from models.job_models import Job


class JobCard:
    """Component for displaying job information in a card layout"""

    def __init__(self, job: Job):
        self.job = job

    def render(self):
        """Render the job card"""
        status_config = {
            "Running": {"color": "#10b981", "icon": "🟢"},
            "Completed": {"color": "#3b82f6", "icon": "✅"},
            "Failed": {"color": "#ef4444", "icon": "❌"},
            "Pending": {"color": "#f59e0b", "icon": "🟡"},
            "Cancelled": {"color": "#6b7280", "icon": "⚫"}
        }

        config = status_config.get(self.job.status, status_config["Pending"])

        # Create a professional card layout
        with st.container():
            st.markdown(f"""
                <div class="job-card" style="
                    border-left: 4px solid {config['color']};
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 0.5rem 0;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <h4 style="margin: 0; color: #002855;">{self.job.name}</h4>
                                <span style="font-size: 0.9em; color: #666;">{config['icon']}</span>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em; color: #666;">
                                <div>ID: {self.job.id}</div>
                                <div>Type: {self.job.type}</div>
                                <div>Solver: {self.job.solver}</div>
                                <div>Priority: {self.job.priority}</div>
                                <div colspan="2">Submitted: {self.job.submitted_date[:16]}</div>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: end; gap: 8px;">
                            <div style="
                                background-color: {config['color']};
                                color: white;
                                padding: 4px 12px;
                                border-radius: 12px;
                                font-size: 0.8em;
                                font-weight: 500;
                            ">
                                {self.job.status}
                            </div>
                            <div style="display: flex; gap: 4px;">
                                <button class="card-button" onclick="alert('Details for {self.job.id}')">
                                    📊
                                </button>
                                <button class="card-button" onclick="alert('Cancel {self.job.id}')">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Note: The button functionality would need JavaScript for full implementation
# For Streamlit, we'd use st.button with unique keys
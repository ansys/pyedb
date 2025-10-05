# src/pyedb/workflows/job_manager/components/resource_monitor.py
"""
Resource monitoring components with animated gauges
"""

import streamlit as st
import psutil
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time


class ResourceMonitor:
    """Monitors and displays system resources with animated gauges"""

    @staticmethod
    def get_system_resources():
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "memory_used_gb": round(psutil.virtual_memory().used / (1024 ** 3), 1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
            "disk_used_gb": round(psutil.disk_usage('/').used / (1024 ** 3), 1),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024 ** 3), 1),
        }

    @staticmethod
    def render_cpu_gauge():
        """Render CPU usage gauge"""
        resources = ResourceMonitor.get_system_resources()

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=resources["cpu_percent"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU Usage", 'font': {'size': 16}},
            delta={'reference': 50, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#002855"},
                'bar': {'color': "#002855"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#d1fae5'},
                    {'range': [50, 80], 'color': '#fef3c7'},
                    {'range': [80, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=50, b=20),
            font={'color': "#002855", 'family': "Arial"}
        )

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False})

    @staticmethod
    def render_memory_gauge():
        """Render memory usage gauge"""
        resources = ResourceMonitor.get_system_resources()

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=resources["memory_percent"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Memory Usage<br>{resources['memory_used_gb']}/{resources['memory_total_gb']} GB",
                   'font': {'size': 14}},
            delta={'reference': 60, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#065f46"},
                'bar': {'color': "#065f46"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 60], 'color': '#d1fae5'},
                    {'range': [60, 85], 'color': '#fef3c7'},
                    {'range': [85, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=60, b=20),
            font={'color': "#065f46", 'family': "Arial"}
        )

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False})

    @staticmethod
    def render_disk_gauge():
        """Render disk usage gauge"""
        resources = ResourceMonitor.get_system_resources()

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=resources["disk_percent"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Disk Usage<br>{resources['disk_used_gb']}/{resources['disk_total_gb']} GB",
                   'font': {'size': 14}},
            delta={'reference': 70, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#92400e"},
                'bar': {'color': "#92400e"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 70], 'color': '#d1fae5'},
                    {'range': [70, 90], 'color': '#fef3c7'},
                    {'range': [90, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))

        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=60, b=20),
            font={'color': "#92400e", 'family': "Arial"}
        )

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False})
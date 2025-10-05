# src/pyedb/workflows/job_manager/utils/styles.py
"""
Custom styling utilities for corporate professional appearance
"""

import streamlit as st


def load_custom_css():
    """Load custom CSS for professional corporate styling"""
    st.markdown("""
    <style>
    /* ANSYS Corporate Color Scheme */
    :root {
        --ansys-blue: #002855;
        --ansys-light-blue: #0047BB;
        --ansys-gray: #666666;
        --ansys-light-gray: #f8f9fa;
    }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, var(--ansys-blue) 0%, var(--ansys-light-blue) 100%);
        color: white;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Professional card styling */
    .job-card {
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }

    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    /* Button styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        transform: translateY(-1px);
    }

    /* Metric card styling */
    .stMetric {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid var(--ansys-blue);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--ansys-light-gray);
    }

    /* Form styling */
    .stForm {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--ansys-blue);
    }

    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--ansys-blue);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--ansys-light-blue);
    }
    </style>
    """, unsafe_allow_html=True)


def apply_corporate_styling():
    """Apply ANSYS corporate styling to Streamlit components"""
    st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom font styling */
    .css-1d391kg, .css-1outpf7, .css-1kyxreq {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Success message styling */
    .stAlert [data-testid="stMarkdownContainer"] {
        font-weight: 500;
    }

    /* Info box styling */
    .stInfo {
        border-left: 4px solid var(--ansys-blue);
    }
    </style>
    """, unsafe_allow_html=True)
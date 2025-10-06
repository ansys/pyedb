"""
Simplified Streamlit app with connection debugging - FIXED
"""

import asyncio
import json
from typing import Any, Dict, Optional

import aiohttp
import streamlit as st


class DebugBackendClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.debug_log = []

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status with debug logging - FIXED to create session per request"""
        self.debug_log.append(f"📡 Calling GET {self.base_url}/system/status")

        try:
            # Create a new session for each request to avoid event loop issues
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/system/status") as response:
                    self.debug_log.append(f"📊 Response HTTP {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        self.debug_log.append("✅ Successfully parsed JSON response")
                        return data
                    else:
                        error_text = await response.text()
                        self.debug_log.append(f"❌ HTTP Error: {error_text}")
                        return {"error": f"HTTP {response.status}", "details": error_text}

        except aiohttp.ClientConnectorError as e:
            self.debug_log.append(f"🔌 Connection Error: {e}")
            return {"error": f"Cannot connect to backend: {e}"}
        except Exception as e:
            self.debug_log.append(f"💥 Unexpected error: {e}")
            return {"error": str(e)}

    async def submit_job(self, config: Dict[str, Any], priority: int = 0) -> Optional[str]:
        """Submit job with debug logging - FIXED to create session per request"""
        self.debug_log.append(f"📤 Calling POST {self.base_url}/jobs/submit")
        self.debug_log.append(f"📦 Payload: {json.dumps(config, indent=2)}")

        try:
            payload = {"config": config, "priority": priority}

            # Create a new session for each request to avoid event loop issues
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/jobs/submit", json=payload, headers={"Content-Type": "application/json"}
                ) as response:
                    self.debug_log.append(f"📊 Response HTTP {response.status}")
                    response_text = await response.text()
                    self.debug_log.append(f"📦 Response body: {response_text}")

                    if response.status == 200:
                        result = json.loads(response_text)
                        if result.get("success"):
                            self.debug_log.append(f"✅ Job submitted successfully: {result.get('job_id')}")
                            return result.get("job_id")
                        else:
                            self.debug_log.append(f"❌ Submission failed: {result.get('error')}")
                    return None

        except Exception as e:
            self.debug_log.append(f"💥 Submission error: {e}")
            return None

    def get_debug_log(self):
        return self.debug_log.copy()

    def clear_debug_log(self):
        self.debug_log.clear()


# FIXED: Proper async handling for Streamlit
async def handle_test_connection():
    """Handle connection test with proper error handling"""
    client = DebugBackendClient()

    try:
        status = await client.get_system_status()
        return status, client.get_debug_log()
    except Exception as e:
        return {"error": str(e)}, client.get_debug_log()


async def handle_submit_job(config, priority=0):
    """Handle job submission with proper error handling"""
    client = DebugBackendClient()

    try:
        job_id = await client.submit_job(config, priority)
        return job_id, client.get_debug_log()
    except Exception as e:
        return None, client.get_debug_log()


def main():
    st.set_page_config(page_title="PyEDB Job Manager - Debug", layout="wide")
    st.title("🔧 PyEDB Job Manager - Connection Debug")

    # FIXED: Don't store client in session state
    # Instead, create a fresh client for each operation

    # Debug panel
    with st.sidebar:
        st.subheader("🔍 Debug Panel")

        if st.button("Test Connection"):
            with st.spinner("Testing connection..."):
                try:
                    # Use asyncio.run to handle the event loop properly
                    status, debug_log = asyncio.run(handle_test_connection())

                    if "error" in status:
                        st.error(f"💥 Connection failed: {status['error']}")
                    else:
                        st.success("✅ Connection successful!")
                        st.write("Status:", status)

                    # Show debug log
                    st.subheader("Debug Log")
                    for i, log_entry in enumerate(debug_log):
                        st.text(f"{i + 1:2d}. {log_entry}")

                except RuntimeError as e:
                    if "Event loop is closed" in str(e):
                        st.error("💥 Event loop error - retrying...")
                        # Retry with fresh event loop
                        try:
                            status, debug_log = asyncio.run(handle_test_connection())
                            if "error" in status:
                                st.error(f"💥 Connection failed: {status['error']}")
                            else:
                                st.success("✅ Connection successful!")
                                st.write("Status:", status)
                        except Exception as retry_e:
                            st.error(f"💥 Retry failed: {str(retry_e)}")
                    else:
                        st.error(f"💥 Unexpected error: {str(e)}")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🚀 Submit Test Job")

        with st.form("test_job_form"):
            job_name = st.text_input("Job Name", "test_job_frontend")
            project_path = st.text_input("Project Path", r"D:\Temp\test_jobs\test1.aedb")

            submitted = st.form_submit_button("Submit Test Job")

            if submitted:
                config = {
                    "jobid": job_name,
                    "project_path": project_path,
                    "scheduler_type": "none",
                    "ansys_edt_path": r"C:\Program Files\ANSYS Inc\v252\AnsysEM\ansysedt.exe",
                }

                with st.spinner("Submitting job..."):
                    try:
                        job_id, debug_log = asyncio.run(handle_submit_job(config))

                        if job_id:
                            st.success(f"✅ Job submitted! ID: {job_id}")
                        else:
                            st.error("❌ Job submission failed")

                        # Show debug log
                        with st.expander("Debug Log"):
                            for i, log_entry in enumerate(debug_log):
                                st.text(f"{i + 1:2d}. {log_entry}")

                    except RuntimeError as e:
                        if "Event loop is closed" in str(e):
                            st.error("💥 Event loop error during submission - retrying...")
                            try:
                                job_id, debug_log = asyncio.run(handle_submit_job(config))
                                if job_id:
                                    st.success(f"✅ Job submitted! ID: {job_id}")
                                else:
                                    st.error("❌ Job submission failed")
                            except Exception as retry_e:
                                st.error(f"💥 Retry failed: {str(retry_e)}")

    with col2:
        st.subheader("📊 System Status")

        if st.button("Refresh Status"):
            with st.spinner("Refreshing status..."):
                try:
                    status, debug_log = asyncio.run(handle_test_connection())
                    st.write("Current Status:", status)

                    # Show debug log in expander
                    with st.expander("Debug Log"):
                        for i, log_entry in enumerate(debug_log):
                            st.text(f"{i + 1:2d}. {log_entry}")

                except RuntimeError as e:
                    st.error(f"💥 Error: {str(e)}")


if __name__ == "__main__":
    main()

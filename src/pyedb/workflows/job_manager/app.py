"""
Simplified Streamlit app with connection debugging
"""
import asyncio
import aiohttp
import streamlit as st
import json
from typing import Dict, Any, Optional

class DebugBackendClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.debug_log = []

    async def initialize(self):
        """Initialize HTTP session with debug logging"""
        self.debug_log.append("🔄 Initializing HTTP session")
        self.session = aiohttp.ClientSession()
        self.debug_log.append("✅ HTTP session created")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status with debug logging"""
        self.debug_log.append(f"📡 Calling GET {self.base_url}/system/status")

        try:
            async with self.session.get(f"{self.base_url}/system/status") as response:
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
        """Submit job with debug logging"""
        self.debug_log.append(f"📤 Calling POST {self.base_url}/jobs/submit")
        self.debug_log.append(f"📦 Payload: {json.dumps(config, indent=2)}")

        try:
            payload = {"config": config, "priority": priority}

            async with self.session.post(
                f"{self.base_url}/jobs/submit",
                json=payload,
                headers={"Content-Type": "application/json"}
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

async def main():
    st.set_page_config(page_title="PyEDB Job Manager - Debug", layout="wide")

    st.title("🔧 PyEDB Job Manager - Connection Debug")

    # Initialize client
    if "client" not in st.session_state:
        st.session_state.client = DebugBackendClient()
        await st.session_state.client.initialize()
        st.session_state.initialized = True

    client = st.session_state.client

    # Debug panel
    with st.sidebar:
        st.subheader("🔍 Debug Panel")

        if st.button("Clear Debug Log"):
            client.clear_debug_log()
            st.rerun()

        if st.button("Test Connection"):
            with st.spinner("Testing connection..."):
                status = await client.get_system_status()
                st.write("Status:", status)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🚀 Submit Test Job")

        with st.form("test_job_form"):
            job_name = st.text_input("Job Name", "test_job_frontend")
            project_path = st.text_input("Project Path", "/tmp/test_project.aedt")

            submitted = st.form_submit_button("Submit Test Job")

            if submitted:
                config = {
                    "jobid": job_name,
                    "project_path": project_path,
                    "scheduler_type": "none",
                    "ansys_edt_path": "/mock/ansysedt"
                }

                with st.spinner("Submitting job..."):
                    job_id = await client.submit_job(config)

                    if job_id:
                        st.success(f"✅ Job submitted! ID: {job_id}")
                    else:
                        st.error("❌ Job submission failed")

    with col2:
        st.subheader("📊 System Status")

        if st.button("Refresh Status"):
            status = await client.get_system_status()
            st.write("Current Status:", status)

    # Debug log
    st.subheader("📋 Debug Log")
    debug_log = client.get_debug_log()

    if debug_log:
        for i, log_entry in enumerate(debug_log[-20:]):  # Show last 20 entries
            st.text(f"{i+1:2d}. {log_entry}")
    else:
        st.info("No debug entries yet. Perform actions to see logs.")

if __name__ == "__main__":
    asyncio.run(main())
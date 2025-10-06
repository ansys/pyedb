import asyncio
import aiohttp
import streamlit as st
import json


class ConnectionTester:
    def __init__(self, backend_url="http://localhost:8080"):
        self.backend_url = backend_url
        self.session = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def test_all_endpoints(self):
        """Test all backend endpoints from frontend perspective"""
        results = {}

        endpoints = {
            "system_status": "/system/status",
            "jobs_list": "/jobs",
            "queue_stats": "/queue",
            "resources": "/resources"
        }

        for name, endpoint in endpoints.items():
            try:
                async with self.session.get(f"{self.backend_url}{endpoint}") as response:
                    results[name] = {
                        "status": response.status,
                        "content_type": response.content_type,
                        "data": await response.json() if response.status == 200 else None
                    }
                    print(f"✅ {name}: HTTP {response.status}")
            except Exception as e:
                results[name] = {"error": str(e)}
                print(f"❌ {name}: {e}")

        return results

    async def test_job_submission(self):
        """Test submitting a job from frontend"""
        test_job = {
            "config": {
                "jobid": f"frontend_test_{st.get_option('server.port')}",
                "project_path": "/tmp/test_project.aedt",
                "scheduler_type": "none",
                "ansys_edt_path": "/mock/ansysedt",
                "design_name": "TestDesign",
                "setup_name": "TestSetup"
            },
            "priority": 0
        }

        try:
            async with self.session.post(
                    f"{self.backend_url}/jobs/submit",
                    json=test_job,
                    headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                return {
                    "status": response.status,
                    "result": result
                }
        except Exception as e:
            return {"error": str(e)}


def main():
    st.set_page_config(page_title="Frontend-Backend Test", layout="wide")
    st.title("🔗 Frontend-Backend Connection Test")

    if "tester" not in st.session_state:
        st.session_state.tester = ConnectionTester()
        st.session_state.initialized = False

    # Initialize connection
    if not st.session_state.initialized:
        with st.spinner("Initializing connection tester..."):
            asyncio.run(st.session_state.tester.initialize())
            st.session_state.initialized = True

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Test Backend Endpoints")
        if st.button("Run Endpoint Tests"):
            with st.spinner("Testing endpoints..."):
                results = asyncio.run(st.session_state.tester.test_all_endpoints())

                for endpoint, result in results.items():
                    with st.expander(f"Endpoint: {endpoint}"):
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(f"HTTP Status: {result['status']}")
                            st.code(f"Content-Type: {result.get('content_type', 'N/A')}")
                            if result.get('data'):
                                st.json(result['data'])

    with col2:
        st.subheader("2. Test Job Submission")
        if st.button("Test Job Submission"):
            with st.spinner("Submitting test job..."):
                result = asyncio.run(st.session_state.tester.test_job_submission())

                if "error" in result:
                    st.error(f"Submission failed: {result['error']}")
                else:
                    st.success(f"HTTP Status: {result['status']}")
                    st.json(result.get('result', {}))

        st.subheader("3. Manual HTTP Test")
        st.code("""
# Test from terminal while Streamlit is running:
curl http://localhost:8080/system/status
curl http://localhost:8080/jobs
curl -X POST http://localhost:8080/jobs/submit -H "Content-Type: application/json" -d '{"config": {"jobid":"test","project_path":"/tmp/test.aedt"}}'
        """)


if __name__ == "__main__":
    main()
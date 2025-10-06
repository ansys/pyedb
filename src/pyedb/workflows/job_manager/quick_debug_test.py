import asyncio
import aiohttp


async def debug_flow():
    """Test the complete flow with print statements"""
    print("1. Testing backend connection...")

    async with aiohttp.ClientSession() as session:
        # Test system status
        print("2. Calling /system/status...")
        async with session.get("http://localhost:8080/system/status") as response:
            print(f"   Status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Data: {data}")

        # Test job submission
        print("3. Calling /jobs/submit...")
        test_job = {
            "config": {
                "jobid": "debug_test",
                "project_path": "/tmp/debug.aedt",
                "scheduler_type": "none"
            }
        }

        async with session.post("http://localhost:8080/jobs/submit", json=test_job) as response:
            print(f"   Status: {response.status}")
            result = await response.text()
            print(f"   Result: {result}")


if __name__ == "__main__":
    asyncio.run(debug_flow())
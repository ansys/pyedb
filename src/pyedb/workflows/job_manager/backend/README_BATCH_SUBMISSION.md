# Batch Job Submission

## Overview

The `submit_batch_jobs.py` script allows you to submit multiple HFSS projects to the job manager by scanning a directory for `.aedb` folders and `.aedt` files.

## Features

- **Automatic Project Discovery**: Scans a root directory for all `.aedb` folders and `.aedt` files
- **Smart Pairing**: When both an `.aedb` folder and corresponding `.aedt` file exist, the `.aedt` file is used
- **Asynchronous Submission**: Jobs are submitted concurrently to the job manager for faster processing
- **Recursive Scanning**: Optional recursive directory scanning
- **Configurable Concurrency**: Control how many jobs are submitted simultaneously

## Prerequisites

1. The job manager service must be running before executing this script:
   ```bash
   python -m pyedb.workflows.job_manager.backend.job_manager_handler
   ```

2. Install required dependencies:
   ```bash
   pip install aiohttp
   ```

## Usage

### Basic Usage

Submit all projects in a directory:

```bash
python submit_batch_jobs.py --root-dir "D:\Temp\test_jobs"
```

### Advanced Options

```bash
python submit_batch_jobs.py \
    --host localhost \
    --port 8080 \
    --root-dir "D:\Temp\test_jobs" \
    --num-cores 8 \
    --max-concurrent 5 \
    --delay-ms 100 \
    --recursive \
    --verbose
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--host` | Job manager host address | `localhost` |
| `--port` | Job manager port | `8080` |
| `--root-dir` | Root directory to scan (required) | - |
| `--num-cores` | Number of cores per job | `8` |
| `--max-concurrent` | Max concurrent submissions | `5` |
| `--delay-ms` | Delay in milliseconds between submissions | `100` |
| `--recursive` | Scan subdirectories recursively | `False` |
| `--verbose` | Enable debug logging | `False` |

## How It Works

1. **Scanning Phase**:
   - Searches for all `.aedb` folders in the root directory
   - Searches for all `.aedt` files in the root directory
   - For each `.aedb` folder, checks if a corresponding `.aedt` file exists:
     - If yes: Uses the `.aedt` file
     - If no: Uses the `.aedb` folder
   - Standalone `.aedt` files (without corresponding `.aedb`) are also included

2. **Submission Phase**:
   - Creates job configurations for each project
   - Submits jobs asynchronously to the job manager REST API
   - Limits concurrent submissions using a semaphore
   - Reports success/failure for each submission

3. **Results**:
   - Displays a summary with total, successful, and failed submissions
   - Logs detailed information about each submission

## Example Output

```
2025-11-07 10:30:15 - __main__ - INFO - Scanning D:\Temp\test_jobs for projects (recursive=False)
2025-11-07 10:30:15 - __main__ - INFO - Found AEDB folder: D:\Temp\test_jobs\project1.aedb
2025-11-07 10:30:15 - __main__ - INFO - Found AEDT file: D:\Temp\test_jobs\project2.aedt
2025-11-07 10:30:15 - __main__ - INFO - Using AEDB folder for project: D:\Temp\test_jobs\project1.aedb
2025-11-07 10:30:15 - __main__ - INFO - Using standalone AEDT file: D:\Temp\test_jobs\project2.aedt
2025-11-07 10:30:15 - __main__ - INFO - Found 2 project(s) to submit
2025-11-07 10:30:15 - __main__ - INFO - Starting batch submission of 2 project(s) to http://localhost:8080
2025-11-07 10:30:16 - __main__ - INFO - ✓ Successfully submitted: project1.aedb (status=200)
2025-11-07 10:30:16 - __main__ - INFO - ✓ Successfully submitted: project2.aedt (status=200)
2025-11-07 10:30:16 - __main__ - INFO - ============================================================
2025-11-07 10:30:16 - __main__ - INFO - Batch submission complete:
2025-11-07 10:30:16 - __main__ - INFO -   Total projects: 2
2025-11-07 10:30:16 - __main__ - INFO -   ✓ Successful: 2
2025-11-07 10:30:16 - __main__ - INFO -   ✗ Failed: 0
2025-11-07 10:30:16 - __main__ - INFO - ============================================================
```

## Comparison with submit_local_job.py

| Feature | submit_local_job.py | submit_batch_jobs.py |
|---------|---------------------|----------------------|
| Projects | Single project | Multiple projects |
| Scanning | Manual path | Automatic discovery |
| Submission | Single | Concurrent/Async |
| Pairing | N/A | .aedb ↔ .aedt pairing |
| Recursive | N/A | Optional |

## Error Handling

- **Service Not Running**: If the job manager service is not accessible, submissions will fail with connection errors
- **Invalid Projects**: Projects that fail to create valid configurations will be logged as errors
- **Network Timeouts**: 120-second timeout for each submission request
- **Partial Failures**: The script continues submitting other jobs even if some fail

## Notes

- The script does not wait for jobs to complete, only for submission confirmation
- Job execution happens asynchronously in the job manager service
- Use `--max-concurrent` to limit load on the job manager service
- Use `--delay-ms` to add a pause between submissions, ensuring HTTP requests are fully sent (default: 100ms)
- For large batch submissions, consider increasing the timeout in the code if needed
- Set `--delay-ms 0` to disable the delay if network is very fast and reliable


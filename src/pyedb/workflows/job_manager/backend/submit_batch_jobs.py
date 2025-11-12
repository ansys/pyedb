#!/usr/bin/env python3

# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Submit multiple HFSS jobs to the local job-manager service by scanning a directory.
Job submissions are done via REST API asynchronously.
The service must be running locally (default: localhost:8080) prior to executing this script.
To start the service, run this command in another terminal:
    python -m pyedb.workflows.job_manager.backend.job_manager_handler

Usage examples
--------------
# Get help
python submit_batch_jobs.py --help

# Submit all projects in a directory with explicit values
python submit_batch_jobs.py \
    --host 127.0.0.1 \
    --port 8080 \
    --root-dir "D:\\Temp\\test_jobs" \
    --num-cores 8

# Use defaults (localhost:8080, 8 cores)
python submit_batch_jobs.py --root-dir "D:\\Temp\\test_jobs"

# Recursive scan
python submit_batch_jobs.py --root-dir "D:\\Temp\\test_jobs" --recursive
"""

import argparse
import asyncio
import logging
from pathlib import Path
import sys
from typing import Any, List, cast

import aiohttp

from pyedb.workflows.job_manager.backend.job_submission import (
    MachineNode,
    create_hfss_config,
)

logger = logging.getLogger(__name__)


def scan_projects(root_dir: Path, recursive: bool = False) -> List[Path]:
    """
    Scan a directory for AEDB folders and AEDT files.

    For each AEDB folder found, check if a corresponding AEDT file exists.
    If it does, use the AEDT file; otherwise, use the AEDB folder.

    Parameters
    ----------
    root_dir : Path
        Root directory to scan for projects.
    recursive : bool, optional
        If True, scan subdirectories recursively. Default is False.

    Returns
    -------
    List[Path]
        List of project paths (either .aedt files or .aedb folders) to submit.
    """
    projects = []
    aedb_folders = set()
    aedt_files = set()

    # Determine the glob pattern based on recursive flag
    glob_pattern = "**/*" if recursive else "*"

    logger.info("Scanning %s for projects (recursive=%s)", root_dir, recursive)

    # Find all .aedb folders
    for path in root_dir.glob(glob_pattern):
        if path.is_dir() and path.suffix == ".aedb":
            aedb_folders.add(path)
            logger.debug("Found AEDB folder: %s", path)

    # Find all .aedt files
    if recursive:
        for path in root_dir.glob("**/*.aedt"):
            if path.is_file():
                aedt_files.add(path)
                logger.debug("Found AEDT file: %s", path)
    else:
        for path in root_dir.glob("*.aedt"):
            if path.is_file():
                aedt_files.add(path)
                logger.debug("Found AEDT file: %s", path)

    # Process AEDB folders: check if corresponding AEDT exists
    for aedb_folder in aedb_folders:
        # Check for corresponding .aedt file (same name, same directory)
        corresponding_aedt = aedb_folder.with_suffix(".aedt")

        if corresponding_aedt in aedt_files:
            # Use the AEDT file and remove it from the set to avoid duplicates
            projects.append(corresponding_aedt)
            aedt_files.discard(corresponding_aedt)
            logger.info("Using AEDT file for project: %s", corresponding_aedt)
        else:
            # Use the AEDB folder
            projects.append(aedb_folder)
            logger.info("Using AEDB folder for project: %s", aedb_folder)

    # Add remaining AEDT files that don't have corresponding AEDB folders
    for aedt_file in aedt_files:
        projects.append(aedt_file)
        logger.info("Using standalone AEDT file: %s", aedt_file)

    # Sort for consistent ordering
    projects.sort()

    logger.info("Found %d project(s) to submit", len(projects))
    return projects


async def submit_single_job(
    session: aiohttp.ClientSession,
    backend_url: str,
    project_path: Path,
    num_cores: int,
    priority: int = 0,
) -> tuple[Path, bool, Any]:
    """
    Submit a single job to the job manager.

    Parameters
    ----------
    session : aiohttp.ClientSession
        Async HTTP session for making requests.
    backend_url : str
        Base URL of the job manager service.
    project_path : Path
        Path to the project file or folder.
    num_cores : int
        Number of CPU cores to allocate.
    priority : int, optional
        Job priority (default: 0).

    Returns
    -------
    tuple[Path, bool, Any]
        Tuple of (project_path, success_flag, response_data).
    """
    try:
        cfg = create_hfss_config(project_path=str(project_path))

        # Ensure we have at least one machine node and configure it
        if not cfg.machine_nodes:
            cfg.machine_nodes.append(MachineNode())

        # Use a typed reference to avoid static-analysis/indexing warnings
        node = cast(MachineNode, cfg.machine_nodes[0])
        node.cores = num_cores
        node.max_cores = num_cores

        async with session.post(
            f"{backend_url}/jobs/submit",
            json={
                "config": cfg.model_dump(mode="json", exclude_defaults=False),
                "priority": priority,
            },
        ) as resp:
            status = resp.status
            # Try to parse JSON reply safely; fall back to text
            try:
                reply: Any = await resp.json()
            except Exception:
                reply = await resp.text()

            success = 200 <= status < 300
            if success:
                logger.info("✓ Successfully submitted: %s (status=%s)", project_path.name, status)
            else:
                logger.error("✗ Failed to submit: %s (status=%s): %s", project_path.name, status, reply)

            return (project_path, success, reply)

    except asyncio.CancelledError:
        # Re-raise cancellation so callers can handle it
        raise
    except Exception as exc:
        logger.exception("✗ Exception submitting %s: %s", project_path.name, exc)
        return (project_path, False, str(exc))


async def submit_batch_jobs(
    *,
    host: str,
    port: int,
    projects: List[Path],
    num_cores: int,
    max_concurrent: int = 5,
    delay_ms: int = 100,
) -> None:
    """
    Submit multiple jobs asynchronously to the job manager.

    Parameters
    ----------
    host : str
        Job manager host address.
    port : int
        Job manager port.
    projects : List[Path]
        List of project paths to submit.
    num_cores : int
        Number of CPU cores to allocate per job.
    max_concurrent : int, optional
        Maximum number of concurrent submissions (default: 5).
    delay_ms : int, optional
        Delay in milliseconds between job submissions (default: 100).
    """
    backend_url = f"http://{host}:{port}"

    logger.info("Starting batch submission of %d project(s) to %s", len(projects), backend_url)
    logger.info("Max concurrent submissions: %d", max_concurrent)
    logger.info("Delay between submissions: %d ms", delay_ms)

    # Use a reasonable timeout for network operations
    timeout = aiohttp.ClientTimeout(total=120)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Create a semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def submit_with_semaphore(project: Path) -> tuple[Path, bool, Any]:
            async with semaphore:
                result = await submit_single_job(session, backend_url, project, num_cores)
                # Add a small delay to ensure HTTP request is fully sent before next submission
                await asyncio.sleep(delay_ms / 1000.0)
                return result

        # Submit all jobs concurrently (but limited by semaphore)
        tasks = [submit_with_semaphore(project) for project in projects]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Summarize results
        successful = 0
        failed = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error("Task raised exception: %s", result)
                failed += 1
            else:
                project_path, success, _reply = result
                if success:
                    successful += 1
                else:
                    failed += 1

        logger.info("=" * 60)
        logger.info("Batch submission complete:")
        logger.info("  Total projects: %d", len(projects))
        logger.info("  ✓ Successful: %d", successful)
        logger.info("  ✗ Failed: %d", failed)
        logger.info("=" * 60)


def parse_cli() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Submit multiple HFSS jobs to the local job-manager service by scanning a directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Job-manager host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Job-manager port (default: 8080)",
    )
    parser.add_argument(
        "--root-dir",
        required=True,
        type=Path,
        help="Root directory to scan for .aedb folders and .aedt files",
    )
    parser.add_argument(
        "--num-cores",
        type=int,
        default=8,
        help="Number of cores to allocate per job (default: 8)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subdirectories recursively",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum number of concurrent job submissions (default: 5)",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=100,
        help="Delay in milliseconds between job submissions (default: 100)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the batch job submission script."""
    args = parse_cli()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # Basic sanity checks
    if not args.root_dir.exists():
        logger.error("Error: root directory does not exist: %s", args.root_dir)
        print(f"Error: root directory does not exist: {args.root_dir}", file=sys.stderr)
        sys.exit(1)

    if not args.root_dir.is_dir():
        logger.error("Error: root-dir must be a directory: %s", args.root_dir)
        print(f"Error: root-dir must be a directory: {args.root_dir}", file=sys.stderr)
        sys.exit(1)

    if args.num_cores <= 0:
        logger.error("Error: --num-cores must be positive")
        print("Error: --num-cores must be positive", file=sys.stderr)
        sys.exit(1)

    if args.max_concurrent <= 0:
        logger.error("Error: --max-concurrent must be positive")
        print("Error: --max-concurrent must be positive", file=sys.stderr)
        sys.exit(1)

    if args.delay_ms < 0:
        logger.error("Error: --delay-ms must be non-negative")
        print("Error: --delay-ms must be non-negative", file=sys.stderr)
        sys.exit(1)

    # Scan for projects
    projects = scan_projects(args.root_dir, recursive=args.recursive)

    if not projects:
        logger.warning("No projects found in %s", args.root_dir)
        print(f"Warning: No .aedb folders or .aedt files found in {args.root_dir}")
        sys.exit(0)

    # Submit jobs
    asyncio.run(
        submit_batch_jobs(
            host=args.host,
            port=args.port,
            projects=projects,
            num_cores=args.num_cores,
            max_concurrent=args.max_concurrent,
            delay_ms=args.delay_ms,
        )
    )


if __name__ == "__main__":
    main()

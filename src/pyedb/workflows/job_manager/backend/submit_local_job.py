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
Submit an HFSS job to the local job-manager service.
Job Submission is done via REST API asynchronously.
The service must be running locally (default: localhost:8080) prior to executing this script.
To start the service, run this command in another terminal:
    python -m pyedb.workflows.job_manager.backend.job_manager_handler

Usage examples
--------------
# Get help
python submit_job.py --help

# Submit with explicit values
python submit_local_job.py \
    --host 127.0.0.1 \
    --port 8080 \
    --project-path "D:\\Temp\\test_jobs\\test1.aedb" \
    --num-cores 8

# Use defaults (localhost:8080, 8 cores)
python submit_local_job.py --project-path "D:\\Temp\\test_jobs\\test1.aedb"
"""

import argparse
import asyncio
import logging
from pathlib import Path
import sys
from typing import Any, cast

import aiohttp

from pyedb.workflows.job_manager.backend.job_submission import (
    MachineNode,
    create_hfss_config,
)

logger = logging.getLogger(__name__)


async def submit_job(*, host: str, port: int, project_path: str, num_cores: int) -> None:
    """Send the job-configuration to the REST endpoint."""
    backend_url = f"http://{host}:{port}"
    cfg = create_hfss_config(project_path=project_path)

    # Ensure we have at least one machine node and configure it
    if not cfg.machine_nodes:
        cfg.machine_nodes.append(MachineNode())

    # Use a typed reference to avoid static-analysis/indexing warnings
    node = cast(MachineNode, cfg.machine_nodes[0])
    node.cores = num_cores
    node.max_cores = num_cores

    # Use a reasonable timeout for network operations
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                f"{backend_url}/jobs/submit",
                json={
                    "config": cfg.model_dump(mode="json", exclude_defaults=False),
                    "priority": 0,
                },
            ) as resp:
                status = resp.status
                # Try to parse JSON reply safely; fall back to text
                try:
                    reply: Any = await resp.json()
                except Exception:
                    reply = await resp.text()

                if 200 <= status < 300:
                    logger.info("Job submit successful (status=%s)", status)
                    logger.debug("Reply: %s", reply)
                else:
                    logger.error("Job submit failed (status=%s): %s", status, reply)
        except asyncio.CancelledError:
            # Re-raise cancellation so callers can handle it
            raise
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to submit job to %s: %s", backend_url, exc)


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit an HFSS job to the local job-manager service.")
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
        "--project-path",
        required=True,
        type=Path,
        help="Full path to the .aedb project",
    )
    parser.add_argument(
        "--num-cores",
        type=int,
        default=8,
        help="Number of cores to allocate (default: 8)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli()

    # Configure basic logging if the caller didn't
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)

    # Basic sanity checks
    if not args.project_path.exists():
        logger.error("Error: project path does not exist: %s", args.project_path)
        print(f"Error: project path does not exist: {args.project_path}", file=sys.stderr)
        sys.exit(1)
    if args.num_cores <= 0:
        logger.error("Error: --num-cores must be positive")
        print("Error: --num-cores must be positive", file=sys.stderr)
        sys.exit(1)

    asyncio.run(
        submit_job(
            host=args.host,
            port=args.port,
            project_path=str(args.project_path),
            num_cores=args.num_cores,
        )
    )


if __name__ == "__main__":
    main()

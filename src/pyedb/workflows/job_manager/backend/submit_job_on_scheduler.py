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

# ---------------  submit_job_on_scheduler.py  -----------------
#!/usr/bin/env python3
"""
Submit an HFSS job to the *scheduler* back-end service.

The service must be running (default: localhost:8080) before this script is executed.
To start it:

    python -m pyedb.workflows.job_manager.backend.job_manager_handler

Usage
-----
# Get help
python submit_job_on_scheduler.py --help

# Explicit values
python submit_job_on_scheduler.py \
    --host 127.0.0.1 \
    --port 8080 \
    --project-path "/tmp/jobs/job1.aedb" \
    --partition default \
    --nodes 1 \
    --cores-per-node 8

# Use defaults (localhost:8080, 1 node, 1 core, partition default)
python submit_job_on_scheduler.py \
    --project-path "/tmp/jobs/job1.aedb"
"""

"""
Submit an HFSS job to the SLURM back-end service.
Same CLI as submit_local_job.py, but forces SLURM execution.
"""

import argparse
import asyncio
import logging
from pathlib import Path
import sys

import aiohttp

from pyedb.workflows.job_manager.backend.job_submission import (
    SchedulerOptions,
    SchedulerType,
    create_hfss_config,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080
DEFAULT_PARTITION = "default"
DEFAULT_NODES = 1
DEFAULT_CORES_PER_NODE = 1


async def submit_slurm_job(
    *,
    host: str,
    port: int,
    project_path: str,
    partition: str,
    nodes: int,
    cores_per_node: int,
) -> None:
    """Send the SLURM job-configuration to the REST endpoint."""
    backend_url = f"http://{host}:{port}"

    # 1.  Build the *generic* scheduler options that SLURM understands
    scheduler_opts = SchedulerOptions(
        queue=partition,
        nodes=nodes,
        cores_per_node=cores_per_node,
        time="24:00:00",  # you can expose --time if you wish
    )

    # 2.  Create the HFSS config (scheduler_type=SLURM is the key)
    cfg = create_hfss_config(
        project_path=project_path,
        scheduler_options=scheduler_opts,
    )
    cfg.auto = True  # keep the original behaviour

    # 3.  POST it
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
                try:
                    reply = await resp.json()
                except Exception:
                    reply = await resp.text()

                if 200 <= status < 300:
                    logger.info("Job submitted successfully (status=%s)", status)
                    logger.debug("Server reply: %s", reply)
                else:
                    logger.error("Job submission failed (status=%s): %s", status, reply)
        except Exception as exc:
            logger.exception("Failed to submit job to %s: %s", backend_url, exc)
            sys.exit(2)


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit an HFSS job to the scheduler back-end service.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--project-path", required=True, type=Path)
    parser.add_argument("--partition", default=DEFAULT_PARTITION)
    parser.add_argument("--nodes", type=int, default=DEFAULT_NODES)
    parser.add_argument("--cores-per-node", type=int, default=DEFAULT_CORES_PER_NODE)
    return parser.parse_args()


def main() -> None:
    args = parse_cli()
    if not args.project_path.exists():
        logger.error("Project path does not exist: %s", args.project_path)
        sys.exit(1)
    if args.nodes <= 0 or args.cores_per_node <= 0:
        logger.error("--nodes and --cores-per-node must be positive")
        sys.exit(1)

    asyncio.run(
        submit_slurm_job(
            host=args.host,
            port=args.port,
            project_path=str(args.project_path),
            partition=args.partition,
            nodes=args.nodes,
            cores_per_node=args.cores_per_node,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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
Start the PyEDB Job-Manager service via JobManagerHandler.

Usage
-----
$ python start_service.py --host 0.0.0.0 --port 9090 --min-disk 2 --min-memory 1
✅ Job-manager backend listening on http://0.0.0.0:9090
Press Ctrl-C to shut down gracefully.
"""

import argparse
import signal
import sys
import threading

from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the PyEDB asynchronous job-manager service.")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="IP address or hostname to bind the server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="TCP port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--min-disk",
        type=float,
        default=10.0,
        help="Minimum free disk space in GB (default: 10.0)",
    )
    parser.add_argument(
        "--min-memory",
        type=float,
        default=2.0,
        help="Minimum free memory in GB (default: 2.0)",
    )
    return parser.parse_args()


def main():
    args = parse_cli()

    handler = JobManagerHandler(host=args.host, port=args.port)

    # Override resource limits from CLI
    handler.manager.resource_limits.min_disk_gb = args.min_disk
    handler.manager.resource_limits.min_memory_gb = args.min_memory

    handler.start_service()  # non-blocking; spins up daemon thread + aiohttp

    print(f"✅ Job-manager backend listening on http://{handler.host}:{handler.port}")
    print(f"   Resource gates: {args.min_disk} GB disk / {args.min_memory} GB memory")

    # Graceful shutdown on Ctrl-C
    stop_event = threading.Event()

    def _shutdown(sig, frame):
        print("\nShutting down...")
        stop_event.set()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        stop_event.wait()  # keep main thread alive
    finally:
        handler.close()
        sys.exit(0)


if __name__ == "__main__":
    main()

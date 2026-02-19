# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

import sys
from time import time


def format_time(seconds):
    """Helper to format time in seconds into a human-readable string with hours, minutes and seconds."""
    s = int(round(seconds))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    if m > 0:
        return f"{m}m{sec:02d}s"
    return f"{sec}s"


# small helper to print progress to terminal
def print_progress(current, total, start_time, prefix_desc="Progress"):
    """Helper to print progress in terminal with rate and ETA. Caller can choose how often to call this function based
    on their needs, e.g. every N iterations or every M seconds

    Parameters
    ----------
    current : int
        Current progress count
    total : int
        Total count for completion, can be 0 or negative if unknown
    start_time : float
        Start time in seconds (e.g. from time.time()) to compute elapsed time and rate
    prefix_desc : str, optional
        Description prefix to show before progress info, by default "Progress"
    """
    try:
        # compute elapsed, rate and ETA
        elapsed = time() - start_time
        elapsed = max(elapsed, 1e-6)
        rate = current / elapsed if current > 0 else 0.0

        if total <= 0:
            percent = 100.0
            eta_seconds = 0.0
        else:
            percent = (current / total) * 100.0 if total > 0 else 100.0
            eta_seconds = (total - current) / rate if rate > 0 else float("inf")

        eta_str = format_time(eta_seconds)
        # carriage return to update the same line
        sys.stdout.write(
            f"\r{prefix_desc}: {current}/{total} ({percent:.1f}%) rate={rate:.1f}/s elapsed={elapsed:.1f}s"
            f" eta={eta_str}"
        )
        sys.stdout.flush()
    except Exception:
        # if stdout isn't available or any error occurs, just ignore
        pass


def finish_progress():
    """helper to end a progress line cleanly"""
    try:
        sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception as e:
        print(e)

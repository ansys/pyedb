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

"""Helper utilities for progress reporting and time formatting in workflows."""

import sys
from time import time


def format_time(seconds: float) -> str:
    """Format time in seconds into a human-readable string.

    Convert a time duration in seconds to a formatted string showing hours,
    minutes, and seconds in a compact format (e.g., "2h15m30s").

    Parameters
    ----------
    seconds : float
        Time duration in seconds to format.

    Returns
    -------
    str
        Formatted time string. Returns format "Xh Ym Zs" for durations with hours,
        "Ym Zs" for durations with minutes, or "Zs" for durations under one minute.

    Examples
    --------
    >>> format_time(45)
    '45s'
    >>> format_time(125)
    '2m05s'
    >>> format_time(3665)
    '1h01m05s'
    >>> format_time(7384.5)
    '2h03m05s'

    """
    s = int(round(seconds))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    if m > 0:
        return f"{m}m{sec:02d}s"
    return f"{sec}s"


def print_progress(current: int, total: int, start_time: float, prefix_desc: str = "Progress") -> None:
    """Print progress information to terminal with rate and ETA.

    Display a dynamic progress line in the terminal showing current progress,
    percentage completion, processing rate, elapsed time, and estimated time
    remaining. The display updates in-place using carriage return.

    Parameters
    ----------
    current : int
        Current progress count (number of items processed).
    total : int
        Total count for completion. Can be 0 or negative if unknown,
        in which case percentage will show 100%.
    start_time : float
        Start time in seconds from ``time.time()`` used to compute
        elapsed time and processing rate.
    prefix_desc : str, optional
        Description prefix to show before progress information.
        The default is ``"Progress"``.

    Examples
    --------
    Basic usage for processing items:

    >>> from time import time
    >>> start = time()
    >>> for i in range(100):
    ...     # do some work
    ...     print_progress(i + 1, 100, start, "Processing items")
    Processing items: 100/100 (100.0%) rate=50.0/s elapsed=2.0s eta=0s

    Processing with unknown total:

    >>> start = time()
    >>> for i in range(50):
    ...     # do some work
    ...     print_progress(i + 1, 0, start, "Reading files")
    Reading files: 50/0 (100.0%) rate=25.0/s elapsed=2.0s eta=0s

    Processing database records:

    >>> from time import time, sleep
    >>> start = time()
    >>> total_records = 1000
    >>> for i in range(total_records):
    ...     # Process each record
    ...     if i % 10 == 0:  # Update every 10 items
    ...         print_progress(i, total_records, start, "Processing records")
    ... finish_progress()
    Processing records: 1000/1000 (100.0%) rate=500.0/s elapsed=2.0s eta=0s

    Notes
    -----
    - Uses carriage return (``\\r``) to update the same line
    - Call ``finish_progress()`` after the loop to add a newline
    - Silently ignores exceptions if stdout is unavailable
    - Caller controls update frequency (e.g., every N iterations or M seconds)

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
    except Exception:  # nosec B110
        # if stdout isn't available or any error occurs, just ignore
        pass


def finish_progress() -> None:
    """End a progress line cleanly by adding a newline.

    This function should be called after completing a progress reporting loop
    to move the cursor to a new line and prevent subsequent output from
    overwriting the final progress message.

    Examples
    --------
    Complete progress reporting workflow:

    >>> from time import time
    >>> start = time()
    >>> total = 100
    >>> for i in range(total):
    ...     # Process items
    ...     print_progress(i + 1, total, start, "Processing")
    ... finish_progress()
    ... print("Processing complete!")
    Processing: 100/100 (100.0%) rate=50.0/s elapsed=2.0s eta=0s
    Processing complete!

    Using in a workflow:

    >>> from time import time, sleep
    >>> def process_files(file_list):
    ...     start = time()
    ...     for i, file in enumerate(file_list):
    ...         # Process file
    ...         print_progress(i + 1, len(file_list), start, "Processing files")
    ...     finish_progress()
    ...     print(f"Processed {len(file_list)} files")

    Notes
    -----
    - Always call this after using ``print_progress()`` in a loop
    - Silently handles exceptions if stdout is unavailable
    - Adds a newline character to move to the next line

    """
    try:
        sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception as e:
        print(e)

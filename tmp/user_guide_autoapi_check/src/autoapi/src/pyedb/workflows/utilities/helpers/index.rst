src.pyedb.workflows.utilities.helpers
=====================================

.. py:module:: src.pyedb.workflows.utilities.helpers

.. autoapi-nested-parse::

   Helper utilities for progress reporting and time formatting in workflows.



Functions
---------

.. autoapisummary::

   src.pyedb.workflows.utilities.helpers.format_time
   src.pyedb.workflows.utilities.helpers.print_progress
   src.pyedb.workflows.utilities.helpers.finish_progress


Module Contents
---------------

.. py:function:: format_time(seconds: float) -> str

   Format time in seconds into a human-readable string.

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


.. py:function:: print_progress(current: int, total: int, start_time: float, prefix_desc: str = 'Progress') -> None

   Print progress information to terminal with rate and ETA.

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
   - Uses carriage return (``\r``) to update the same line
   - Call ``finish_progress()`` after the loop to add a newline
   - Silently ignores exceptions if stdout is unavailable
   - Caller controls update frequency (e.g., every N iterations or M seconds)


.. py:function:: finish_progress() -> None

   End a progress line cleanly by adding a newline.

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



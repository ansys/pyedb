# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Optional, bounded progress notifications without a GUI dependency."""

from time import monotonic


def throttle_progress(callback):
    """Bound UI notifications while retaining stage changes and completion."""
    previous = 0.0
    previous_stage = None

    def report(stage, current, total):
        nonlocal previous, previous_stage
        now = monotonic()
        if stage != previous_stage or current == total or now - previous >= 0.08:
            previous, previous_stage = now, stage
            callback(stage, current, total)

    return report


def progress_items(load, progress, stage):
    """Report collection discovery and completed items, including filtered items."""
    if progress is not None:
        progress(stage, 0, 0)
    items = load()
    total = len(items)
    if progress is not None:
        progress(stage, 0, total)
    for current, item in enumerate(items, 1):
        yield item
        if progress is not None and (current % 64 == 0 or current == total):
            progress(stage, current, total)

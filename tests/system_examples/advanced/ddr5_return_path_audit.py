# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Audit reference-via proximity around DDR5 signal-via transitions.

This standalone example uses direct PyEDB net and padstack APIs. It finds all
signal vias on selected DDR5 nets, locates the nearest reference-net vias, and
writes a CSV report for layout review.
"""

from __future__ import annotations

import argparse
import csv
from math import hypot
from pathlib import Path

from pyedb import Edb


def xy(instance) -> tuple[float, float]:
    """Return a padstack-instance position in metres."""
    x, y = instance.position
    return float(x), float(y)


def audit_return_paths(
    source_edb: Path,
    signal_nets: list[str],
    reference_net: str,
    maximum_distance_mm: float,
    report_file: Path,
    version: str,
) -> list[dict]:
    """Find the nearest reference via for each selected signal via."""
    maximum_distance_m = maximum_distance_mm / 1000.0
    edb = Edb(str(source_edb.resolve()), version=version)
    try:
        missing = [name for name in [*signal_nets, reference_net] if name not in edb.nets]
        if missing:
            raise ValueError(f"Nets not found: {', '.join(missing)}")

        signal_vias = edb.padstacks.get_via_instance_from_net(signal_nets)
        reference_vias = edb.padstacks.get_via_instance_from_net(reference_net)
        if not signal_vias:
            raise RuntimeError("No signal vias were found on the selected DDR5 nets")
        if not reference_vias:
            raise RuntimeError(f"No vias were found on reference net {reference_net}")

        findings = []
        for signal_via in signal_vias:
            sx, sy = xy(signal_via)
            candidates = []
            for reference_via in reference_vias:
                rx, ry = xy(reference_via)
                candidates.append((hypot(sx - rx, sy - ry), reference_via))
            distance_m, nearest = min(candidates, key=lambda item: item[0])
            findings.append(
                {
                    "signal_via": signal_via.name,
                    "signal_net": signal_via.net_name,
                    "signal_start_layer": signal_via.start_layer,
                    "signal_stop_layer": signal_via.stop_layer,
                    "nearest_reference_via": nearest.name,
                    "reference_start_layer": nearest.start_layer,
                    "reference_stop_layer": nearest.stop_layer,
                    "distance_mm": distance_m * 1000.0,
                    "maximum_distance_mm": maximum_distance_mm,
                    "status": "PASS" if distance_m <= maximum_distance_m else "REVIEW",
                }
            )
    finally:
        edb.close()

    report_file.parent.mkdir(parents=True, exist_ok=True)
    with report_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=findings[0].keys())
        writer.writeheader()
        writer.writerows(findings)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--signal-net", action="append", required=True)
    parser.add_argument("--reference-net", default="GND")
    parser.add_argument("--maximum-distance-mm", type=float, required=True)
    parser.add_argument("--report", type=Path, default=Path("ddr5_return_path_audit.csv"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    findings = audit_return_paths(
        args.source_edb,
        args.signal_net,
        args.reference_net,
        args.maximum_distance_mm,
        args.report,
        args.version,
    )
    review_count = sum(item["status"] == "REVIEW" for item in findings)
    print(f"Transitions checked: {len(findings)}")
    print(f"Transitions requiring review: {review_count}")
    print(f"Report: {args.report.resolve()}")


if __name__ == "__main__":
    main()

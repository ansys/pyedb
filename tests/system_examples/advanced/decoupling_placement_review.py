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

"""Review local decoupling around selected load components.

The script uses direct Components, Component, and PadstackInstance APIs. A
candidate capacitor must have one pin on the selected power net and one pin on
the reference net. Distance is measured from each load power pin to the nearest
power or reference pin on each qualifying capacitor.
"""

from __future__ import annotations

import argparse
import csv
from math import hypot
from pathlib import Path

from pyedb import Edb


def pin_xy(pin) -> tuple[float, float]:
    x, y = pin.position
    return float(x), float(y)


def review_decoupling(
    source_edb: Path,
    power_net: str,
    reference_net: str,
    load_components: list[str],
    maximum_distance_mm: float,
    report_file: Path,
    version: str,
) -> list[dict]:
    """Find the nearest connected decoupling capacitor for each load power pin."""
    maximum_distance_m = maximum_distance_mm / 1000.0
    edb = Edb(str(source_edb.resolve()), version=version)
    try:
        missing_components = [name for name in load_components if name not in edb.components.instances]
        if missing_components:
            raise ValueError(f"Load components not found: {', '.join(missing_components)}")

        qualifying_capacitors = []
        for refdes, capacitor in edb.components.capacitors.items():
            nets = {pin.net_name for pin in capacitor.pins.values()}
            if {power_net, reference_net}.issubset(nets):
                qualifying_capacitors.append((refdes, capacitor))
        if not qualifying_capacitors:
            raise RuntimeError(f"No capacitors were found between {power_net} and {reference_net}")

        findings = []
        for load_name in load_components:
            load = edb.components[load_name]
            load_pins = [pin for pin in load.pins.values() if pin.net_name == power_net]
            if not load_pins:
                findings.append(
                    {
                        "load_component": load_name,
                        "load_pin": "",
                        "nearest_capacitor": "",
                        "distance_mm": "",
                        "maximum_distance_mm": maximum_distance_mm,
                        "status": "NO_POWER_PIN",
                    }
                )
                continue

            for load_pin in load_pins:
                lx, ly = pin_xy(load_pin)
                candidates = []
                for capacitor_name, capacitor in qualifying_capacitors:
                    for capacitor_pin in capacitor.pins.values():
                        cx, cy = pin_xy(capacitor_pin)
                        candidates.append((hypot(lx - cx, ly - cy), capacitor_name, capacitor_pin.name))
                distance_m, capacitor_name, capacitor_pin_name = min(candidates, key=lambda item: item[0])
                findings.append(
                    {
                        "load_component": load_name,
                        "load_pin": load_pin.name,
                        "nearest_capacitor": capacitor_name,
                        "nearest_capacitor_pin": capacitor_pin_name,
                        "distance_mm": distance_m * 1000.0,
                        "maximum_distance_mm": maximum_distance_mm,
                        "status": "PASS" if distance_m <= maximum_distance_m else "REVIEW",
                    }
                )
    finally:
        edb.close()

    report_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for finding in findings for key in finding})
    with report_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(findings)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--power-net", required=True)
    parser.add_argument("--reference-net", default="GND")
    parser.add_argument("--load-component", action="append", required=True)
    parser.add_argument("--maximum-distance-mm", type=float, required=True)
    parser.add_argument("--report", type=Path, default=Path("decoupling_review.csv"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    findings = review_decoupling(
        args.source_edb,
        args.power_net,
        args.reference_net,
        args.load_component,
        args.maximum_distance_mm,
        args.report,
        args.version,
    )
    review_count = sum(item["status"] != "PASS" for item in findings)
    print(f"Load pins checked: {len(findings)}")
    print(f"Items requiring review: {review_count}")
    print(f"Report: {args.report.resolve()}")


if __name__ == "__main__":
    main()

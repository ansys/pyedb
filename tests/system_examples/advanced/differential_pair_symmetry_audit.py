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

"""Audit the physical symmetry of a high-speed differential pair.

The example compares routed path length, per-layer length, via count, via layer
spans, and padstack definitions using direct Net, Path, and PadstackInstance
objects from PyEDB.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyedb import Edb


def net_metrics(net) -> dict:
    """Extract physical topology metrics from a direct PyEDB Net object."""
    paths = [primitive for primitive in net.primitives if primitive.type == "path"]
    layer_names = sorted({path.layer_name for path in paths})
    per_layer_length = {layer: sum(path.length for path in paths if path.layer_name == layer) for layer in layer_names}
    via_spans = sorted(
        {
            (
                via.padstack_definition,
                via.start_layer,
                via.stop_layer,
                str(via.backdrill_type),
            )
            for via in net.padstack_instances
            if not via.is_pin
        }
    )
    return {
        "net": net.name,
        "path_count": len(paths),
        "total_length_m": sum(path.length for path in paths),
        "minimum_trace_width_m": net.get_smallest_trace_width(),
        "per_layer_length_m": per_layer_length,
        "via_count": sum(not via.is_pin for via in net.padstack_instances),
        "via_topologies": [
            {
                "padstack_definition": definition,
                "start_layer": start,
                "stop_layer": stop,
                "backdrill_type": backdrill,
            }
            for definition, start, stop, backdrill in via_spans
        ],
        "connected_components": sorted(net.components),
    }


def audit_pair(
    source_edb: Path,
    positive_net: str,
    negative_net: str,
    maximum_length_mismatch_mm: float,
    report_file: Path,
    version: str,
) -> dict:
    """Compare both legs and write a structured audit report."""
    edb = Edb(str(source_edb.resolve()), version=version)
    try:
        missing = [name for name in (positive_net, negative_net) if name not in edb.nets]
        if missing:
            raise ValueError(f"Differential-pair nets not found: {', '.join(missing)}")
        positive = net_metrics(edb.nets[positive_net])
        negative = net_metrics(edb.nets[negative_net])
    finally:
        edb.close()

    mismatch_m = abs(positive["total_length_m"] - negative["total_length_m"])
    layer_mismatch = sorted(set(positive["per_layer_length_m"]) ^ set(negative["per_layer_length_m"]))
    report = {
        "positive": positive,
        "negative": negative,
        "length_mismatch_mm": mismatch_m * 1000.0,
        "maximum_length_mismatch_mm": maximum_length_mismatch_mm,
        "via_count_mismatch": abs(positive["via_count"] - negative["via_count"]),
        "routing_layer_mismatch": layer_mismatch,
        "status": "PASS"
        if mismatch_m <= maximum_length_mismatch_mm / 1000.0
        and positive["via_count"] == negative["via_count"]
        and not layer_mismatch
        else "REVIEW",
    }
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--positive-net", required=True)
    parser.add_argument("--negative-net", required=True)
    parser.add_argument("--maximum-length-mismatch-mm", type=float, required=True)
    parser.add_argument("--report", type=Path, default=Path("differential_pair_audit.json"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    report = audit_pair(
        args.source_edb,
        args.positive_net,
        args.negative_net,
        args.maximum_length_mismatch_mm,
        args.report,
        args.version,
    )
    print(f"Status: {report['status']}")
    print(f"Length mismatch: {report['length_mismatch_mm']:.4f} mm")
    print(f"Via-count mismatch: {report['via_count_mismatch']}")
    print(f"Report: {args.report.resolve()}")


if __name__ == "__main__":
    main()

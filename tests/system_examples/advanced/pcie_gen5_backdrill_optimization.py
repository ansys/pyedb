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

"""Create a backdrilled PCIe channel variant with direct PyEDB APIs.

This standalone example copies an input EDB, identifies all vias on a selected
PCIe differential pair, reports their layer spans and padstack definitions,
and creates dielectric-filled backdrills on the working copy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from pyedb import Edb


def copy_aedb(source: Path, target: Path) -> Path:
    """Copy an AEDB directory so the source design remains unchanged."""
    source = source.resolve()
    target = target.resolve()
    if not source.is_dir() or source.suffix.lower() != ".aedb":
        raise FileNotFoundError(f"AEDB directory not found: {source}")
    if source == target:
        raise ValueError("Source and output AEDB paths must be different")
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def create_backdrilled_variant(
    source_edb: Path,
    output_edb: Path,
    positive_net: str,
    negative_net: str,
    target_layer: str,
    diameter: str,
    fill_material: str,
    permittivity: float,
    loss_tangent: float,
    version: str,
) -> dict:
    """Apply dielectric-filled backdrills to both legs of a differential pair."""
    working_edb = copy_aedb(source_edb, output_edb)
    edb = Edb(str(working_edb), version=version)
    try:
        missing_nets = [name for name in (positive_net, negative_net) if name not in edb.nets]
        if missing_nets:
            raise ValueError(f"Signal nets not found: {', '.join(missing_nets)}")

        signal_nets = [positive_net, negative_net]
        vias = edb.padstacks.get_via_instance_from_net(signal_nets)
        if not vias:
            raise RuntimeError("No vias were found on the selected differential pair")

        via_inventory = [
            {
                "name": via.name,
                "net": via.net_name,
                "padstack_definition": via.padstack_definition,
                "start_layer": via.start_layer,
                "stop_layer": via.stop_layer,
                "layer_range": list(via.layer_range_names),
                "existing_backdrill_type": str(via.backdrill_type),
            }
            for via in vias
        ]
        definitions = sorted({via.padstack_definition for via in vias})

        created = edb.padstacks.create_dielectric_filled_backdrills(
            layer=target_layer,
            diameter=diameter,
            material=fill_material,
            permittivity=permittivity,
            dielectric_loss_tangent=loss_tangent,
            padstack_definition=definitions,
            nets=signal_nets,
        )
        if not created:
            raise RuntimeError("PyEDB did not create any dielectric-filled backdrills")

        edb.padstacks.clear_instances_cache()
        updated_vias = edb.padstacks.get_via_instance_from_net(signal_nets)
        updated = [
            {
                "name": via.name,
                "net": via.net_name,
                "backdrill_type": str(via.backdrill_type),
                "backdrill_layer": str(via.backdrill_layer),
                "backdrill_diameter": str(via.backdrill_diameter),
                "backdrill_offset": str(via.backdrill_offset),
            }
            for via in updated_vias
        ]
        edb.save()
    finally:
        edb.close()

    report = {
        "source_edb": str(source_edb.resolve()),
        "output_edb": str(working_edb),
        "signal_nets": signal_nets,
        "target_layer": target_layer,
        "diameter": diameter,
        "fill_material": fill_material,
        "padstack_definitions": definitions,
        "before": via_inventory,
        "after": updated,
    }
    report_path = output_edb.parent / "pcie_backdrill_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--output-edb", type=Path, required=True)
    parser.add_argument("--positive-net", required=True)
    parser.add_argument("--negative-net", required=True)
    parser.add_argument("--target-layer", required=True)
    parser.add_argument("--diameter", default="0.25mm")
    parser.add_argument("--fill-material", default="EPON_827")
    parser.add_argument("--permittivity", type=float, default=3.8)
    parser.add_argument("--loss-tangent", type=float, default=0.015)
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    report = create_backdrilled_variant(
        args.source_edb,
        args.output_edb,
        args.positive_net,
        args.negative_net,
        args.target_layer,
        args.diameter,
        args.fill_material,
        args.permittivity,
        args.loss_tangent,
        args.version,
    )
    print(f"Updated {len(report['after'])} signal vias")
    print(f"Working EDB: {report['output_edb']}")


if __name__ == "__main__":
    main()

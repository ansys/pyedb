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

"""Prepare a multi-location SIwave PDN model using direct PyEDB APIs.

The script copies an input EDB, validates a power rail and its components,
creates circuit ports between the power and reference nets at the VRM and load
components, creates a SIwave setup, and saves an analysis-ready working EDB.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from pyedb import Edb


def copy_aedb(source: Path, target: Path) -> Path:
    source = source.resolve()
    target = target.resolve()
    if not source.is_dir() or source.suffix.lower() != ".aedb":
        raise FileNotFoundError(source)
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def build_pdn_model(
    source_edb: Path,
    output_edb: Path,
    power_net: str,
    reference_net: str,
    vrm_component: str,
    load_components: list[str],
    setup_name: str,
    version: str,
) -> dict:
    """Create PDN observation ports and a direct SIwave simulation setup."""
    working_edb = copy_aedb(source_edb, output_edb)
    edb = Edb(str(working_edb), version=version)
    try:
        missing_nets = [name for name in (power_net, reference_net) if name not in edb.nets]
        if missing_nets:
            raise ValueError(f"PDN nets not found: {', '.join(missing_nets)}")
        components = [vrm_component, *load_components]
        missing_components = [name for name in components if name not in edb.components.instances]
        if missing_components:
            raise ValueError(f"Components not found: {', '.join(missing_components)}")

        port_records = []
        for component_name in components:
            component = edb.components[component_name]
            component_nets = set(component.nets)
            required_nets = {power_net, reference_net}
            if not required_nets.issubset(component_nets):
                raise ValueError(f"{component_name} is not connected to both {power_net} and {reference_net}")
            port_name = f"Z_{component_name}_{power_net}"
            created_name = edb.excitation_manager.create_circuit_port_on_net(
                component_name,
                power_net,
                component_name,
                reference_net,
                50.0,
                port_name,
            )
            if not created_name:
                raise RuntimeError(f"Failed to create circuit port {port_name}")
            port_records.append(
                {
                    "port": created_name,
                    "component": component_name,
                    "power_net": power_net,
                    "reference_net": reference_net,
                }
            )

        setup = edb.simulation_setups.create_siwave_setup(setup_name)
        if setup is None:
            raise RuntimeError(f"Failed to create SIwave setup {setup_name}")
        setup.settings.enabled = True
        edb.save()
        available_setups = sorted(edb.simulation_setups.siwave)
    finally:
        edb.close()

    report = {
        "working_edb": str(working_edb),
        "power_net": power_net,
        "reference_net": reference_net,
        "ports": port_records,
        "siwave_setups": available_setups,
        "next_step": "Open the working EDB in SIwave and define the project-specific frequency sweep.",
    }
    report_file = output_edb.parent / "pdn_port_map.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--output-edb", type=Path, required=True)
    parser.add_argument("--power-net", required=True)
    parser.add_argument("--reference-net", default="GND")
    parser.add_argument("--vrm-component", required=True)
    parser.add_argument("--load-component", action="append", required=True)
    parser.add_argument("--setup-name", default="PDN_SYZ")
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    report = build_pdn_model(
        args.source_edb,
        args.output_edb,
        args.power_net,
        args.reference_net,
        args.vrm_component,
        args.load_component,
        args.setup_name,
        args.version,
    )
    print(f"Ports created: {len(report['ports'])}")
    print(f"Working EDB: {report['working_edb']}")


if __name__ == "__main__":
    main()

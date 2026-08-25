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

"""Discover and batch high-speed channels for HFSS."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyedb.workflows.sipi.hfss_auto_configuration import create_hfss_auto_configuration

from ..common import load_inventory


def batch_channels(source_edb: Path, output_dir: Path, inventory_file: Path, version: str) -> list:
    inventory = load_inventory(inventory_file)
    batch_folder = output_dir / "hfss_batches"
    batch_folder.mkdir(parents=True, exist_ok=True)
    config = create_hfss_auto_configuration(
        source_edb_path=str(source_edb),
        target_edb_path=str(output_dir / "hfss_channels.aedb"),
        batch_group_folder=str(batch_folder),
        ansys_version=version,
        reference_net=inventory["reference_net"],
        batch_size=30,
        port_type="coaxial",
        extent_type="convex_hull",
        cutout_expansion="3mm",
        auto_mesh_seeding=True,
    )
    pattern = inventory.get("si_pattern")
    if pattern and not pattern.startswith("<"):
        config.auto_populate_batch_groups(pattern=[pattern])
    else:
        config.signal_nets = list(inventory["differential_pair"])
        config.auto_populate_batch_groups()

    summary = []
    for group in config.batch_groups:
        summary.append({"name": group.name, "nets": list(group.nets)})
        print(group.name, list(group.nets))
    if not summary:
        raise RuntimeError("No HFSS batch groups were discovered")

    config.add_simulation_setup(
        meshing_frequency="10GHz",
        maximum_pass_number=15,
        start_frequency="1GHz",
        stop_frequency="20GHz",
        frequency_step="0.1GHz",
    )
    config.create_projects()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_edb", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    print(batch_channels(args.source_edb, args.output_dir, args.inventory, args.version))


if __name__ == "__main__":
    main()

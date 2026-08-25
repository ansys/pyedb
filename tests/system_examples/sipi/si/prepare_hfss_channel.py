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

"""Prepare one known differential channel for HFSS 3D Layout."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyedb import Edb

from ..common import copy_edb, directory_checksum, load_inventory, require_names


def prepare_channel(source_edb: Path, output_dir: Path, inventory_file: Path, version: str) -> dict:
    inventory = load_inventory(inventory_file)
    source_hash = directory_checksum(source_edb)
    working_edb = copy_edb(source_edb, output_dir / "hfss_channel.aedb")
    config_file = output_dir / "hfss_channel.json"
    p_net, n_net = inventory["differential_pair"]
    tx, rx = inventory["si_endpoints"]
    reference = inventory["reference_net"]

    edb = Edb(str(working_edb), version=version)
    try:
        require_names(edb.components.components, [tx, rx], "endpoint components")
        require_names(edb.nets.nets, [p_net, n_net, reference], "channel nets")
        cfg = edb.configuration.create_config_builder()
        cfg.nets.add_signal_nets([p_net, n_net])
        cfg.nets.add_reference_nets([reference])
        cfg.operations.add_cutout(
            signal_nets=cfg.nets.signal_nets,
            reference_nets=cfg.nets.reference_nets,
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )
        cfg.ports.add_coax_port(reference_designator=tx, net_list=[p_net, n_net])
        cfg.ports.add_coax_port(reference_designator=rx, net_list=[p_net, n_net])
        setup = cfg.setups.add_hfss_setup(name="HFSS_SI", adapt_type="broadband")
        setup.set_broadband_adaptive(low_freq="5GHz", high_freq="16GHz", max_passes=15, max_delta=0.02)
        setup.set_auto_mesh_operation(enabled=True, trace_ratio_seeding=3.0, signal_via_side_number=12)
        setup.add_frequency_sweep(name="Sweep_SI", start="1GHz", stop="20GHz", step_or_count="0.1GHz")
        cfg.to_json(str(config_file))
        edb.configuration.run(cfg)
    finally:
        edb.close()

    if directory_checksum(source_edb) != source_hash:
        raise RuntimeError("The source EDB changed during the example")
    return {"working_edb": str(working_edb), "configuration": str(config_file)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_edb", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    print(prepare_channel(args.source_edb, args.output_dir, args.inventory, args.version))


if __name__ == "__main__":
    main()

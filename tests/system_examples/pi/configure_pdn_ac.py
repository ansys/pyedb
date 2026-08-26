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

"""Configure a PI-oriented SIwave AC analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyedb import Edb
from pyedb.configuration.cfg_ports_sources import CfgTerminalInfo

from ..common import copy_edb, load_inventory, require_names


def configure_pdn_ac(source_edb: Path, output_dir: Path, inventory_file: Path, version: str) -> dict:
    inventory = load_inventory(inventory_file)
    working_edb = copy_edb(source_edb, output_dir / "pdn_ac.aedb")
    config_file = output_dir / "pdn_ac.json"
    power = inventory["power_net"]
    ground = inventory["reference_net"]
    vrm = inventory["vrm_component"]
    load = inventory["load_component"]

    edb = Edb(str(working_edb), version=version)
    try:
        require_names(edb.components.components, [vrm, load], "PI components")
        require_names(edb.nets.nets, [power, ground], "PI nets")
        cfg = edb.configuration.create_config_builder()
        cfg.nets.add_signal_nets([power])
        cfg.nets.add_reference_nets([ground])
        cfg.pin_groups.add(name="VRM_POWER", reference_designator=vrm, net=power)
        cfg.pin_groups.add(name="VRM_GND", reference_designator=vrm, net=ground)
        cfg.pin_groups.add(name="LOAD_POWER", reference_designator=load, net=power)
        cfg.pin_groups.add(name="LOAD_GND", reference_designator=load, net=ground)
        cfg.sources.add_voltage_source(
            name="VRM_SOURCE",
            positive_terminal=CfgTerminalInfo.pin_group("VRM_POWER"),
            negative_terminal=CfgTerminalInfo.pin_group("VRM_GND"),
            magnitude=1.0,
            impedance="1mohm",
            reference_designator=vrm,
        )
        cfg.ports.add_circuit_port(
            name="PDN_OBSERVATION",
            positive_terminal=CfgTerminalInfo.pin_group("LOAD_POWER"),
            negative_terminal=CfgTerminalInfo.pin_group("LOAD_GND"),
            impedance=50.0,
        )
        setup = cfg.setups.add_siwave_ac_setup(name="PDN_AC", pi_slider_position=2, use_si_settings=False)
        setup.add_frequency_sweep(
            name="PDN_SWEEP",
            start="1kHz",
            stop="1GHz",
            step_or_count=201,
            distribution="log_count",
        )
        cfg.to_json(str(config_file))
        edb.configuration.run(cfg)
    finally:
        edb.close()
    return {"working_edb": str(working_edb), "configuration": str(config_file)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_edb", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    print(configure_pdn_ac(args.source_edb, args.output_dir, args.inventory, args.version))


if __name__ == "__main__":
    main()

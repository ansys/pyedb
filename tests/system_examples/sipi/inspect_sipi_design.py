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

"""Inspect the generic board used by the SI/PI examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import copy_edb, load_inventory, require_names

from pyedb import Edb


def inspect_design(source_edb: Path, output_dir: Path, inventory_file: Path, version: str) -> dict:
    inventory = load_inventory(inventory_file)
    working_edb = copy_edb(source_edb, output_dir / "inspect_sipi_design.aedb")
    edb = Edb(str(working_edb), version=version)
    try:
        components = edb.components.components
        nets = edb.nets.nets
        require_names(components, list(inventory["si_endpoints"]), "SI endpoint components")
        require_names(
            components,
            [inventory["vrm_component"], inventory["load_component"]],
            "PI components",
        )
        require_names(
            nets,
            list(inventory["differential_pair"]) + [inventory["power_net"], inventory["reference_net"]],
            "nets",
        )
        result = {
            "working_edb": str(working_edb),
            "components": sorted(components),
            "nets": sorted(nets),
            "layers": sorted(edb.stackup.layers),
            "ports": sorted(edb.ports),
            "setups": sorted(edb.setups),
            "inventory": inventory,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "sipi_design_inventory.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result
    finally:
        edb.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_edb", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    result = inspect_design(args.source_edb, args.output_dir, args.inventory, args.version)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

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

"""Create a small transmission-line EDB with PyEDB."""

from __future__ import annotations  # noqa: I001

import argparse
import shutil
from pathlib import Path

from pyedb import Edb


def build_transmission_line(output_dir: Path, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    edb_path = output_dir / "simple_si_line.aedb"
    if edb_path.exists():
        shutil.rmtree(edb_path)

    edb = Edb(str(edb_path), version=version)
    try:
        edb.stackup.add_layer("BOTTOM")
        edb.stackup.add_layer(
            "DIELECTRIC",
            base_layer="BOTTOM",
            layer_type="dielectric",
            thickness="0.2mm",
            material="FR4_epoxy",
        )
        edb.stackup.add_layer(
            "TOP",
            base_layer="DIELECTRIC",
            thickness="35um",
            material="copper",
        )

        edb.modeler.create_trace(
            [["0mm", "0mm"], ["30mm", "0mm"]],
            "TOP",
            width="0.2mm",
            net_name="SIG",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        edb.modeler.create_polygon(
            [["-1mm", "-5mm"], ["31mm", "-5mm"], ["31mm", "5mm"], ["-1mm", "5mm"]],
            "BOTTOM",
            net_name="GND",
        )
        edb.padstacks.create("signal_via")
        edb.padstacks.place(["0mm", "0mm"], "signal_via", net_name="SIG")
        edb.padstacks.place(["30mm", "0mm"], "signal_via", net_name="SIG")
        edb.save()
    finally:
        edb.close()

    check = Edb(str(edb_path), version=version)
    try:
        if "SIG" not in check.nets.nets or "GND" not in check.nets.nets:
            raise RuntimeError("Generated signal or reference net is missing")
    finally:
        check.close()
    return edb_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("sipi_output"))
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    print(build_transmission_line(args.output_dir, args.version))


if __name__ == "__main__":
    main()

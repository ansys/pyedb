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

"""Generate HFSS cutout variants for a scope-sensitivity study.

Each variant is created from the same source EDB with the direct Edb.cutout
API. The script records output size and retained object counts so an engineer
can compare model scope before solving the variants.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyedb import Edb

VARIANTS = (
    ("Bounding", "2mm"),
    ("ConvexHull", "2mm"),
    ("ConvexHull", "5mm"),
    ("Conforming", "2mm"),
)


def directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def generate_variants(
    source_edb: Path,
    positive_net: str,
    negative_net: str,
    reference_net: str,
    output_directory: Path,
    version: str,
) -> list[dict]:
    """Create independent Bounding, ConvexHull, and Conforming cutouts."""
    source_edb = source_edb.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    results = []
    for extent_type, expansion_size in VARIANTS:
        variant_name = f"{extent_type.lower()}_{expansion_size}"
        output_edb = output_directory / f"{variant_name}.aedb"
        edb = Edb(str(source_edb), version=version)
        try:
            missing = [name for name in (positive_net, negative_net, reference_net) if name not in edb.nets]
            if missing:
                raise ValueError(f"Nets not found: {', '.join(missing)}")
            result = edb.cutout(
                signal_list=[positive_net, negative_net],
                reference_list=[reference_net],
                extent_type=extent_type,
                expansion_size=expansion_size,
                output_aedb_path=str(output_edb),
                open_cutout_at_end=False,
                remove_single_pin_components=True,
                check_terminals=True,
                preserve_components_with_model=True,
            )
            if result is False:
                raise RuntimeError(f"Cutout failed for {extent_type} {expansion_size}")
        finally:
            edb.close()

        check = Edb(str(output_edb), version=version)
        try:
            results.append(
                {
                    "extent_type": extent_type,
                    "expansion_size": expansion_size,
                    "output_edb": str(output_edb.resolve()),
                    "directory_size_bytes": directory_size(output_edb),
                    "net_count": len(check.nets),
                    "component_count": len(check.components.instances),
                    "primitive_count": len(check.layout.primitives),
                    "padstack_instance_count": len(check.padstacks.instances),
                    "terminal_count": len(check.terminals),
                }
            )
        finally:
            check.close()

    manifest = output_directory / "cutout_scope_study.json"
    manifest.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-edb", type=Path, required=True)
    parser.add_argument("--positive-net", required=True)
    parser.add_argument("--negative-net", required=True)
    parser.add_argument("--reference-net", default="GND")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--version", default="2026.1")
    args = parser.parse_args()
    results = generate_variants(
        args.source_edb,
        args.positive_net,
        args.negative_net,
        args.reference_net,
        args.output_directory,
        args.version,
    )
    print("Cutout scope study")
    for item in results:
        print(
            f"{item['extent_type']:<12} {item['expansion_size']:<5} {item['directory_size_bytes'] / 1_000_000:.2f} MB"
        )


if __name__ == "__main__":
    main()

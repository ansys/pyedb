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

"""Launch with ``python -m pyedb.viewer board.aedb`` or ``--demo``."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Interactive PySide6/RHI 2D EDB layout viewer")
    parser.add_argument("path", nargs="?", type=Path, help="Existing .aedb directory")
    parser.add_argument(
        "--backend",
        choices=("auto", "vulkan", "d3d11", "metal"),
        default=None,
        help="Graphics API (default: platform native)",
    )
    parser.add_argument("--demo", action="store_true", help="Show a synthetic board without an EDB session")
    parser.add_argument("--version", help="EDB server version, for example 2026.1")
    parser.add_argument("--layer", action="append", help="Include this layer (repeatable)")
    parser.add_argument("--net", action="append", help="Include this net (repeatable)")
    precision = parser.add_mutually_exclusive_group()
    precision.add_argument("--arc-segments", type=int, help="Use a fixed subdivision count instead of adaptive chords")
    precision.add_argument(
        "--chord-error", type=float, default=0.002, help="Maximum chord error in mm (default: 0.002)"
    )
    parser.add_argument("--analytic-traces", action="store_true", help="Preserve analytic traces for deep zoom")
    parser.add_argument("--exact-component-bounds", action="store_true", help="Read exact source component envelopes")
    parser.add_argument(
        "--no-progressive", action="store_true", help="Wait for complete geometry before displaying copper"
    )
    colors = parser.add_mutually_exclusive_group()
    colors.add_argument(
        "--color-by-net",
        action="store_true",
        dest="color_by_net",
        help="Use PyEDB's existing network palette (default)",
    )
    colors.add_argument("--color-by-layer", action="store_false", dest="color_by_net", help="Use source layer colors")
    parser.set_defaults(color_by_net=True)
    args = parser.parse_args(argv)
    if args.demo == (args.path is not None):
        parser.error("Provide an AEDB directory or --demo.")
    from pyedb.viewer import launch_viewer

    if args.demo:
        from pyedb.viewer.demo import demo_scene

        launch_viewer(scene=demo_scene(), color_by_net=args.color_by_net, backend=args.backend)
        return
    if not args.path.is_dir() or args.path.suffix.lower() != ".aedb":
        parser.error("path must be an existing .aedb directory.")
    from pyedb import Edb

    edb = Edb(edbpath=str(args.path.resolve()), grpc=True, isreadonly=True, version=args.version)
    try:
        edb.view_layout(
            layers=args.layer,
            backend=args.backend,
            nets=args.net,
            arc_segments=args.arc_segments,
            color_by_net=args.color_by_net,
            analytic_traces=args.analytic_traces,
            exact_component_bounds=args.exact_component_bounds,
            chord_error=args.chord_error,
            progressive=not args.no_progressive,
        )
    finally:
        edb.close()


if __name__ == "__main__":
    main()

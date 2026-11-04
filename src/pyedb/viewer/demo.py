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

"""Small synthetic board for trying the renderer without an EDB license."""

from __future__ import annotations

import math

from pyedb.viewer.scene import LayoutScene, SceneComponent, SceneLayer, ScenePad, ScenePolygon, SceneTrace


def _rectangle(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float], ...]:
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def _circle(x: float, y: float, radius: float) -> tuple[tuple[float, float], ...]:
    return tuple(
        (x + radius * math.cos(i * math.tau / 64), y + radius * math.sin(i * math.tau / 64)) for i in range(64)
    )


def demo_scene() -> LayoutScene:
    """Return top copper with overlapping voids over a lower ground plane."""
    layers = (
        SceneLayer("TOP", (0.95, 0.61, 0.20, 1.0)),
        SceneLayer("INNER1", (0.27, 0.78, 0.62, 1.0)),
        SceneLayer("BOTTOM", (0.29, 0.53, 0.94, 1.0)),
    )
    polygons = [
        ScenePolygon(1, "BOTTOM", "GND", _rectangle(-48, -28, 48, 28), (_circle(-42, -22, 2), _circle(42, 22, 2))),
        ScenePolygon(2, "INNER1", "GND", _rectangle(-39, -21, 39, 21), (_rectangle(-16, -9, 17, 10),)),
        ScenePolygon(
            3,
            "TOP",
            "GND",
            ((-46, -26), (46, -26), (46, 12), (29, 12), (29, 26), (-46, 26)),
            (_rectangle(-25, -15, 5, 15), _rectangle(-5, -7, 23, 7), _circle(-42, -22, 2)),
        ),
    ]
    for index in range(12):
        x = -34 + index * 6
        polygons.append(ScenePolygon(10 + index, "TOP", "DATA", _rectangle(x, 18, x + 2.2, 22)))
        polygons.append(ScenePolygon(30 + index, "BOTTOM", "DATA", _rectangle(x, -24, x + 2.2, -20)))
    traces, pads = [], []
    for index in range(6):
        y = -14 + index * 5
        traces.append(SceneTrace(50 + index, "TOP", "SIGNAL", (28, y), (42, y), 0.65))
        for layer in ("TOP", "INNER1", "BOTTOM"):
            pads.append(ScenePad(70 + index, layer, "SIGNAL", (28, y), (2.8, 2.8), hole_radius=0.65))
    traces.append(SceneTrace(90, "TOP", "DATA", (-12, 0), (0, 12), 1.2, (0, 0), -math.pi / 2))
    pads.append(ScenePad(110, "TOP", "DATA", (-33, 20), (2.2, 4), "rectangle", component="J1", pin_name="1"))
    return LayoutScene(
        layers,
        tuple(polygons),
        "Synthetic board",
        (
            "Synthetic millimeter-based scene. No AEDB was opened.",
            "The two overlapping TOP voids form a union; lower copper remains visible through both.",
        ),
        traces=tuple(traces),
        pads=tuple(pads),
        components=(
            SceneComponent(100, "U1", "TOP", ("GND", "DATA"), (-15, -10, 16, 14)),
            SceneComponent(101, "J1", "TOP", ("DATA",), (-35, 17, 35, 23)),
            SceneComponent(102, "J2", "BOTTOM", ("DATA",), (-35, -25, 35, -19), "bottom"),
        ),
    )

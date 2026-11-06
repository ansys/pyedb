# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""World-anchored, adaptive shader grid. Navigation updates uniforms only."""

import math


def grid_spacing(scale, pixel_ratio=1.0):
    """Choose a readable 1/2/5 millimeter step at the current zoom."""
    target = 20.0 / (scale * pixel_ratio)
    base = 10.0 ** math.floor(math.log10(target))
    return min((base * multiple for multiple in (1, 2, 5, 10)), key=lambda step: abs(math.log(step / target)))


class GridRenderer:
    def __init__(self):
        self.spacing = 1.0

    def draw(self, device, uniforms, camera, pixel_ratio, visible):
        self.spacing = grid_spacing(camera.scale, pixel_ratio)
        values = uniforms.copy()
        values[38:40] = self.spacing, visible
        major = self.spacing * 5
        values[40:44] = (
            camera.center_x % self.spacing,
            camera.center_y % self.spacing,
            camera.center_x % major,
            camera.center_y % major,
        )
        device.draw("grid", values, layout="fullscreen", count=3, blend="replace")

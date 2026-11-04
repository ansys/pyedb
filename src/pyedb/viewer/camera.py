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

"""Orthographic camera in millimeters and logical screen pixels."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class Camera:
    center_x: float = 0.0
    center_y: float = 0.0
    scale: float = 10.0
    width: float = 1.0
    height: float = 1.0
    mirror: bool = False

    def resize(self, width: float, height: float) -> None:
        self.width, self.height = max(float(width), 1.0), max(float(height), 1.0)

    def fit(
        self,
        bounds: tuple[float, float, float, float] | None,
        padding: tuple[float, float, float, float] = (0, 0, 0, 0),
    ) -> None:
        if bounds is None:
            self.center_x = self.center_y = 0.0
            self.scale = 10.0
            return
        x0, y0, x1, y1 = bounds
        left, top, right, bottom = padding
        width = max(self.width - left - right, 1)
        height = max(self.height - top - bottom, 1)
        self.center_x, self.center_y = x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2
        self.scale = 0.9 * min(width / max(x1 - x0, 1e-9), height / max(y1 - y0, 1e-9))
        self.scale = min(max(self.scale, 1e-6), 1e9)
        self.center_x += (-1 if self.mirror else 1) * (right - left) / (2 * self.scale)
        self.center_y += (top - bottom) / (2 * self.scale)

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        sign = -1.0 if self.mirror else 1.0
        return self.center_x + sign * (x - self.width / 2) / self.scale, self.center_y - (
            y - self.height / 2
        ) / self.scale

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        sign = -1.0 if self.mirror else 1.0
        return self.width / 2 + sign * (x - self.center_x) * self.scale, self.height / 2 - (
            y - self.center_y
        ) * self.scale

    def pan(self, dx: float, dy: float) -> None:
        sign = -1.0 if self.mirror else 1.0
        self.center_x -= sign * dx / self.scale
        self.center_y += dy / self.scale

    def zoom_at(self, x: float, y: float, factor: float) -> None:
        if not math.isfinite(factor) or factor <= 0:
            raise ValueError("Zoom factor must be positive and finite.")
        before = self.screen_to_world(x, y)
        self.scale = min(max(self.scale * factor, 1e-6), 1e9)
        after = self.screen_to_world(x, y)
        self.center_x += before[0] - after[0]
        self.center_y += before[1] - after[1]

    def visible(self, bounds: tuple[float, float, float, float]) -> bool:
        x0, y0, x1, y1 = bounds
        half_w, half_h = self.width / (2 * self.scale), self.height / (2 * self.scale)
        return not (
            x1 < self.center_x - half_w
            or x0 > self.center_x + half_w
            or y1 < self.center_y - half_h
            or y0 > self.center_y + half_h
        )

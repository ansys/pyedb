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

"""PyEDB materials shared by the CPU copper pass and GPU analytic primitives."""

from __future__ import annotations

from pyedb.generic.constants import CSS4_COLORS

NET_COLORS = tuple(tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)) for value in CSS4_COLORS.values())
BACKGROUND_COLOR = (1.0, 1.0, 1.0, 1.0)
DRILL_COLOR = (0.6, 0.6, 0.6, 1.0)
# Component envelope color sampled from the supplied reference (#b87333).
COMPONENT_OUTLINE_COLOR = (184 / 255, 115 / 255, 51 / 255)
COMPONENT_COLORS = {"top": COMPONENT_OUTLINE_COLOR, "bottom": COMPONENT_OUTLINE_COLOR}
# Reserved interaction colors, outside CSS4_COLORS. The dark keyline makes
# these states distinguishable even over a visually similar network material.
HOVER_COLOR = (0 / 255, 87 / 255, 255 / 255)  # #0057FF
SELECTION_COLOR = (255 / 255, 0 / 255, 110 / 255)  # #FF006E
HIGHLIGHT_KEYLINE_COLOR = (17 / 255, 24 / 255, 39 / 255)  # #111827
# Thin shape outlines share the near-black keyline.
OUTLINE_COLOR = HIGHLIGHT_KEYLINE_COLOR


def net_color(net_id: int) -> tuple[float, ...] | None:
    """Match nets.plot's existing CSS4 palette; id zero retains layer color."""
    return NET_COLORS[(net_id - 1) % len(NET_COLORS)] if net_id else None

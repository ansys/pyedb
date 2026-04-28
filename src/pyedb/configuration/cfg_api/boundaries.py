# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""HFSS boundary / open-region builder API."""

from __future__ import annotations

from typing import Optional

from pyedb.configuration.cfg_boundaries import CfgBoundaries


class BoundariesConfig(CfgBoundaries):
    """Fluent builder for the ``boundaries`` configuration section.

    Inherits all fields from :class:`~pyedb.configuration.cfg_boundaries.CfgBoundaries`.
    All fields default to ``None`` so ``to_dict()`` only emits explicitly-set keys.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    # ── convenience setters ───────────────────────────────────────────────

    def set_radiation_boundary(self, use_open_region: bool = True):
        self.use_open_region = use_open_region
        self.open_region_type = "radiation"

    def set_pml_boundary(self, operating_freq, radiation_level: float = 20, is_pml_visible: bool = False):
        self.use_open_region = True
        self.open_region_type = "pml"
        self.operating_freq = operating_freq
        self.radiation_level = radiation_level
        self.is_pml_visible = is_pml_visible

    def set_air_box_extents(
        self,
        horizontal_size,
        horizontal_is_multiple: bool = False,
        positive_vertical_size=0.15,
        positive_vertical_is_multiple: bool = False,
        negative_vertical_size=0.15,
        negative_vertical_is_multiple: bool = False,
        sync: bool = False,
        truncate_at_ground: bool = False,
    ):
        PD = CfgBoundaries.PaddingData
        self.air_box_horizontal_extent = PD(size=horizontal_size, is_multiple=horizontal_is_multiple)
        self.air_box_positive_vertical_extent = PD(size=positive_vertical_size, is_multiple=positive_vertical_is_multiple)
        self.air_box_negative_vertical_extent = PD(size=negative_vertical_size, is_multiple=negative_vertical_is_multiple)
        self.sync_air_box_vertical_extent = sync
        self.truncate_air_box_at_ground = truncate_at_ground

    def set_extent(self, extent_type: str = "BoundingBox", base_polygon: Optional[str] = None, truncate_air_box_at_ground: bool = False):
        self.extent_type = extent_type
        if base_polygon:
            self.base_polygon = base_polygon
        self.truncate_air_box_at_ground = truncate_air_box_at_ground

    def set_dielectric_extent(self, extent_type: str = "BoundingBox", expansion_size=0, is_multiple: bool = False, base_polygon: Optional[str] = None, honor_user_dielectric: bool = False):
        self.dielectric_extent_type = extent_type
        self.dielectric_extent_size = CfgBoundaries.PaddingData(size=expansion_size, is_multiple=is_multiple)
        if base_polygon:
            self.dielectric_base_polygon = base_polygon
        if honor_user_dielectric:
            self.honor_user_dielectric = honor_user_dielectric

    def to_dict(self) -> dict:
        """Serialise only explicitly-set (non-None / non-default-False) fields."""
        raw = self.model_dump(exclude_none=True)
        # honor_user_dielectric defaults to False in the root model — omit unless True
        if not self.honor_user_dielectric:
            raw.pop("honor_user_dielectric", None)
        return raw

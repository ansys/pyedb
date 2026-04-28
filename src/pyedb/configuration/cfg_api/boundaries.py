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

from typing import Optional, Union


class BoundariesConfig:
    """Fluent builder for the ``boundaries`` configuration section.

    All attributes default to ``None`` so that ``to_dict()`` only emits
    keys that have been explicitly set.
    """

    class _PaddingData:
        def __init__(self, size, is_multiple=False):
            self.size = size
            self.is_multiple = is_multiple

        def to_dict(self):
            return {"size": self.size, "is_multiple": self.is_multiple}

    def __init__(self):
        self.use_open_region: Optional[bool] = None
        self.open_region_type: Optional[str] = None
        self.operating_freq = None
        self.radiation_level: Optional[float] = None
        self.is_pml_visible: Optional[bool] = None
        self.air_box_horizontal_extent = None
        self.air_box_positive_vertical_extent = None
        self.air_box_negative_vertical_extent = None
        self.sync_air_box_vertical_extent: Optional[bool] = None
        self.truncate_air_box_at_ground: Optional[bool] = None
        self.extent_type: Optional[str] = None
        self.base_polygon: Optional[str] = None
        self.dielectric_extent_type: Optional[str] = None
        self.dielectric_extent_size = None
        self.dielectric_base_polygon: Optional[str] = None
        self.honor_user_dielectric: Optional[bool] = None

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
        self.air_box_horizontal_extent = self._PaddingData(horizontal_size, horizontal_is_multiple)
        self.air_box_positive_vertical_extent = self._PaddingData(positive_vertical_size, positive_vertical_is_multiple)
        self.air_box_negative_vertical_extent = self._PaddingData(negative_vertical_size, negative_vertical_is_multiple)
        self.sync_air_box_vertical_extent = sync
        self.truncate_air_box_at_ground = truncate_at_ground

    def set_extent(self, extent_type: str = "BoundingBox", base_polygon: Optional[str] = None, truncate_air_box_at_ground: bool = False):
        self.extent_type = extent_type
        if base_polygon:
            self.base_polygon = base_polygon
        self.truncate_air_box_at_ground = truncate_air_box_at_ground

    def set_dielectric_extent(self, extent_type: str = "BoundingBox", expansion_size=0, is_multiple: bool = False, base_polygon: Optional[str] = None, honor_user_dielectric: bool = False):
        self.dielectric_extent_type = extent_type
        self.dielectric_extent_size = self._PaddingData(expansion_size, is_multiple)
        if base_polygon:
            self.dielectric_base_polygon = base_polygon
        self.honor_user_dielectric = honor_user_dielectric if honor_user_dielectric else None

    def to_dict(self) -> dict:
        data = {}
        for key in (
            "use_open_region", "open_region_type", "operating_freq", "radiation_level",
            "is_pml_visible", "sync_air_box_vertical_extent", "truncate_air_box_at_ground",
            "extent_type", "base_polygon", "dielectric_extent_type", "dielectric_base_polygon",
            "honor_user_dielectric",
        ):
            val = getattr(self, key)
            if val is not None:
                data[key] = val
        for key in ("air_box_horizontal_extent", "air_box_positive_vertical_extent",
                    "air_box_negative_vertical_extent", "dielectric_extent_size"):
            val = getattr(self, key)
            if val is not None:
                data[key] = val.to_dict()
        return data

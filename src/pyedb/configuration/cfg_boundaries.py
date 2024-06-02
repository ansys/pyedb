# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from enum import Enum


class CfgBoundaries:
    def __init__(self, pdata, boundaries_dict):
        self._pedb = pdata._pedb
        self._boundaries_dict = boundaries_dict
        self.open_region = self._boundaries_dict.get("open_region", None)
        self._map_open_region_type()
        self.pml_visible = self._boundaries_dict.get("pml_visible", None)
        self.pml_operation_frequency = self._boundaries_dict.get("pml_operation_frequency", None)
        self.pml_radiation_factor = self._boundaries_dict.get("pml_radiation_factor", None)
        self._map_dielectric_extend_type()
        self.dielectric_base_polygon = self._boundaries_dict.get("dielectric_base_polygon", None)
        self.horizontal_padding = self._boundaries_dict.get("horizontal_padding", None)
        self.honor_primitives_on_dielectric_layers = self._boundaries_dict.get(
            "honor_primitives_on_dielectric_layers", False
        )
        self._map_air_box_extend_type()
        self.air_box_base_polygon = self._boundaries_dict.get("air_box_base_polygon", None)
        self.air_box_truncate_model_ground_layers = self._boundaries_dict.get(
            "air_box_truncate_model_ground_layers", None
        )
        self.air_box_horizontal_padding = self._boundaries_dict.get("air_box_horizontal_padding", None)
        self.air_box_positive_vertical_padding = self._boundaries_dict.get("air_box_positive_vertical_padding", None)
        self.air_box_negative_vertical_padding = self._boundaries_dict.get("air_box_negative_vertical_padding", None)

    def _map_air_box_extend_type(self):
        air_box_type = self._boundaries_dict.get("air_box_extents_type", None)
        if air_box_type == "bounding_box":
            self.air_box_extents_type = self.ExtentType.BOUNDING_BOX
        elif air_box_type == "conformal":
            self.air_box_extents_type = self.ExtentType.CONFORMAL
        elif air_box_type == "convex_hull":
            self.air_box_extents_type = self.ExtentType.CONVEX_HULL
        elif air_box_type == "polygon":
            self.air_box_extents_type = self.ExtentType.POLYGON
        else:
            self.air_box_extents_type = self.ExtentType.BOUNDING_BOX

    def _map_open_region_type(self):
        open_region = self._boundaries_dict.get("open_region_type", None)
        if open_region == "radiation":
            self.open_region_type = self.OpenRegionType.RADIATION
        elif open_region == "pec":
            self.open_region_type = self.OpenRegionType.PEC
        else:
            self.open_region_type = self.OpenRegionType.RADIATION

    def _map_dielectric_extend_type(self):
        extend_type = self._boundaries_dict.get("dielectric_extents_type", None)
        if extend_type == "bounding_box":
            self.dielectric_extents_type = self.ExtentType.BOUNDING_BOX
        elif extend_type == "conformal":
            self.dielectric_extents_type = self.ExtentType.CONFORMAL
        elif extend_type == "convex_hull":
            self.dielectric_extents_type = self.ExtentType.CONVEX_HULL
        elif extend_type == "polygon":
            self.dielectric_extents_type = self.ExtentType.POLYGON
        else:
            self.dielectric_extents_type = self.ExtentType.BOUNDING_BOX

    class OpenRegionType(Enum):
        RADIATION = 0
        PEC = 1

    class ExtentType(Enum):
        BOUNDING_BOX = 0
        CONFORMAL = 1
        CONVEX_HULL = 2
        POLYGON = 3

    def apply(self):
        """Imports boundary information from JSON."""
        if self.open_region is not None:
            self._pedb.hfss.hfss_extent_info.use_open_region = self.open_region
        self._pedb.hfss.hfss_extent_info.open_region_type = self.open_region_type.name.lower()
        if self.pml_visible is not None:
            self._pedb.hfss.hfss_extent_info.is_pml_visible = self.pml_visible
        if self.pml_operation_frequency:
            self._pedb.hfss.hfss_extent_info.operating_freq = self.pml_operation_frequency
        if self.pml_radiation_factor:
            self._pedb.hfss.hfss_extent_info.radiation_level = self.pml_radiation_factor
        self._pedb.hfss.hfss_extent_info.extent_type = self.dielectric_extents_type.name.lower()
        if self.dielectric_base_polygon:
            self._pedb.hfss.hfss_extent_info.dielectric_base_polygon = self.dielectric_base_polygon
        if self.horizontal_padding:
            self._pedb.hfss.hfss_extent_info.dielectric_extent_size = float(self.horizontal_padding)
        if self.honor_primitives_on_dielectric_layers is not None:
            self._pedb.hfss.hfss_extent_info.honor_user_dielectric = self.honor_primitives_on_dielectric_layers
        self._pedb.hfss.hfss_extent_info.extent_type = self.air_box_extents_type.name.lower()
        if self.air_box_truncate_model_ground_layers is not None:
            self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground = self.air_box_truncate_model_ground_layers
        if self.air_box_horizontal_padding:
            self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent = float(self.air_box_horizontal_padding)
        if self.air_box_positive_vertical_padding:
            self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent = float(
                self.air_box_positive_vertical_padding
            )
        if self.air_box_negative_vertical_padding:
            self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent = float(
                self.air_box_negative_vertical_padding
            )

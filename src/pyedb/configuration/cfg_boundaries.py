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

from pyedb.configuration.cfg_common import CfgBase


class CfgBoundaries(CfgBase):
    def __init__(self, pedb, boundary_data):
        self._pedb = pedb
        self.open_region = boundary_data.get("open_region", None)
        self.open_region_type = boundary_data.get("map_open_region_type", None)
        self.pml_visible = boundary_data.get("pml_visible", None)
        self.pml_operation_frequency = boundary_data.get("pml_operation_frequency", None)
        self.pml_radiation_factor = boundary_data.get("pml_radiation_factor", None)
        self.dielectric_extent_type = boundary_data.get("dielectric_extent_type", None)
        # self.dielectric_base_polygon = self.**kwargs.get("dielectric_base_polygon", None)
        self.horizontal_padding = boundary_data.get("horizontal_padding", None)
        self.honor_primitives_on_dielectric_layers = boundary_data.get("honor_primitives_on_dielectric_layers", False)
        self.air_box_extent_type = boundary_data.get("air_box_extent_type", None)
        self.air_box_base_polygon = boundary_data.get("air_box_base_polygon", None)
        self.air_box_truncate_model_ground_layers = boundary_data.get("air_box_truncate_model_ground_layers", None)
        self.air_box_horizontal_padding = boundary_data.get("air_box_horizontal_padding", None)
        self.air_box_positive_vertical_padding = boundary_data.get("air_box_positive_vertical_padding", None)
        self.air_box_negative_vertical_padding = boundary_data.get("air_box_negative_vertical_padding", None)

    def apply(self):
        """Imports boundary information from JSON."""
        if self.open_region is not None:
            self._pedb.hfss.hfss_extent_info.use_open_region = self.open_region
        if self.open_region_type:
            self._pedb.hfss.hfss_extent_info.open_region_type = self.open_region_type.lower()
        if self.pml_visible is not None:
            self._pedb.hfss.hfss_extent_info.is_pml_visible = self.pml_visible
        if self.pml_operation_frequency:
            self._pedb.hfss.hfss_extent_info.operating_freq = self.pml_operation_frequency
        if self.pml_radiation_factor:
            self._pedb.hfss.hfss_extent_info.radiation_level = self.pml_radiation_factor
        if self.dielectric_extent_type:
            self._pedb.hfss.hfss_extent_info.extent_type = self.dielectric_extent_type.lower()
        # if self.dielectric_base_polygon:
        #    self._pedb.hfss.hfss_extent_info.dielectric_base_polygon = self.dielectric_base_polygon
        if self.horizontal_padding:
            self._pedb.hfss.hfss_extent_info.dielectric_extent_size = float(self.horizontal_padding)
        if self.honor_primitives_on_dielectric_layers is not None:
            self._pedb.hfss.hfss_extent_info.honor_user_dielectric = self.honor_primitives_on_dielectric_layers
        if self.air_box_extent_type:
            self._pedb.hfss.hfss_extent_info.extent_type = self.air_box_extent_type.lower()
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

    def get_data_from_db(self):
        self.open_region = self._pedb.hfss.hfss_extent_info.use_open_region
        self.open_region_type = self._pedb.hfss.hfss_extent_info.open_region_type
        self.pml_visible = self._pedb.hfss.hfss_extent_info.is_pml_visible
        self.pml_operation_frequency = self._pedb.hfss.hfss_extent_info.operating_freq.tostring
        self.pml_radiation_factor = self._pedb.hfss.hfss_extent_info.radiation_level.tostring
        self.dielectric_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
        # self.dielectric_base_polygon = self._pedb.hfss.hfss_extent_info.dielectric_base_polygon
        self.horizontal_padding = self._pedb.hfss.hfss_extent_info.dielectric_extent_size
        self.honor_primitives_on_dielectric_layers = self._pedb.hfss.hfss_extent_info.honor_user_dielectric
        self.air_box_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
        self.air_box_truncate_model_ground_layers = self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground
        self.air_box_horizontal_padding = self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent
        self.air_box_positive_vertical_padding = self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent
        self.air_box_negative_vertical_padding = self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent
        return self.get_attributes()

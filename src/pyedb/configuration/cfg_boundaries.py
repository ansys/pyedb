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
    class Grpc:
        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent.pedb
            self.open_region = self.parent.boundary_data.get("open_region", None)
            self.open_region_type = self.parent.boundary_data.get("map_open_region_type", None)
            self.pml_visible = self.parent.boundary_data.get("pml_visible", None)
            self.pml_operation_frequency = self.parent.boundary_data.get("pml_operation_frequency", None)
            self.pml_radiation_factor = self.parent.boundary_data.get("pml_radiation_factor", None)
            self.dielectric_extent_type = self.parent.boundary_data.get("dielectric_extent_type", None)
            self.horizontal_padding = self.parent.boundary_data.get("horizontal_padding", None)
            self.honor_primitives_on_dielectric_layers = self.parent.boundary_data.get(
                "honor_primitives_on_dielectric_layers", False
            )
            self.air_box_extent_type = self.parent.boundary_data.get("air_box_extent_type", None)
            self.air_box_base_polygon = self.parent.boundary_data.get("air_box_base_polygon", None)
            self.air_box_truncate_model_ground_layers = self.parent.boundary_data.get(
                "air_box_truncate_model_ground_layers", None
            )
            self.air_box_horizontal_padding = self.parent.boundary_data.get("air_box_horizontal_padding", None)
            self.air_box_positive_vertical_padding = self.parent.boundary_data.get(
                "air_box_positive_vertical_padding", None
            )
            self.air_box_negative_vertical_padding = self.parent.boundary_data.get(
                "air_box_negative_vertical_padding", None
            )

        def set_parameters_to_edb(self):
            if self.open_region is not None:
                self._pedb.hfss.hfss_extent_info.use_open_region = self.open_region
            if self.open_region_type:
                self._pedb.hfss.hfss_extent_info.open_region_type = self.open_region_type.lower()
            if self.pml_visible is not None:
                self._pedb.hfss.hfss_extent_info.is_pml_visible = self.pml_visible
            if self.pml_operation_frequency:
                self._pedb.hfss.hfss_extent_info.operating_freq = self.pml_operation_frequency
            if self.pml_radiation_factor:
                self._pedb.hfss.hfss_extent_info.pml_radiation_factor = self.pml_radiation_factor
            if self.dielectric_extent_type:
                self._pedb.hfss.hfss_extent_info.extent_type = self.dielectric_extent_type.lower()
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

        def get_parameters_from_edb(self):
            self.parent.open_region = self._pedb.hfss.hfss_extent_info.use_open_region
            self.parent.open_region_type = self._pedb.hfss.hfss_extent_info.open_region_type
            self.parent.pml_visible = self._pedb.hfss.hfss_extent_info.is_pml_visible
            self.parent.pml_operation_frequency = self._pedb.hfss.hfss_extent_info.operating_freq
            self.parent.pml_radiation_factor = self._pedb.hfss.hfss_extent_info.pml_radiation_factor
            self.parent.dielectric_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
            self.parent.horizontal_padding = self._pedb.hfss.hfss_extent_info.dielectric_extent_size
            self.parent.honor_primitives_on_dielectric_layers = self._pedb.hfss.hfss_extent_info.honor_user_dielectric
            self.parent.air_box_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
            self.parent.air_box_truncate_model_ground_layers = (
                self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground
            )
            self.parent.air_box_horizontal_padding = self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent
            self.parent.air_box_positive_vertical_padding = (
                self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent
            )
            self.parent.air_box_negative_vertical_padding = (
                self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent
            )
            return self.parent.get_attributes(exclude="boundary_data")

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def get_parameters_from_edb(self):
            self.parent.open_region = self._pedb.hfss.hfss_extent_info.use_open_region
            self.parent.open_region_type = self._pedb.hfss.hfss_extent_info.open_region_type
            self.parent.pml_visible = self._pedb.hfss.hfss_extent_info.is_pml_visible
            self.parent.pml_operation_frequency = self._pedb.hfss.hfss_extent_info.operating_freq.tostring
            self.parent.pml_radiation_factor = self._pedb.hfss.hfss_extent_info.radiation_level.tostring
            self.parent.dielectric_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
            self.parent.horizontal_padding = self._pedb.hfss.hfss_extent_info.dielectric_extent_size
            self.parent.honor_primitives_on_dielectric_layers = self._pedb.hfss.hfss_extent_info.honor_user_dielectric
            self.parent.air_box_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
            self.parent.air_box_truncate_model_ground_layers = (
                self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground
            )
            self.parent.air_box_horizontal_padding = self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent
            self.parent.air_box_positive_vertical_padding = (
                self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent
            )
            self.parent.air_box_negative_vertical_padding = (
                self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent
            )
            return self.parent.get_attributes(exclude="boundary_data")

        def set_parameters_to_edb(self):
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
                if self._pedb.grpc:
                    self._pedb.hfss.hfss_extent_info.pml_radiation_factor = self.pml_radiation_factor
                else:
                    self._pedb.hfss.hfss_extent_info.radiation_level = self.pml_radiation_factor
            if self.dielectric_extent_type:
                self._pedb.hfss.hfss_extent_info.extent_type = self.dielectric_extent_type.lower()
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

    def __init__(self, pedb, boundary_data):
        self.pedb = pedb
        self.boundary_data = boundary_data
        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

    def apply(self):
        """Imports boundary information from JSON."""
        self.api.set_parameters_to_edb()

    def get_data_from_db(self):
        return self.api.get_parameters_from_edb()

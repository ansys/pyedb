# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import Optional, Any, Union
from pydantic import BaseModel, Field


class CfgBase(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class PaddingData(CfgBase):
    size: Union[float, str]
    is_multiple: bool


class CfgBoundaries(CfgBase):
    open_region: Optional[Any] = Field(default=None)
    open_region_type: Optional[Any] = Field(default=None)
    pml_visible: Optional[Any] = Field(default=None)
    pml_operation_frequency: Optional[Any] = Field(default=None)
    pml_radiation_factor: Optional[Any] = Field(default=None)

    dielectric_extent_type: Optional[str] = Field(default=None)
    dielectric_base_polygon: Optional[str] = Field(default=None)
    horizontal_padding:  Optional[PaddingData] = Field(default=None)
    honor_primitives_on_dielectric_layers: bool = Field(default=False)

    air_box_extent_type: Optional[Any] = Field(default=None)
    air_box_base_polygon: Optional[Any] = Field(default=None)
    air_box_truncate_model_ground_layers: Optional[Any] = Field(default=None)
    air_box_horizontal_padding: Optional[PaddingData] = Field(default=None)
    air_box_positive_vertical_padding: Optional[PaddingData] = Field(default=None)
    air_box_negative_vertical_padding: Optional[PaddingData] = Field(default=None)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def get_parameters_from_edb(self):
        self.open_region = self._pedb.hfss.hfss_extent_info.use_open_region
        self.open_region_type = self._pedb.hfss.hfss_extent_info.open_region_type
        self.pml_visible = self._pedb.hfss.hfss_extent_info.is_pml_visible
        self.pml_operation_frequency = self._pedb.hfss.hfss_extent_info.operating_freq.tostring
        self.pml_radiation_factor = self._pedb.hfss.hfss_extent_info.radiation_level.tostring
        self.dielectric_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
        self.horizontal_padding = self._pedb.hfss.hfss_extent_info.dielectric_extent_size
        self.honor_primitives_on_dielectric_layers = self._pedb.hfss.hfss_extent_info.honor_user_dielectric
        self.air_box_extent_type = self._pedb.hfss.hfss_extent_info.extent_type
        self.air_box_truncate_model_ground_layers = self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground
        self.air_box_horizontal_padding = self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent
        self.air_box_positive_vertical_padding = self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent
        self.air_box_negative_vertical_padding = self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent
        return self.get_attributes(exclude="boundary_data")

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


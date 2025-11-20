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
from typing import Any, Optional, Union

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
    use_open_region: Optional[Any] = Field(default=None)
    open_region_type: Optional[Any] = Field(default=None)
    is_pml_visible: Optional[Any] = Field(default=None)
    operating_freq: Optional[Any] = Field(default=None)
    pml_radiation_factor: Optional[int] = Field(default=None)

    dielectric_extent_type: Optional[str] = Field(default=None)
    dielectric_base_polygon: Optional[str] = Field(default=None)
    dielectric_extent_size: Optional[PaddingData] = Field(default=None)
    honor_user_dielectric: bool = Field(default=False)

    extent_type: Optional[Any] = Field(default=None)
    base_polygon: Optional[Any] = Field(default=None)
    truncate_air_box_at_ground: Optional[Any] = Field(default=None)
    air_box_horizontal_extent: Optional[PaddingData] = Field(default=None)
    air_box_positive_vertical_extent: Optional[PaddingData] = Field(default=None)
    air_box_negative_vertical_extent: Optional[PaddingData] = Field(default=None)
    sync_air_box_vertical_extent: Optional[bool] = Field(default=None)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

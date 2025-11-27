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


from typing import Any, Optional

from pydantic import Field


class CfgBoundaries(CfgBase):
    use_open_region: Optional[bool] = Field(default=None, description="Whether to enable the use of an open region")
    open_region_type: Optional[str] = Field(
        default=None, description="Type of open region to use; e.g., `radiation` or `pml` as defined."
    )
    is_pml_visible: Optional[bool] = Field(
        default=None,
        description=(
            "Whether the PML (Perfectly Matched Layer) boundary is visible when using PML."
            "If `True`, the PML volume is shown in the model; otherwise it is hidden. "
        ),
    )
    operating_freq: Optional[Any] = Field(
        default=None,
        description=(
            "Operating frequency (in Hz) used to compute PML boundary thickness. "
            "This parameter influences how thick the PML layer is calculated. "
        ),
    )
    radiation_level: Optional[int] = Field(
        default=None,
        description=(
            "Radiation factor for PML, controlling the relative thickness of the PML boundary. "
            "Typically ranges on a scale (e.g., 0–10) to define how aggressively the PML absorbs. "
        ),
    )

    dielectric_extent_type: Optional[str] = Field(
        default=None,
        description=(
            "Method used to derive the base polygon for the dielectric region. "
            "Can be e.g. `Bounding Box`, `Conformal`, `Convex Hull`, or `Polygon` as in HFSS geometry extents. "
        ),
    )
    dielectric_base_polygon: Optional[str] = Field(
        default=None,
        description=(
            "Name of the base polygon used for the dielectric extent. "
            "When `dielectric_extent_type` is `Polygon`, this defines which polygon to use. "
        ),
    )
    dielectric_extent_size: Optional[PaddingData] = Field(
        default=None,
        description=(
            "Padding (size, is_multiple) for the dielectric extent. "
            "Specifies how much to expand the dielectric base polygon, either as an absolute value or scaled factor. "
        ),
    )
    honor_user_dielectric: bool = Field(
        default=False,
        description=(
            "If `True`, honors user-defined geometry on dielectric layers; otherwise, the base polygon is expanded "
            "to define the dielectric region. "
        ),
    )

    extent_type: Optional[str] = Field(
        default=None,
        description=(
            "Type of overall HFSS extent. "
            "This determines how the base polygon for both airbox and dielectric is computed. "
        ),
    )
    base_polygon: Optional[str] = Field(
        default=None,
        description=("Base polygon name for the extent region, used when the extent type is `Polygon`. "),
    )
    truncate_air_box_at_ground: Optional[bool] = Field(
        default=None,
        description=(
            "Whether to truncate (cap) the airbox at ground layers. "
            "If `True`, the simulation volume is limited by the ground layer instead of extending indefinitely. "
        ),
    )
    air_box_horizontal_extent: Optional[PaddingData] = Field(
        default=None,
        description=(
            "Horizontal padding of the airbox (size, is_multiple). "
            "Defines how far the airbox extends in the X-Y direction. "
        ),
    )
    air_box_positive_vertical_extent: Optional[PaddingData] = Field(
        default=None,
        description=(
            "Vertical padding (positive Z direction) of the airbox (size, is_multiple). "
            "Controls the top extension of the airbox. "
        ),
    )
    air_box_negative_vertical_extent: Optional[PaddingData] = Field(
        default=None,
        description=(
            "Vertical padding (negative Z direction) of the airbox (size, is_multiple). "
            "Controls how far below the model the airbox extends. "
        ),
    )
    sync_air_box_vertical_extent: Optional[bool] = Field(
        default=None,
        description=(
            "If `True`, synchronizes the positive and negative vertical airbox extents. "
            "This means both directions use the same padding value. "
        ),
    )

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

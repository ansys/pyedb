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

"""Build the ``boundaries`` configuration section.

This module provides a thin fluent layer over
:class:`pyedb.configuration.cfg_boundaries.CfgBoundaries` for defining HFSS
open-region settings, air-box padding, and dielectric extent controls.
"""

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
        """Configure a radiation open region.

        Parameters
        ----------
        use_open_region : bool, default: True
            Whether to enable the open-region boundary.

        """
        self.use_open_region = use_open_region
        self.open_region_type = "radiation"

    def set_pml_boundary(self, operating_freq, radiation_level: float = 20, is_pml_visible: bool = False):
        """Configure a perfectly matched layer boundary.

        Parameters
        ----------
        operating_freq : str or float
            Operating frequency used by the PML configuration.
        radiation_level : float, default: 20
            Radiation level in decibels.
        is_pml_visible : bool, default: False
            Whether the PML region should be visible in the model.
        """
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
        """Set horizontal and vertical air-box padding.

        Parameters
        ----------
        horizontal_size : str or float
            Horizontal air-box padding value.
        horizontal_is_multiple : bool, default: False
            Whether ``horizontal_size`` is expressed as a wavelength multiple.
        positive_vertical_size : str or float, default: 0.15
            Air-box padding above the layout.
        positive_vertical_is_multiple : bool, default: False
            Whether ``positive_vertical_size`` is a wavelength multiple.
        negative_vertical_size : str or float, default: 0.15
            Air-box padding below the layout.
        negative_vertical_is_multiple : bool, default: False
            Whether ``negative_vertical_size`` is a wavelength multiple.
        sync : bool, default: False
            Whether to synchronize positive and negative vertical extents.
        truncate_at_ground : bool, default: False
            Whether to truncate the air box at the ground reference.

        """
        PD = CfgBoundaries.PaddingData
        self.air_box_horizontal_extent = PD(size=horizontal_size, is_multiple=horizontal_is_multiple)
        self.air_box_positive_vertical_extent = PD(
            size=positive_vertical_size,
            is_multiple=positive_vertical_is_multiple,
        )
        self.air_box_negative_vertical_extent = PD(
            size=negative_vertical_size,
            is_multiple=negative_vertical_is_multiple,
        )
        self.sync_air_box_vertical_extent = sync
        self.truncate_air_box_at_ground = truncate_at_ground

    def set_extent(
        self,
        extent_type: str = "BoundingBox",
        base_polygon: Optional[str] = None,
        truncate_air_box_at_ground: bool = False,
    ):
        """Set the layout extent used for region construction.

        Parameters
        ----------
        extent_type : str, default: "BoundingBox"
            Extent strategy understood by ``CfgBoundaries``.
        base_polygon : str, optional
            Named polygon to use when the selected extent mode requires one.
        truncate_air_box_at_ground : bool, default: False
            Whether the air box should stop at the ground reference.
        """
        self.extent_type = extent_type
        if base_polygon:
            self.base_polygon = base_polygon
        self.truncate_air_box_at_ground = truncate_air_box_at_ground

    def set_dielectric_extent(
        self,
        extent_type: str = "BoundingBox",
        expansion_size=0,
        is_multiple: bool = False,
        base_polygon: Optional[str] = None,
        honor_user_dielectric: bool = False,
    ):
        """Configure the dielectric extent envelope.

        Parameters
        ----------
        extent_type : str, default: "BoundingBox"
            Dielectric extent strategy understood by ``CfgBoundaries``.
        expansion_size : str or float, default: 0
            Amount of dielectric expansion.
        is_multiple : bool, default: False
            Whether ``expansion_size`` is specified as a wavelength multiple.
        base_polygon : str, optional
            Named polygon to use when the selected extent mode requires one.
        honor_user_dielectric : bool, default: False
            Whether user-defined dielectric regions should be preserved.
        """
        self.dielectric_extent_type = extent_type
        self.dielectric_extent_size = CfgBoundaries.PaddingData(size=expansion_size, is_multiple=is_multiple)
        if base_polygon:
            self.dielectric_base_polygon = base_polygon
        if honor_user_dielectric:
            self.honor_user_dielectric = honor_user_dielectric

    def to_dict(self) -> dict:
        """Serialize explicitly configured boundary fields.

        Returns
        -------
        dict
            Dictionary ready for the ``boundaries`` section of a pyedb
            configuration file.
        """
        raw = self.model_dump(exclude_none=True)
        # honor_user_dielectric defaults to False in the root model — omit unless True
        if not self.honor_user_dielectric:
            raw.pop("honor_user_dielectric", None)
        return raw

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

"""HFSS boundary / open-region builder API.

Data model: :class:`~pyedb.configuration.cfg_boundaries.CfgBoundaries`.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from pyedb.configuration.cfg_boundaries import CfgBoundaries

PaddingData = CfgBoundaries.PaddingData


class BoundariesConfig:
    """Fluent builder for the ``boundaries`` configuration section.

    Wraps :class:`~pyedb.configuration.cfg_boundaries.CfgBoundaries`.

    Examples
    --------
    >>> cfg.boundaries.set_radiation_boundary()
    >>> cfg.boundaries.set_air_box_extents(horizontal_size=0.15, horizontal_is_multiple=True)
    """

    def __init__(self):
        self._model = CfgBoundaries()

    # ── convenience setters ───────────────────────────────────────────────

    def set_radiation_boundary(self, use_open_region: bool = True):
        """Configure a radiation open region."""
        self._model.use_open_region = use_open_region
        self._model.open_region_type = "radiation"

    def set_pml_boundary(
        self,
        operating_freq: Union[str, float],
        radiation_level: float = 20,
        is_pml_visible: bool = False,
    ):
        """Configure a PML open region."""
        self._model.use_open_region = True
        self._model.open_region_type = "pml"
        self._model.operating_freq = operating_freq
        self._model.radiation_level = radiation_level
        self._model.is_pml_visible = is_pml_visible

    def set_air_box_extents(
        self,
        horizontal_size: Union[float, str],
        horizontal_is_multiple: bool = False,
        positive_vertical_size: Union[float, str] = 0.15,
        positive_vertical_is_multiple: bool = False,
        negative_vertical_size: Union[float, str] = 0.15,
        negative_vertical_is_multiple: bool = False,
        sync: bool = False,
        truncate_at_ground: bool = False,
    ):
        """Set airbox padding extents."""
        self._model.air_box_horizontal_extent = PaddingData(size=horizontal_size, is_multiple=horizontal_is_multiple)
        self._model.air_box_positive_vertical_extent = PaddingData(
            size=positive_vertical_size,
            is_multiple=positive_vertical_is_multiple,
        )
        self._model.air_box_negative_vertical_extent = PaddingData(
            size=negative_vertical_size,
            is_multiple=negative_vertical_is_multiple,
        )
        self._model.sync_air_box_vertical_extent = sync
        self._model.truncate_air_box_at_ground = truncate_at_ground

    def set_extent(
        self,
        extent_type: str = "BoundingBox",
        base_polygon: Optional[str] = None,
        truncate_air_box_at_ground: bool = False,
    ):
        """Set the overall HFSS extent type."""
        self._model.extent_type = extent_type
        if base_polygon:
            self._model.base_polygon = base_polygon
        self._model.truncate_air_box_at_ground = truncate_air_box_at_ground

    def set_dielectric_extent(
        self,
        extent_type: str = "BoundingBox",
        expansion_size: Union[float, str] = 0,
        is_multiple: bool = False,
        base_polygon: Optional[str] = None,
        honor_user_dielectric: bool = False,
    ):
        """Set dielectric region extent."""
        self._model.dielectric_extent_type = extent_type
        self._model.dielectric_extent_size = PaddingData(size=expansion_size, is_multiple=is_multiple)
        if base_polygon:
            self._model.dielectric_base_polygon = base_polygon
        self._model.honor_user_dielectric = honor_user_dielectric

    def to_dict(self) -> dict:
        """Serialise to a dict compatible with :class:`~pyedb.configuration.cfg_boundaries.CfgBoundaries`."""
        return self._model.model_dump(exclude_none=True)

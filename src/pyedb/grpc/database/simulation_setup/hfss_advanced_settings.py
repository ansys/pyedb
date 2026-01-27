# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
        HFSSAdvancedSettings as GrpcHFSSAdvancedSettings,
    )
from ansys.edb.core.simulation_setup.simulation_settings import ViaStyle as GrpcViaStyle


class HFSSAdvancedSettings:
    def __init__(self, pedb, core: "GrpcHFSSAdvancedSettings"):
        """PyEDB HFSS advanced settings class."""
        self.core = core
        self._pedb = pedb

    @property
    def defeature_abs_length(self) -> float:
        """Absolute length used as tolerance when defeaturing polygons.

        .. deprecated:: 0.77.3
            Use :attr:`defeature_absolute_length` instead.

        """
        warnings.warn(
            "The 'defeature_abs_length' property is deprecated. Please use 'defeature_absolute_length' instead.",
            DeprecationWarning,
        )
        return self.defeature_absolute_length

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):
        warnings.warn(
            "The 'defeature_abs_length' property is deprecated. Please use 'defeature_absolute_length' instead.",
            DeprecationWarning,
        )
        self.defeature_absolute_length = value

    @property
    def defeature_absolute_length(self) -> str:
        """Absolute length used as tolerance when defeaturing polygons.

        Returns
        -------
        str
            Length value.

        """
        return self.core.defeature_absolute_length

    @defeature_absolute_length.setter
    def defeature_absolute_length(self, value):
        self.core.defeature_absolute_length = str(value)

    @property
    def defeature_ratio(self) -> float:
        """Extent ratio used as tolerance when defeaturing polygons.

        Returns
        -------
        float
            Ratio value.

        """
        return self.core.defeature_ratio

    @defeature_ratio.setter
    def defeature_ratio(self, value: float):
        self.core.defeature_ratio = value

    @property
    def healing_option(self) -> int:
        """Enable/disable healing of mis-aligned points and edges.

        Returns
        -------
        int
            Healing option value.

        """
        return self.core.healing_option

    @healing_option.setter
    def healing_option(self, value: int):
        self.core.healing_option = value

    @property
    def ic_mode_auto_resolution(self) -> bool:
        """Flag indicating if model resolution is automatically calculated for IC designs..

        Returns
        -------
        bool
            True if IC mode auto resolution is enabled, False otherwise.

        """
        return self.core.ic_mode_auto_resolution

    @ic_mode_auto_resolution.setter
    def ic_mode_auto_resolution(self, value: bool):
        self.core.ic_mode_auto_resolution = value

    @property
    def mesh_for_via_plating(self) -> bool:
        """Flag indicating if meshing for via plating is enabled.

        Returns
        -------
        bool
            True if meshing for via plating is enabled, False otherwise.

        """
        return self.core.mesh_for_via_plating

    @mesh_for_via_plating.setter
    def mesh_for_via_plating(self, value: bool):
        self.core.mesh_for_via_plating = value

    @property
    def model_type(self) -> str:
        """HFSS model type.

        Returns
        -------
        str
            Model type name.

        """
        if self.core.model_type.value == 0:
            return "general"
        else:
            return "ic"

    @property
    def via_density(self) -> float:
        """Density of vias.

        .. deprecated:: 0.77.3
            Use :attr:`num_via_density` instead.

        """
        return self.num_via_density

    @via_density.setter
    def via_density(self, value: float):
        warnings.warn(
            "The 'via_density' property is deprecated. Please use 'num_via_density' instead.",
            DeprecationWarning,
        )
        self.num_via_density = value

    @property
    def num_via_density(self) -> float:
        """Spacing between vias.

        Returns
        -------
        int
            Spacing value.

        """
        return self.core.num_via_density

    @num_via_density.setter
    def num_via_density(self, value: float):
        self.core.num_via_density = value

    @property
    def via_num_sides(self) -> int:
        """Number of sides a via is considered to have.

        .. deprecated:: 0.77.3
            Use :attr:`num_via_sides` instead.

        """
        return self.num_via_sides

    @via_num_sides.setter
    def via_num_sides(self, value: int):
        warnings.warn(
            "The 'via_num_sides' property is deprecated. Please use 'num_via_sides' instead.",
            DeprecationWarning,
        )
        self.num_via_sides = value

    @property
    def num_via_sides(self) -> int:
        """Number of sides a via is considered to have.

        Returns
        -------
        int
            Number of via sides value.

        """
        return self.core.num_via_sides

    @num_via_sides.setter
    def num_via_sides(self, value: int):
        self.core.num_via_sides = value

    @property
    def remove_floating_geometry(self) -> bool:
        """Flag indicating if a geometry not connected to any other geometry is removed.

        Returns
        -------
        bool
            True if floating geometry is removed, False otherwise.

        """
        return self.core.remove_floating_geometry

    @remove_floating_geometry.setter
    def remove_floating_geometry(self, value: bool):
        self.core.remove_floating_geometry = value

    @property
    def small_void_area(self) -> float:
        """Voids with an area smaller than this value are ignored during simulation.

        Returns
        -------
        float
            Small void area value.

        """
        return self.core.small_void_area

    @small_void_area.setter
    def small_void_area(self, value: float):
        self.core.small_void_area = value

    @property
    def union_polygons(self) -> bool:
        """Flag indicating if polygons are unioned.

        Returns
        -------
        bool
            True if polygons are unioned, False otherwise.

        """
        return self.core.union_polygons

    @union_polygons.setter
    def union_polygons(self, value: bool):
        self.core.union_polygons = value

    @property
    def use_defeature(self) -> bool:
        """Flag indicating if defeaturing is used.

        Returns
        -------
        bool
            True if defeaturing is used, False otherwise.

        """
        return self.core.use_defeature

    @use_defeature.setter
    def use_defeature(self, value: bool):
        self.core.use_defeature = value

    @property
    def use_defeature_abs_length(self) -> bool:
        """Flag indicating if absolute length defeaturing is used.

        .. deprecated:: 0.77.3
            Use :attr:`use_defeature_absolute_length` instead.

        """
        warnings.warn(
            "The 'use_defeature_abs_length' property is deprecated. "
            "Please use 'use_defeature_absolute_length' instead.",
            DeprecationWarning,
        )
        return self.use_defeature_absolute_length

    @use_defeature_abs_length.setter
    def use_defeature_abs_length(self, value: bool):
        warnings.warn(
            "The 'use_defeature_abs_length' property is deprecated. "
            "Please use 'use_defeature_absolute_length' instead.",
            DeprecationWarning,
        )
        self.use_defeature_absolute_length = value

    @property
    def use_defeature_absolute_length(self) -> bool:
        """Flag indicating if absolute length or extent ratio is used when defeaturing polygons.

        Returns
        -------
        bool
            True if absolute length defeaturing is used, False otherwise.

        """
        return self.core.use_defeature_absolute_length

    @use_defeature_absolute_length.setter
    def use_defeature_absolute_length(self, value: bool):
        self.core.use_defeature_absolute_length = value

    @property
    def via_material(self) -> str:
        """Default via material.

        Returns
        -------
        str
            Via material name.

        """
        return self.core.via_material

    @via_material.setter
    def via_material(self, value: str):
        self.core.via_material = value

    @property
    def via_style(self) -> str:
        """Via style.

        .. deprecated:: 0.77.3
            Use :attr:`via_model_type` instead.

        """
        return self.via_model_type

    @via_style.setter
    def via_style(self, value):
        warnings.warn(
            "The 'via_style' property is deprecated. Please use 'via_model_type' instead.",
            DeprecationWarning,
        )
        self.via_model_type = value

    @property
    def via_model_type(self) -> str:
        """Via model type.

        Returns
        -------
        str
            Via model type name.

        """
        return self.core.via_model_type.name.lower()

    @via_model_type.setter
    def via_model_type(self, value):
        if isinstance(value, str):
            if value.upper() == "WIREBOND":
                self.core.via_model_type = GrpcViaStyle.WIREBOND
            elif value.lower() == "RIBBON":
                self.core.via_model_type = GrpcViaStyle.RIBBON
            elif value.lower() == "MESH":
                self.core.via_model_type = GrpcViaStyle.MESH
            elif value.lower() == "FIELD":
                self.core.ia_model_type = GrpcViaStyle.FIELD
            elif value.lower() == "NUM_VIA_STYLE":
                self.core.via_model_type = GrpcViaStyle.NUM_VIA_STYLE

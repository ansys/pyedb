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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DAdvancedSettings as GrpcQ3DAdvancedSettings


class Q3DAdvancedSettings:
    """Q3D advanced simulation settings.

    Parameters
    ----------
    pedb : :class:`Edb < pyedb.grpc.edb.Edb>`
        Inherited object.
    """

    def __init__(self, pedb, core: GrpcQ3DAdvancedSettings):
        self._pedb = pedb
        self.core = core

    @property
    def defeature_absolute_length(self) -> float:
        """Absolute length used as tolerance when defeaturing polygons.

        Returns
        -------
        float
            Defeature absolute length value.
        """
        return self._pedb.value(self.core.defeature_absolute_length)

    @defeature_absolute_length.setter
    def defeature_absolute_length(self, value: float):
        self.core.defeature_absolute_length = str(self._pedb.edb_value(value))

    @property
    def defeature_ratio(self) -> float:
        """Extent ratio used as tolerance when defeaturing polygons.

        Returns
        -------
        float
            Defeature ratio value.
        """
        return self.core.defeature_ratio

    @defeature_ratio.setter
    def defeature_ratio(self, value: float):
        self.core.defeature_ratio = value

    @property
    def healing_option(self) -> int:
        """Healing option.

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
        """Flag indicating if model resolution is automatically calculated for IC designs.

        Returns
        -------
        bool
            IC mode auto resolution value.
        """
        return self.core.ic_mode_auto_resolution

    @ic_mode_auto_resolution.setter
    def ic_mode_auto_resolution(self, value: bool):
        self.core.ic_mode_auto_resolution = value

    @property
    def ic_mode_length(self) -> float:
        """Model resolution to use when manually setting the model resolution of IC designs.

        Returns
        -------
        float
            IC mode length value.
        """
        return self._pedb.value(self.core.ic_mode_length)

    @ic_mode_length.setter
    def ic_mode_length(self, value: float):
        self.core.ic_mode_length = str(self._pedb.edb_value(value))

    @property
    def max_passes(self) -> int:
        """Maximum number of mesh refinement cycles to perform.

        Returns
        -------
        int
            Max passes value.
        """
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value: int):
        self.core.max_passes = value

    @property
    def max_refine_per_pass(self) -> float:
        """How many tetrahedra are added at each iteration of the adaptive refinement process.

        Returns
        -------
        float
            Max refine per pass value.
        """
        return self.core.max_refine_per_pass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value: float):
        self.core.max_refine_per_pass = value

    @property
    def mesh_for_via_plating(self) -> bool:
        """Flag indicating whether to mesh the via plating.

        Returns
        -------
        bool
            Mesh for via plating value.
        """
        return self.core.mesh_for_via_plating

    @mesh_for_via_plating.setter
    def mesh_for_via_plating(self, value: bool):
        self.core.mesh_for_via_plating = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum number of converged passes before stopping the adaptive refinement process.

        Returns
        -------
        int
            Min converged passes value.
        """
        return self.core.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value: int):
        self.core.min_converged_passes = value

    @property
    def min_passes(self) -> int:
        """Minimum number of mesh refinement cycles to perform.

        Returns
        -------
        int
            Min passes value.
        """
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        self.core.min_passes = value

    @property
    def num_via_density(self) -> float:
        """Spacing between vias.

        Returns
        -------
        float
            Num via density value.
        """
        return self.core.num_via_density

    @num_via_density.setter
    def num_via_density(self, value: float):
        self.core.num_via_density = value

    @property
    def num_via_sides(self) -> int:
        """Number of sides to use when meshing vias.

        Returns
        -------
        int
            Num via sides value.
        """
        return self.core.num_via_sides

    @num_via_sides.setter
    def num_via_sides(self, value: int):
        self.core.num_via_sides = value

    @property
    def percent_error(self) -> float:
        """Target percent error for adaptive mesh refinement.

        Returns
        -------
        float
            Percent error value.
        """
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        self.core.percent_error = value

    @property
    def remove_floating_geometry(self) -> bool:
        """Flag indicating if a geometry not connected to any other geometry is removed.

        Returns
        -------
        bool
            Remove floating geometry value.
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
        self.core.small_void_area = self._pedb.edb_value(value)

    @property
    def union_polygons(self) -> bool:
        """Flag indicating if polygons are united before meshing.

        Returns
        -------
        bool
            Union polygons value.
        """
        return self.core.union_polygons

    @union_polygons.setter
    def union_polygons(self, value: bool):
        self.core.union_polygons = value

    @property
    def use_defeature(self) -> bool:
        """Flag indicating if defeaturing is used when meshing.

        Returns
        -------
        bool
            Use defeature value.
        """
        return self.core.use_defeature

    @use_defeature.setter
    def use_defeature(self, value: bool):
        self.core.use_defeature = value

    @property
    def use_defeature_absolute_length(self) -> bool:
        """Flag indicating if absolute length or extent ratio is used when defeaturing polygons.

        Returns
        -------
        bool
            Use defeature absolute length value.
        """
        return self.core.use_defeature_absolute_length

    @use_defeature_absolute_length.setter
    def use_defeature_absolute_length(self, value: bool):
        self.core.use_defeature_absolute_length = value

    @property
    def via_material(self) -> str:
        """Material used for vias.

        Returns
        -------
        str
            Via material value.
        """
        return self.core.via_material

    @via_material.setter
    def via_material(self, value: str):
        self.core.via_material = value

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

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
        SIWaveDCAdvancedSettings as CoreSIWaveDCAdvancedSettings,
    )


class SIWaveDCAdvancedSettings:
    """Siwave DC Advanced simulation settings class."""

    def __init__(self, pedb, core: "CoreSIWaveDCAdvancedSettings"):
        self._pedb = pedb
        self.core = core

    @property
    def dc_min_plane_area_to_mesh(self) -> str:
        """Minimum plane area to mesh.

        Returns
        -------
        float
            Minimum plane area to mesh value.
        """
        return self.core.dc_min_plane_area_to_mesh

    @dc_min_plane_area_to_mesh.setter
    def dc_min_plane_area_to_mesh(self, value: str):
        self.core.dc_min_plane_area_to_mesh = value

    @property
    def dc_min_void_area_to_mesh(self) -> str:
        """Minimum void area to mesh.

        Returns
        -------
        str
            Minimum void area to mesh value.
        """
        return self.core.dc_min_void_area_to_mesh

    @dc_min_void_area_to_mesh.setter
    def dc_min_void_area_to_mesh(self, value: str):
        self.core.dc_min_void_area_to_mesh = value

    @property
    def energy_error(self) -> float:
        """Energy error.

        Returns
        -------
        float
            Energy error value.
        """
        return self.core.energy_error

    @energy_error.setter
    def energy_error(self, value: float):
        self.core.energy_error = value

    @property
    def max_init_mesh_edge_length(self) -> str:
        """Maximum initial mesh edge length.

        Returns
        -------
        str
            Maximum initial mesh edge length value.
        """
        return self.core.max_init_mesh_edge_length

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value: str):
        self.core.max_init_mesh_edge_length = value

    @property
    def max_num_passes(self) -> int:
        """Maximum number of passes.

        Returns
        -------
        int
            Maximum number of passes value.
        """
        return self.core.max_num_passes

    @max_num_passes.setter
    def max_num_passes(self, value: int):
        self.core.max_num_passes = value
    
    @property
    def max_passes(self) -> int:
        """Maximum number of passes for broadband adaptive solution.

        Returns
        -------
        int
            Maximum number of passes.

        """
        return self.max_num_passes

    @max_passes.setter
    def max_passes(self, value):
        self.max_num_passes = value
    
    @property
    def mesh_bws(self) -> bool:
        """Mesh BWS.

        Returns
        -------
        bool
            Mesh BWS value.
        """
        return self.core.mesh_bws

    @mesh_bws.setter
    def mesh_bws(self, value: bool):
        self.core.mesh_bws = value

    @property
    def mesh_vias(self) -> bool:
        """Mesh vias.

        Returns
        -------
        bool
            Mesh vias value.
        """
        return self.core.mesh_vias

    @mesh_vias.setter
    def mesh_vias(self, value: bool):
        self.core.mesh_vias = value

    @property
    def min_num_passes(self) -> int:
        """Minimum number of passes.

        Returns
        -------
        int
            Minimum number of passes value.
        """
        return self.core.min_num_passes

    @min_num_passes.setter
    def min_num_passes(self, value: int):
        self.core.min_num_passes = value

    @property
    def num_bw_sides(self) -> int:
        """Number of BWS sides.

        Returns
        -------
        int
            Number of BWS sides value.
        """
        return self.core.num_bw_sides

    @num_bw_sides.setter
    def num_bw_sides(self, value: int):
        self.core.num_bw_sides = value

    @property
    def num_via_sides(self) -> int:
        """Number of via sides.

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
    def percent_local_refinement(self) -> float:
        """Percentage of local refinement.

        Returns
        -------
        float
            Percentage of local refinement value.
        """
        return self.core.percent_local_refinement

    @percent_local_refinement.setter
    def percent_local_refinement(self, value: float):
        self.core.percent_local_refinement = value

    @property
    def perform_adaptive_refinement(self) -> bool:
        """Perform adaptive refinement.

        Returns
        -------
        bool
            Perform adaptive refinement value.
        """
        return self.core.perform_adaptive_refinement

    @perform_adaptive_refinement.setter
    def perform_adaptive_refinement(self, value: bool):
        self.core.perform_adaptive_refinement = value

    @property
    def refine_bws(self) -> bool:
        """Refine BWS.

        Returns
        -------
        bool
            Refine BWS value.
        """
        return self.core.refine_bws

    @refine_bws.setter
    def refine_bws(self, value: bool):
        self.core.refine_bws = value

    @property
    def refine_vias(self) -> bool:
        """Refine vias.

        Returns
        -------
        bool
            Refine vias value.
        """
        return self.core.refine_vias

    @refine_vias.setter
    def refine_vias(self, value: bool):
        self.core.refine_vias = value

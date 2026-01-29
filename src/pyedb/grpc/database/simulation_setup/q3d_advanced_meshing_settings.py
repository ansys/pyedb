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
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import (
        Q3DAdvancedMeshingSettings as CoreQ3DAdvancedMeshingSettings,
    )


class Q3DAdvancedMeshingSettings:
    """Q3D advanced meshing settings class."""

    def __init__(self, pedb, core: "CoreQ3DAdvancedMeshingSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def arc_step_size(self) -> float:
        """Arc step size in micrometers.

        Returns
        -------
        float
            Arc step size in micrometers.
        """
        return self._pedb.value(self.core.arc_step_size)

    @arc_step_size.setter
    def arc_step_size(self, value: float):
        self.core.arc_step_size = str(self._pedb.value(value))

    @property
    def arc_to_chord_error(self) -> float:
        """Arc to chord error in micrometers.

        Returns
        -------
        float
            Arc to chord error in micrometers.
        """
        return self._pedb.value(self.core.arc_to_chord_error)

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value: float):
        self.core.arc_to_chord_error = str(self._pedb.value(value))

    @property
    def circle_start_azimuth(self) -> float:
        """Circle start azimuth in degrees.

        Returns
        -------
        float
            Circle start azimuth in degrees.
        """
        return self._pedb.value(self.core.circle_start_azimuth)

    @circle_start_azimuth.setter
    def circle_start_azimuth(self, value: float):
        self.core.circle_start_azimuth = str(self._pedb.value(value))

    @property
    def layer_alignment(self) -> str:
        """Snapping tolerance for hierarchical layer alignment.

        Returns
        -------
        float
            Snapping tolerance for hierarchical layer alignment.
        """
        return self.core.layer_alignment

    @layer_alignment.setter
    def layer_alignment(self, value: str):
        self.core.layer_alignment = str(value)

    @property
    def max_num_arc_points(self) -> int:
        """Maximum number of points used to approximate arcs.

        Returns
        -------
        int
            Maximum number of arc points.
        """
        return self.core.max_num_arc_points

    @max_num_arc_points.setter
    def max_num_arc_points(self, value: int):
        self.core.max_num_arc_points = value

    @property
    def use_arc_chord_error_approx(self) -> bool:
        """Flag indicating if arc to chord error approximation is used.

        Returns
        -------
        bool
            True if arc to chord error approximation is used, False otherwise.
        """
        return self.core.use_arc_chord_error_approx

    @use_arc_chord_error_approx.setter
    def use_arc_chord_error_approx(self, value: bool):
        self.core.use_arc_chord_error_approx = value

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
        HFSSAdvancedMeshingSettings as CoreHFSSAdvancedMeshingSettings,
    )


class HFSSAdvancedMeshingSettings:
    def __init__(self, pedb, core: "CoreHFSSAdvancedMeshingSettings"):
        """PyEDB HFSS advanced meshing settings class."""
        self.core = core
        self._pedb = pedb

    @property
    def arc_step_size(self) -> str:
        """Get or set the arc step size.

        Returns
        -------
        float
            Arc step size.
        """
        return self.core.arc_step_size

    @arc_step_size.setter
    def arc_step_size(self, value: str):
        self.core.arc_step_size = value

    @property
    def arc_to_chord_error(self) -> str:
        """Get or set the arc to chord error.

        Returns
        -------
        float
            Arc to chord error.
        """
        return self.core.arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value: str):
        self.core.arc_to_chord_error = value

    @property
    def circle_start_azimuth(self) -> str:
        """Get or set the circle start azimuth.

        Returns
        -------
        float
            Circle start azimuth.
        """
        return self.core.circle_start_azimuth

    @circle_start_azimuth.setter
    def circle_start_azimuth(self, value: str):
        self.core.circle_start_azimuth = value

    @property
    def layer_snap_tol(self) -> str:
        """Get or set the layer snap tolerance.

        Returns
        -------
        str
            Layer snap tolerance.
        """
        return self.core.layer_snap_tol

    @layer_snap_tol.setter
    def layer_snap_tol(self, value: str):
        self.core.layer_snap_tol = str(value)

    @property
    def max_arc_points(self) -> int:
        """Get or set the maximum number of arc points.

        .. deprecated:: 0.77.3
            Use :attr:`max_num_arc_points` instead.
        """
        warnings.warn(
            "The 'max_arc_points' property is deprecated and will be removed in future releases.", DeprecationWarning
        )
        return self.max_num_arc_points

    @max_arc_points.setter
    def max_arc_points(self, value: int):
        warnings.warn(
            "The 'max_arc_points' property is deprecated and will be removed in future releases.", DeprecationWarning
        )
        self.max_num_arc_points = value

    @property
    def max_num_arc_points(self) -> int:
        """Get or set the maximum number of arc points.

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
        """Get or set whether to use arc chord error approximation.

        Returns
        -------
        bool
            True if using arc chord error approximation, False otherwise.
        """
        return self.core.use_arc_chord_error_approx

    @use_arc_chord_error_approx.setter
    def use_arc_chord_error_approx(self, value: bool):
        self.core.use_arc_chord_error_approx = value

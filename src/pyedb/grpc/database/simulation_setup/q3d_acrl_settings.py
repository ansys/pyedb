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
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DACRLSettings as CoreQ3DACRLSettings


class Q3DACRLSettings:
    """Q3D ACRL settings class."""

    def __init__(self, pedb, core: "CoreQ3DACRLSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def max_passes(self) -> int:
        """Maximum number of mesh refinement cycles to perform.

        Returns
        -------
        int
            Maximum number of passes.
        """
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value: int):
        self.core.max_passes = value

    @property
    def max_refine_per_pass(self) -> float:
        """Maximum percentage of elements to refine per pass.

        Returns
        -------
        float
            Maximum percentage of elements to refine per pass.
        """
        return self.core.max_refine_per_pass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value: float):
        self.core.max_refine_per_pass = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum number of converged passes required.

        Returns
        -------
        int
            Minimum number of converged passes.
        """
        return self.core.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value: int):
        self.core.min_converged_passes = value

    @property
    def min_passes(self) -> int:
        """Minimum number of passes required.

        Returns
        -------
        int
            Minimum number of passes.
        """
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        self.core.min_passes = value

    @property
    def percent_error(self) -> float:
        """Target percent error for convergence.

        Returns
        -------
        float
            Target percent error.
        """
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        self.core.percent_error = value

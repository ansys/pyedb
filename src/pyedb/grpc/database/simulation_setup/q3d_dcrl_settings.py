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
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DDCRLSettings as GrpcQ3DDCRLSettings
from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DSolutionOrder as GrpcQ3DSolutionOrder

_mapping_solution_order = {
    "normal": GrpcQ3DSolutionOrder.NORMAL,
    "high": GrpcQ3DSolutionOrder.HIGH,
    "higher": GrpcQ3DSolutionOrder.HIGHER,
    "highest": GrpcQ3DSolutionOrder.HIGHEST,
    "num_solution_order": GrpcQ3DSolutionOrder.NUM_SOLUTION_ORDER,
}


class Q3DDCRLSettings:
    def __init__(self, pedb, core: "GrpcQ3DDCRLSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def max_passes(self) -> int:
        """Maximum number of passes.

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
        """Maximum refinement per pass.

        Returns
        -------
        float
            Maximum refinement per pass.
        """
        return self.core.max_refine_per_pass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value: float):
        self.core.max_refine_per_pass = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum number of converged passes.

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
        """Minimum number of passes.

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
        """Percent error.

        Returns
        -------
        float
            Percent error.
        """
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        self.core.percent_error = value

    @property
    def solution_order(self) -> str:
        """Solution order.

        Returns
        -------
        str
            Solution order.
        """
        reverse_mapping = {v: k for k, v in _mapping_solution_order.items()}
        return reverse_mapping.get(self.core.solution_order, "normal")

    @solution_order.setter
    def solution_order(self, value: str):
        if value.lower() in _mapping_solution_order:
            self.core.solution_order = _mapping_solution_order[value.lower()]
        else:
            self.core.solution_order = GrpcQ3DSolutionOrder.NORMAL

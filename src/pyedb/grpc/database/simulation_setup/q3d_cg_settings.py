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
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DCGSettings as GrpcQ3DCGSettings
from ansys.edb.core.simulation_setup.q3d_simulation_settings import (
    Q3DSolutionOrder as GrpcQ3DSolutionOrder,
    SolverType as GrpcSolverType,
)

_mapping_solution_order = {
    "normal": GrpcQ3DSolutionOrder.NORMAL,
    "high": GrpcQ3DSolutionOrder.HIGH,
    "higher": GrpcQ3DSolutionOrder.HIGHER,
    "highest": GrpcQ3DSolutionOrder.HIGHEST,
    "num_solution_order": GrpcQ3DSolutionOrder.NUM_SOLUTION_ORDER,
}

_mapping_solver_type = {
    "direct": GrpcSolverType.DIRECT_SOLVER,
    "iterative": GrpcSolverType.ITERATIVE_SOLVER,
    "auto": GrpcSolverType.AUTO_SOLVER,
}


class Q3DCGSettings:
    """Q3D CG settings class."""

    def __init__(self, pedb, core: "GrpcQ3DCGSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def auto_incr_sol_order(self) -> bool:
        """Get auto increment solution order setting.

        Returns
        -------
        bool
            Auto increment solution order setting.
        """
        return self.core.auto_incr_sol_order

    @auto_incr_sol_order.setter
    def auto_incr_sol_order(self, value: bool):
        self.core.auto_incr_sol_order = value

    @property
    def compression_tol(self) -> float:
        """Get compression tolerance.

        Returns
        -------
        float
            Compression tolerance.
        """
        return self._pedb.value(self.core.compression_tol)

    @compression_tol.setter
    def compression_tol(self, value: float):
        self.core.compression_tol = value

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
        return self._pedb.value(self.core.max_refine_per_pass)

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
        """
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        self.core.min_passes = value

    @property
    def percent_error(self) -> float:
        """Percent error during conduction adaptive passes.

        Returns
        -------
        float
            Percent error during conduction adaptive passes.
        """
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        self.core.percent_error = value

    @property
    def solution_order(self) -> str:
        """Get solution order.

        Returns
        -------
        str
            Solution order.
        """
        reverse_mapping = {v: k for k, v in _mapping_solution_order.items()}
        return reverse_mapping[self.core.solution_order]

    @solution_order.setter
    def solution_order(self, value: str):
        if not (self.core.solution_order in _mapping_solution_order.keys()):
            raise ValueError(
                f"Invalid solution order: {value}. Valid options are: {list(_mapping_solution_order.keys())}"
            )
        self.core.solution_order = _mapping_solution_order[value]

    @property
    def solver_type(self) -> str:
        """Get solver type.

        Returns
        -------
        str
            Solver type.
        """
        reverse_mapping = {v: k for k, v in _mapping_solver_type.items()}
        return reverse_mapping[self.core.solver_type]

    @solver_type.setter
    def solver_type(self, value: str):
        if not (value in _mapping_solver_type.keys()):
            raise ValueError(f"Invalid solver type: {value}. Valid options are: {list(_mapping_solver_type.keys())}")
        self.core.solver_type = _mapping_solver_type[value]

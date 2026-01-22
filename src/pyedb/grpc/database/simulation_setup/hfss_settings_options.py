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
    from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
        BasisFunctionOrder as GrpcBasisFunctionOrder,
        HFSSSettingsOptions as GrpcHFSSSettingsOptions,
        SolverType as GrpcSolverType,
    )


class HFSSSettingsOptions:
    """PyEDB-core HFSS settings options class."""

    def __init__(self, _pedb, core: GrpcHFSSSettingsOptions):
        self.core = core
        self._pedb = _pedb

    @property
    def do_lambda_refine(self) -> bool:
        """Flag to enable/disable lambda refinement.

        Returns
        -------
        bool
            True if lambda refinement is enabled, False otherwise.

        """
        return self.core.do_lambda_refine

    @do_lambda_refine.setter
    def do_lambda_refine(self, value: bool):
        self.core.do_lambda_refine = value

    @property
    def enhanced_low_frequency_accuracy(self) -> bool:
        """Flag to enable/disable enhanced low frequency accuracy.

        Returns
        -------
        bool
            True if enhanced low frequency accuracy is enabled, False otherwise.

        """
        return self.core.enhanced_low_frequency_accuracy

    @enhanced_low_frequency_accuracy.setter
    def enhanced_low_frequency_accuracy(self, value: bool):
        self.core.enhanced_low_frequency_accuracy = value

    @property
    def lambda_target(self) -> float:
        """Lambda target value.

        Returns
        -------
        float
            Lambda target value.

        """
        return self.core.lambda_target

    @lambda_target.setter
    def lambda_target(self, value: float):
        self.core.lambda_target = value

    @property
    def max_refinement_per_pass(self) -> int:
        """Maximum refinement per pass.

        Returns
        -------
        int
            Maximum refinement per pass.

        """
        return self.core.max_refinement_per_pass

    @max_refinement_per_pass.setter
    def max_refinement_per_pass(self, value: int):
        self.core.max_refinement_per_pass = value

    @property
    def mesh_size_factor(self) -> float:
        """Mesh size factor.

        Returns
        -------
        float
            Mesh size factor.

        """
        return self.core.mesh_size_factor

    @mesh_size_factor.setter
    def mesh_size_factor(self, value: float):
        self.core.mesh_size_factor = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum converged passes.

        Returns
        -------
        int
            Minimum converged passes.

        """
        return self.core.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value: int):
        self.core.min_converged_passes = value

    @property
    def min_passes(self) -> int:
        """Minimum passes.

        Returns
        -------
        int
            Minimum passes.

        """
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        self.core.min_passes = value

    @property
    def order_basis(self) -> str:
        """Order basis name.

        Returns
        -------
        str
            Order basis name.

        """
        return self.core.order_basis.name

    @order_basis.setter
    def order_basis(self, value):
        if value == "ZERO_ORDER":
            self.core.order_basis = GrpcBasisFunctionOrder.ZERO_ORDER
        elif value == "FIRST_ORDER":
            self.core.order_basis = GrpcBasisFunctionOrder.FIRST_ORDER
        elif value == "SECOND_ORDER":
            self.core.order_basis = GrpcBasisFunctionOrder.SECOND_ORDER
        elif value == "MIXED_ORDER":
            self.core.order_basis = GrpcBasisFunctionOrder.MIXED_ORDER

    @property
    def relative_residual(self) -> float:
        """Relative residual value that the HFSS iterative solver is to use.

        Returns
        -------
        float
            Relative residual value.

        """
        return self.core.relative_residual

    @relative_residual.setter
    def relative_residual(self, value: float):
        self.core.relative_residual = value

    @property
    def solver_type(self):
        return self.core.solver_type.name()

    @solver_type.setter
    def solver_type(self, value):
        if value == "AUTO_SOLVER":
            self.core.solver_type = GrpcSolverType.AUTO_SOLVER
        elif value == "DIRECT_SOLVER":
            self.core.solver_type = GrpcSolverType.DIRECT_SOLVER
        elif value == "ITERATIVE_SOLVER":
            self.core.solver_type = GrpcSolverType.ITERATIVE_SOLVER
        elif value == "NUM_SOLVER_TYPES":
            self.core.solver_type = GrpcSolverType.NUM_SOLVER_TYPES

    @property
    def use_default_lambda_value(self) -> bool:
        """Flag to indicate whether to use the default lambda value.

        Returns
        -------
        bool
            True if using the default lambda value, False otherwise.

        """
        return self.core.use_default_lambda_value

    @use_default_lambda_value.setter
    def use_default_lambda_value(self, value: bool):
        self.core.use_default_lambda_value = value

    @property
    def use_max_refinement(self) -> bool:
        """Flag to indicate whether to use maximum refinement.

        Returns
        -------
        bool
            True if using maximum refinement, False otherwise.

        """
        return self.core.use_max_refinement

    @use_max_refinement.setter
    def use_max_refinement(self, value: bool):
        self.core.use_max_refinement = value

    @property
    def use_shell_elements(self) -> bool:
        """Flag to indicate whether to use shell elements.

        Returns
        -------
        bool
            True if using shell elements, False otherwise.

        """
        return self.core.use_shell_elements

    @use_shell_elements.setter
    def use_shell_elements(self, value: bool):
        self.core.use_shell_elements = value

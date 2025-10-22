# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    BasisFunctionOrder as GrpcBasisFunctionOrder,
    HFSSSettingsOptions as GrpcHFSSSettingsOptions,
    SolverType as GrpcSolverType,
)


class HFSSSettingsOptions(GrpcHFSSSettingsOptions):
    """PyEDB-core HFSS settings options class."""

    def __init__(self, _pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = _pedb

    @property
    def order_basis(self) -> str:
        """Order basis name.

        Returns
        -------
        str
            Order basis name.

        """
        return self.order_basis.name

    @order_basis.setter
    def order_basis(self, value):
        if value == "ZERO_ORDER":
            self.order_basis = GrpcBasisFunctionOrder.ZERO_ORDER
        elif value == "FIRST_ORDER":
            self.order_basis = GrpcBasisFunctionOrder.FIRST_ORDER
        elif value == "SECOND_ORDER":
            self.order_basis = GrpcBasisFunctionOrder.SECOND_ORDER
        elif value == "MIXED_ORDER":
            self.order_basis = GrpcBasisFunctionOrder.MIXED_ORDER

    @property
    def solver_type(self):
        return self.solver_type.name()

    @solver_type.setter
    def solver_type(self, value):
        if value == "AUTO_SOLVER":
            self.solver_type = GrpcSolverType.AUTO_SOLVER
        elif value == "DIRECT_SOLVER":
            self.solver_type = GrpcSolverType.DIRECT_SOLVER
        elif value == "ITERATIVE_SOLVER":
            self.solver_type = GrpcSolverType.ITERATIVE_SOLVER
        elif value == "NUM_SOLVER_TYPES":
            self.solver_type = GrpcSolverType.NUM_SOLVER_TYPES

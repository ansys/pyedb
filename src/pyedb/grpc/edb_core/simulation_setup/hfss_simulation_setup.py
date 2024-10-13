# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


from ansys.edb.core.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup as GrpcHfssSimulationSetup,
)

# from pyedb.grpc.edb_core.simulation_setup.hfss_simulation_settings import (
#     HFSSSimulationSettings,
# )
# from pyedb.grpc.edb_core.simulation_setup.mesh_operation import MeshOperation
# from pyedb.grpc.edb_core.simulation_setup.sweep_data import SweepData


class HfssSimulationSetup(GrpcHfssSimulationSetup):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, pedb, edb_object, name: str = None):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._name = name

    # @property
    # def settings(self):
    #     return HFSSSimulationSettings(self._pedb, self.settings)
    #
    # @property
    # def sweep_data(self):
    #     return SweepData(self._pedb, super().sweep_data)
    #
    # @property
    # def mesh_operations(self):
    #     """Mesh operations settings Class.
    #
    #     Returns
    #     -------
    #     List of :class:`dotnet.edb_core.edb_data.hfss_simulation_setup_data.MeshOperation`
    #
    #     """
    #     return MeshOperation(self._pedb, super().mesh_operations)

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


from ansys.edb.core.simulation_setup.q3d_simulation_setup import Q3DSimulationSetup as GrpcQ3DSimulationSetup

from pyedb.grpc.database.simulation_setup.q3d_simulation_settings import Q3DSimulationSettings
from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup
from pyedb.grpc.database.simulation_setup.sweep_data import SweepData


class Q3DSimulationSetup(SimulationSetup):
    """Q3D simulation setup management.

    Parameters
    ----------
    pedb : :class:`Edb < pyedb.grpc.edb.Edb>`
        Inherited object.
    """

    def __init__(self, pedb, core: GrpcQ3DSimulationSetup):
        super().__init__(pedb, core)
        self.core: GrpcQ3DSimulationSetup
        self._pedb = pedb

    @classmethod
    def create(cls, edb: "Edb", name: str = "Q3D_setup") -> "Q3DSimulationSetup":
        """Create a Q3D simulation setup.

        Parameters
        ----------
        edb : :class:`Edb < pyedb.grpc.edb.Edb>`
            Inherited object.

        name : str, optional
            Name of the simulation setup, by default "Q3D_setup".

        Returns
        -------
        :class:`Q3DSimulationSetup < pyedb.grpc.database.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup>`
            The Q3D simulation setup object.
        """
        core = GrpcQ3DSimulationSetup.create(edb.active_cell, name)
        return cls(edb, core)

    @property
    def settings(self) -> Q3DSimulationSettings:
        """Q3D simulation settings.

        Returns
        -------
        :class:`Q3DSimulationSettings
        < pyedb.grpc.database.simulation_setup.q3d_simulation_settings.Q3DSimulationSettings>`
            The Q3D simulation settings object.
        """
        return Q3DSimulationSettings(self._pedb, self.core.settings)

    @property
    def sweep_data(self) -> list[SweepData]:
        """Get sweep data.

        Returns
        -------
        list[:class:`SweepData < pyedb.grpc.database.simulation_setup.sweep_data.SweepData>`]
            List of sweep data objects.
        """
        return [SweepData(self._pedb, sd) for sd in self.core.sweep_data]

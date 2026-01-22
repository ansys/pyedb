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
import warnings

from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup
import pyedb.grpc.edb

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.raptor_x_simulation_setup import (
        RaptorXSimulationSetup as GrpcRaptorXSimulationSetup,
    )

from pyedb.grpc.database.simulation_setup.raptor_x_simulation_settings import RaptorXSimulationSettings
from pyedb.grpc.database.simulation_setup.sweep_data import SweepData


class RaptorXSimulationSetup(SimulationSetup):
    """RaptorX simulation setup."""

    def __init__(self, pedb, core: "GrpcRaptorXSimulationSetup"):
        super().__init__(pedb, core)
        self.core = core
        self._pedb = pedb

    @classmethod
    def create(cls, edb: pyedb.grpc.edb.Edb, name: str = "RaptorX_Simulation_Setup"):
        """Create RaptorX simulation setup.

        Parameters
        ----------
        edb : PyEDB Edb object
            PyEDB Edb object.
        name : str
            Name of the simulation setup.

        Returns
        -------
        RaptorXSimulationSetup
            RaptorX simulation setup object.

        """
        core = GrpcRaptorXSimulationSetup.create(edb.active_cell, name)
        return cls(edb, core)

    @property
    def settings(self) -> RaptorXSimulationSettings:
        """RaptorX simulation settings.

        Returns
        -------
        RaptorXSimulationSettings
            RaptorX simulation settings object.

        """
        return RaptorXSimulationSettings(self._pedb, self.core.settings)

    @property
    def sweep_data(self) -> list[SweepData]:
        """Returns Frequency sweeps.

        Returns
        -------
        list[SweepData]
            List of SweepData objects.

        """
        sweeps = []
        for sweep in self.core.sweep_data:
            sweeps.append(SweepData(self._pedb, core=sweep))
        return sweeps

    @sweep_data.setter
    def sweep_data(self, value: list[SweepData]):
        sweep_data = [sweep.core for sweep in value]
        self.core.sweep_data = sweep_data

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


import warnings

from ansys.edb.core.simulation_setup.siwave_dcir_simulation_setup import (
    SIWaveDCIRSimulationSetup as GrpcSIWaveDCIRSimulationSetup,
)

from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_dc_settings import SIWaveDCSettings
from pyedb.grpc.database.simulation_setup.siwave_simulation_settings import SIWaveSimulationSettings


class SIWaveDCIRSimulationSetup(SimulationSetup):
    """Siwave Dcir simulation setup class."""

    def __init__(self, pedb, core: "GrpcSIWaveDCIRSimulationSetup"):
        super().__init__(pedb, core)
        self.core = core
        self._pedb = pedb

    @classmethod
    def create(cls, edb: "ansys.edb.core.Edb", name: str = "Siwave_DCIR"):
        """Create a SIWave DCIR simulation setup.

        Parameters
        ----------
        edb : ansys.edb.core.Edb
            An EDB instance.

        name : str
            Name of the simulation setup.

        Returns
        -------
        SIWaveDCIRSimulationSetup
            The SIWave DCIR simulation setup object.

        """
        core_setup = GrpcSIWaveDCIRSimulationSetup.create(edb.active_cell, name=name)
        return cls(edb, core_setup)

    @property
    def dc_ir_settings(self):
        """SIWave DCIR simulation settings.

        ... deprecated:: 0.77.3
        Use :attr:`settings.dc
        <pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup.settings>`
        instead.

        """
        warnings.warn("`dc_ir_settings` is deprecated. Use `settings.dc` instead.", DeprecationWarning)
        return SIWaveDCSettings(self._pedb, self.core.settings)

    @property
    def settings(self) -> SIWaveSimulationSettings:
        """SIWave DCIR simulation settings.

        Returns
        -------
        SIWaveSimulationSettings
            The SIWave DCIR simulation settings object.

        """
        return SIWaveSimulationSettings(self._pedb, self.core.settings)

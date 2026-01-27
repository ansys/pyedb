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

from ansys.edb.core.simulation_setup.siwave_simulation_setup import SIWaveSimulationSetup as GrpcSIWaveSimulationSetup

from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_advanced_settings import SIWaveAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_advanced import SIWaveDCAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_settings import SIWaveDCSettings
from pyedb.grpc.database.simulation_setup.siwave_simulation_settings import SIWaveSimulationSettings

if TYPE_CHECKING:
    from pyedb.grpc.edb import Edb


class SiwaveSimulationSetup(SimulationSetup):
    """SIwave simulation setup class."""

    def __init__(self, pedb, core: "GrpcSIWaveSimulationSetup"):
        super().__init__(pedb, core)
        # give static analyzers a concrete type for core
        self.core: GrpcSIWaveSimulationSetup = core
        self._pedb = pedb

    @classmethod
    def create(cls, edb: "Edb", name: str = "siwave_setup") -> "SiwaveSimulationSetup":
        """Create a SIWave simulation setup object.

        Parameters
        ----------
        edb : :class:`Edb`
            Inherited object.

        name : str, optional
            Name of the simulation setup. The default is "siwave_setup".

        Returns
        -------
        SiwaveSimulationSetup
            The SIWave simulation setup object.
        """
        core = GrpcSIWaveSimulationSetup.create(edb.active_cell, name)
        return cls(edb, core)

    @property
    def settings(self) -> SIWaveSimulationSettings:
        """Setup simulation settings."""
        return SIWaveSimulationSettings(self._pedb, self.core.settings)

    @property
    def advanced_settings(self) -> SIWaveAdvancedSettings:
        """Setup advanced settings."""
        return self.settings.advanced

    @property
    def dc_settings(self) -> SIWaveDCSettings:
        """Setup dc settings."""
        return self.settings.dc

    @property
    def dc_advanced_settings(self) -> SIWaveDCAdvancedSettings:
        """Setup dc settings."""
        return self.settings.dc_advanced

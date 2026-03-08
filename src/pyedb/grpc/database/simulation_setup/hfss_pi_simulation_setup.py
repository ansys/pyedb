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

from ansys.edb.core.simulation_setup.hfss_pi_simulation_setup import HFSSPISimulationSetup as CoreHFSSPISimulationSetup

from pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings import HFSSPISimulationSettings
from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup

if TYPE_CHECKING:
    from pyedb.grpc.edb import Edb


class HFSSPISimulationSetup(SimulationSetup):
    """HFSS PI simulation setup class."""

    def __init__(self, pedb, core: "CoreHFSSPISimulationSetup"):
        super().__init__(pedb, core)
        self.core = core
        self._pedb = pedb

    @classmethod
    def create(cls, edb: "Edb", name: str = "HFSS_PI") -> "HFSSPISimulationSetup":
        """Create a HFSS PI simulation setup.

        Parameters
        ----------
        edb : Edb
            An EDB instance.

        name : str
            Name of the simulation setup.

        Returns
        -------
        HFSSPISimulationSetup
            The HFSS PI simulation setup object.

        """
        core_setup = CoreHFSSPISimulationSetup.create(edb.active_cell, name)
        return cls(edb, core_setup)

    @property
    def settings(self) -> HFSSPISimulationSettings:
        """Get the HFSS PI simulation settings.

        Returns
        -------
        HFSSPISimulationSettings
            The HFSS PI simulation settings object.

        """
        return HFSSPISimulationSettings(self._pedb, self.core.settings)

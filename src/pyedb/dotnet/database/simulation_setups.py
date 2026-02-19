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


from pyedb.dotnet.database.utilities.hfss_simulation_setup import HfssSimulationSetup
from pyedb.dotnet.database.utilities.siwave_simulation_setup import SiwaveDCSimulationSetup, SiwaveSimulationSetup
from pyedb.generic.general_methods import generate_unique_name


class SimulationSetups:
    """Simulation setups container class."""

    def __init__(self, pedb):
        self._pedb = pedb

    def create(
        self,
        name=None,
        solver="hfss",
    ):
        """Add analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        solver : str, optional
            Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptor_x", "q3d").
        """
        if not name:
            name = generate_unique_name(f"{solver}_setup")
        if name in self._pedb.setups:
            raise ValueError(f"Simulation setup {name} already defined.")
        if solver.lower() == "hfss":
            setup = HfssSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"HFSS setup {name} created.")
        elif solver.lower() == "siwave":
            setup = SiwaveSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave setup {name} created.")
        elif solver.lower() == "siwave_dcir":
            setup = SiwaveDCSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave DCIR setup {name} created.")
        else:
            raise ValueError(f"Unsupported solver type: {solver}.")
        return setup

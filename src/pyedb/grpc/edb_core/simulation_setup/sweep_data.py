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

from ansys.edb.core.simulation_setup.simulation_setup import (
    FreqSweepType as GrpcFreqSweepType,
)
from ansys.edb.core.simulation_setup.simulation_setup import SweepData as GrpcSweepData


class SweepData(GrpcSweepData):
    """Manages EDB methods for a frequency sweep.

    Parameters
    ----------
    sim_setup : :class:`pyedb.dotnet.edb_core.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
    name : str, optional
        Name of the frequency sweep.
    edb_object : :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`, optional
        EDB object. The default is ``None``.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def sweep_type(self):
        """Sweep type.

        Options are:
        - ``"INTERPOLATING_SWEEP"``
        - ``"DISCRETE_SWEEP"``
        - ``"BROADBAND_SWEEP"``

        Returns
        -------
        str
            Sweep type.
        """
        return self.type.name

    @property
    def type(self):
        return self.type.name

    @type.setter
    def type(self, value):
        if value.upper() == "INTERPOLATING_SWEEP":
            self.type = GrpcFreqSweepType.INTERPOLATING_SWEEP
        elif value.upper() == "DISCRETE_SWEEP":
            self.type = GrpcFreqSweepType.DISCRETE_SWEEP
        elif value.upper() == "BROADBAND_SWEEP":
            self.type = GrpcFreqSweepType.BROADBAND_SWEEP

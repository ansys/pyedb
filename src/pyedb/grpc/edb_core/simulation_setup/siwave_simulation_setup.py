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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.edb.core.simulation_setup.simulation_setup import (
    SimulationSetupType as GrpcSimulationSetupType,
)
from ansys.edb.core.simulation_setup.siwave_simulation_setup import (
    SIWaveSimulationSetup as GrpcSIWaveSimulationSetup,
)


class SiwaveSimulationSetup(GrpcSIWaveSimulationSetup):
    """Manages EDB methods for SIwave simulation setup."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def type(self):
        return super().type.name

    @type.setter
    def type(self, value):
        if value.upper() == "SI_WAVE":
            super(SiwaveSimulationSetup, self.__class__).type.__set__(self, GrpcSimulationSetupType.SI_WAVE)
        elif value.upper() == "SI_WAVE_DCIR":
            super(SiwaveSimulationSetup, self.__class__).type.__set__(self, GrpcSimulationSetupType.SI_WAVE_DCIR)

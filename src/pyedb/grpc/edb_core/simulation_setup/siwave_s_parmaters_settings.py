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


from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SIWaveSParameterSettings as GrpcSIWaveSParameterSettings,
)
from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SParamDCBehavior as GrpcSParamDCBehavior,
)
from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SParamExtrapolation as GrpcSParamExtrapolation,
)
from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SParamInterpolation as GrpcSParamInterpolation,
)


class SIWaveSParameterSettings(GrpcSIWaveSParameterSettings):
    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb

    @property
    def dc_behavior(self):
        return GrpcSParamDCBehavior.name

    @dc_behavior.setter
    def dc_behavior(self, value):
        if value == "ZERO_DC":
            self.dc_behavior = GrpcSParamDCBehavior.ZERO_DC
        elif value == "SAME_DC":
            self.dc_behavior = GrpcSParamDCBehavior.SAME_DC
        elif value == "LINEAR_DC":
            self.dc_behavior = GrpcSParamDCBehavior.LINEAR_DC
        elif value == "CONSTANT_DC":
            self.dc_behavior = GrpcSParamDCBehavior.CONSTANT_DC
        elif value == "ONE_PORT_CAPACITOR_DC":
            self.dc_behavior = GrpcSParamDCBehavior.ONE_PORT_CAPACITOR_DC
        elif value == "OPEN_DC":
            self.dc_behavior = GrpcSParamDCBehavior.OPEN_DC

    @property
    def extrapolation(self):
        return self.extrapolation.name

    @extrapolation.setter
    def extrapolation(self, value):
        if value == "ZERO_EX":
            self.extrapolation = GrpcSParamExtrapolation.ZERO_EX
        elif value == "SAME_EX":
            self.extrapolation = GrpcSParamExtrapolation.SAME_EX
        elif value == "LINEAR_EX":
            self.extrapolation = GrpcSParamExtrapolation.LINEAR_EX
        elif value == "CONSTANT_EX":
            self.extrapolation = GrpcSParamExtrapolation.CONSTANT_EX

    @property
    def interpolation(self):
        return self.interpolation.name

    @interpolation.setter
    def interpolation(self, value):
        if value == "POINT_IN":
            self.interpolation = GrpcSParamInterpolation.POINT_IN
        elif value == "LINEAR_IN":
            self.interpolation = GrpcSParamInterpolation.LINEAR_IN
        elif value == "STEP_IN":
            self.interpolation = GrpcSParamInterpolation.STEP_IN

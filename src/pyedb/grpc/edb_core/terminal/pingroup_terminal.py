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

from ansys.edb.core.terminal.terminals import BoundaryType as GrpcBoundaryType
from ansys.edb.core.terminal.terminals import PinGroupTerminal as GrpcPinGroupTerminal

from pyedb.grpc.edb_core.nets.net import Net


class PinGroupTerminal(GrpcPinGroupTerminal):
    """Manages pin group terminal properties."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._edb_object = edb_object
        self._pedb = pedb

    @property
    def boundary_type(self):
        return super().boundary_type.name.lower()

    @boundary_type.setter
    def boundary_type(self, value):
        if value == "voltage_source":
            value = GrpcBoundaryType.VOLTAGE_SOURCE
        if value == "current_source":
            value = GrpcBoundaryType.CURRENT_SOURCE
        if value == "port":
            value = GrpcBoundaryType.PORT
        if value == "voltage_probe":
            value = GrpcBoundaryType.VOLTAGE_PROBE
        super(PinGroupTerminal, self.__class__).boundary_type.__set__(self, value)

    @property
    def magnitude(self):
        return self.source_amplitude

    @magnitude.setter
    def magnitude(self, value):
        self.source_amplitude = value

    @property
    def phase(self):
        return self.source_phase

    @phase.setter
    def phase(self, value):
        self.source_phase = value

    @property
    def source_amplitude(self):
        return super().source_amplitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        super(PinGroupTerminal, self.__class__).source_amplitude.__set__(self, value)

    @property
    def source_phase(self):
        return super().source_amplitude.value

    @source_phase.setter
    def source_phase(self, value):
        super(PinGroupTerminal, self.__class__).source_phase.__set__(self, value)

    @property
    def impedance(self):
        return super().impedance.value

    @impedance.setter
    def impedance(self, value):
        super(PinGroupTerminal, self.__class__).impedance.__set__(self, value)

    @property
    def net(self):
        return Net(self._pedb, super().net)

    @net.setter
    def net(self, value):
        super(PinGroupTerminal, self.__class__).net.__set__(self, value)

    @property
    def pin_group(self):
        from pyedb.grpc.edb_core.hierarchy.pingroup import PinGroup

        return PinGroup(self._pedb, super().pin_group)

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

from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as GrpcPinGroupTerminal,
)
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

from pyedb.grpc.database.net.net import Net
from pyedb.misc.misc import deprecated_property


class PinGroupTerminal(GrpcPinGroupTerminal):
    """Manages pin group terminal properties."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._edb_object = edb_object
        self._pedb = pedb

    @property
    def boundary_type(self):
        """Boundary type.

        Returns
        -------
        str : boundary type.
        """
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
    def is_port(self):
        if self.boundary_type == "port":
            return True
        return False

    @property
    def magnitude(self):
        """Source magnitude.

        Returns
        -------
        float : magnitude value.

        """
        return self.source_amplitude

    @magnitude.setter
    def magnitude(self, value):
        self.source_amplitude = value

    @property
    def phase(self):
        """Source phase.

        Returns
        -------
        float : phase value.

        """
        return self.source_phase

    @phase.setter
    def phase(self, value):
        self.source_phase = value

    @property
    def source_amplitude(self):
        """Source amplitude.

        Returns
        -------
        float : source magnitude.

        """
        return super().source_amplitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        super(PinGroupTerminal, self.__class__).source_amplitude.__set__(self, value)

    @property
    def source_phase(self):
        """Source phase.

        Returns
        -------
        foat : source phase.

        """
        return super().source_amplitude.value

    @source_phase.setter
    def source_phase(self, value):
        super(PinGroupTerminal, self.__class__).source_phase.__set__(self, value)

    @property
    def impedance(self):
        """Terminal impedance.

        Returns
        -------
        float : terminal impedance.

        """
        return super().impedance.value

    @impedance.setter
    def impedance(self, value):
        super(PinGroupTerminal, self.__class__).impedance.__set__(self, value)

    @property
    def net(self):
        """Terminal net.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
            Terminal Net object.

        """
        return Net(self._pedb, super().net)

    @net.setter
    def net(self, value):
        super(PinGroupTerminal, self.__class__).net.__set__(self, value)

    @property
    def pin_group(self):
        """Pingroup.

        Returns
        -------
        :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
            Terminal pingroup.

        """
        from pyedb.grpc.database.hierarchy.pingroup import PinGroup

        return PinGroup(self._pedb, super().pin_group)

    @property
    def terminal_type(self):
        return "PinGroupTerminal"

    @property
    @deprecated_property
    def ref_terminal(self):
        """Property keeping DotNet compatibility

        ..deprecated:: 0.43.0
           Use: func:`reference_terminal` property instead.

        """
        self._pedb.logger.warning("ref_terminal property is deprecated, use reference_terminal property instead.")
        return PinGroupTerminal(self._pedb, self.reference_terminal)

    @ref_terminal.setter
    def ref_terminal(self, value):
        self._pedb.logger.warning("ref_terminal is deprecated, use reference_terminal instead.")
        self.reference_terminal = value

    @property
    def hfss_type(self):
        return "circuit"

    @property
    def is_current_source(self):
        if self.boundary_type == "current_source":
            return True
        return False

    @property
    def is_voltage_source(self):
        if self.boundary_type == "voltage_source":
            return True
        return False

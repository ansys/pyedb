# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.grpc.database.net.net import Net
from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as GrpcPinGroupTerminal,
)
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecated_property

boundary_type_mapping = {
    "voltage_source": GrpcBoundaryType.VOLTAGE_SOURCE,
    "current_source": GrpcBoundaryType.CURRENT_SOURCE,
    "port": GrpcBoundaryType.PORT,
    "voltage_probe": GrpcBoundaryType.VOLTAGE_PROBE,
}


class PinGroupTerminal:
    """Manages pin group terminal properties."""

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @property
    def name(self) -> str:
        """Terminal name.

        Returns
        -------
        str : terminal name.
        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def boundary_type(self) -> str:
        """Boundary type.

        Returns
        -------
        str : boundary type.
        `"voltage_source"`, `"current_source"`, `"port"`, `"voltage_probe"`.
        """
        return self.core.boundary_type.name.lower()

    @boundary_type.setter
    def boundary_type(self, value):
        if isinstance(value, str):
            value = boundary_type_mapping.get(value, None)
        if value is None:
            raise Exception(f"Unknown boundary type")
        self.core.boundary_type = value

    @property
    def is_port(self) -> bool:
        if self.boundary_type == "port":
            return True
        return False

    @property
    def magnitude(self) -> float:
        """Source magnitude.

        Returns
        -------
        float : magnitude value.

        """
        return Value(self.source_amplitude)

    @magnitude.setter
    def magnitude(self, value):
        self.source_amplitude = Value(value)

    @property
    def phase(self) -> float:
        """Source phase.

        Returns
        -------
        float : phase value.

        """
        return Value(self.source_phase)

    @phase.setter
    def phase(self, value):
        self.source_phase = Value(value)

    @property
    def source_amplitude(self) -> float:
        """Source amplitude.

        Returns
        -------
        float : source magnitude.

        """
        return Value(self.core.source_amplitude)

    @source_amplitude.setter
    def source_amplitude(self, value):
        self.core.source_amplitude = Value(value)

    @property
    def source_phase(self) -> float:
        """Source phase.

        Returns
        -------
        foat : source phase.

        """
        return self.core.source_amplitude

    @source_phase.setter
    def source_phase(self, value):
        self.core.source_phase = Value(value)

    @property
    def impedance(self) -> float:
        """Terminal impedance.

        Returns
        -------
        float : terminal impedance.

        """
        return self.core.impedance

    @impedance.setter
    def impedance(self, value):
        self.core.impedance = Value(value)

    @property
    def net(self) -> Net:
        """Terminal net.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
            Terminal Net object.

        """
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.net)

    @net.setter
    def net(self, value):
        self.core.net = value

    @property
    def pin_group(self) -> any:
        """Pingroup.

        Returns
        -------
        :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
            Terminal pingroup.

        """
        from pyedb.grpc.database.hierarchy.pingroup import PinGroup

        return PinGroup(self._pedb, self.core.pin_group)

    @property
    def terminal_type(self) -> str:
        return "PinGroupTerminal"

    @property
    def is_null(self) -> bool:
        """Check if the terminal is a null terminal.

        Returns
        -------
        bool
            True if the terminal is null, False otherwise.

        """
        return self.core.is_null

    @property
    def reference_terminal(self) -> any:
        """Reference terminal.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`
            Reference terminal.

        """
        return PinGroupTerminal(self._pedb, self.core.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        if isinstance(value, PinGroupTerminal):
            self.core.reference_terminal = value.core
        elif isinstance(value, GrpcPinGroupTerminal):
            self.core.reference_terminal = value
        else:
            raise TypeError("Value must be a PinGroupTerminal or GrpcPinGroupTerminal object.")

    @property
    def is_reference_terminal(self) -> bool:
        """Check if the terminal is a reference terminal.

        Returns
        -------
        bool
            True if the terminal is a reference terminal, False otherwise.

        """
        return self.core.is_reference_terminal

    @property
    @deprecated_property
    def ref_terminal(self):
        """Property keeping DotNet compatibility

        ..deprecated:: 0.43.0
           Use: func:`reference_terminal` property instead.

        """
        Exception("ref_terminal property is deprecated, use reference_terminal property instead.", DeprecationWarning)
        return PinGroupTerminal(self._pedb, self.core.reference_terminal)

    @ref_terminal.setter
    def ref_terminal(self, value):
        Exception("ref_terminal property is deprecated, use reference_terminal property instead.", DeprecationWarning)
        self.core.reference_terminal = value

    @property
    def hfss_type(self) -> str:
        return "circuit"

    @property
    def is_current_source(self) -> bool:
        if self.boundary_type == "current_source":
            return True
        return False

    @property
    def is_voltage_source(self):
        if self.boundary_type == "voltage_source":
            return True
        return False

    @classmethod
    def create(cls, layout, name, pin_group, net=None, is_ref=False):
        """Create a pin group terminal.
        Parameters
        ----------
        layout : :class:`.Layout`
            Layout to create the pin group terminal in.
        name : :obj:`str`
            Name of the pin group terminal.
        pin_group : :class:`.PinGroup`
            Pin group.
        net : :class:`.Net` or :obj:`str`, optional
            Net.
        is_ref : :obj:`bool`, default: False
            Whether the pin group terminal is a reference terminal.
        Returns
        -------
        PinGroupTerminal
        """
        term = GrpcPinGroupTerminal.create(layout.core, name, pin_group.core, net.core, is_ref)
        return cls(layout._pedb, term)

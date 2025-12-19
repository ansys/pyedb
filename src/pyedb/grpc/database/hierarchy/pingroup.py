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
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from typing import Union

from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.database.utility.value import Value


class PinGroup:
    """Manages pin groups."""

    def __init__(self, pedb, edb_pin_group=None):
        if edb_pin_group:
            self.core = edb_pin_group
        self._pedb = pedb

    @classmethod
    def create(cls, layout, name, padstack_instances) -> PinGroup:
        """Create a pin group.

        Parameters
        ----------
        layout : :class:`Layout <ansys.edb.core.layout.layout.Layout>`
            Layout object.
        name : str
            Pin group name.
        padstack_instances : List[:class:
        `PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            List of padstack instances.

        Returns
        -------
        :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
            Pin group object.

        """
        if not isinstance(padstack_instances, list):
            raise TypeError("padstack_instances must be list of PadstackInstance")
        pin_group = GrpcPinGroup.create(layout.core, name, [inst.core for inst in padstack_instances])
        return cls(layout._pedb, pin_group)

    @property
    def name(self):
        """Pin group name.

        Returns
        -------
        str
            Pin group name.

        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def _active_layout(self):
        """Active layout.

        Returns
        -------
        :class:`Layout <ansys.edb.core.layout.layout.Layout>`
            Active layout.

        """
        return self._pedb.active_layout

    @property
    def component(self) -> Component:
        """Component.

        Return
        ------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`
            Pin group component.
        """

        return Component(self._pedb, self.core.component)

    @component.setter
    def component(self, value):
        from pyedb.grpc.database.hierarchy.component import Component

        if isinstance(value, Component):
            if isinstance(value, Component):
                self.core.component = value.core

    @property
    def is_null(self) -> bool:
        """Check if pin group is null.

        Returns
        -------
        bool
            ``True`` if pin group is null, ``False`` otherwise.

        """
        return self.core.is_null

    @property
    def pins(self) -> dict[str, PadstackInstance]:
        """Pin group pins.

        Returns
        -------
        Dict[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`].
        """
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        return {i.name: PadstackInstance(self._pedb, i) for i in self.core.pins}

    @property
    def net(self) -> Net:
        """Net.

        Returns
        -------
        :class:`Net <ansys.edb.core.net.net.Net>`.
        """
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.net)

    @net.setter
    def net(self, value):
        from pyedb.grpc.database.net.net import Net

        if isinstance(value, Net):
            self.core.net = value.core

    @property
    def net_name(self) -> str:
        """Net name.

        Returns
        -------
        str
            Net name.

        """
        return self.net.name

    @property
    def terminal(self) -> Union[PinGroupTerminal, None]:
        """Terminal."""
        term = self.core.pin_group_terminal
        if not term.is_null:
            term = PinGroupTerminal(self._pedb, term)
            return term
        else:
            return None

    @staticmethod
    def unique_name(layout, base_name: str) -> str:
        """Generate unique name.

        Parameters
        ----------
        layout : :class:`Layout <pyedb.edb.layout.layout.Layout>`
            Layout object.
        base_name : str
            Base name.

        Returns
        -------
        str
            Unique name.

        """
        return GrpcPinGroup.unique_name(layout.core, base_name)

    def create_terminal(self, name=None) -> PinGroupTerminal:
        """Create a terminal.

        Parameters
        ----------
        name : str, optional
            Name of the terminal.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
            Pin group terminal.

        """
        if not name:
            name = generate_unique_name(self.name)
        term = PinGroupTerminal.create(
            layout=self._active_layout, name=name, pin_group=self, net=self.net, is_ref=False
        )
        return PinGroupTerminal(self._pedb, term)

    def _json_format(self) -> dict[str, any]:
        """Format json.

        Returns
        -------
        Dict
        """
        dict_out = {"component": self.component, "name": self.name, "net": self.net, "node_type": self.core.node_type}
        return dict_out

    def create_current_source_terminal(self, magnitude=1.0, phase=0, impedance=1e6) -> PinGroupTerminal:
        """Create current source terminal.

        Parameters
        ----------
        magnitude : float or int, optional
            Source magnitude, default value ``1.0``.
        phase : float or int, optional
            Source phase, default value ``0.0``.
        impedance : float, optional
            Source impedance, default value ``1e6``.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
            Pin group terminal.

        """
        terminal = self.create_terminal()
        terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
        terminal.source_amplitude = Value(magnitude)
        terminal.source_phase = Value(phase)
        terminal.impedance = Value(impedance)
        return terminal

    def create_voltage_source_terminal(self, magnitude=1, phase=0, impedance=0.001) -> PinGroupTerminal:
        """Create voltage source terminal.

        Parameters
        ----------
        magnitude : float or int, optional
            Source magnitude, default value ``1.0``.
        phase : float or int, optional
            Source phase, default value ``0.0``.
        impedance : float, optional
            Source impedance, default value ``1e-3``.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
            Pin group terminal.

        """
        terminal = self.create_terminal()
        terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
        terminal.source_amplitude = Value(magnitude)
        terminal.source_phase = Value(phase)
        terminal.impedance = Value(impedance)
        return terminal

    def create_voltage_probe_terminal(self, impedance=1e6) -> PinGroupTerminal:
        """Create voltage probe terminal.

        Parameters
        ----------
        impedance : float, optional
            Probe impedance, default value ``1e6``.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
            Pin group terminal.

        """
        terminal = self.create_terminal()
        terminal.boundary_type = GrpcBoundaryType.VOLTAGE_PROBE
        terminal.impedance = Value(impedance)
        return terminal

    def create_port_terminal(self, impedance=50) -> PinGroupTerminal:
        """Create port terminal.

        Parameters
        ----------
        impedance : float, optional
            Port impedance, default value ``50``.

        Returns
        -------
        :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
            Pin group terminal.

        """
        terminal = self.create_terminal()
        terminal.boundary_type = "port"
        terminal.impedance = Value(impedance)
        terminal.is_circuit_port = True
        return terminal

    def delete(self):
        """Delete active pin group.

        Returns
        -------
        bool

        """
        return self.core.delete()

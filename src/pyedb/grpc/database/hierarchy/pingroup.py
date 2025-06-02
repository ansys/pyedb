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


from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.hierarchy.component import Component
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal


class PinGroup(GrpcPinGroup):
    """Manages pin groups."""

    def __init__(self, pedb, edb_pin_group=None):
        if edb_pin_group:
            super().__init__(edb_pin_group.msg)
        self._pedb = pedb

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
    def component(self):
        """Component.

        Return
        ------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`
            Pin group component.
        """
        return Component(self._pedb, super().component)

    @component.setter
    def component(self, value):
        if isinstance(value, Component):
            super(PinGroup, self.__class__).component.__set__(self, value)

    @property
    def pins(self):
        """Pin group pins.

        Returns
        -------
        Dict[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`].
        """
        return {i.name: PadstackInstance(self._pedb, i) for i in super().pins}

    @property
    def net(self):
        """Net.

        Returns
        -------
        :class:`Net <ansys.edb.core.net.net.Net>`.
        """
        return Net(self._pedb, super().net)

    @net.setter
    def net(self, value):
        if isinstance(value, Net):
            super(PinGroup, self.__class__).net.__set__(self, value)

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Net name.

        """
        return self.net.name

    @property
    def terminal(self):
        """Terminal."""
        term = self.pin_group_terminal
        if not term.is_null:
            term = PinGroupTerminal(self._pedb, term)
            return term
        else:
            return None

    def create_terminal(self, name=None):
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

    def _json_format(self):
        """Format json.

        Returns
        -------
        Dict
        """
        dict_out = {"component": self.component, "name": self.name, "net": self.net, "node_type": self.node_type}
        return dict_out

    def create_current_source_terminal(self, magnitude=1.0, phase=0, impedance=1e6):
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
        terminal.source_amplitude = GrpcValue(magnitude)
        terminal.source_phase = GrpcValue(phase)
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_voltage_source_terminal(self, magnitude=1, phase=0, impedance=0.001):
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
        terminal.source_amplitude = GrpcValue(magnitude)
        terminal.source_phase = GrpcValue(phase)
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_voltage_probe_terminal(self, impedance=1e6):
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
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_port_terminal(self, impedance=50):
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
        terminal.boundary_type = GrpcBoundaryType.PORT
        terminal.impedance = GrpcValue(impedance)
        terminal.is_circuit_port = True
        return terminal

    # def delete(self):
    #     """Delete active pin group.
    #
    #     Returns
    #     -------
    #     bool
    #
    #     """
    #     terminal = self.get_pin_group_terminal()  # TODO check method exists in grpc
    #     self.delete()
    #     terminal.delete()
    #     return True

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
from ansys.edb.core.terminal.terminals import BoundaryType as GrpcBoundaryType
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.edb_core.hierarchy.component import Component
from pyedb.grpc.edb_core.nets.net import Net
from pyedb.grpc.edb_core.primitive.padstack_instances import PadstackInstance
from pyedb.grpc.edb_core.terminal.pingroup_terminal import PinGroupTerminal


class PinGroup(GrpcPinGroup):
    """Manages pin groups."""

    def __init__(self, pedb, edb_pin_group):
        super().__init__(edb_pin_group.msg)
        self._pedb = pedb
        self._edb_pin_group = edb_pin_group
        self._name = edb_pin_group.name
        self._component = ""
        self._node_pins = []
        self._net = ""
        self._edb_object = self._edb_pin_group

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def component(self):
        """Component."""
        return Component(self._pedb, self.component)

    @component.setter
    def component(self, value):
        if isinstance(value, Component):
            self.component = value._edb_object

    @property
    def pins(self):
        """Gets the pins belong to this pin group."""
        return {i.name: PadstackInstance(self._pedb, i) for i in self.pins}

    @property
    def net(self):
        """Net."""
        return Net(self._pedb, self.net)

    @net.setter
    def net(self, value):
        if isinstance(value, Net):
            self.net = value._edb_object

    @property
    def net_name(self):
        return self.net.name

    @property
    def terminal(self):
        """Terminal."""
        term = PinGroupTerminal(self._pedb, self.get_pin_group_terminal())  # TODO check method is missing
        return term if not term.is_null else None

    def create_terminal(self, name=None):
        """Create a terminal.

        Parameters
        ----------
        name : str, optional
            Name of the terminal.
        """
        if not name:
            name = generate_unique_name(self.name)
        term = PinGroupTerminal(self._pedb, self._edb_object)
        term = term.create(name, self.net_name, self.name)
        return term

    def _json_format(self):
        dict_out = {"component": self.component, "name": self.name, "net": self.net, "node_type": self.node_type}
        return dict_out

    def create_current_source_terminal(self, magnitude=1, phase=0, impedance=1e6):
        terminal = self.create_terminal()._edb_object
        terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
        terminal.source_amplitude = GrpcValue(magnitude)
        terminal.source_phase = GrpcValue(phase)
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_voltage_source_terminal(self, magnitude=1, phase=0, impedance=0.001):
        terminal = self.create_terminal()._edb_object
        terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
        terminal.source_amplitude = GrpcValue(magnitude)
        terminal.source_phase = GrpcValue(phase)
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_voltage_probe_terminal(self, impedance=1000000):
        terminal = self.create_terminal()._edb_object
        terminal.boundary_type = GrpcBoundaryType.VOLTAGE_PROBE
        terminal.impedance = GrpcValue(impedance)
        return terminal

    def create_port_terminal(self, impedance=50):
        terminal = self.create_terminal()._edb_object
        terminal.boundary_type = GrpcBoundaryType.PORT
        terminal.impedance = GrpcValue(impedance)
        terminal.is_circuit_port = True
        return terminal

    def delete(self):
        """Delete active pin group.

        Returns
        -------
        bool

        """
        terminal = self.get_pin_group_terminal()  # TODO check method exists in grpc
        self.delete()
        terminal.delete()
        return True

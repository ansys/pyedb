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

"""
This module contains these classes: `EdbLayout` and `Shape`.
"""
from typing import Union

from ansys.edb.core.layout.layout import Layout as GrpcLayout

from pyedb.grpc.edb_core.hierarchy.component import Component
from pyedb.grpc.edb_core.hierarchy.pingroup import PinGroup
from pyedb.grpc.edb_core.layout.voltage_regulator import VoltageRegulator
from pyedb.grpc.edb_core.nets.differential_pair import DifferentialPair
from pyedb.grpc.edb_core.nets.extended_net import ExtendedNet
from pyedb.grpc.edb_core.nets.net import Net
from pyedb.grpc.edb_core.nets.net_class import NetClass
from pyedb.grpc.edb_core.primitive.padstack_instances import PadstackInstance
from pyedb.grpc.edb_core.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.edb_core.terminal.edge_terminal import EdgeTerminal
from pyedb.grpc.edb_core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.edb_core.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.edb_core.terminal.point_terminal import PointTerminal


class Layout(GrpcLayout):
    def __init__(self, pedb):
        super().__init__(pedb.active_cell._Cell__stub.GetLayout(pedb.active_cell.msg))
        self._pedb = pedb

    @property
    def cell(self):
        """:class:`Cell <ansys.edb.layout.Cell>`: Owning cell for this layout.

        Read-Only.
        """
        return self._pedb._active_cell

    @property
    def terminals(self):
        """Get terminals belonging to active layout.

        Returns
        -------
        Terminal dictionary : Dict[str, pyedb.dotnet.edb_core.edb_data.terminals.Terminal]
        """
        temp = []
        for i in self._pedb.active_cell.layout.terminals:
            if i.type == "pin_group":
                temp.append(PinGroupTerminal(self._pedb, i))
            elif i.type == "padstack_instance":
                temp.append(PadstackInstanceTerminal(self._pedb, i))
            elif i.type == "edge":
                temp.append(EdgeTerminal(self._pedb, i))
            elif i.type == "bundle":
                temp.append(BundleTerminal(self._pedb, i))
            elif i.type == "point":
                temp.append(PointTerminal(self._pedb, i))
        return temp

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        """
        return [Net(self._pedb, net) for net in super().nets]

    @property
    def bondwires(self):
        """Bondwires.

        Returns
        -------
        list :
            List of bondwires.
        """
        return [i for i in self.primitives if i.primitive_type == "bondwire"]

    @property
    def groups(self):
        return [Component(self._pedb, g) for g in self._pedb.active_cell.layout.groups]

    @property
    def pin_groups(self):
        return [PinGroup(pedb=self._pedb, edb_pin_group=i) for i in self._pedb.active_cell.layout.pin_groups]

    @property
    def net_classes(self):
        return [NetClass(self._pedb, i) for i in self._pedb.active_cell.layout.net_classes]

    @property
    def extended_nets(self):
        return [ExtendedNet(self._pedb, i) for i in self._pedb.active_cell.layout.extended_nets]

    @property
    def differential_pairs(self):
        return [DifferentialPair(self._pedb, i) for i in self._pedb.active_cell.layout.differential_pairs]

    @property
    def padstack_instances(self):
        """Get all padstack instances in a list."""
        return [PadstackInstance(self._pedb, i) for i in self._pedb.active_cell.layout.padstack_instances]

    #
    @property
    def voltage_regulators(self):
        return [VoltageRegulator(self._pedb, i) for i in self._pedb.active_cell.layout.voltage_regulators]

    def find_primitive(self, layer_name: Union[str, list]) -> list:
        """Find a primitive objects by layer name.

        Parameters
        ----------
        layer_name : str, list
            Name of the layer.
        Returns
        -------
        list
        """
        layer_name = layer_name if isinstance(layer_name, list) else [layer_name]
        return [i for i in self.primitives if i.layer.name in layer_name]

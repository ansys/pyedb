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

from pyedb.dotnet.edb_core.cell.hierarchy.component import EDBComponent
from pyedb.dotnet.edb_core.cell.terminal.bundle_terminal import BundleTerminal
from pyedb.dotnet.edb_core.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.edb_core.cell.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.dotnet.edb_core.cell.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.dotnet.edb_core.cell.terminal.point_terminal import PointTerminal
from pyedb.dotnet.edb_core.cell.voltage_regulator import VoltageRegulator
from pyedb.dotnet.edb_core.edb_data.nets_data import (
    EDBDifferentialPairData,
    EDBExtendedNetData,
    EDBNetClassData,
    EDBNetsData,
)
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.edb_core.edb_data.sources import PinGroup


class Layout(GrpcLayout):
    def __init__(self, pedb):
        super().__init__(self.msg)
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
        for i in self.terminals:
            if i.terminal_type == "pin_group":
                temp.append(PinGroupTerminal(self._pedb, i))
            elif i.terminal_type == "padstack_instance":
                temp.append(PadstackInstanceTerminal(self._pedb, i))
            elif i.terminal_type == "edge":
                temp.append(EdgeTerminal(self._pedb, i))
            elif i.terminal_type == "Bundle":
                temp.append(BundleTerminal(self._pedb, i))
            elif i.terminal_type == "Point":
                temp.append(PointTerminal(self._pedb, i))
        return temp

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        """
        return [EDBNetsData(net, self._pedb) for net in self.nets]

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
        temp = []
        for i in self.groups:
            if i.component:
                temp.append(EDBComponent(self._pedb, i))
            else:
                pass
        return temp

    @property
    def pin_groups(self):
        return [PinGroup(pedb=self._pedb, edb_pin_group=i, name=i.name) for i in self.pin_groups]

    @property
    def net_classes(self):
        return [EDBNetClassData(self._pedb, i) for i in self.net_classes]

    @property
    def extended_nets(self):
        return [EDBExtendedNetData(self._pedb, i) for i in self.extended_nets]

    @property
    def differential_pairs(self):
        return [EDBDifferentialPairData(self._pedb, i) for i in self.differential_pairs]

    @property
    def padstack_instances(self):
        """Get all padstack instances in a list."""
        return [EDBPadstackInstance(i, self._pedb) for i in self.padstack_instances]

    @property
    def voltage_regulators(self):
        return [VoltageRegulator(self._pedb, i) for i in self.voltage_regulators]

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

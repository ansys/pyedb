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
import ansys.edb.core.primitive.bondwire
import ansys.edb.core.primitive.circle
import ansys.edb.core.primitive.padstack_instance
import ansys.edb.core.primitive.path
import ansys.edb.core.primitive.polygon
import ansys.edb.core.primitive.primitive
import ansys.edb.core.primitive.rectangle

from pyedb.grpc.database.hierarchy.component import Component
from pyedb.grpc.database.hierarchy.pingroup import PinGroup
from pyedb.grpc.database.layout.voltage_regulator import VoltageRegulator
from pyedb.grpc.database.net.differential_pair import DifferentialPair
from pyedb.grpc.database.net.extended_net import ExtendedNet
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.net.net_class import NetClass
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.database.terminal.point_terminal import PointTerminal


class Layout(GrpcLayout):
    """Manage Layout class."""

    def __init__(self, pedb):
        super().__init__(pedb.active_cell._Cell__stub.GetLayout(pedb.active_cell.msg))
        self._pedb = pedb

    @property
    def cell(self):
        """:class:`Cell <ansys.edb.core.layout.cel.Cell>`: Owning cell for this layout.

        Read-Only.
        """
        return self._pedb._active_cell

    @property
    def primitives(self):
        prims = []
        for prim in super().primitives:
            if isinstance(prim, ansys.edb.core.primitive.path.Path):
                prims.append(Path(self._pedb, prim))
            elif isinstance(prim, ansys.edb.core.primitive.polygon.Polygon):
                prims.append(Polygon(self._pedb, prim))
            elif isinstance(prim, ansys.edb.core.primitive.padstack_instance.PadstackInstance):
                prims.append(PadstackInstance(self._pedb, prim))
            elif isinstance(prim, ansys.edb.core.primitive.rectangle.Rectangle):
                prims.append(Rectangle(self._pedb, prim))
            elif isinstance(prim, ansys.edb.core.primitive.circle.Circle):
                prims.append(Circle(self._pedb, prim))
            elif isinstance(prim, ansys.edb.core.primitive.bondwire.Bondwire):
                prims.append(Bondwire(self._pedb, prim))
        return prims

    @property
    def terminals(self):
        """Get terminals belonging to active layout.

        Returns
        -------
        Terminal dictionary : Dict[str, :class:`Terminal <pyedb.grpc.database.terminal.Terminal>`]
            Dictionary of terminals.
        """
        temp = []
        for i in self._pedb.active_cell.layout.terminals:
            if i.type.name.lower() == "pin_group":
                temp.append(PinGroupTerminal(self._pedb, i))
            elif i.type.name.lower() == "padstack_inst":
                temp.append(PadstackInstanceTerminal(self._pedb, i))
            elif i.type.name.lower() == "edge":
                temp.append(EdgeTerminal(self._pedb, i))
            elif i.type.name.lower() == "bundle":
                temp.append(BundleTerminal(self._pedb, i))
            elif i.type.name.lower() == "point":
                temp.append(PointTerminal(self._pedb, i))
        return temp

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        List[:class:`Net <pyedb.grpc.database.net.net.Net>`]
            List of Net.
        """
        return [Net(self._pedb, net) for net in super().nets]

    @property
    def bondwires(self):
        """Bondwires.

        Returns
        -------
        list [:class:`pyedb.grpc.database.primitive.primitive.Primitive`]:
            List of bondwires.
        """
        return [i for i in self.primitives if i.primitive_type == "bondwire"]

    @property
    def groups(self):
        """Groups

        Returns
        -------
        List[:class:`Group <pyedb.grpc.database.hierarch.component.Component>`].
            List of Component.

        """
        return [Component(self._pedb, g) for g in self._pedb.active_cell.layout.groups]

    @property
    def pin_groups(self):
        """Pin groups.

        Returns
        -------
        List[:class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`]
            List of PinGroup.

        """
        return [PinGroup(self._pedb, i) for i in self._pedb.active_cell.layout.pin_groups]

    @property
    def net_classes(self):
        """Net classes.

        Returns
        -------
        List[:class:`NetClass <pyedb.grpc.database.net.net_class.NetClass>`]
            List of NetClass.

        """
        return [NetClass(self._pedb, i) for i in self._pedb.active_cell.layout.net_classes]

    @property
    def extended_nets(self):
        """Extended nets.

        Returns
        -------
        List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            List of extended nets.
        """

        return [ExtendedNet(self._pedb, i) for i in self._pedb.active_cell.layout.extended_nets]

    @property
    def differential_pairs(self):
        """Differential pairs.

        Returns
        -------
        List[:class:`DifferentialPair <pyedb.grpc.database.net.differential_pair.DifferentialPair>`
            List of DifferentialPair.

        """
        return [DifferentialPair(self._pedb, i) for i in self._pedb.active_cell.layout.differential_pairs]

    @property
    def padstack_instances(self):
        """Get all padstack instances in a list."""
        return [PadstackInstance(self._pedb, i) for i in self._pedb.active_cell.layout.padstack_instances]

    #
    @property
    def voltage_regulators(self):
        """Voltage regulators.

        List[:class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`.
            List of VoltageRegulator.

        """
        return [VoltageRegulator(self._pedb, i) for i in self._pedb.active_cell.layout.voltage_regulators]

    def find_primitive(
        self, layer_name: Union[str, list] = None, name: Union[str, list] = None, net_name: Union[str, list] = None
    ) -> list:
        """Find a primitive objects by layer name.
        Parameters
        ----------
        layer_name : str, list
        layer_name : str, list, optional
            Name of the layer.
        name : str, list, optional
            Name of the primitive
        net_name : str, list, optional
            Name of the primitive
        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive`].
            List of Primitive.
        """
        if layer_name:
            layer_name = layer_name if isinstance(layer_name, list) else [layer_name]
        if name:
            name = name if isinstance(name, list) else [name]
        if net_name:
            net_name = net_name if isinstance(net_name, list) else [net_name]
        prims = self.primitives
        prims = [i for i in prims if i.aedt_name in name] if name is not None else prims
        prims = [i for i in prims if i.layer_name in layer_name] if layer_name is not None else prims
        prims = [i for i in prims if i.net_name in net_name] if net_name is not None else prims
        return prims

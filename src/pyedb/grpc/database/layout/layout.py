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

"""
This module contains these classes: `EdbLayout` and `Shape`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.dotnet.database.general import Primitives
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    from pyedb.grpc.database.primitive.primitive import Primitive

from pyedb.grpc.database.hierarchy.pingroup import PinGroup
from pyedb.grpc.database.layout.voltage_regulator import VoltageRegulator
from pyedb.grpc.database.net.differential_pair import DifferentialPair
from pyedb.grpc.database.net.extended_net import ExtendedNet
from pyedb.grpc.database.net.net_class import NetClass
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.database.terminal.point_terminal import PointTerminal

_PRIMITIVE_TYPE_MAP = {
    "Path": ("pyedb.grpc.database.primitive.path", "Path"),
    "Polygon": ("pyedb.grpc.database.primitive.polygon", "Polygon"),
    "PadstackInstance": ("pyedb.grpc.database.primitive.padstack_instance", "PadstackInstance"),
    "Rectangle": ("pyedb.grpc.database.primitive.rectangle", "Rectangle"),
    "Circle": ("pyedb.grpc.database.primitive.circle", "Circle"),
    "Bondwire": ("pyedb.grpc.database.primitive.bondwire", "Bondwire"),
}

# Cache wrapper classes after first import
_WRAPPER_CLASS_CACHE = {}


def _get_wrapper_class(prim_type: str):
    """Cached wrapper class retrieval"""
    if prim_type not in _WRAPPER_CLASS_CACHE:
        if prim_type in _PRIMITIVE_TYPE_MAP:
            module_path, class_name = _PRIMITIVE_TYPE_MAP[prim_type]
            # Import only once per type
            module = __import__(module_path, fromlist=[class_name])
            _WRAPPER_CLASS_CACHE[prim_type] = getattr(module, class_name)

    return _WRAPPER_CLASS_CACHE.get(prim_type)


class Layout:
    """Manage Layout class."""

    def __init__(self, pedb):
        self.core = pedb.active_cell.layout
        self._pedb = pedb
        self.__primitives = []
        self.__padstack_instances = {}

    @property
    def layout_instance(self):
        return self.core.layout_instance

    @property
    def cell(self):
        """:class:`Cell <ansys.edb.core.layout.cel.Cell>`: Owning cell for this layout.

        Read-Only.
        """
        return self._pedb._active_cell

    @property
    def primitives(self) -> list["Primitive"]:
        primitives = self.core.primitives
        self.__primitives = []
        for prim in primitives:
            wrapper_class = _get_wrapper_class(prim.__class__.__name__)
            if wrapper_class:
                self.__primitives.append(wrapper_class(self._pedb, prim))
        return self.__primitives

    @property
    def terminals(self) -> list[any]:
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
    def nets(self) -> list["Net"]:
        """Nets.

        Returns
        -------
        List[:class:`Net <pyedb.grpc.database.net.net.Net>`]
            List of Net.
        """
        from pyedb.grpc.database.net.net import Net

        return [Net(self._pedb, net) for net in self.core.nets]

    @property
    def bondwires(self) -> list[Bondwire]:
        """Bondwires.

        Returns
        -------
        list [:class:`pyedb.grpc.database.primitive.primitive.Primitive`]:
            List of bondwires.
        """
        return [i for i in self.primitives if i.primitive_type == "bondwire"]

    @property
    def groups(self) -> list[Component]:
        """Groups

        Returns
        -------
        List[:class:`Group <pyedb.grpc.database.hierarch.component.Component>`].
            List of Component.

        """
        from pyedb.grpc.database.hierarchy.component import Component

        return [Component(self._pedb, g) for g in self._pedb.active_cell.layout.groups]

    @property
    def pin_groups(self) -> list[PinGroup]:
        """Pin groups.

        Returns
        -------
        List[:class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`]
            List of PinGroup.

        """
        return [PinGroup(self._pedb, i) for i in self._pedb.active_cell.layout.pin_groups]

    @property
    def net_classes(self) -> list[NetClass]:
        """Net classes.

        Returns
        -------
        List[:class:`NetClass <pyedb.grpc.database.net.net_class.NetClass>`]
            List of NetClass.

        """
        return [NetClass(self._pedb, i) for i in self._pedb.active_cell.layout.net_classes]

    @property
    def extended_nets(self) -> list[ExtendedNet]:
        """Extended nets.

        Returns
        -------
        List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            List of extended nets.
        """

        return [ExtendedNet(self._pedb, i) for i in self._pedb.active_cell.layout.extended_nets]

    @property
    def differential_pairs(self) -> list[DifferentialPair]:
        """Differential pairs.

        Returns
        -------
        List[:class:`DifferentialPair <pyedb.grpc.database.net.differential_pair.DifferentialPair>`
            List of DifferentialPair.

        """
        return [DifferentialPair(self._pedb, i) for i in self._pedb.active_cell.layout.differential_pairs]

    @property
    def padstack_instances(self) -> Dict[int, PadstackInstance]:
        """Get all padstack instances in a list."""
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        pad_stack_inst = self.core.padstack_instances
        self.__padstack_instances = {i.edb_uid: PadstackInstance(self._pedb, i) for i in pad_stack_inst}
        return self.__padstack_instances

    @property
    def voltage_regulators(self) -> list[VoltageRegulator]:
        """Voltage regulators.

        List[:class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`.
            List of VoltageRegulator.

        """
        return [VoltageRegulator(self._pedb, i) for i in self._pedb.active_cell.layout.voltage_regulators]

    def find_primitive(
        self, layer_name: Union[str, list] = None, name: Union[str, list] = None, net_name: Union[str, list] = None
    ) -> list[any]:
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

    def find_padstack_instances(
        self,
        aedt_name: Union[str, List[str]] = None,
        component_name: Union[str, List[str]] = None,
        component_pin_name: Union[str, List[str]] = None,
        net_name: Union[str, List[str]] = None,
        instance_id: Union[int, List[int]] = None,
    ) -> List:
        """
        Finds padstack instances matching the specified criteria.

        This method filters the available padstack instances based on specified attributes such as
        `aedt_name`, `component_name`, `component_pin_name`, `net_name`, or `instance_id`. Criteria
        can be passed as individual values or as a list of values. If no padstack instances match
        the criteria, an error is raised.

        Parameters
        ----------
        aedt_name : Union[str, List[str]], optional
            Name(s) of the AEDT padstack instance(s) to filter.
        component_name : Union[str, List[str]], optional
            Name(s) of the component(s) to filter padstack instances by.
        component_pin_name : Union[str, List[str]], optional
            Name(s) of the component pin(s) to filter padstack instances by.
        net_name : Union[str, List[str]], optional
            Name(s) of the net(s) to filter padstack instances by.
        instance_id : Union[int, List[int]], optional
            ID(s) of the padstack instance(s) to filter.

        Returns
        -------
        List
            A list of padstack instances matching the specified criteria.
        """
        padstacks = self.padstack_instances
        instances_found = []
        if instance_id is not None:
            instance_ids = instance_id if isinstance(instance_id, list) else [instance_id]
            if instance_id in instance_ids:
                instances_found.append(padstacks[instance_id])

        if aedt_name is not None:
            name = aedt_name if isinstance(aedt_name, list) else [aedt_name]
            [instances_found.append(i) for i in list(padstacks.values()) if i.aedt_name in name]

        if component_name is not None:
            value = component_name if isinstance(component_name, list) else [component_name]
            for inst in padstacks.values():
                if inst.component:
                    if inst.component.name in value:
                        instances_found.append(inst)

        if net_name is not None:
            value = net_name if isinstance(net_name, list) else [net_name]
            for inst in padstacks.values():
                if inst.net:
                    if inst.net.name in value:
                        instances_found.append(inst)

        if component_pin_name is not None:
            value = component_pin_name if isinstance(component_name, list) else [component_pin_name]
            for inst in padstacks.values():
                if inst.component:
                    if hasattr(inst, "name"):
                        if inst.name in value:
                            instances_found.append(inst)
        if not instances_found:  # pragma: no cover
            raise ValueError(
                f"Failed to find padstack instances with aedt_name={aedt_name}, component_name={component_name}, "
                f"net_name={net_name}, component_pin_name={component_pin_name}"
            )
        return instances_found

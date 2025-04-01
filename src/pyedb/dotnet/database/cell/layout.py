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

from pyedb.dotnet.database.cell.hierarchy.component import EDBComponent
from pyedb.dotnet.database.cell.primitive.bondwire import Bondwire
from pyedb.dotnet.database.cell.primitive.path import Path
from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal
from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.dotnet.database.cell.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal
from pyedb.dotnet.database.cell.voltage_regulator import VoltageRegulator
from pyedb.dotnet.database.edb_data.nets_data import (
    EDBDifferentialPairData,
    EDBExtendedNetData,
    EDBNetClassData,
    EDBNetsData,
)
from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.primitives_data import (
    EdbCircle,
    EdbPolygon,
    EdbRectangle,
    EdbText,
)
from pyedb.dotnet.database.edb_data.sources import PinGroup
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.utilities.obj_base import ObjBase


def primitive_cast(pedb, edb_object):
    if edb_object.GetPrimitiveType().ToString() == "Rectangle":
        return EdbRectangle(edb_object, pedb)
    elif edb_object.GetPrimitiveType().ToString() == "Circle":
        return EdbCircle(edb_object, pedb)
    elif edb_object.GetPrimitiveType().ToString() == "Polygon":
        return EdbPolygon(edb_object, pedb)
    elif edb_object.GetPrimitiveType().ToString() == "Path":
        return Path(pedb, edb_object)
    elif edb_object.GetPrimitiveType().ToString() == "Bondwire":
        return Bondwire(pedb, edb_object)
    elif edb_object.GetPrimitiveType().ToString() == "Text":
        return EdbText(pedb, edb_object)
    elif edb_object.GetPrimitiveType().ToString() == "PrimitivePlugin":
        return
    elif edb_object.GetPrimitiveType().ToString() == "Path3D":
        return
    elif edb_object.GetPrimitiveType().ToString() == "BoardBendDef":
        return
    else:
        return


class Layout(ObjBase):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def cell(self):
        """:class:`Cell <ansys.edb.layout.Cell>`: Owning cell for this layout.

        Read-Only.
        """
        return self._pedb._active_cell

    @property
    def layer_collection(self):
        """:class:`LayerCollection <ansys.edb.layer.LayerCollection>` : Layer collection of this layout."""
        return self._edb_object.GetLayerCollection()

    @layer_collection.setter
    def layer_collection(self, layer_collection):
        """Set layer collection."""
        self._edb_object.SetLayerCollection(layer_collection)

    @property
    def _edb(self):
        return self._pedb.edb_api

    def expanded_extent(self, nets, extent, expansion_factor, expansion_unitless, use_round_corner, num_increments):
        """Get an expanded polygon for the Nets collection.

        Parameters
        ----------
        nets : list[:class:`Net <ansys.edb.net.Net>`]
            A list of nets.
        extent : :class:`ExtentType <ansys.edb.geometry.ExtentType>`
            Geometry extent type for expansion.
        expansion_factor : float
            Expansion factor for the polygon union. No expansion occurs if the `expansion_factor` is less than or \
            equal to 0.
        expansion_unitless : bool
            When unitless, the distance by which the extent expands is the factor multiplied by the longer dimension\
            (X or Y distance) of the expanded object/net.
        use_round_corner : bool
            Whether to use round or sharp corners.
            For round corners, this returns a bounding box if its area is within 10% of the rounded expansion's area.
        num_increments : int
            Number of iterations desired to reach the full expansion.

        Returns
        -------
        :class:`PolygonData <ansys.edb.geometry.PolygonData>`

        Notes
        -----
        Method returns the expansion of the contour, so any voids within expanded objects are ignored.
        """
        nets = [i._edb_object for i in nets]
        return self._edb_object.GetExpandedExtentFromNets(
            convert_py_list_to_net_list(nets),
            extent,
            expansion_factor,
            expansion_unitless,
            use_round_corner,
            num_increments,
        )

    def convert_primitives_to_vias(self, primitives, is_pins=False):
        """Convert a list of primitives into vias or pins.

        Parameters
        ----------
        primitives : list[:class:`Primitive <ansys.edb.primitive.Primitive>`]
            List of primitives to convert.
        is_pins : bool, optional
            True for pins, false for vias (default).
        """
        self._edb_object.ConvertPrimitivestoVias(convert_py_list_to_net_list(primitives), is_pins)

    @property
    def zone_primitives(self):
        """:obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>` : List of all the primitives in \
        :term:`zones <Zone>`.

        Read-Only.
        """
        return list(self._edb_object.GetZonePrimitives())

    @property
    def fixed_zone_primitive(self):
        """:class:`Primitive <ansys.edb.primitive.Primitive>` : Fixed :term:`zones <Zone>` primitive."""
        return list(self._edb_object.GetFixedZonePrimitive())

    @fixed_zone_primitive.setter
    def fixed_zone_primitive(self, value):
        self._edb_object.SetFixedZonePrimitives(value)

    @property
    def terminals(self):
        """Get terminals belonging to active layout.

        Returns
        -------
        Terminal dictionary : Dict[str, pyedb.dotnet.database.edb_data.terminals.Terminal]
        """
        temp = []
        for i in list(self._edb_object.Terminals):
            terminal_type = i.ToString().split(".")[-1]
            if terminal_type == "PinGroupTerminal":
                temp.append(PinGroupTerminal(self._pedb, i))
            elif terminal_type == "PadstackInstanceTerminal":
                temp.append(PadstackInstanceTerminal(self._pedb, i))
            elif terminal_type == "EdgeTerminal":
                temp.append(EdgeTerminal(self._pedb, i))
            elif terminal_type == "BundleTerminal":
                temp.append(BundleTerminal(self._pedb, i))
            elif terminal_type == "PointTerminal":
                temp.append(PointTerminal(self._pedb, i))
        return temp

    @property
    def cell_instances(self):
        """:obj:`list` of :class:`CellInstance <ansys.edb.hierarchy.CellInstances>` : List of the cell instances in \
                this layout.

                Read-Only.
                """
        return list(self._edb_object.CellInstances)

    @property
    def layout_instance(self):
        """:class:`LayoutInstance <ansys.edb.layout_instance.LayoutInstance>` : Layout instance of this layout.

        Read-Only.
        """
        return self._edb_object.GetLayoutInstance()

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        """

        return [EDBNetsData(net, self._pedb) for net in self._edb_object.Nets if net]

    @property
    def primitives(self):
        """List of primitives.Read-Only.

        Returns
        -------
        list of :class:`dotnet.database.dotnet.primitive.PrimitiveDotNet` cast objects.
        """
        return [primitive_cast(self._pedb, p) for p in self._edb_object.Primitives if p]

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
        return [EDBComponent(self._pedb, i) for i in self._edb_object.Groups if i.ToString().endswith(".Component")]

    @property
    def pin_groups(self):
        return [PinGroup(pedb=self._pedb, edb_pin_group=i, name=i.GetName()) for i in self._edb_object.PinGroups]

    @property
    def net_classes(self):
        return [EDBNetClassData(self._pedb, i) for i in list(self._edb_object.NetClasses)]

    @property
    def extended_nets(self):
        return [EDBExtendedNetData(self._pedb, i) for i in self._edb_object.ExtendedNets]

    @property
    def differential_pairs(self):
        return [EDBDifferentialPairData(self._pedb, i) for i in list(self._edb_object.DifferentialPairs)]

    @property
    def padstack_instances(self):
        """Get all padstack instances in a list."""
        return [EDBPadstackInstance(i, self._pedb) for i in self._edb_object.PadstackInstances]

    @property
    def voltage_regulators(self):
        return [VoltageRegulator(self._pedb, i) for i in list(self._edb_object.VoltageRegulators)]

    @property
    def port_reference_terminals_connected(self):
        """:obj:`bool`: Determine if port reference terminals are connected, applies to lumped ports and circuit ports.

        True if they are connected, False otherwise.
        Read-Only.
        """
        return self._edb_object.ArePortReferenceTerminalsConnected()

    def find_object_by_id(self, value: int):
        """Find a layout object by Database ID.

        Parameters
        ----------
        value : int
            ID of the object.
        """
        obj = self._pedb._edb.Cell.Connectable.FindById(self._edb_object, value)
        if obj is None:
            raise RuntimeError(f"Object Id {value} not found")

        if obj.GetObjType().ToString() == "PadstackInstance":
            return EDBPadstackInstance(obj, self._pedb)

        if obj.GetObjType().ToString() == "Primitive":
            return primitive_cast(self._pedb, obj)

    def find_net_by_name(self, value: str):
        """Find a net object by name

        Parameters
        ----------
        value : str
            Name of the net.

        Returns
        -------

        """
        obj = self._pedb._edb.Cell.Net.FindByName(self._edb_object, value)
        if obj.IsNull():
            return None
        else:
            return EDBNetsData(obj, self._pedb)

    def find_component_by_name(self, value: str):
        """Find a component object by name. Component name is the reference designator in layout.

        Parameters
        ----------
        value : str
            Name of the component.
        Returns
        -------

        """
        obj = self._pedb._edb.Cell.Hierarchy.Component.FindByName(self._edb_object, value)
        return EDBComponent(self._pedb, obj) if obj is not None else None

    def find_primitive(
        self, layer_name: Union[str, list] = None, name: Union[str, list] = None, net_name: Union[str, list] = None
    ) -> list:
        """Find a primitive objects by layer name.

        Parameters
        ----------
        layer_name : str, list, optional
            Name of the layer.
        name : str, list, optional
            Name of the primitive
        net_name : str, list, optional
            Name of the primitive
        Returns
        -------
        list
        """
        if layer_name is not None:
            layer_name = layer_name if isinstance(layer_name, list) else [layer_name]
        if name is not None:
            name = name if isinstance(name, list) else [name]
        if net_name is not None:
            net_name = net_name if isinstance(net_name, list) else [net_name]

        prims = self.primitives
        prims = [i for i in prims if i.aedt_name in name] if name is not None else prims
        prims = [i for i in prims if i.layer_name in layer_name] if layer_name is not None else prims
        prims = [i for i in prims if i.net_name in net_name] if net_name is not None else prims
        return prims

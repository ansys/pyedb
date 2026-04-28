# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""This module contains these classes: `EdbLayout` and `Shape`.
"""

from typing import TypeVar

from pyedb.dotnet.database.cell.hierarchy.component import EDBComponent
from pyedb.dotnet.database.cell.primitive.bondwire import Bondwire
from pyedb.dotnet.database.cell.primitive.path import Path
from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal
from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import PadstackInstanceTerminal
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
from pyedb.misc.decorators import deprecate_argument_name, deprecated

TPrimitiveClass = TypeVar("TPrimitiveClass")


def primitive_cast(pedb, edb_object):
    if not hasattr(edb_object, "GetPrimitiveType"):
        return
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


class PrimitivesQuery:
    def __init__(self, pedb):
        self._pedb = pedb
        self._primitives = []

    @staticmethod
    def _as_filter_set(values):
        if values is None:
            return None
        if isinstance(values, (list, tuple, set)):
            return set(values)
        return {values}

    def _group_primitives_by(
        self,
        attribute_name: str,
        primitives: list[Primitive] | None = None,
        initial_keys: list[str] | None = None,
    ) -> dict:
        grouped_primitives = {key: [] for key in initial_keys or []}
        for primitive in primitives if primitives is not None else self.primitives:
            grouped_primitives.setdefault(getattr(primitive, attribute_name), []).append(primitive)
        return grouped_primitives

    def _primitives_by_class(self, primitive_class: type[TPrimitiveClass]) -> list[TPrimitiveClass]:
        return [primitive for primitive in self.primitives if isinstance(primitive, primitive_class)]

    def _normalize_layer_filter(self, layer) -> set[str] | None:
        layer_names = self._as_filter_set(layer)
        if layer_names is None:
            return None
        signal_layers = set(self._pedb.stackup.signal_layers.keys())
        valid_layer_names = layer_names.intersection(signal_layers)
        return valid_layer_names or None

    def _normalize_point_query_nets(self, nets):
        if not nets:
            return None

        net_names = self._as_filter_set(nets)
        net_objects = []
        for net_name in net_names:
            if net_name not in self._pedb.nets:
                self._pedb.logger.warning(
                    f"Net {net_name} used to find primitive from layer point and net not found, skipping it."
                )
                continue
            net_objects.append(self._pedb.nets[net_name].net_obj)

        if not net_objects:
            return None
        return convert_py_list_to_net_list(net_objects)

    def _layout_object_instances_at_point(self, point, nets=None):
        point_data = self._pedb.core.Geometry.PointData(self._pedb.edb_value(point[0]), self._pedb.edb_value(point[1]))
        return list(self._pedb.layout_instance.FindLayoutObjInstance(point_data, None, nets).Items)

    def _primitive_lookup_by_id(self, primitives: list[Primitive] | None = None) -> dict[int, Primitive]:
        return {primitive.id: primitive for primitive in self._iter_primitives_with_voids(primitives)}

    def _iter_primitives_with_voids(self, primitives: list[Primitive] | None = None):
        for primitive in primitives if primitives is not None else self.primitives:
            yield primitive
            yield from self._iter_primitives_with_voids(primitive.voids)

    def _find_primitive_or_void_by_id(self, value: int, primitives: list[Primitive] | None = None) -> Primitive | None:
        for primitive in primitives if primitives is not None else self.primitives:
            if primitive.id == value:
                return primitive

            void_match = self._find_primitive_or_void_by_id(value, primitive.voids)
            if void_match is not None:
                return void_match

        return None

    @staticmethod
    def _layout_obj_matches_layers(layout_obj_instance, layer_names: set[str] | None) -> bool:
        if layer_names is None:
            return True
        return any(layer.GetName() in layer_names for layer in list(layout_obj_instance.GetLayers()))

    @staticmethod
    def _is_terminal_layout_obj(layout_obj) -> bool:
        return "Terminal" in str(layout_obj)

    @staticmethod
    def _get_polygon_data_object(polygon):
        if hasattr(polygon, "polygon_data"):
            polygon_data = polygon.polygon_data
            return polygon_data._edb_object if hasattr(polygon_data, "_edb_object") else polygon_data
        return polygon.GetPolygonData()

    @staticmethod
    def _polygon_point_to_list(point) -> list[float]:
        if point.IsArc():
            return [point.X.ToDouble()]
        return [point.X.ToDouble(), point.Y.ToDouble()]

    @staticmethod
    def _polygon_bbox_to_list(bounding_box) -> list[float]:
        return [
            bounding_box.Item1.X.ToDouble(),
            bounding_box.Item1.Y.ToDouble(),
            bounding_box.Item2.X.ToDouble(),
            bounding_box.Item2.Y.ToDouble(),
        ]

    def filter_primitives(
        self,
        layer_name: str | list = None,
        name: str | list = None,
        net_name: str | list = None,
        prim_type: str | list = None,
        is_void: bool | None = None,
    ) -> list[Primitive]:
        """Filter primitives by one or more attributes.

        Parameters
        ----------
        layer_name : str, list, optional
            Layer name or layer names.
        name : str, list, optional
            Primitive AEDT name or names.
        net_name : str, list, optional
            Net name or net names.
        prim_type : str, list, optional
            Primitive type or primitive types. Both lowercase values like ``"polygon"`` and
            EDB-style values like ``"Polygon"`` are accepted.
        is_void : bool, optional
            Void flag filter. When ``None``, void state is not used as a filter.

        Returns
        -------
        list[Primitive]
            Filtered primitives.

        """
        layer_name_set = self._as_filter_set(layer_name)
        name_set = self._as_filter_set(name)
        net_name_set = self._as_filter_set(net_name)
        prim_type_set = self._as_filter_set(prim_type)

        return [
            primitive
            for primitive in self._iter_primitives_with_voids()
            if (layer_name_set is None or primitive.layer_name in layer_name_set)
            and (name_set is None or primitive.aedt_name in name_set)
            and (net_name_set is None or primitive.net_name in net_name_set)
            and (prim_type_set is None or primitive.primitive_type in prim_type_set or primitive.type in prim_type_set)
            and (is_void is None or primitive.is_void == is_void)
        ]

    @property
    def primitives_by_aedt_name(self) -> dict:
        """Primitives."""
        return {i.aedt_name: i for i in self._iter_primitives_with_voids()}

    @property
    def primitives(self) -> list[Primitive]:
        """List of primitives.Read-Only.

        Returns
        -------
        list of :class:`dotnet.database.dotnet.primitive.PrimitiveDotNet` cast objects.

        """
        primitives = list(self._edb_object.Primitives)
        if len(primitives) != len(self._primitives):
            self._primitives = [primitive_cast(self._pedb, p) for p in primitives]
        return [p for p in self._primitives if p is not None]

    @property
    def zone_primitives(self):
        """:obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>` : List of all the primitives in \
        :term:`zones <Zone>`.

        Read-Only.
        """
        return list(self._edb_object.GetZonePrimitives())

    @property
    def bondwires(self) -> list[Bondwire]:
        """Bondwires.

        Returns
        -------
        list :
            List of bondwires.

        """
        return self._primitives_by_class(Bondwire)

    def find_object_by_id(self, value: int) -> EDBPadstackInstance | Primitive | None:
        """Find a layout object by Database ID.

        Parameters
        ----------
        value : int
            ID of the object.

        """
        object_by_id = self._find_primitive_or_void_by_id(value)
        if object_by_id is not None:
            return object_by_id

        obj = self._pedb._edb.Cell.Connectable.FindById(self._edb_object, value)
        if obj is None:
            raise RuntimeError(f"Object Id {value} not found")

        obj_type = obj.GetObjType().ToString()
        if obj_type == "PadstackInstance":
            return EDBPadstackInstance(obj, self._pedb)

        if obj_type == "Primitive":
            return primitive_cast(self._pedb, obj)

        return None

    @deprecate_argument_name({"layer_name": "layer"})
    def get_primitive_by_layer_and_point(self, point=None, layer=None, nets=None):
        """Return primitive given coordinate point [x, y], layer name and nets.

        Parameters
        ----------
        point : list
            Coordinate [x, y]

        layer : list or str, optional
            list of layer name or layer name applied on filter.

        nets : list or str, optional
            list of net name or single net name applied on filter

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives, polygons, paths and rectangles.

        """
        layer_names = self._normalize_layer_filter(layer)
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            self._pedb.logger.error("Provided point must be a list of two values")
            return False
        net_list = self._normalize_point_query_nets(nets)
        if nets and net_list is None:
            return []
        obj_instances = self._layout_object_instances_at_point(point, nets=net_list)

        if layer_names is None:
            primitives_by_id = self._primitive_lookup_by_id()
            return [
                primitive
                for obj_instance in obj_instances
                for primitive in [primitives_by_id.get(obj_instance.GetLayoutObj().GetId())]
                if primitive is not None
            ]

        primitives_by_id = self._primitive_lookup_by_id(
            self.filter_primitives(prim_type=["polygon", "path", "rectangle", "circle"])
        )
        return [
            primitive
            for obj_instance in obj_instances
            if self._layout_obj_matches_layers(obj_instance, layer_names)
            for layout_obj in [obj_instance.GetLayoutObj()]
            if not self._is_terminal_layout_obj(layout_obj)
            for primitive in [primitives_by_id.get(layout_obj.GetId())]
            if primitive is not None
        ]

    def find_primitive(
        self,
        layer_name: str | list = None,
        name: str | list = None,
        net_name: str | list = None,
        prim_type: str | list = None,
        is_void: bool | None = None,
    ) -> list[Primitive]:
        """Find a primitive objects by layer name.

        Parameters
        ----------
        layer_name : str, list, optional
            Name of the layer.
        name : str, list, optional
            Name of the primitive
        net_name : str, list, optional
            Name of the net
        prim_type : str, list, optional
            Primitive type, e.g. ``"polygon"``, ``"path"``.
        is_void : bool, optional
            When ``True``, return only void primitives. When ``False``, return only non-void primitives.
            When ``None`` (default), void state is not used as a filter.
        Returns
        -------
        list

        """
        return self.filter_primitives(
            layer_name=layer_name, name=name, net_name=net_name, prim_type=prim_type, is_void=is_void
        )

    @property
    def primitives_by_layer(self) -> dict:
        """Get primitives by layer name.

        Returns
        -------
        dict
            Returns dict[str, list] with all specified layer names as keys organized by layer.

        """
        return self._group_primitives_by(
            "layer_name",
            list(self._iter_primitives_with_voids()),
            initial_keys=list(self._pedb.stackup.layers.keys()),
        )

    @property
    def polygons_by_layer(self) -> dict:
        """Get polygons by layer name.

        Returns
        -------
        dict
            dictionary of polygons with layer name as key and list of polygons as value.

        """
        return self._group_primitives_by(
            "layer_name",
            self.polygons,
            initial_keys=list(self._pedb.stackup.layers.keys()),
        )

    @property
    def primitives_by_net(self) -> dict:
        """Get primitives by net name.

        Returns
        -------
        dict
            Returns dict[str, list] with all specified net names as keys organized by net.

        """
        return self._group_primitives_by(
            "net_name",
            list(self._iter_primitives_with_voids()),
            initial_keys=list(self._pedb.nets.nets.keys()),
        )

    @property
    def rectangles(self) -> list[EdbRectangle]:
        return self._primitives_by_class(EdbRectangle)

    @property
    def circles(self) -> list[EdbCircle]:
        return self._primitives_by_class(EdbCircle)

    @property
    def paths(self) -> list[Path]:
        return self._primitives_by_class(Path)

    @property
    def polygons(self) -> list[EdbPolygon]:
        return self._primitives_by_class(EdbPolygon)

    @deprecate_argument_name({"layer_name": "layer", "net_list": "nets"})
    def get_polygons_by_layer(self, layer, nets=None) -> list[EdbPolygon]:
        return [
            primitive
            for primitive in self.filter_primitives(layer_name=layer, net_name=nets, prim_type="polygon")
            if isinstance(primitive, EdbPolygon)
        ]

    def get_polygon_bounding_box(self, polygon) -> list[float] | None:
        """Retrieve a polygon bounding box.

        Parameters
        ----------
        polygon :
            Polygon object.

        Returns
        -------
        List of bounding box coordinates in the format ``[-x, -y, +x, +y]``.

        Examples
        --------
        >>> poly = database.modeler.get_polygons_by_layer("GND")
        >>> bounding = database.modeler.get_polygon_bounding_box(poly[0])

        """
        try:
            polygon_data = self._get_polygon_data_object(polygon)
        except AttributeError:
            return None

        return self._polygon_bbox_to_list(polygon_data.GetBBox())

    def get_polygon_points(self, polygon) -> list[list[float]]:
        """Retrieve polygon points.

        .. note::
           For arcs, one point is returned.

        Parameters
        ----------
        polygon :
            class: `dotnet.database.edb_data.primitives_data.Primitive`

        Returns
        -------
        List of tuples. Each tuple provides x, y point coordinate. If the length of two consecutives tuples
        from the list equals 2, a segment is defined. The first tuple defines the starting point while the second
        tuple the ending one. If the length of one tuple equals one, that means a polyline is defined and the value
        is giving the arc height. Therefore to polyline is defined as starting point for the tuple
        before in the list, the current one the arc height and the tuple after the polyline ending point.

        Examples
        --------

        >>> poly = database.modeler.get_polygons_by_layer("GND")
        >>> points = database.modeler.get_polygon_points(poly[0])

        """
        polygon_data = self._get_polygon_data_object(polygon)
        points = []
        index = 0
        prev_point = None
        while True:
            try:
                point = polygon_data.GetPoint(index)
            except Exception:
                break

            if prev_point == point:
                break

            points.append(self._polygon_point_to_list(point))
            prev_point = point
            index += 1
        return points

    @deprecated("Use `filter_primitives` instead.")
    def get_primitives(self, net_name=None, layer_name=None, prim_type=None, is_void=None) -> list[Primitive]:
        """Get primitives by conditions.

        Parameters
        ----------
        net_name : str, optional
            Set filter on net_name. Default is ``None``.
        layer_name : str, optional
            Set filter on layer_name. Default is ``None``.
        prim_type :  str, optional
            Set filter on primitive type. Default is ``None``.
        is_void : bool, optional
            Set filter on is_void. When ``None``, both standard primitives and voids are returned.
        Returns
        -------
        List of filtered primitives

        """
        return self.filter_primitives(
            net_name=net_name,
            layer_name=layer_name,
            prim_type=prim_type,
            is_void=is_void,
        )


class Layout(ObjBase, PrimitivesQuery):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        PrimitivesQuery.__init__(self, pedb)

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
        return self._pedb.core

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
        if isinstance(nets, list) and all(isinstance(item, str) for item in nets):
            nets = [self._pedb.nets.nets[i] for i in nets if i in self.nets]

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
    def groups(self):
        return [EDBComponent(self._pedb, i) for i in self._edb_object.Groups if i.ToString().endswith(".Component")]

    @property
    def pin_groups(self) -> list[PinGroup]:
        return [PinGroup(pedb=self._pedb, edb_pin_group=i, name=i.GetName()) for i in self._edb_object.PinGroups]

    @property
    def net_classes(self) -> list[EDBNetClassData]:
        return [EDBNetClassData(self._pedb, i) for i in list(self._edb_object.NetClasses)]

    @property
    def extended_nets(self) -> list[EDBExtendedNetData]:
        return [EDBExtendedNetData(self._pedb, i) for i in self._edb_object.ExtendedNets]

    @property
    def differential_pairs(self) -> list[EDBDifferentialPairData]:
        return [EDBDifferentialPairData(self._pedb, i) for i in list(self._edb_object.DifferentialPairs)]

    @property
    def padstack_instances(self) -> list[EDBPadstackInstance]:
        """Get all padstack instances in a list."""
        return [EDBPadstackInstance(i, self._pedb) for i in self._edb_object.PadstackInstances]

    @property
    def voltage_regulators(self) -> list[VoltageRegulator]:
        return [VoltageRegulator(self._pedb, i) for i in list(self._edb_object.VoltageRegulators)]

    @property
    def port_reference_terminals_connected(self) -> bool:
        """:obj:`bool`: Determine if port reference terminals are connected, applies to lumped ports and circuit ports.

        True if they are connected, False otherwise.
        Read-Only.
        """
        return self._edb_object.ArePortReferenceTerminalsConnected()

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

    def find_component_by_name(self, value: str) -> EDBComponent | None:
        """Find a component object by name. Component name is the reference designator in layout.

        Parameters
        ----------
        value : str
            Name of the component.
        Returns
        -------

        """
        obj = self._pedb.core.Cell.Hierarchy.Component.FindByName(self._edb_object, value)
        return EDBComponent(self._pedb, obj) if not obj.IsNull() else None

    def find_padstack_instances(
        self,
        aedt_name: str | list[str] = None,
        component_name: str | list[str] = None,
        component_pin_name: str | list[str] = None,
        net_name: str | list[str] = None,
        instance_id: int | list[int] = None,
    ) -> list[EDBPadstackInstance]:
        """Finds padstack instances matching the specified criteria.

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
        candidates = self.padstack_instances  # make a copy of the list to filter down
        if instance_id is not None:
            id_set = instance_id if isinstance(instance_id, list) else [instance_id]
            id_set = {int(i) for i in id_set}
            id_found = []
            remaining = set(id_set)
            for c in candidates:
                cid = c.id
                if cid in remaining:
                    id_found.append(c)
                    remaining.remove(cid)
                    if not remaining:  # all ids found
                        break
            candidates = id_found

        if aedt_name is not None:
            name_set = set(aedt_name) if isinstance(aedt_name, list) else {aedt_name}
            name_found = []
            remaining = set(name_set)
            for c in candidates:
                cname = c.aedt_name
                if cname in remaining:
                    name_found.append(c)
                    remaining.remove(cname)
                    if not remaining:  # all names found
                        break
            candidates = name_found

        if component_name is not None:
            value = component_name if isinstance(component_name, list) else [component_name]
            candidates = [i for i in candidates if i.component_name in value]

        if net_name is not None:
            net_name_set = set(net_name) if isinstance(net_name, list) else {net_name}
            net_name_found = []
            remaining = set(net_name_set)
            for c in candidates:
                n_name = c.net_name
                if n_name in remaining:
                    net_name_found.append(c)
                    remaining.remove(n_name)
                    if not remaining:  # all net names found
                        break
            candidates = net_name_found

        if component_pin_name is not None:
            c_pin_name_set = set(component_pin_name) if isinstance(component_pin_name, list) else {component_pin_name}
            c_pin_name_found = []
            remaining = set(c_pin_name_set)
            for c in candidates:
                p_name = c.name
                if p_name in remaining:
                    c_pin_name_found.append(c)
                    remaining.remove(p_name)
                    if not remaining:  # all component pin names found
                        break
            candidates = c_pin_name_found

        if not candidates:  # pragma: no cover
            raise ValueError(
                f"Failed to find padstack instances with aedt_name={aedt_name}, component_name={component_name}, "
                f"net_name={net_name}, component_pin_name={component_pin_name}"
            )
        return candidates

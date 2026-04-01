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

"""
This module contains these classes: `EdbLayout` and `Shape`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ansys.edb.core.layout.layout import Layout as CoreLayout

    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.primitive.bondwire import Bondwire
    from pyedb.grpc.database.primitive.circle import Circle
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
    from pyedb.grpc.database.primitive.path import Path
    from pyedb.grpc.database.primitive.polygon import Polygon
    from pyedb.grpc.database.primitive.primitive import Primitive
    from pyedb.grpc.database.primitive.rectangle import Rectangle

from typing import List, Union

from ansys.edb.core.geometry.point_data import PointData as CorePointData

from pyedb.grpc.database.hierarchy.pingroup import PinGroup
from pyedb.grpc.database.layout.voltage_regulator import VoltageRegulator
from pyedb.grpc.database.net.differential_pair import DifferentialPair
from pyedb.grpc.database.net.extended_net import ExtendedNet
from pyedb.grpc.database.net.net_class import NetClass
from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal
from pyedb.grpc.database.terminal.padstack_instance_terminal import PadstackInstanceTerminal
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.database.terminal.point_terminal import PointTerminal
from pyedb.misc.decorators import deprecate_argument_name, deprecated

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


def _resolve_primitive_type_name(value: Any) -> str | None:
    candidates = []

    if isinstance(value, str):
        candidates.append(value)
    elif isinstance(value, type):
        candidates.extend([value.__name__, value.__qualname__, value.__module__])
    elif value is not None:
        candidates.extend([value.__class__.__name__, value.__class__.__qualname__, value.__class__.__module__])
        for attr_name in ("primitive_type", "type"):
            attr_value = getattr(value, attr_name, None)
            if attr_value is not None:
                candidates.extend([getattr(attr_value, "name", None), str(attr_value)])

    normalized_candidates = [
        "".join(ch for ch in str(candidate) if ch.isalnum()).lower() for candidate in candidates if candidate
    ]

    for primitive_type in _PRIMITIVE_TYPE_MAP:
        primitive_key = primitive_type.lower()
        if any(candidate == primitive_key for candidate in normalized_candidates):
            return primitive_type

    for primitive_type in _PRIMITIVE_TYPE_MAP:
        primitive_key = primitive_type.lower()
        if any(candidate.endswith(primitive_key) or primitive_key in candidate for candidate in normalized_candidates):
            return primitive_type

    return None


def _get_wrapper_class(primitive_type: Any):
    """Cached wrapper class retrieval."""
    resolved_type = _resolve_primitive_type_name(primitive_type)
    if resolved_type is None:
        return None

    if resolved_type not in _WRAPPER_CLASS_CACHE and resolved_type in _PRIMITIVE_TYPE_MAP:
        module_path, class_name = _PRIMITIVE_TYPE_MAP[resolved_type]
        module = __import__(module_path, fromlist=[class_name])
        _WRAPPER_CLASS_CACHE[resolved_type] = getattr(module, class_name)

    return _WRAPPER_CLASS_CACHE.get(resolved_type)


class PrimitivesQuery:
    core: CoreLayout

    def __init__(self, pedb):
        self._pedb = pedb
        self._primitives = []

    @staticmethod
    def _as_filter_set(values) -> set | None:
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
    ) -> dict[str, list[Primitive]]:
        grouped_primitives = {key: [] for key in initial_keys or []}
        for primitive in primitives if primitives is not None else self.primitives:
            grouped_primitives.setdefault(getattr(primitive, attribute_name), []).append(primitive)
        return grouped_primitives

    def _wrap_primitive(self, primitive) -> Any | None:
        wrapper_class = _get_wrapper_class(primitive)
        if wrapper_class is None:
            return None
        if isinstance(primitive, wrapper_class):
            return primitive
        return wrapper_class(self._pedb, primitive)

    def _primitives_by_class(self, primitive_class: str | type) -> list[Any]:
        wrapper_class = _get_wrapper_class(primitive_class)
        if wrapper_class is None:
            return []
        return [primitive for primitive in self.primitives if isinstance(primitive, wrapper_class)]

    def _normalize_layer_filter(self, layer) -> set[str] | None:
        layer_names = self._as_filter_set(layer)
        if layer_names is None:
            return None
        signal_layers = set(self._pedb.stackup.signal_layers.keys())
        valid_layer_names = layer_names.intersection(signal_layers)
        return valid_layer_names or None

    def _normalize_point_query_nets(self, nets) -> list[Any] | None:
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
            net_objects.append(self._pedb.nets[net_name].core)

        if not net_objects:
            return None
        return net_objects

    def _layout_object_instances_at_point(self, point, layer_names: set[str] | None = None, nets=None) -> list[Any]:
        point_data = CorePointData(point)
        return self._pedb.layout_instance.query_layout_obj_instances(
            layer_filter=list(layer_names) if layer_names is not None else None,
            net_filter=nets,
            spatial_filter=point_data,
        )

    def _primitive_lookup_by_id(self, primitives: list[Primitive] | None = None) -> dict[int, Primitive]:
        return {primitive.id: primitive for primitive in (primitives if primitives is not None else self.primitives)}

    def _find_primitive_or_void_by_id(self, value: int, primitives: list[Primitive] | None = None) -> Primitive | None:
        for primitive in primitives if primitives is not None else self.primitives:
            if primitive.id == value:
                return primitive

            void_match = self._find_primitive_or_void_by_id(value, primitive.voids)
            if void_match is not None:
                return void_match

        return None

    @staticmethod
    def _is_terminal_layout_obj(layout_obj) -> bool:
        return "Terminal" in str(layout_obj)

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
            for primitive in self.primitives
            if (layer_name_set is None or primitive.layer_name in layer_name_set)
            and (name_set is None or primitive.aedt_name in name_set)
            and (net_name_set is None or primitive.net_name in net_name_set)
            and (prim_type_set is None or primitive.primitive_type in prim_type_set or primitive.type in prim_type_set)
            and (is_void is None or primitive.is_void == is_void)
        ]

    @property
    def primitives_by_aedt_name(self) -> dict[str, Primitive]:
        """Primitives."""
        return {i.aedt_name: i for i in self.primitives}

    @property
    def primitives(self) -> list[Primitive]:
        self._primitives = []
        for primitive in self.core.primitives:
            wrapped_primitive = self._wrap_primitive(primitive)
            if wrapped_primitive is not None:
                self._primitives.append(wrapped_primitive)
        return self._primitives

    @property
    def zone_primitives(self):
        """:obj:`list` of :class:`Primitive <ansys.edb.primitive.primitive.Primitive>` : List of all the primitives in \
        :term:`zones <Zone>`.

        Read-Only.
        """
        zone_primitives = []
        for primitive in self.core.zone_primitives:
            wrapped_primitive = self._wrap_primitive(primitive)
            if wrapped_primitive is not None:
                zone_primitives.append(wrapped_primitive)
        return zone_primitives

    @property
    def bondwires(self) -> list[Bondwire]:
        """Bondwires.

        Returns
        -------
        list :
            List of bondwires.
        """
        return self._primitives_by_class("Bondwire")

    def find_object_by_id(self, value: int) -> PadstackInstance | Primitive | None:
        """Find a layout object by Database ID.

        Parameters
        ----------
        value : int
            ID of the object.
        """
        object_by_id = self._find_primitive_or_void_by_id(value)
        if object_by_id is not None:
            return object_by_id

        for padstack_instance in getattr(self, "padstack_instances", []):
            if padstack_instance.id == value:
                return padstack_instance

        raise RuntimeError(f"Object Id {value} not found")

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
        list of :class:`pyedb.grpc.database.primitive.primitive.Primitive`
            List of primitives, polygons, paths and rectangles.
        """
        layer_names = self._normalize_layer_filter(layer)
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            self._pedb.logger.error("Provided point must be a list of two values")
            return False
        net_list = self._normalize_point_query_nets(nets)
        if nets and net_list is None:
            return []
        obj_instances = self._layout_object_instances_at_point(point, layer_names=layer_names, nets=net_list)

        return [
            wrapped_primitive
            for obj_instance in obj_instances
            for layout_obj in [obj_instance.layout_obj]
            if not self._is_terminal_layout_obj(layout_obj)
            for wrapped_primitive in [self._wrap_primitive(layout_obj)]
            if wrapped_primitive is not None
        ]

    def find_primitive(
        self, layer_name: str | list = None, name: str | list = None, net_name: str | list = None
    ) -> list[Primitive]:
        """Find a primitive objects by layer name.

        Parameters
        ----------
        layer_name : str, list, optional
            Name of the layer.
        name : str, list, optional
            Name of the primitive
        net_name : str, list, optional
            Name of the primitive
        point : tuple[float, float], optional
            Coordinate point (x, y) to find primitives at a specific location. If provided, only primitives that contain
            this point will be returned.
        Returns
        -------
        list
        """
        return self.filter_primitives(layer_name=layer_name, name=name, net_name=net_name)

    @property
    def primitives_by_layer(self) -> dict[str, list[Primitive]]:
        """Get primitives by layer name.

        Returns
        -------
        dict
            Returns dict[str, list] with all specified layer names as keys organized by layer.
        """
        return self._group_primitives_by("layer_name", initial_keys=list(self._pedb.stackup.layers.keys()))

    @property
    def polygons_by_layer(self) -> dict[str, list[Primitive]]:
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
        return self._group_primitives_by("net_name", initial_keys=list(self._pedb.nets.nets.keys()))

    @property
    def rectangles(self) -> list[Rectangle]:
        return self._primitives_by_class("Rectangle")

    @property
    def circles(self) -> list[Circle]:
        return self._primitives_by_class("Circle")

    @property
    def paths(self) -> list[Path]:
        return self._primitives_by_class("Path")

    @property
    def polygons(self) -> list[Polygon]:
        return self._primitives_by_class("Polygon")

    @deprecate_argument_name({"layer_name": "layer", "net_list": "nets"})
    def get_polygons_by_layer(self, layer, nets=None) -> list[Polygon]:
        layer_name_set = self._as_filter_set(layer)
        net_name_set = self._as_filter_set(nets)
        return [
            primitive
            for primitive in self.polygons
            if (layer_name_set is None or primitive.layer_name in layer_name_set)
            and (net_name_set is None or primitive.net_name in net_name_set)
        ]

    def get_polygon_bounding_box(self, polygon) -> list[float] | None:
        """Retrieve a polygon bounding box."""
        try:
            bounding_box = polygon.polygon_data.bounding_box
        except AttributeError:
            return None
        return [bounding_box[0][0], bounding_box[0][1], bounding_box[1][0], bounding_box[1][1]]

    def get_polygon_points(self, polygon) -> list[list[float]]:
        """Retrieve polygon points."""
        try:
            polygon_data = polygon.polygon_data
        except AttributeError:
            return []

        points = []
        previous_point = None
        for point in polygon_data.points_raw:
            if previous_point == point:
                break
            if point.is_arc:
                points.append([point.x.value])
            else:
                points.append([point.x.value, point.y.value])
            previous_point = point
        return points

    @deprecated("Use `filter_primitives` instead.")
    def get_primitives(self, net_name=None, layer_name=None, prim_type=None, is_void=False) -> list[Primitive]:
        """Get primitives by conditions.

        Parameters
        ----------
        net_name : str, optional
            Set filter on net_name. Default is ``None``.
        layer_name : str, optional
            Set filter on layer_name. Default is ``None``.
        prim_type :  str, optional
            Set filter on primitive type. Default is ``None``.
        is_void : bool
            Set filter on is_void. Default is '``False'``
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


class Layout(PrimitivesQuery):
    """Manage Layout class."""

    def __init__(self, pedb, core: CoreLayout):
        super().__init__(pedb)
        self.core = core
        self._pedb = pedb
        self.__primitives = []
        self.__padstack_instances = {}

    @property
    def layout_instance(self) -> Any:
        return self.core.layout_instance

    @property
    def terminals(
        self,
    ) -> list[PinGroupTerminal | PadstackInstanceTerminal | EdgeTerminal | BundleTerminal | PointTerminal]:
        """Get terminals belonging to active layout.

        Returns
        -------
        Terminal dictionary : Dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
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
    def padstack_instances(self) -> list[PadstackInstance]:
        """Get all padstack instances in a list."""
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        return [PadstackInstance(self._pedb, i) for i in self.core.padstack_instances]

    @property
    def voltage_regulators(self) -> list[VoltageRegulator]:
        """Voltage regulators.

        List[:class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`.
            List of VoltageRegulator.

        """
        return [VoltageRegulator(self._pedb, i) for i in self._pedb.active_cell.layout.voltage_regulators]

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
            candidates = [i for i in candidates if i.component and i.component.name in value]

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

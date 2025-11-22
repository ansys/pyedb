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

import math
from typing import Any, Dict, Iterable, List, Optional, Union

from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import (
    PolygonData as GrpcPolygonData,
)
from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.primitive.bondwire import BondwireType as GrpcBondwireType
from ansys.edb.core.primitive.path import PathCornerType as GrpcPathCornerType, PathEndCapType as GrpcPathEndCapType
from ansys.edb.core.primitive.rectangle import (
    RectangleRepresentationType as GrpcRectangleRepresentationType,
)

from pyedb.dotnet.database.cell.hierarchy.hierarchy_obj import CellInstance
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.utility.layout_statistics import LayoutStatistics
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecate_argument_name


def normalize_pairs(points: Iterable[float]) -> List[List[float]]:
    """
    Convert any reasonable point description into [[x1, y1], [x2, y2], …]
    """
    pts = list(points)
    if not pts:  # empty input
        return []

    # Detect flat vs nested
    if isinstance(pts[0], (list, tuple)):
        # already nested – just ensure every item is a *list* (not tuple)
        return [list(pair) for pair in pts]
    else:
        # flat list – chunk into pairs
        if len(pts) % 2:
            raise ValueError("Odd number of coordinates supplied")
        return [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]


class Modeler(object):
    """Manages EDB methods for primitives management accessible from `Edb.modeler`.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.modeler
    """

    def __getitem__(self, name: Union[str, int]) -> Primitive:
        """Get a primitive by name or ID.

        Parameters
        ----------
        name : str or int
            Name or ID of the primitive.

        Returns
        -------
        :class:`pyedb.grpc.database.primitive.primitive.Primitive`
            Primitive instance if found, None otherwise.

        Raises
        ------
        TypeError
            If name is not str or int.
        """

        if isinstance(name, int):
            return self._primitives.get(name)
        return self.primitives_by_name.get(name)

    def __init__(self, p_edb) -> None:
        """Initialize Modeler instance."""
        self._pedb = p_edb
        # Core cache
        self._primitives: dict[str, Primitive] = {}

        # Lazy indexes
        self._primitives_by_name: dict[str, Primitive] | None = None
        self._primitives_by_net: dict[str, list[Primitive]] | None = None
        self._primitives_by_layer: dict[str, list[Primitive]] | None = None
        self._primitives_by_layer_and_net: Dict[str, Dict[str, List[Primitive]]] | None = None

        # ============================================================

    # Cache management
    # ============================================================

    def _reload_all(self):
        """Force reload of all primitives and reset indexes."""
        self._primitives = {p.edb_uid: p for p in self._pedb.layout.primitives}
        self._primitives_by_name = None
        self._primitives_by_net = None
        self._primitives_by_layer = None
        self._primitives_by_layer_and_net = None

    def _add_primitive(self, prim: Any):
        """Add primitive wrapper to caches."""
        try:
            self._primitives[prim.edb_uid] = prim
            if self._primitives_by_name is not None:
                self._primitives_by_name[prim.aedt_name] = prim
            if self._primitives_by_net is not None and hasattr(prim, "net"):
                self._primitives_by_net.setdefault(prim.net, []).append(prim)
            if hasattr(prim, "layer"):
                if self._primitives_by_layer is not None and prim.layer_name:
                    self._primitives_by_layer.setdefault(prim.layer_name, []).append(prim)
        except:
            self._reload_all()

    def _remove_primitive(self, prim: Primitive):
        """Remove primitive wrapper from all caches efficiently and safely."""
        uid = prim.edb_uid

        # 1. Remove from primary cache
        self._primitives.pop(uid, None)

        # 2. Remove from name cache if initialized
        if self._primitives_by_name is not None:
            self._primitives_by_name.pop(prim.aedt_name, None)

        # 3. Remove from net cache if initialized
        if self._primitives_by_net is not None and hasattr(prim, "net") and not prim.net.is_null:
            net_name = prim.net.name
            net_prims = self._primitives_by_net.get(net_name)
            if net_prims:
                try:
                    net_prims.remove(prim)
                except ValueError:
                    pass  # Not found, skip
                if not net_prims:
                    self._primitives_by_net.pop(net_name, None)

        # 4. Remove from layer cache if initialized
        if self._primitives_by_layer is not None and hasattr(prim, "layer") and prim.layer_name:
            layer_name = prim.layer.name
            layer_prims = self._primitives_by_layer.get(layer_name)
            if layer_prims:
                try:
                    layer_prims.remove(prim)
                except ValueError:
                    pass
                if not layer_prims:
                    self._primitives_by_layer.pop(layer_name, None)

        # 5. Remove from layer+net cache if initialized
        if self._primitives_by_layer_and_net is not None:
            if hasattr(prim, "layer") and hasattr(prim, "net") and not prim.net.is_null:
                layer_name = prim.layer.name
                net_name = prim.net.name
                layer_dict = self._primitives_by_layer_and_net.get(layer_name)
                if layer_dict:
                    net_list = layer_dict.get(net_name)
                    if net_list:
                        try:
                            net_list.remove(prim)
                        except ValueError:
                            pass
                        if not net_list:
                            layer_dict.pop(net_name, None)
                        if not layer_dict:
                            self._primitives_by_layer_and_net.pop(layer_name, None)

    def delete_batch_primitives(self, prim_list: List[Primitive]) -> None:
        """Delete a batch of primitives and update caches.

        Parameters
        ----------
        prim_list : list
            List of primitive objects to delete.
        """
        for prim in prim_list:
            prim._edb_object.delete()
        self._reload_all()

    @property
    def primitives(self) -> list[Primitive]:
        if not self._primitives:
            self._reload_all()
        return list(self._primitives.values())

    @property
    def primitives_by_name(self):
        if self._primitives_by_name is None:
            self._primitives_by_name = {p.aedt_name: p for p in self.primitives}
        return self._primitives_by_name

    @property
    def primitives_by_net(self):
        if self._primitives_by_net is None:
            d = {}
            for p in self.primitives:
                if hasattr(p, "net"):
                    d.setdefault(p.net.name, []).append(p)
            self._primitives_by_net = d
        return self._primitives_by_net

    @property
    def primitives_by_layer(self):
        if self._primitives_by_layer is None:
            d = {}
            for p in self.primitives:
                if p.layer_name:
                    d.setdefault(p.layer_name, []).append(p)
            self._primitives_by_layer = d
        return self._primitives_by_layer

    @property
    def primitives_by_layer_and_net(self) -> Dict[str, Dict[str, List[Primitive]]]:
        """Return all primitives indexed first by layer, then by net.

        Returns
        -------
        dict
            Nested dictionary:  layer -> net -> list[Primitive]
        """
        if self._primitives_by_layer_and_net is None:
            idx: Dict[str, Dict[str, List[Primitive]]] = {}
            for prim in self.primitives:
                if not prim.layer_name or not hasattr(prim, "net") or prim.net.is_null:
                    continue
                layer = prim.layer_name
                net = prim.net.name
                idx.setdefault(layer, {}).setdefault(net, []).append(prim)
            self._primitives_by_layer_and_net = idx
        return self._primitives_by_layer_and_net

    @property
    def _edb(self) -> Any:
        """EDB API object.

        Returns
        -------
        object
            EDB API object.
        """
        return self._pedb

    @property
    def _logger(self) -> Any:
        """Logger instance.

        Returns
        -------
        :class:`logger.Logger`
            Logger instance.
        """
        return self._pedb.logger

    @property
    def _active_layout(self) -> Any:
        """Active layout.

        Returns
        -------
        :class:`ansys.edb.core.layout.Layout`
            Active layout object.
        """
        return self._pedb.active_layout

    @property
    def _layout(self) -> Any:
        """Current layout.

        Returns
        -------
        :class:`ansys.edb.core.layout.Layout`
            Layout object.
        """
        return self._pedb.layout

    @property
    def _cell(self) -> Any:
        """Active cell.

        Returns
        -------
        :class:`ansys.edb.core.hierarchy.Cell`
            Active cell object.
        """
        return self._pedb.active_cell

    @property
    def db(self) -> Any:
        """Database object.

        Returns
        -------
        ansys.edb.core.database.Database
            Database object.
        """
        return self._pedb.active_db

    @property
    def layers(self) -> Dict[str, object]:
        """Dictionary of layers.

        Returns
        -------
        dict
            Dictionary of layers with layer names as keys.
        """
        return self._pedb.stackup.layers

    def get_primitive(self, primitive_id: int, edb_uid=True) -> Optional[Primitive]:
        """Retrieve primitive by ID.

        Parameters
        ----------
        primitive_id : int
            Primitive ID.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive` or bool
            Primitive object if found, False otherwise.
        """
        if edb_uid:
            for p in self._layout.primitives:
                if p.edb_uid == primitive_id:
                    return self.__mapping_primitive_type(p)
            for p in self._layout.primitives:
                for v in p.voids:
                    if v.edb_uid == primitive_id:
                        return self.__mapping_primitive_type(v)
        else:
            for p in self._layout.primitives:
                if p.id == primitive_id:
                    return self.__mapping_primitive_type(p)
            for p in self._layout.primitives:
                for v in p.voids:
                    if v.id == primitive_id:
                        return self.__mapping_primitive_type(v)

    def __mapping_primitive_type(self, primitive):
        from ansys.edb.core.primitive.primitive import (
            PrimitiveType as GrpcPrimitiveType,
        )

        if primitive.primitive_type == GrpcPrimitiveType.POLYGON:
            return Polygon(self._pedb, primitive)
        elif primitive.primitive_type == GrpcPrimitiveType.PATH:
            return Path(self._pedb, primitive)
        elif primitive.primitive_type == GrpcPrimitiveType.RECTANGLE:
            return Rectangle(self._pedb, primitive)
        elif primitive.primitive_type == GrpcPrimitiveType.CIRCLE:
            return Circle(self._pedb, primitive)
        elif primitive.primitive_type == GrpcPrimitiveType.BONDWIRE:
            return Bondwire(self._pedb, primitive)
        else:
            return False

    @property
    def polygons_by_layer(self) -> Dict[str, List[Primitive]]:
        """Primitives organized by layer names.

        Returns
        -------
        dict
            Dictionary where keys are layer names and values are lists of polygons.
        """
        polygon_by_layer = {}
        for lay in self.layers:
            if lay in self.primitives_by_layer:
                polygon_by_layer[lay] = [prim for prim in self.primitives_by_layer[lay] if prim.type == "polygon"]
            else:
                polygon_by_layer[lay] = []
        return polygon_by_layer

    @property
    def rectangles(self) -> List[Rectangle]:
        """All rectangle primitives.

        Returns
        -------
        list
            List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Rectangle` objects.
        """
        return [Rectangle(self._pedb, i) for i in self.primitives if i.type == "rectangle"]

    @property
    def circles(self) -> List[Circle]:
        """All circle primitives.

        Returns
        -------
        list
            List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Circle` objects.
        """
        return [Circle(self._pedb, i) for i in self.primitives if i.type == "circle"]

    @property
    def paths(self) -> List[Path]:
        """All path primitives.

        Returns
        -------
        list
            List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Path` objects.
        """
        return [Path(self._pedb, i) for i in self.primitives if i.type == "path"]

    @property
    def polygons(self) -> List[Polygon]:
        """All polygon primitives.

        Returns
        -------
        list
            List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon` objects.
        """
        return [Polygon(self._pedb, i) for i in self.primitives if i.type == "polygon"]

    def get_polygons_by_layer(self, layer_name: str, net_list: Optional[List[str]] = None) -> List[Primitive]:
        """Retrieve polygons by layer.

        Parameters
        ----------
        layer_name : str
            Layer name.
        net_list : list, optional
            List of net names to filter by.

        Returns
        -------
        list
            List of polygon objects.
        """
        polygons = self.polygons_by_layer.get(layer_name, [])
        if net_list:
            polygons = [p for p in polygons if p.net_name in net_list]
        return polygons

    def get_primitive_by_layer_and_point(
        self,
        point: Optional[List[float]] = None,
        layer: Optional[Union[str, List[str]]] = None,
        nets: Optional[Union[str, List[str]]] = None,
    ) -> List[Primitive]:
        """Get primitive at specified point on layer.

        Parameters
        ----------
        point : list, optional
            [x, y] coordinate point.
        layer : str or list, optional
            Layer name(s) to filter by.
        nets : str or list, optional
            Net name(s) to filter by.

        Returns
        -------
        list
            List of primitive objects at the point.

        Raises
        ------
        ValueError
            If point is invalid.
        """
        from ansys.edb.core.primitive.circle import Circle as GrpcCircle
        from ansys.edb.core.primitive.path import Path as GrpcPath
        from ansys.edb.core.primitive.polygon import Polygon as GrpcPolygon
        from ansys.edb.core.primitive.rectangle import Rectangle as GrpcRectangle

        if isinstance(layer, str) and layer not in list(self._pedb.stackup.signal_layers.keys()):
            layer = None
        if not isinstance(point, list) and len(point) == 2:
            self._logger.error("Provided point must be a list of two values")
            return False
        pt = GrpcPointData(point)
        if isinstance(nets, str):
            nets = [nets]
        elif nets and not isinstance(nets, list) and len(nets) == len([net for net in nets if isinstance(net, str)]):
            _nets = []
            for net in nets:
                if net not in self._pedb.nets:
                    self._logger.error(
                        f"Net {net} used to find primitive from layer point and net not found, skipping it."
                    )
                else:
                    _nets.append(self._pedb.nets[net])
            if _nets:
                nets = _nets
        if not isinstance(layer, list) and layer:
            layer = [layer]
        _obj_instances = self._pedb.layout_instance.query_layout_obj_instances(
            layer_filter=layer, net_filter=nets, spatial_filter=pt
        )
        returned_obj = []
        for inst in _obj_instances:
            primitive = inst.layout_obj.cast()
            if isinstance(primitive, GrpcPath):
                returned_obj.append(Path(self._pedb, primitive))
            elif isinstance(primitive, GrpcPolygon):
                returned_obj.append(Polygon(self._pedb, primitive))
            elif isinstance(primitive, GrpcRectangle):
                returned_obj.append(Rectangle(self._pedb, primitive))
            elif isinstance(primitive, GrpcCircle):
                returned_obj.append(Circle(self._pedb, primitive))
        return returned_obj

    @staticmethod
    def get_polygon_bounding_box(polygon: Primitive) -> List[float]:
        """Get bounding box of polygon.

        Parameters
        ----------
        polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Polygon primitive.

        Returns
        -------
        list
            Bounding box coordinates [min_x, min_y, max_x, max_y].
        """
        bounding_box = polygon.polygon_data.bbox()
        return [Value(bounding_box[0].x), Value(bounding_box[0].y), Value(bounding_box[1].x), Value(bounding_box[1].y)]

    @staticmethod
    def get_polygon_points(polygon) -> List[List[float]]:
        """Get points defining a polygon.

        Parameters
        ----------
        polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Polygon primitive.

        Returns
        -------
        list
            List of point coordinates.
        """
        points = []
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = polygon.polygon_data.points[i]
                if prev_point != point:
                    if point.is_arc:
                        points.append([Value(point.x)])
                    else:
                        points.append([Value(point.x), Value(point.y)])
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        return points

    def parametrize_polygon(self, polygon, selection_polygon, offset_name="offsetx", origin=None) -> bool:
        """Parametrize polygon points based on another polygon.

        Parameters
        ----------
        polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Polygon to parametrize.
        selection_polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Polygon used for selection.
        offset_name : str, optional
            Name of offset parameter.
        origin : list, optional
            [x, y] origin point for vector calculation.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """

        def calc_slope(point, origin):
            if point[0] - origin[0] != 0:
                slope = math.atan((point[1] - origin[1]) / (point[0] - origin[0]))
                xcoeff = math.sin(slope)
                ycoeff = math.cos(slope)

            else:
                if point[1] > 0:
                    xcoeff = 0
                    ycoeff = 1
                else:
                    xcoeff = 0
                    ycoeff = -1
            if ycoeff > 0:
                ycoeff = "+" + str(ycoeff)
            else:
                ycoeff = str(ycoeff)
            if xcoeff > 0:
                xcoeff = "+" + str(xcoeff)
            else:
                xcoeff = str(xcoeff)
            return xcoeff, ycoeff

        selection_polygon_data = selection_polygon.polygon_data
        polygon_data = polygon.polygon_data
        bound_center = polygon_data.bounding_circle()[0]
        bound_center2 = selection_polygon_data.bounding_circle()[0]
        center = [Value(bound_center.x), Value(bound_center.y)]
        center2 = [Value(bound_center2.x), Value(bound_center2.y)]
        x1, y1 = calc_slope(center2, center)

        if not origin:
            origin = [center[0] + float(x1) * 10000, center[1] + float(y1) * 10000]
        self._pedb.add_design_variable(offset_name, 0.0, is_parameter=True)
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = polygon_data.points[i]
                if prev_point != point:
                    check_inside = selection_polygon_data.is_inside(point)
                    if check_inside:
                        xcoeff, ycoeff = calc_slope([Value(point.x), Value(point.x)], origin)

                        new_points = GrpcPointData(
                            [
                                Value(str(Value(point.x) + f"{xcoeff}*{offset_name}")),
                                Value(str(Value(point.y)) + f"{ycoeff}*{offset_name}"),
                            ]
                        )
                        polygon_data.points[i] = new_points
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        polygon.polygon_data = polygon_data
        return True

    def _create_path(
        self,
        points,
        layer_name,
        width=1,
        net_name="",
        start_cap_style="Round",
        end_cap_style="Round",
        corner_style="Round",
    ):
        """
        Create a path based on a list of points.

        Parameters
        ----------
        points: .:class:`dotnet.database.layout.Shape`
            List of points.
        layer_name : str
            Name of the layer on which to create the path.
        width : float, optional
            Width of the path. The default is ``1``.
        net_name: str, optional
            Name of the net. The default is ``""``.
        start_cap_style : str, optional
            Style of the cap at its start. Options are ``"Round"``,
            ``"Extended", `` and ``"Flat"``. The default is
            ``"Round".
        end_cap_style : str, optional
            Style of the cap at its end. Options are ``"Round"``,
            ``"Extended", `` and ``"Flat"``. The default is
            ``"Round".
        corner_style : str, optional
            Style of the corner. Options are ``"Round"``,
            ``"Sharp"`` and ``"Mitered"``. The default is ``"Round".

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            ``True`` when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if start_cap_style.lower() == "round":
            start_cap_style = GrpcPathEndCapType.ROUND
        elif start_cap_style.lower() == "extended":
            start_cap_style = GrpcPathEndCapType.EXTENDED
        else:
            start_cap_style = GrpcPathEndCapType.FLAT
        if end_cap_style.lower() == "round":
            end_cap_style = GrpcPathEndCapType.ROUND
        elif end_cap_style.lower() == "extended":
            end_cap_style = GrpcPathEndCapType.EXTENDED
        else:
            end_cap_style = GrpcPathEndCapType.FLAT
        if corner_style.lower() == "round":
            corner_style = GrpcPathEndCapType.ROUND
        elif corner_style.lower() == "sharp":
            corner_style = GrpcPathCornerType.SHARP
        else:
            corner_style = GrpcPathCornerType.MITER
        _points = []
        if isinstance(points, (list, tuple)):
            points = normalize_pairs(points)
            for pt in points:
                _pt = []
                for coord in pt:
                    coord = Value(coord, self._pedb.active_cell)
                    _pt.append(coord)
                _points.append(_pt)
            points = _points
            width = Value(width, self._pedb.active_cell)
            polygon_data = GrpcPolygonData(points)
        elif isinstance(points, GrpcPolygonData):
            polygon_data = points
        else:
            raise TypeError("Points must be a list of points or a PolygonData object.")
        path = Path(self._pedb).create(
            layout=self._active_layout,
            layer=layer_name,
            net=net,
            width=width,
            end_cap1=start_cap_style,
            end_cap2=end_cap_style,
            corner_style=corner_style,
            points=polygon_data,
        )
        if path.is_null:  # pragma: no cover
            self._logger.error("Null path created")
            return False
        return Path(self._pedb, path)

    def create_trace(
        self,
        path_list: Union[Iterable[float], GrpcPolygonData],
        layer_name: str,
        width: float = 1,
        net_name: str = "",
        start_cap_style: str = "Round",
        end_cap_style: str = "Round",
        corner_style: str = "Round",
    ) -> Optional[Primitive]:
        """Create trace path.

        Parameters
        ----------
        path_list : Iterable
            List of points [x,y] or [[x, y], ...]
            or [(x, y)...].
        layer_name : str
            Layer name.
        width : float, optional
            Trace width.
        net_name : str, optional
            Associated net name.
        start_cap_style : str, optional
            Start cap style ("Round", "Extended", "Flat").
        end_cap_style : str, optional
            End cap style ("Round", "Extended", "Flat").
        corner_style : str, optional
            Corner style ("Round", "Sharp", "Mitered").

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Path` or bool
            Path object if created, False otherwise.
        """

        primitive = self._create_path(
            points=path_list,
            layer_name=layer_name,
            net_name=net_name,
            width=width,
            start_cap_style=start_cap_style,
            end_cap_style=end_cap_style,
            corner_style=corner_style,
        )
        self._add_primitive(primitive)  # update cache
        return primitive

    def create_polygon(
        self,
        points: Union[List[List[float]], GrpcPolygonData],
        layer_name: str,
        voids: Optional[List[Any]] = [],
        net_name: str = "",
    ) -> Optional[Primitive]:
        """Create polygon primitive.

        Parameters
        ----------
        points : list or :class:`ansys.edb.core.geometry.polygon_data.PolygonData`
            Polygon points or PolygonData object.
        layer_name : str
            Layer name.
        voids : list, optional
            List of void shapes or points.
        net_name : str, optional
            Associated net name.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon` or bool
            Polygon object if created, False otherwise.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if isinstance(points, list):
            new_points = []
            for idx, i in enumerate(points):
                new_points.append(
                    GrpcPointData([Value(i[0], self._pedb.active_cell), Value(i[1], self._pedb.active_cell)])
                )
            polygon_data = GrpcPolygonData(points=new_points)

        elif isinstance(points, GrpcPolygonData):
            polygon_data = points
        else:
            polygon_data = points
        if not polygon_data.points:
            self._logger.error("Failed to create main shape polygon data")
            return False
        for void in voids:
            if isinstance(void, list):
                void_polygon_data = GrpcPolygonData(points=void)
            elif isinstance(void, GrpcPolygonData):
                void_polygon_data = void
            else:
                void_polygon_data = void.polygon_data
            if not void_polygon_data.points:
                self._logger.error("Failed to create void polygon data")
                return False
            polygon_data.holes.append(void_polygon_data)
        polygon = Polygon(self._pedb, None).create(
            layout=self._active_layout, layer=layer_name, net=net, polygon_data=polygon_data
        )
        if polygon.is_null or polygon_data is False:  # pragma: no cover
            self._logger.error("Null polygon created")
            return False
        self._add_primitive(polygon)
        return Polygon(self._pedb, polygon)

    def create_rectangle(
        self,
        layer_name: str,
        net_name: str = "",
        lower_left_point: str = "",
        upper_right_point: str = "",
        center_point: str = "",
        width: Union[str, float] = "",
        height: Union[str, float] = "",
        representation_type: str = "lower_left_upper_right",
        corner_radius: str = "0mm",
        rotation: str = "0deg",
    ) -> Optional[Primitive]:
        """Create rectangle primitive.

        Parameters
        ----------
        layer_name : str
            Layer name.
        net_name : str, optional
            Associated net name.
        lower_left_point : list, optional
            [x,y] lower left point.
        upper_right_point : list, optional
            [x,y] upper right point.
        center_point : list, optional
            [x,y] center point.
        width : str or float, optional
            Rectangle width.
        height : str or float, optional
            Rectangle height.
        representation_type : str, optional
            "lower_left_upper_right" or "center_width_height".
        corner_radius : str, optional
            Corner radius with units.
        rotation : str, optional
            Rotation angle with units.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Rectangle` or bool
            Rectangle object if created, False otherwise.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)
        if representation_type == "lower_left_upper_right":
            rect = Rectangle(self._pedb).create(
                layout=self._active_layout,
                layer=layer_name,
                net=edb_net,
                rep_type=representation_type,
                param1=Value(lower_left_point[0]),
                param2=Value(lower_left_point[1]),
                param3=Value(upper_right_point[0]),
                param4=Value(upper_right_point[1]),
                corner_rad=Value(corner_radius),
                rotation=Value(rotation),
            )
        else:
            rep_type = GrpcRectangleRepresentationType.CENTER_WIDTH_HEIGHT
            if isinstance(width, str):
                if width in self._pedb.variables:
                    width = Value(width, self._pedb.active_cell)
                else:
                    width = Value(width)
            else:
                width = Value(width)
            if isinstance(height, str):
                if height in self._pedb.variables:
                    height = Value(height, self._pedb.active_cell)
                else:
                    height = Value(width)
            else:
                height = Value(width)
            rect = Rectangle(self._pedb).create(
                layout=self._active_layout,
                layer=layer_name,
                net=edb_net,
                rep_type=rep_type,
                param1=Value(center_point[0]),
                param2=Value(center_point[1]),
                param3=Value(width),
                param4=Value(height),
                corner_rad=Value(corner_radius),
                rotation=Value(rotation),
            )
        if not rect.is_null:
            self._add_primitive(rect)
            return rect
        return False

    def create_circle(
        self, layer_name: str, x: Union[float, str], y: Union[float, str], radius: Union[float, str], net_name: str = ""
    ) -> Optional[Primitive]:
        """Create circle primitive.

        Parameters
        ----------
        layer_name : str
            Layer name.
        x : float
            Center x-coordinate.
        y : float
            Center y-coordinate.
        radius : float
            Circle radius.
        net_name : str, optional
            Associated net name.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Circle` or bool
            Circle object if created, False otherwise.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)

        circle = Circle(self._pedb).create(
            layout=self._active_layout,
            layer=layer_name,
            net=edb_net,
            center_x=Value(x),
            center_y=Value(y),
            radius=Value(radius),
        )
        if not circle.is_null:
            self._add_primitive(circle)
            return circle
        return False

    def delete_primitives(self, net_names: Union[str, List[str]]) -> bool:
        """Delete primitives by net name(s).

        Parameters
        ----------
        net_names : str or list
            Net name(s).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p in self.primitives[:]:
            if p.net_name in net_names:
                p.delete()
        return True

    def get_primitives(
        self,
        net_name: Optional[str] = None,
        layer_name: Optional[str] = None,
        prim_type: Optional[str] = None,
        is_void: bool = False,
    ) -> List[Primitive]:
        """Get primitives with filtering.

        Parameters
        ----------
        net_name : str, optional
            Net name filter.
        layer_name : str, optional
            Layer name filter.
        prim_type : str, optional
            Primitive type filter.
        is_void : bool, optional
            Void primitive filter.

        Returns
        -------
        list
            List of filtered primitives.
        """
        prims = []
        for el in self.primitives:
            if not el.primitive_type:
                continue
            if net_name:
                if not el.net.name == net_name:
                    continue
            if layer_name:
                if not el.layer.name == layer_name:
                    continue
            if prim_type:
                if not el.primitive_type.name.lower() == prim_type:
                    continue
            if not el.is_void == is_void:
                continue
            prims.append(el)
        return prims

    def fix_circle_void_for_clipping(self) -> bool:
        """Fix circle void clipping issues.

        Returns
        -------
        bool
            True if changes made, False otherwise.
        """
        for void_circle in self.circles:
            if not void_circle.is_void:
                continue
            circ_params = void_circle.get_parameters()

            cloned_circle = Circle.create(
                layout=self._active_layout,
                layer=void_circle.layer_name,
                net=void_circle.net,
                center_x=Value(circ_params[0]),
                center_y=Value(circ_params[1]),
                radius=Value(circ_params[2]),
            )
            if not cloned_circle.is_null:
                cloned_circle.is_negative = True
                void_circle.delete()
        return True

    def _validatePoint(self, point, allowArcs=True):
        if len(point) == 2:
            if not isinstance(point[0], (int, float, str)):
                self._logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):
                self._logger.error("Point Y value must be a number.")
                return False
            return True
        elif len(point) == 3:
            if not allowArcs:  # pragma: no cover
                self._logger.error("Arc found but arcs are not allowed in _validatePoint.")
                return False
            if not isinstance(point[0], (int, float, str)):  # pragma: no cover
                self._logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._logger.error("Point Y value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._logger.error("Invalid point height.")
                return False
            return True
        elif len(point) == 5:
            if not allowArcs:  # pragma: no cover
                self._logger.error("Arc found but arcs are not allowed in _validatePoint.")
                return False
            if not isinstance(point[0], (int, float, str)):  # pragma: no cover
                self._logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._logger.error("Point Y value must be a number.")
                return False
            if not isinstance(point[2], str) or point[2] not in ["cw", "ccw"]:
                self._logger.error("Invalid rotation direction {} is specified.")
                return False
            if not isinstance(point[3], (int, float, str)):  # pragma: no cover
                self._logger.error("Arc center point X value must be a number.")
                return False
            if not isinstance(point[4], (int, float, str)):  # pragma: no cover
                self._logger.error("Arc center point Y value must be a number.")
                return False
            return True
        else:  # pragma: no cover
            self._logger.error("Arc point descriptor has incorrect number of elements (%s)", len(point))
            return False

    def parametrize_trace_width(
        self,
        nets_name: Union[str, List[str]],
        layers_name: Optional[Union[str, List[str]]] = None,
        parameter_name: str = "trace_width",
        variable_value: Optional[Union[float, str]] = None,
    ) -> bool:
        """Parametrize trace width.

        Parameters
        ----------
        nets_name : str or list
            Net name(s).
        layers_name : str or list, optional
            Layer name(s) filter.
        parameter_name : str, optional
            Parameter name prefix.
        variable_value : float or str, optional
            Initial parameter value.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(nets_name, str):
            nets_name = [nets_name]
        if isinstance(layers_name, str):
            layers_name = [layers_name]
        for net_name in nets_name:
            for p in self.paths:
                _parameter_name = f"{parameter_name}_{p.id}"
                if not p.net.is_null:
                    if p.net.name == net_name:
                        if not layers_name:
                            if not variable_value:
                                variable_value = p.width
                            self._pedb.active_cell.add_variable(
                                name=_parameter_name, value=Value(variable_value), is_param=True
                            )
                            p.width = Value(_parameter_name, self._pedb.active_cell)
                        elif p.layer.name in layers_name:
                            if not variable_value:
                                variable_value = p.width
                            self._pedb.add_design_variable(parameter_name, variable_value, True)
                            p.width = Value(_parameter_name, self._pedb.active_cell)
        return True

    def unite_polygons_on_layer(
        self,
        layer_name: Optional[Union[str, List[str]]] = None,
        delete_padstack_gemometries: bool = False,
        net_names_list: Optional[List[str]] = None,
    ) -> bool:
        """Unite polygons on layer.

        Parameters
        ----------
        layer_name : str or list, optional
            Layer name(s) to process.
        delete_padstack_gemometries : bool, optional
            Whether to delete padstack geometries.
        net_names_list : list, optional
            Net names filter.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(layer_name, str):
            layer_name = [layer_name]
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        if net_names_list is None:
            net_names_list = []

        for lay in layer_name:
            self._logger.info(f"Uniting Objects on layer {lay}.")
            poly_by_nets = {}
            all_voids = []
            list_polygon_data = []
            delete_list = []
            for poly in self.polygons_by_layer.get(lay, []):
                if poly.net_name:
                    poly_by_nets.setdefault(poly.net_name, []).append(poly)
            for net, polys in poly_by_nets.items():
                if net in net_names_list or not net_names_list:
                    for p in polys:
                        list_polygon_data.append(p.polygon_data)
                        delete_list.append(p)
                        all_voids.extend(p.voids)
            united = GrpcPolygonData.unite(list_polygon_data)
            for item in united:
                for void in all_voids:
                    if item.intersection_type(void.polygon_data) == 2:
                        item.add_hole(void.polygon_data)
                self.create_polygon(item, layer_name=lay, voids=[], net_name=net)
            for void in all_voids:
                for poly in poly_by_nets[net]:  # pragma no cover
                    if void.polygon_data.intersection_type(poly.polygon_data).value >= 2:
                        try:
                            id = delete_list.index(poly)
                        except ValueError:
                            id = -1
                        if id >= 0:
                            delete_list.pop(id)
            for poly in list(set(delete_list)):
                poly.delete()

        if delete_padstack_gemometries:
            self._logger.info("Deleting Padstack Definitions")
            for pad in self._pedb.padstacks.definitions:
                p1 = self._pedb.padstacks.definitions[pad].edb_padstack.data
                if len(p1.get_layer_names()) > 1:
                    self._pedb.padstacks.remove_pads_from_padstack(pad)
        return True

    def defeature_polygon(self, poly: Polygon, tolerance: float = 0.001) -> bool:
        """Defeature polygon.

        Parameters
        ----------
        poly : :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon`
            Polygon to defeature.
        tolerance : float, optional
            Maximum surface deviation tolerance.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        new_poly = poly.polygon_data.defeature(tol=tolerance)
        if not new_poly.points:
            self._pedb.logger.error(
                f"Defeaturing on polygon {poly.id} returned empty polygon, tolerance threshold might too large. "
            )
            return False
        poly.polygon_data = new_poly
        return True

    def get_layout_statistics(
        self, evaluate_area: bool = False, net_list: Optional[List[str]] = None
    ) -> LayoutStatistics:
        """Get layout statistics.

        Parameters
        ----------
        evaluate_area : bool, optional
            Whether to compute metal area statistics.
        net_list : list, optional
            Net list for area computation.

        Returns
        -------
        :class:`LayoutStatistics`
            Layout statistics object.
        """
        stat_model = LayoutStatistics()
        stat_model.num_layers = len(list(self._pedb.stackup.layers.values()))
        stat_model.num_capacitors = len(self._pedb.components.capacitors)
        stat_model.num_resistors = len(self._pedb.components.resistors)
        stat_model.num_inductors = len(self._pedb.components.inductors)
        bbox = self._pedb._hfss.get_layout_bounding_box(self._active_layout)
        stat_model._layout_size = round(bbox[2] - bbox[0], 6), round(bbox[3] - bbox[1], 6)
        stat_model.num_discrete_components = (
            len(self._pedb.components.Others) + len(self._pedb.components.ICs) + len(self._pedb.components.IOs)
        )
        stat_model.num_inductors = len(self._pedb.components.inductors)
        stat_model.num_resistors = len(self._pedb.components.resistors)
        stat_model.num_capacitors = len(self._pedb.components.capacitors)
        stat_model.num_nets = len(self._pedb.nets.nets)
        stat_model.num_traces = len(self._pedb.modeler.paths)
        stat_model.num_polygons = len(self._pedb.modeler.polygons)
        stat_model.num_vias = len(self._pedb.padstacks.instances)
        stat_model.stackup_thickness = round(self._pedb.stackup.get_layout_thickness(), 6)
        if evaluate_area:
            outline_surface = stat_model.layout_size[0] * stat_model.layout_size[1]
            if net_list:
                netlist = list(self._pedb.nets.nets.keys())
                _poly = self._pedb.get_conformal_polygon_from_netlist(netlist)
            else:
                for layer in list(self._pedb.stackup.signal_layers.keys()):
                    surface = 0.0
                    primitives = self.primitives_by_layer[layer]
                    for prim in primitives:
                        if prim.primitive_type.name == "PATH":
                            surface += Path(self._pedb, prim).length * Value(prim.cast().width)
                        if prim.primitive_type.name == "POLYGON":
                            surface += prim.polygon_data.area()
                            stat_model.occupying_surface[layer] = round(surface, 6)
                            stat_model.occupying_ratio[layer] = round(surface / outline_surface, 6)
        return stat_model

    def create_bondwire(
        self,
        definition_name: str,
        placement_layer: str,
        width: Union[float, str],
        material: str,
        start_layer_name: str,
        start_x: Union[float, str],
        start_y: Union[float, str],
        end_layer_name: str,
        end_x: Union[float, str],
        end_y: Union[float, str],
        net: str,
        start_cell_instance_name: Optional[str] = None,
        end_cell_instance_name: Optional[str] = None,
        bondwire_type: str = "jedec4",
    ) -> Optional[Primitive]:
        """Create bondwire.

        Parameters
        ----------
        definition_name : str
            Bondwire definition name.
        placement_layer : str
            Placement layer name.
        width : float or str
            Bondwire width.
        material : str
            Material name.
        start_layer_name : str
            Start layer name.
        start_x : float or str
            Start x-coordinate.
        start_y : float or str
            Start y-coordinate.
        end_layer_name : str
            End layer name.
        end_x : float or str
            End x-coordinate.
        end_y : float or str
            End y-coordinate.
        net : str
            Associated net name.
        start_cell_instance_name : str, optional
            Start cell instance name.
        end_cell_instance_name : str, optional
            End cell instance name.
        bondwire_type : str, optional
            Bondwire type ("jedec4", "jedec5", "apd").

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Bondwire` or bool
            Bondwire object if created, False otherwise.
        """

        from ansys.edb.core.hierarchy.cell_instance import (
            CellInstance as GrpcCellInstance,
        )

        start_cell_inst = None
        end_cell_inst = None
        cell_instances = {cell_inst.name: cell_inst for cell_inst in self._active_layout.cell_instances}
        if start_cell_instance_name:
            if start_cell_instance_name not in cell_instances:
                start_cell_inst = GrpcCellInstance.create(
                    self._pedb.active_layout, start_cell_instance_name, ref=self._pedb.active_layout
                )
            else:
                start_cell_inst = cell_instances[start_cell_instance_name]
                cell_instances = {cell_inst.name: cell_inst for cell_inst in self._active_layout.cell_instances}
        if end_cell_instance_name:
            if end_cell_instance_name not in cell_instances:
                end_cell_inst = GrpcCellInstance.create(
                    self._pedb.active_layout, end_cell_instance_name, ref=self._pedb.active_layout
                )
            else:
                end_cell_inst = cell_instances[end_cell_instance_name]

        if bondwire_type == "jedec4":
            bondwire_type = GrpcBondwireType.JEDEC4
        elif bondwire_type == "jedec5":
            bondwire_type = GrpcBondwireType.JEDEC5
        elif bondwire_type == "apd":
            bondwire_type = GrpcBondwireType.APD
        else:
            bondwire_type = GrpcBondwireType.JEDEC4
        bw = Bondwire.create(
            layout=self._active_layout,
            bondwire_type=bondwire_type,
            definition_name=definition_name,
            placement_layer=placement_layer,
            width=Value(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=Value(start_x),
            start_y=Value(start_y),
            end_layer_name=end_layer_name,
            end_x=Value(end_x),
            end_y=Value(end_y),
            net=net,
            end_context=end_cell_inst,
            start_context=start_cell_inst,
        )
        bondwire = Bondwire(self._pedb, bw)
        self._add_primitive(bondwire)
        return bondwire

    def create_pin_group(
        self,
        name: str,
        pins_by_id: Optional[List[int]] = None,
        pins_by_aedt_name: Optional[List[str]] = None,
        pins_by_name: Optional[List[str]] = None,
    ) -> bool:
        """Create pin group.

        Parameters
        ----------
        name : str
            Pin group name.
        pins_by_id : list, optional
            List of pin IDs.
        pins_by_aedt_name : list, optional
            List of pin AEDT names.
        pins_by_name : list, optional
            List of pin names.

        Returns
        -------
        :class:`pyedb.dotnet.database.siwave.pin_group.PinGroup` or bool
            PinGroup object if created, False otherwise.
        """
        # TODO move this method to components and merge with existing one
        pins = {}
        if pins_by_id:
            if isinstance(pins_by_id, int):
                pins_by_id = [pins_by_id]
            for p in pins_by_id:
                edb_pin = None
                if p in self._pedb.padstacks.instances:
                    edb_pin = self._pedb.padstacks.instances[p]
                if edb_pin and not p in pins:
                    pins[p] = edb_pin
        if not pins_by_aedt_name:
            pins_by_aedt_name = []
        if not pins_by_name:
            pins_by_name = []
        if pins_by_aedt_name or pins_by_name:
            if isinstance(pins_by_aedt_name, str):
                pins_by_aedt_name = [pins_by_aedt_name]
            if isinstance(pins_by_name, str):
                pins_by_name = [pins_by_name]
            p_inst = self._pedb.layout.padstack_instances
            _pins = {
                pin_id: pin
                for pin_id, pin in p_inst.items()
                if pin.aedt_name in pins_by_aedt_name or pin.name in pins_by_name
            }
            if not pins:
                pins = _pins
            else:
                for id, pin in _pins.items():
                    if not id in pins:
                        pins[id] = pin
        if not pins:
            self._logger.error("No pin found.")
            return False
        pins = list(pins.values())
        obj = GrpcPinGroup.create(layout=self._pedb.active_layout, name=name, padstack_instances=pins)
        if obj.is_null:
            raise RuntimeError(f"Failed to create pin group {name}.")
        else:
            net_obj = [i.net for i in pins if not i.net.is_null]
            if net_obj:
                obj.net = net_obj[0]
        return self._pedb.siwave.pin_groups[name]

    @staticmethod
    def add_void(shape: "Primitive", void_shape: Union["Primitive", List["Primitive"]]) -> bool:
        """Add void to shape.

        Parameters
        ----------
        shape : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Main shape.
        void_shape : list or :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Void shape(s).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not isinstance(void_shape, list):
            void_shape = [void_shape]
        for void in void_shape:
            if isinstance(void, Primitive):
                shape._edb_object.add_void(void)
                flag = True
            else:
                shape._edb_object.add_void(void)
                flag = True
            if not flag:
                return flag
        return True

    def insert_cell_instance(self, cell_name,
                             placement_layer,
                             instance_name=None,
                             scale:Union[float]=1,
                             rotation:Union[float, str]=0,
                             offset_x:Union[float, str]=0,
                             offset_y:Union[float, str]=0,
                             mirror:bool=False,
                             )-> CellInstance:
        """Insert a layout instance into the active layout."""
        from pyedb.generic.general_methods import generate_unique_name
        from ansys.edb.core.hierarchy.cell_instance import CellInstance
        from ansys.edb.core.layout.cell import Cell, CellType

        instance_name = instance_name if instance_name else generate_unique_name(cell_name, n=2)
        cell = Cell.find(self._pedb._db, CellType.CIRCUIT_CELL, cell_name)
        cell_inst = CellInstance.create(self._pedb.active_layout, instance_name, cell.layout)
        cell_inst.placement_layer = self._pedb.stackup.layers[placement_layer]._edb_object
        transform = cell_inst.transform
        transform.scale = scale
        transform.rotation = rotation
        transform.offset_x = offset_x
        transform.offset_y = offset_y
        transform.mirror = mirror
        cell_inst.transform = transform
        return cell_inst

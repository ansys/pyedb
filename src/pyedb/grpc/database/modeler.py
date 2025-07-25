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
import math
from typing import Any, Dict, List, Optional, Union

from ansys.edb.core.geometry.arc_data import ArcData as GrpcArcData
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import (
    PolygonSenseType as GrpcPolygonSenseType,
)
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.inner.exceptions import InvalidArgumentException
from ansys.edb.core.primitive.bondwire import BondwireType as GrpcBondwireType
from ansys.edb.core.primitive.path import PathCornerType as GrpcPathCornerType
from ansys.edb.core.primitive.path import PathEndCapType as GrpcPathEndCapType
from ansys.edb.core.primitive.rectangle import (
    RectangleRepresentationType as GrpcRectangleRepresentationType,
)

from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.utility.layout_statistics import LayoutStatistics
from pyedb.grpc.database.utility.value import Value


class Modeler(object):
    """Manages EDB methods for primitives management accessible from `Edb.modeler`.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.modeler
    """

    def __getitem__(self, name: Union[str, int]) -> Optional[Primitive]:
        """Get a primitive by name or ID.

        Parameters
        ----------
        name : str or int
            Name or ID of the primitive.

        Returns
        -------
        :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent` or None
            Primitive instance if found, None otherwise.

        Raises
        ------
        TypeError
            If name is not str or int.
        """
        for i in self.primitives:
            if (
                (isinstance(name, str) and i.aedt_name == name)
                or (isinstance(name, str) and i.aedt_name == name.replace("__", "_"))
                or (isinstance(name, int) and i.id == name)
            ):
                return i
        self._pedb.logger.error("Primitive not found.")
        return

    def __init__(self, p_edb) -> None:
        """Initialize Modeler instance."""
        self._pedb = p_edb
        self.__primitives = []
        self.__primitives_by_layer = {}

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

    def get_primitive(self, primitive_id: int) -> Optional[Primitive]:
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
        for p in self._layout.primitives:
            if p.edb_uid == primitive_id:
                return self.__mapping_primitive_type(p)
        for p in self._layout.primitives:
            for v in p.voids:
                if v.edb_uid == primitive_id:
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
    def primitives(self) -> List[Primitive]:
        """All primitives in the layout.

        Returns
        -------
        list
            List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive` objects.
        """
        return self._pedb.layout.primitives

    @property
    def polygons_by_layer(self) -> Dict[str, List[Primitive]]:
        """Primitives organized by layer names.

        Returns
        -------
        dict
            Dictionary where keys are layer names and values are lists of polygons.
        """
        _primitives_by_layer = {}
        for lay in self.layers:
            _primitives_by_layer[lay] = self.get_polygons_by_layer(lay)
        return _primitives_by_layer

    @property
    def primitives_by_net(self) -> Dict[str, List[Primitive]]:
        """Primitives organized by net names.

        Returns
        -------
        dict
            Dictionary where keys are net names and values are lists of primitives.
        """
        _prim_by_net = {}
        for net, net_obj in self._pedb.nets.nets.items():
            _prim_by_net[net] = [i for i in net_obj.primitives]
        return _prim_by_net

    @property
    def primitives_by_layer(self) -> Dict[str, List[Primitive]]:
        """Primitives organized by layer names.

        Returns
        -------
        dict
            Dictionary where keys are layer names and values are lists of primitives.
        """
        _primitives_by_layer = {}
        for lay in self.layers:
            _primitives_by_layer[lay] = []
        for lay in self._pedb.stackup.non_stackup_layers:
            _primitives_by_layer[lay] = []
        for i in self._layout.primitives:
            try:
                lay = i.layer.name
                if lay in _primitives_by_layer:
                    _primitives_by_layer[lay].append(i)
            except (InvalidArgumentException, AttributeError):
                pass
        return _primitives_by_layer

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
        objinst = []
        for el in self.polygons:
            if el.layer.name == layer_name:
                if not el.net.is_null:
                    if net_list and el.net.name in net_list:
                        objinst.append(el)
                    else:
                        objinst.append(el)
        return objinst

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
        for pt in points:
            _pt = []
            for coord in pt:
                coord = Value(coord, self._pedb.active_cell)
                _pt.append(coord)
            _points.append(_pt)
        points = _points

        width = Value(width, self._pedb.active_cell)

        polygon_data = GrpcPolygonData(points=[GrpcPointData(i) for i in points])
        path = Path.create(
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
        path_list: List[List[float]],
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
        path_list : list
            List of [x,y] points.
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
            else:
                void_polygon_data = void.polygon_data
            if not void_polygon_data.points:
                self._logger.error("Failed to create void polygon data")
                return False
            polygon_data.holes.append(void_polygon_data)
        polygon = Polygon.create(layout=self._active_layout, layer=layer_name, net=net, polygon_data=polygon_data)
        if polygon.is_null or polygon_data is False:  # pragma: no cover
            self._logger.error("Null polygon created")
            return False
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
            rep_type = GrpcRectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT
            rect = Rectangle.create(
                layout=self._active_layout,
                layer=layer_name,
                net=edb_net,
                rep_type=rep_type,
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
            rect = Rectangle.create(
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
            return Rectangle(self._pedb, rect)
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

        circle = Circle.create(
            layout=self._active_layout,
            layer=layer_name,
            net=edb_net,
            center_x=Value(x),
            center_y=Value(y),
            radius=Value(radius),
        )
        if not circle.is_null:
            return Circle(self._pedb, circle)
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

    @staticmethod
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

    def _createPolygonDataFromPolygon(self, shape):
        points = shape.points
        if not self._validatePoint(points[0]):
            self._logger.error("Error validating point.")
            return None
        arcs = []
        is_parametric = False
        for i in range(len(points) - 1):
            if i == 0:
                startPoint = points[-1]
                endPoint = points[i]
            else:
                startPoint = points[i - 1]
                endPoint = points[i]

            if not self._validatePoint(endPoint):
                return None
            startPoint = [Value(i) for i in startPoint]
            endPoint = [Value(i) for i in endPoint]
            if len(endPoint) == 2:
                is_parametric = (
                    is_parametric
                    or startPoint[0].is_parametric
                    or startPoint[1].is_parametric
                    or endPoint[0].is_parametric
                    or endPoint[1].is_parametric
                )
                arc = GrpcArcData(
                    GrpcPointData([startPoint[0], startPoint[1]]), GrpcPointData([endPoint[0], endPoint[1]])
                )
                arcs.append(arc)
            elif len(endPoint) == 3:
                is_parametric = (
                    is_parametric
                    or startPoint[0].is_parametric
                    or startPoint[1].is_parametric
                    or endPoint[0].is_parametric
                    or endPoint[1].is_parametric
                    or endPoint[2].is_parametric
                )
                arc = GrpcArcData(
                    GrpcPointData([startPoint[0], startPoint[1]]),
                    GrpcPointData([endPoint[0], endPoint[1]]),
                    kwarg={"height": endPoint[2]},
                )
                arcs.append(arc)
            elif len(endPoint) == 5:
                is_parametric = (
                    is_parametric
                    or startPoint[0].is_parametric
                    or startPoint[1].is_parametric
                    or endPoint[0].is_parametric
                    or endPoint[1].is_parametric
                    or endPoint[3].is_parametric
                    or endPoint[4].is_parametric
                )
                if endPoint[2].is_cw:
                    rotationDirection = GrpcPolygonSenseType.SENSE_CW
                elif endPoint[2].is_ccw:
                    rotationDirection = GrpcPolygonSenseType.SENSE_CCW
                else:
                    self._logger.error("Invalid rotation direction %s is specified.", endPoint[2])
                    return None
                arc = GrpcArcData(
                    GrpcPointData(startPoint),
                    GrpcPointData(endPoint),
                )
                # arc.direction = rotationDirection,
                # arc.center = GrpcPointData([endPoint[3], endPoint[4]]),
                arcs.append(arc)
        polygon = GrpcPolygonData(arcs=arcs)
        if not is_parametric:
            return polygon
        else:
            k = 0
            for pt in points:
                point = [Value(i) for i in pt]
                new_points = GrpcPointData(point)
                if len(point) > 2:
                    k += 1
                polygon.set_point(k, new_points)
                k += 1
        return polygon

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

    def _createPolygonDataFromRectangle(self, shape):
        # if not self._validatePoint(shape.pointA, False) or not self._validatePoint(shape.pointB, False):
        #     return None
        # pointA = GrpcPointData(pointA[0]), self._get_edb_value(shape.pointA[1])
        # )
        # pointB = self._edb.geometry.point_data(
        #     self._get_edb_value(shape.pointB[0]), self._get_edb_value(shape.pointB[1])
        # )
        # return self._edb.geometry.polygon_data.create_from_bbox((pointA, pointB))
        pass

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
            if lay in list(self.polygons_by_layer.keys()):
                for poly in self.polygons_by_layer[lay]:
                    poly = poly
                    if not poly.net.name in list(poly_by_nets.keys()):
                        if poly.net.name:
                            poly_by_nets[poly.net.name] = [poly]
                    else:
                        if poly.net.name:
                            poly_by_nets[poly.net.name].append(poly)
            for net in poly_by_nets:
                if net in net_names_list or not net_names_list:
                    for i in poly_by_nets[net]:
                        list_polygon_data.append(i.polygon_data)
                        delete_list.append(i)
                        all_voids.append(i.voids)
            a = GrpcPolygonData.unite(list_polygon_data)
            for item in a:
                for v in all_voids:
                    for void in v:
                        if item.intersection_type(void.polygon_data) == 2:
                            item.add_hole(void.polygon_data)
                self.create_polygon(item, layer_name=lay, voids=[], net_name=net)
            for v in all_voids:
                for void in v:
                    for poly in poly_by_nets[net]:  # pragma no cover
                        if void.polygon_data.intersection_type(poly.polygon_data).value >= 2:
                            try:
                                id = delete_list.index(poly)
                            except ValueError:
                                id = -1
                            if id >= 0:
                                delete_list.pop(id)
            for poly in delete_list:
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
                f"Defeaturing on polygon {poly.id} returned empty polygon, tolerance threshold " f"might too large. "
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
        return Bondwire(self._pedb, bw)

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

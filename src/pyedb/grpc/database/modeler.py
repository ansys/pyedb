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
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.utility.layout_statistics import LayoutStatistics


class Modeler(object):
    """Manages EDB methods for primitives management accessible from `Edb.modeler` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.modeler
    """

    def __getitem__(self, name):
        """Get  a layout instance from the Edb project.

        Parameters
        ----------
        name : str, int

        Returns
        -------
        :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`

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

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._primitives = []

    @property
    def _edb(self):
        return self._pedb

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _layout(self):
        return self._pedb.layout

    @property
    def _cell(self):
        return self._pedb.active_cell

    @property
    def db(self):
        """Db object."""
        return self._pedb.active_db

    @property
    def layers(self):
        """Dictionary of layers.

        Returns
        -------
        dict
            Dictionary of layers.
        """
        return self._pedb.stackup.layers

    def get_primitive(self, primitive_id):
        """Retrieve primitive from give id.

        Parameters
        ----------
        primitive_id : int
            Primitive id.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives.
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
    def primitives(self):
        """Primitives.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives.
        """
        return [self.__mapping_primitive_type(prim) for prim in self._pedb.layout.primitives]

    @property
    def polygons_by_layer(self):
        """Primitives with layer names as keys.

        Returns
        -------
        dict
            Dictionary of primitives with layer names as keys.
        """
        _primitives_by_layer = {}
        for lay in self.layers:
            _primitives_by_layer[lay] = self.get_polygons_by_layer(lay)
        return _primitives_by_layer

    @property
    def primitives_by_net(self):
        """Primitives with net names as keys.

        Returns
        -------
        dict
            Dictionary of primitives with nat names as keys.
        """
        _prim_by_net = {}
        for net, net_obj in self._pedb.nets.nets.items():
            _prim_by_net[net] = [i for i in net_obj.primitives]
        return _prim_by_net

    @property
    def primitives_by_layer(self):
        """Primitives with layer names as keys.

        Returns
        -------
        dict
            Dictionary of primitives with layer names as keys.
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
                    _primitives_by_layer[lay].append(Primitive(self._pedb, i))
            except (InvalidArgumentException, AttributeError):
                pass
        return _primitives_by_layer

    @property
    def rectangles(self):
        """Rectangles.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of rectangles.

        """
        return [Rectangle(self._pedb, i) for i in self.primitives if i.type == "rectangle"]

    @property
    def circles(self):
        """Circles.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of circles.

        """
        return [Circle(self._pedb, i) for i in self.primitives if i.type == "circle"]

    @property
    def paths(self):
        """Paths.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of paths.
        """
        return [Path(self._pedb, i) for i in self.primitives if i.type == "path"]

    @property
    def polygons(self):
        """Polygons.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of polygons.
        """
        return [Polygon(self._pedb, i) for i in self.primitives if i.type == "polygon"]

    def get_polygons_by_layer(self, layer_name, net_list=None):
        """Retrieve polygons by a layer.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        net_list : list, optional
            List of net names.

        Returns
        -------
        list
            List of primitive objects.
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
    def get_polygon_bounding_box(polygon):
        """Retrieve a polygon bounding box.

        Parameters
        ----------
        polygon :
            Name of the polygon.

        Returns
        -------
        list
            List of bounding box coordinates in the format ``[-x, -y, +x, +y]``.

        Examples
        --------
        >>> poly = database.modeler.get_polygons_by_layer("GND")
        >>> bounding = database.modeler.get_polygon_bounding_box(poly[0])
        """
        bounding_box = polygon.polygon_data.bbox()
        return [
            bounding_box[0].x.value,
            bounding_box[0].y.value,
            bounding_box[1].x.value,
            bounding_box[1].y.value,
        ]

    @staticmethod
    def get_polygon_points(polygon):
        """Retrieve polygon points.

        .. note::
           For arcs, one point is returned.

        Parameters
        ----------
        polygon :
            class: `dotnet.database.edb_data.primitives_data.Primitive`

        Returns
        -------
        list
            List of tuples. Each tuple provides x, y point coordinate. If the length of two consecutives tuples
             from the list equals 2, a segment is defined. The first tuple defines the starting point while the second
             tuple the ending one. If the length of one tuple equals one, that means a polyline is defined and the value
             is giving the arc height. Therefore to polyline is defined as starting point for the tuple
             before in the list, the current one the arc height and the tuple after the polyline ending point.

        Examples
        --------

        >>> poly = database.modeler.get_polygons_by_layer("GND")
        >>> points  = database.modeler.get_polygon_points(poly[0])

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
                        points.append([point.x.value])
                    else:
                        points.append([point.x.value, point.y.value])
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        return points

    def parametrize_polygon(self, polygon, selection_polygon, offset_name="offsetx", origin=None):
        """Parametrize pieces of a polygon based on another polygon.

        Parameters
        ----------
        polygon :
            Name of the polygon.
        selection_polygon :
            Polygon to use as a filter.
        offset_name : str, optional
            Name of the offset to create.  The default is ``"offsetx"``.
        origin : list, optional
            List of the X and Y origins, which impacts the vector
            computation and is needed to determine expansion direction.
            The default is ``None``, in which case the vector is
            computed from the polygon's center.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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
        center = [bound_center.x.value, bound_center.y.value]
        center2 = [bound_center2.x.value, bound_center2.y.value]
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
                        xcoeff, ycoeff = calc_slope([point.x.value, point.x.value], origin)

                        new_points = GrpcPointData(
                            [
                                GrpcValue(str(point.x.value) + f"{xcoeff}*{offset_name}"),
                                GrpcValue(str(point.y.value) + f"{ycoeff}*{offset_name}"),
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
                coord = GrpcValue(coord, self._pedb.active_cell)
                _pt.append(coord)
            _points.append(_pt)
        points = _points

        width = GrpcValue(width, self._pedb.active_cell)

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
        path_list,
        layer_name,
        width=1,
        net_name="",
        start_cap_style="Round",
        end_cap_style="Round",
        corner_style="Round",
    ):
        """
        Create a trace based on a list of points.

        Parameters
        ----------
        path_list : list
            List of points.
        layer_name : str
            Name of the layer on which to create the path.
        width : float, optional
            Width of the path. The default is ``1``.
        net_name : str, optional
            Name of the net. The default is ``""``.
        start_cap_style : str, optional
            Style of the cap at its start. Options are ``"Round"``,
            ``"Extended",`` and ``"Flat"``. The default is
            ``"Round"``.
        end_cap_style : str, optional
            Style of the cap at its end. Options are ``"Round"``,
            ``"Extended",`` and ``"Flat"``. The default is
            ``"Round"``.
        corner_style : str, optional
            Style of the corner. Options are ``"Round"``,
            ``"Sharp"`` and ``"Mitered"``. The default is ``"Round"``.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
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

    def create_polygon(self, points, layer_name, voids=[], net_name=""):
        """Create a polygon based on a list of points and voids.

        Parameters
        ----------
        points : list of points or PolygonData.
            - [x, y] coordinate
            - [x, y, height] for an arc with specific height (between previous point and actual point)
            - [x, y, rotation, xc, yc] for an arc given a point, rotation and center.
        layer_name : str
            Name of the layer on which to create the polygon.
        voids : list, optional
            List of shape objects for voids or points that creates the shapes. The default is``[]``.
        net_name : str, optional
            Name of the net. The default is ``""``.

        Returns
        -------
        bool, :class:`dotnet.database.edb_data.primitives.Primitive`
            Polygon when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if isinstance(points, list):
            new_points = []
            for idx, i in enumerate(points):
                new_points.append(
                    GrpcPointData([GrpcValue(i[0], self._pedb.active_cell), GrpcValue(i[1], self._pedb.active_cell)])
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
        layer_name,
        net_name="",
        lower_left_point="",
        upper_right_point="",
        center_point="",
        width="",
        height="",
        representation_type="lower_left_upper_right",
        corner_radius="0mm",
        rotation="0deg",
    ):
        """Create rectangle.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the rectangle.
        net_name : str
            Name of the net. The default is ``""``.
        lower_left_point : list
            Lower left point when ``representation_type="lower_left_upper_right"``. The default is ``""``.
        upper_right_point : list
            Upper right point when ``representation_type="lower_left_upper_right"``. The default is ``""``.
        center_point : list
            Center point when ``representation_type="center_width_height"``. The default is ``""``.
        width : str
            Width of the rectangle when ``representation_type="center_width_height"``. The default is ``""``.
        height : str
            Height of the rectangle when ``representation_type="center_width_height"``. The default is ``""``.
        representation_type : str, optional
            Type of the rectangle representation. The default is ``lower_left_upper_right``. Options are
            ``"lower_left_upper_right"`` and ``"center_width_height"``.
        corner_radius : str, optional
            Radius of the rectangle corner. The default is ``"0mm"``.
        rotation : str, optional
            Rotation of the rectangle. The default is ``"0deg"``.

        Returns
        -------
         :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Rectangle when successful, ``False`` when failed.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)
        if representation_type == "lower_left_upper_right":
            rep_type = GrpcRectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT
            rect = Rectangle.create(
                layout=self._active_layout,
                layer=layer_name,
                net=edb_net,
                rep_type=rep_type,
                param1=GrpcValue(lower_left_point[0]),
                param2=GrpcValue(lower_left_point[1]),
                param3=GrpcValue(upper_right_point[0]),
                param4=GrpcValue(upper_right_point[1]),
                corner_rad=GrpcValue(corner_radius),
                rotation=GrpcValue(rotation),
            )
        else:
            rep_type = GrpcRectangleRepresentationType.CENTER_WIDTH_HEIGHT
            if isinstance(width, str):
                if width in self._pedb.variables:
                    width = GrpcValue(width, self._pedb.active_cell)
                else:
                    width = GrpcValue(width)
            else:
                width = GrpcValue(width)
            if isinstance(height, str):
                if height in self._pedb.variables:
                    height = GrpcValue(height, self._pedb.active_cell)
                else:
                    height = GrpcValue(width)
            else:
                height = GrpcValue(width)
            rect = Rectangle.create(
                layout=self._active_layout,
                layer=layer_name,
                net=edb_net,
                rep_type=rep_type,
                param1=GrpcValue(center_point[0]),
                param2=GrpcValue(center_point[1]),
                param3=GrpcValue(width),
                param4=GrpcValue(height),
                corner_rad=GrpcValue(corner_radius),
                rotation=GrpcValue(rotation),
            )
        if not rect.is_null:
            return Rectangle(self._pedb, rect)
        return False

    def create_circle(self, layer_name, x, y, radius, net_name=""):
        """Create a circle on a specified layer.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        x : float
            Position on the X axis.
        y : float
            Position on the Y axis.
        radius : float
            Radius of the circle.
        net_name : str, optional
            Name of the net. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            Objects of the circle created when successful.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)

        circle = Circle.create(
            layout=self._active_layout,
            layer=layer_name,
            net=edb_net,
            center_x=GrpcValue(x),
            center_y=GrpcValue(y),
            radius=GrpcValue(radius),
        )
        if not circle.is_null:
            return Circle(self._pedb, circle)
        return False

    def delete_primitives(self, net_names):
        """Delete primitives by net names.

        Parameters
        ----------
        net_names : str, list
            Names of the nets to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> Edb.modeler.delete_primitives(net_names=["GND"])
        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p in self.primitives[:]:
            if p.net_name in net_names:
                p.delete()
        return True

    def get_primitives(self, net_name=None, layer_name=None, prim_type=None, is_void=False):
        """Get primitives by conditions.

        Parameters
        ----------
        net_name : str, optional
            Set filter on net_name. Default is `None`.
        layer_name : str, optional
            Set filter on layer_name. Default is `None`.
        prim_type :  str, optional
            Set filter on primitive type. Default is `None`.
        is_void : bool
            Set filter on is_void. Default is 'False'
        Returns
        -------
        list
            List of filtered primitives
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

    def fix_circle_void_for_clipping(self):
        """Fix issues when circle void are clipped due to a bug in EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when no changes were applied.
        """
        for void_circle in self.circles:
            if not void_circle.is_void:
                continue
            circ_params = void_circle.get_parameters()

            cloned_circle = Circle.create(
                layout=self._active_layout,
                layer=void_circle.layer_name,
                net=void_circle.net,
                center_x=GrpcValue(circ_params[0]),
                center_y=GrpcValue(circ_params[1]),
                radius=GrpcValue(circ_params[2]),
            )
            if not cloned_circle.is_null:
                cloned_circle.is_negative = True
                void_circle.delete()
        return True

    @staticmethod
    def add_void(shape, void_shape):
        """Add a void into a shape.

        Parameters
        ----------
        shape : Polygon
            Shape of the main object.
        void_shape : list, Path
            Shape of the voids.
        """
        flag = False
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

    def shape_to_polygon_data(self, shape):
        """Convert a shape to polygon data.

        Parameters
        ----------
        shape : :class:`pyedb.dotnet.database.modeler.Modeler.Shape`
            Type of the shape to convert. Options are ``"rectangle"`` and ``"polygon"``.
        """
        if shape.type == "polygon":
            return self._createPolygonDataFromPolygon(shape)
        elif shape.type == "rectangle":
            return self._createPolygonDataFromRectangle(shape)
        else:
            self._logger.error(
                "Unsupported shape type %s when creating a polygon primitive.",
                shape.type,
            )
            return None

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
            startPoint = [GrpcValue(i) for i in startPoint]
            endPoint = [GrpcValue(i) for i in endPoint]
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
                point = [GrpcValue(i) for i in pt]
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
        nets_name,
        layers_name=None,
        parameter_name="trace_width",
        variable_value=None,
    ):
        """Parametrize a Trace on specific layer or all stackup.

        Parameters
        ----------
        nets_name : str, list
            name of the net or list of nets to parametrize.
        layers_name : str, optional
            name of the layer or list of layers to which the net to parametrize has to be included.
        parameter_name : str, optional
            name of the parameter to create.
        variable_value : str, float, optional
            value with units of parameter to create.
            If None, the first trace width of Net will be used as parameter value.

        Returns
        -------
        bool
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
                                name=_parameter_name, value=GrpcValue(variable_value), is_param=True
                            )
                            p.width = GrpcValue(_parameter_name, self._pedb.active_cell)
                        elif p.layer.name in layers_name:
                            if not variable_value:
                                variable_value = p.width
                            self._pedb.add_design_variable(parameter_name, variable_value, True)
                            p.width = GrpcValue(_parameter_name, self._pedb.active_cell)
        return True

    def unite_polygons_on_layer(self, layer_name=None, delete_padstack_gemometries=False, net_names_list=[]):
        """Try to unite all Polygons on specified layer.

        Parameters
        ----------
        layer_name : str, optional
            Name of layer name to unite objects on. The default is ``None``, in which case all layers are taken.
        delete_padstack_gemometries : bool, optional
            Whether to delete all padstack geometries. The default is ``False``.
        net_names_list : list[str] : optional
            Net names list filter. The default is ``[]``, in which case all nets are taken.

        Returns
        -------
        bool
            ``True`` is successful.
        """
        if isinstance(layer_name, str):
            layer_name = [layer_name]
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())

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

    def defeature_polygon(self, poly, tolerance=0.001):
        """Defeature the polygon based on the maximum surface deviation criteria.

        Parameters
        ----------
        maximum_surface_deviation : float
        poly : Edb Polygon primitive
            Polygon to defeature.
        tolerance : float, optional
            Maximum tolerance criteria. The default is ``0.001``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        new_poly = poly.polygon_data.defeature(tol=tolerance)
        if not new_poly.points:
            self._pedb.logger.error(
                f"Defeaturing on polygon {poly.id} returned empty polygon, tolerance threshold " f"might too large. "
            )
            return False
        poly.polygon_data = new_poly
        return True

    def get_layout_statistics(self, evaluate_area=False, net_list=None):
        """Return EDBStatistics object from a layout.

        Parameters
        ----------

        evaluate_area : optional bool
            When True evaluates the layout metal surface, can take time-consuming,
            avoid using this option on large design.

        Returns
        -------

        EDBStatistics object.

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
                            surface += Path(self._pedb, prim).length * prim.cast().width.value
                        if prim.primitive_type.name == "POLYGON":
                            surface += prim.polygon_data.area()
                            stat_model.occupying_surface[layer] = round(surface, 6)
                            stat_model.occupying_ratio[layer] = round(surface / outline_surface, 6)
        return stat_model

    def create_bondwire(
        self,
        definition_name,
        placement_layer,
        width,
        material,
        start_layer_name,
        start_x,
        start_y,
        end_layer_name,
        end_x,
        end_y,
        net,
        start_cell_instance_name=None,
        end_cell_instance_name=None,
        bondwire_type="jedec4",
    ):
        """Create a bondwire object.

        Parameters
        ----------
        bondwire_type : :class:`BondwireType`
            Type of bondwire: kAPDBondWire or kJDECBondWire types.
        definition_name : str
            Bondwire definition name.
        placement_layer : str
            Layer name this bondwire will be on.
        width : :class:`Value <ansys.edb.utility.Value>`
            Bondwire width.
        material : str
            Bondwire material name.
        start_layer_name : str
            Name of start layer.
        start_x : :class:`Value <ansys.edb.utility.Value>`
            X value of start point.
        start_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of start point.
        end_layer_name : str
            Name of end layer.
        end_x : :class:`Value <ansys.edb.utility.Value>`
            X value of end point.
        end_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of end point.
        net : str or :class:`Net <ansys.edb.net.Net>` or None
            Net of the Bondwire.
        start_cell_instance_name : str, optional
            Cell instance name where the bondwire starts.
        end_cell_instance_name : str, optional
            Cell instance name where the bondwire ends.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.primitive.BondwireDotNet`
            Bondwire object created.
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
            width=GrpcValue(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=GrpcValue(start_x),
            start_y=GrpcValue(start_y),
            end_layer_name=end_layer_name,
            end_x=GrpcValue(end_x),
            end_y=GrpcValue(end_y),
            net=net,
            end_context=end_cell_inst,
            start_context=start_cell_inst,
        )
        return Bondwire(self._pedb, bw)

    def create_pin_group(
        self,
        name: str,
        pins_by_id=None,
        pins_by_aedt_name=None,
        pins_by_name=None,
    ):
        """Create a PinGroup.

        Parameters
        name : str,
            Name of the PinGroup.
        pins_by_id : list[int] or None
            List of pins by ID.
        pins_by_aedt_name : list[str] or None
            List of pins by AEDT name.
        pins_by_name : list[str] or None
            List of pins by name.
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
            _pins = {pin.id: pin for pin in p_inst if pin.aedt_name in pins_by_aedt_name or pin.name in pins_by_name}
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

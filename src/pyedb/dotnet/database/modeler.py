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
import warnings

from pyedb.dotnet.database.cell.primitive.bondwire import Bondwire
from pyedb.dotnet.database.dotnet.primitive import CircleDotNet, RectangleDotNet
from pyedb.dotnet.database.edb_data.primitives_data import Primitive, cast
from pyedb.dotnet.database.edb_data.utilities import EDBStatistics
from pyedb.dotnet.database.general import convert_py_list_to_net_list


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

    @property
    def _edb(self):
        return self._pedb.core

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _edbutils(self):
        return self._pedb.edbutils

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
            if p.id == primitive_id:
                return p
        for p in self._layout.primitives:
            for v in p.voids:
                if v.id == primitive_id:
                    return v

    @property
    def primitives(self):
        """Primitives.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives.
        """
        return self._pedb.layout.primitives

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
            layer = i.layer
            if not layer:
                continue
            lay = layer.name
            if lay in _primitives_by_layer:
                _primitives_by_layer[lay].append(i)
        return _primitives_by_layer

    @property
    def rectangles(self):
        """Rectangles.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of rectangles.

        """
        return [i for i in self.primitives if isinstance(i, RectangleDotNet)]

    @property
    def circles(self):
        """Circles.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of circles.

        """
        return [i for i in self.primitives if isinstance(i, CircleDotNet)]

    @property
    def paths(self):
        """Paths.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of paths.
        """
        return [i for i in self.primitives if i.primitive_type == "path"]

    @property
    def polygons(self):
        """Polygons.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of polygons.
        """
        return [i for i in self.primitives if i.primitive_type == "polygon"]

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
        if isinstance(layer, str) and layer not in list(self._pedb.stackup.signal_layers.keys()):
            layer = None
        if not isinstance(point, list) and len(point) == 2:
            self._logger.error("Provided point must be a list of two values")
            return False
        pt = self._edb.geometry.point_data(self._pedb.edb_value(point[0]), self._pedb.edb_value(point[1]))
        if nets:
            if isinstance(nets, str):
                nets = [nets]
            _nets = []
            for net in nets:
                if net not in self._pedb.nets:
                    self._logger.warning(
                        f"Net {net} used to find primitive from layer point and net not found, skipping it."
                    )
                else:
                    _nets.append(self._pedb.nets[net].net_obj)
            if _nets:
                nets = convert_py_list_to_net_list(_nets)
        _obj_instances = list(self._pedb.layout_instance.FindLayoutObjInstance(pt, None, nets).Items)
        returned_obj = []
        if layer:
            selected_prim = [
                obj.GetLayoutObj()
                for obj in _obj_instances
                if layer in [lay.GetName() for lay in list(obj.GetLayers())]
                and "Terminal" not in str(obj.GetLayoutObj())
            ]
            for prim in selected_prim:
                obj_id = prim.GetId()
                prim_type = str(prim.GetPrimitiveType())
                if prim_type == "Polygon":
                    [returned_obj.append(p) for p in [poly for poly in self.polygons if poly.id == obj_id]]
                elif prim_type == "Path":
                    [returned_obj.append(p) for p in [t for t in self.paths if t.id == obj_id]]
                elif prim_type == "Rectangle":
                    [returned_obj.append(p) for p in [t for t in self.rectangles if t.id == obj_id]]
        else:
            for obj in _obj_instances:
                obj_id = obj.GetLayoutObj().GetId()
                [returned_obj.append(p) for p in [obj for obj in self.primitives if obj.id == obj_id]]
        return returned_obj

    def get_polygon_bounding_box(self, polygon):
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
        bounding = []
        try:
            bounding_box = polygon.GetPolygonData().GetBBox()
            bounding = [
                bounding_box.Item1.X.ToDouble(),
                bounding_box.Item1.Y.ToDouble(),
                bounding_box.Item2.X.ToDouble(),
                bounding_box.Item2.Y.ToDouble(),
            ]
        except:
            pass
        return bounding

    def get_polygon_points(self, polygon):
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
                point = polygon.GetPolygonData().GetPoint(i)
                if prev_point != point:
                    if point.IsArc():
                        points.append([point.X.ToDouble()])
                    else:
                        points.append([point.X.ToDouble(), point.Y.ToDouble()])
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

        from pyedb.dotnet.database.edb_data.primitives_data import EdbPolygon

        if isinstance(selection_polygon, EdbPolygon):
            selection_polygon = selection_polygon._edb_object
        if isinstance(polygon, EdbPolygon):
            polygon = polygon._edb_object

        selection_polygon_data = selection_polygon.GetPolygonData()
        polygon_data = polygon.GetPolygonData()
        bound_center = polygon_data.GetBoundingCircleCenter()
        bound_center2 = selection_polygon_data.GetBoundingCircleCenter()
        center = [bound_center.X.ToDouble(), bound_center.Y.ToDouble()]
        center2 = [bound_center2.X.ToDouble(), bound_center2.Y.ToDouble()]
        x1, y1 = calc_slope(center2, center)

        if not origin:
            origin = [center[0] + float(x1) * 10000, center[1] + float(y1) * 10000]
        self._pedb.add_design_variable(offset_name, 0.0, is_parameter=True)
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = polygon_data.GetPoint(i)
                if prev_point != point:
                    check_inside = selection_polygon_data.PointInPolygon(point)
                    if check_inside:
                        xcoeff, ycoeff = calc_slope([point.X.ToDouble(), point.X.ToDouble()], origin)

                        new_points = self._pedb.point_data(
                            point.X.ToString() + "{}*{}".format(xcoeff, offset_name),
                            point.Y.ToString() + "{}*{}".format(ycoeff, offset_name),
                        )
                        polygon_data.SetPoint(i, new_points)
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        polygon.SetPolygonData(polygon_data)
        return True

    def _create_path(
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
        Create a path based on a list of points.

        Parameters
        ----------
        path_list : :class:`dotnet.database.layout.Shape`
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
            ``True`` when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if start_cap_style.lower() == "round":
            start_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Round
        elif start_cap_style.lower() == "extended":
            start_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Extended  # pragma: no cover
        else:
            start_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Flat  # pragma: no cover
        if end_cap_style.lower() == "round":
            end_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Round  # pragma: no cover
        elif end_cap_style.lower() == "extended":
            end_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Extended  # pragma: no cover
        else:
            end_cap_style = self._edb.cell.primitive.api.PathEndCapStyle.Flat
        if corner_style.lower() == "round":
            corner_style = self._edb.cell.primitive.api.PathCornerStyle.RoundCorner
        elif corner_style.lower() == "sharp":
            corner_style = self._edb.cell.primitive.api.PathCornerStyle.SharpCorner  # pragma: no cover
        else:
            corner_style = self._edb.cell.primitive.api.PathCornerStyle.MiterCorner  # pragma: no cover

        pointlists = [self._pedb.point_data(i[0], i[1]) for i in path_list.points]
        polygonData = self._edb.geometry.polygon_data.dotnetobj(convert_py_list_to_net_list(pointlists), False)
        polygon = self._edb.cell.primitive.path.create(
            self._active_layout,
            layer_name,
            net,
            self._get_edb_value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData,
        )

        if polygon.prim_obj.IsNull():  # pragma: no cover
            self._logger.error("Null path created")
            return False
        polygon = self._pedb.layout.find_object_by_id(polygon.prim_obj.GetId())
        return polygon

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
        path = self.Shape("Polygon", points=path_list)
        primitive = self._create_path(
            path,
            layer_name=layer_name,
            net_name=net_name,
            width=width,
            start_cap_style=start_cap_style,
            end_cap_style=end_cap_style,
            corner_style=corner_style,
        )

        return primitive

    def create_polygon(self, main_shape=None, layer_name="", voids=[], net_name="", points=None):
        """Create a polygon based on a list of points and voids.

        Parameters
        ----------
        main_shape : list of points or PolygonData or ``modeler.Shape``
            Shape or point lists of the main object. Point list can be in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.
            Each point can be:
            - [x, y] coordinate
            - [x, y, height] for an arc with specific height (between previous point and actual point)
            - [x, y, rotation, xc, yc] for an arc given a point, rotation and center.
        layer_name : str
            Name of the layer on which to create the polygon.
        voids : list, optional
            List of shape objects for voids or points that creates the shapes. The default is``[]``.
        net_name : str, optional
            Name of the net. The default is ``""``.
        points : list, optional
            Added for compatibility with grpc.

        Returns
        -------
        bool, :class:`dotnet.database.edb_data.primitives.Primitive`
            Polygon when successful, ``False`` when failed.
        """
        from pyedb.dotnet.database.geometry.polygon_data import PolygonData

        if main_shape:
            warnings.warn(
                "main_shape argument will be deprecated soon with grpc version, use points instead.", DeprecationWarning
            )

        net = self._pedb.nets.find_or_create_net(net_name)
        if points:
            arcs = []
            if isinstance(points, PolygonData):
                points = points.points
            for _ in range(len(points)):
                arcs.append(
                    self._edb.Geometry.ArcData(
                        self._pedb.point_data(0, 0),
                        self._pedb.point_data(0, 0),
                    )
                )
            polygonData = self._edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)

            for idx, i in enumerate(points):
                pdata_0 = self._pedb.edb_value(i[0])
                pdata_1 = self._pedb.edb_value(i[1])
                new_points = self._edb.Geometry.PointData(pdata_0, pdata_1)
                polygonData.SetPoint(idx, new_points)
        if isinstance(main_shape, list):
            arcs = []
            for _ in range(len(main_shape)):
                arcs.append(
                    self._edb.Geometry.ArcData(
                        self._pedb.point_data(0, 0),
                        self._pedb.point_data(0, 0),
                    )
                )
            polygonData = self._edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)

            for idx, i in enumerate(main_shape):
                pdata_0 = self._pedb.edb_value(i[0])
                pdata_1 = self._pedb.edb_value(i[1])
                new_points = self._edb.Geometry.PointData(pdata_0, pdata_1)
                polygonData.SetPoint(idx, new_points)

        elif isinstance(main_shape, Modeler.Shape):
            polygonData = self.shape_to_polygon_data(main_shape)
        else:
            if not points:
                polygonData = main_shape
        if isinstance(polygonData, PolygonData):
            if not polygonData.points:
                raise RuntimeError("Failed to create main shape polygon data")
        else:
            if polygonData.IsNull():
                raise RuntimeError("Failed to create main shape polygon data")
        for void in voids:
            if isinstance(void, list):
                void = self.Shape("polygon", points=void)
                voidPolygonData = self.shape_to_polygon_data(void)
            elif isinstance(void, Modeler.Shape):
                voidPolygonData = self.shape_to_polygon_data(void)
            else:
                voidPolygonData = void.polygon_data._edb_object

            if voidPolygonData is False or voidPolygonData is None or voidPolygonData.IsNull():
                self._logger.error("Failed to create void polygon data")
                return False
            polygonData.AddHole(voidPolygonData)
        if isinstance(polygonData, PolygonData):
            polygonData = polygonData._edb_object
        polygon = self._pedb._edb.Cell.Primitive.Polygon.Create(
            self._active_layout, layer_name, net.net_obj, polygonData
        )
        if polygon.IsNull() or polygonData is False:  # pragma: no cover
            self._logger.error("Null polygon created")
            return False
        else:
            return cast(polygon, self._pedb)

    def create_polygon_from_points(self, point_list, layer_name, net_name=""):
        """Create a new polygon from a point list.

        .. deprecated:: 0.6.73
        Use :func:`create_polygon` method instead. It now supports point lists as arguments.

        Parameters
        ----------
        point_list : list
            Point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.
            Each point can be:
            - [x,y] coordinate
            - [x,y, height] for an arc with specific height (between previous point and actual point)
            - [x,y, rotation, xc,yc] for an arc given a point, rotation and center.
        layer_name : str
            Name of layer on which create the polygon.
        net_name : str, optional
            Name of the net on which create the polygon.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
        """
        warnings.warn(
            "Use :func:`create_polygon` method instead. It now supports point lists as arguments.", DeprecationWarning
        )
        return self.create_polygon(point_list, layer_name, net_name=net_name)

    def create_rectangle(
        self,
        layer_name,
        net_name="",
        lower_left_point="",
        upper_right_point="",
        center_point="",
        width="",
        height="",
        representation_type="LowerLeftUpperRight",
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
            Lower left point when ``representation_type="LowerLeftUpperRight"``. The default is ``""``.
        upper_right_point : list
            Upper right point when ``representation_type="LowerLeftUpperRight"``. The default is ``""``.
        center_point : list
            Center point when ``representation_type="CenterWidthHeight"``. The default is ``""``.
        width : str
            Width of the rectangle when ``representation_type="CenterWidthHeight"``. The default is ``""``.
        height : str
            Height of the rectangle when ``representation_type="CenterWidthHeight"``. The default is ``""``.
        representation_type : str, optional
            Type of the rectangle representation. The default is ``LowerLeftUpperRight``. Options are
            ``"LowerLeftUpperRight"`` and ``"CenterWidthHeight"``.
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
        if representation_type == "LowerLeftUpperRight":
            rep_type = self._edb.cell.primitive.api.RectangleRepresentationType.LowerLeftUpperRight
            rect = self._edb.cell.primitive.rectangle.create(
                self._active_layout,
                layer_name,
                edb_net.net_obj,
                rep_type,
                self._get_edb_value(lower_left_point[0]),
                self._get_edb_value(lower_left_point[1]),
                self._get_edb_value(upper_right_point[0]),
                self._get_edb_value(upper_right_point[1]),
                self._get_edb_value(corner_radius),
                self._get_edb_value(rotation),
            )
        else:
            rep_type = self._edb.cell.primitive.api.RectangleRepresentationType.CenterWidthHeight
            rect = self._edb.cell.primitive.rectangle.create(
                self._active_layout,
                layer_name,
                edb_net.net_obj,
                rep_type,
                self._get_edb_value(center_point[0]),
                self._get_edb_value(center_point[1]),
                self._get_edb_value(width),
                self._get_edb_value(height),
                self._get_edb_value(corner_radius),
                self._get_edb_value(rotation),
            )
        if rect:
            return self._pedb.layout.find_object_by_id(rect._edb_object.GetId())
        return False  # pragma: no cover

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

        circle = self._edb.cell.primitive.circle.create(
            self._active_layout,
            layer_name,
            edb_net,
            self._get_edb_value(x),
            self._get_edb_value(y),
            self._get_edb_value(radius),
        )
        if circle:
            return self._pedb.layout.find_object_by_id(circle._edb_object.GetId())
        return False  # pragma: no cover

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
            if not el.type:
                continue
            if net_name:
                if not el.net_name == net_name:
                    continue
            if layer_name:
                if not el.layer_name == layer_name:
                    continue
            if prim_type:
                if not el.type == prim_type:
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
            (
                res,
                center_x,
                center_y,
                radius,
            ) = void_circle.primitive_object.GetParameters()

            cloned_circle = self._edb.cell.primitive.circle.create(
                self._active_layout,
                void_circle.layer_name,
                void_circle.net,
                self._get_edb_value(center_x),
                self._get_edb_value(center_y),
                self._get_edb_value(radius),
            )
            if res:
                cloned_circle.SetIsNegative(True)
                void_circle.Delete()
        return True

    def add_void(self, shape, void_shape):
        """Add a void into a shape.

        Parameters
        ----------
        shape : Polygon
            Shape of the main object.
        void_shape : list, Path
            Shape of the voids.
        """
        flag = False
        if isinstance(shape, Primitive):
            shape = shape.primitive_object
        if not isinstance(void_shape, list):
            void_shape = [void_shape]
        for void in void_shape:
            if isinstance(void, Primitive):
                flag = shape.AddVoid(void.primitive_object)
            else:
                flag = shape.AddVoid(void)
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
            startPoint = [self._get_edb_value(i) for i in startPoint]
            endPoint = [self._get_edb_value(i) for i in endPoint]
            if len(endPoint) == 2:
                is_parametric = (
                    is_parametric
                    or startPoint[0].IsParametric()
                    or startPoint[1].IsParametric()
                    or endPoint[0].IsParametric()
                    or endPoint[1].IsParametric()
                )
                arc = self._edb.geometry.arc_data(
                    self._pedb.point_data(startPoint[0].ToDouble(), startPoint[1].ToDouble()),
                    self._pedb.point_data(endPoint[0].ToDouble(), endPoint[1].ToDouble()),
                )
                arcs.append(arc)
            elif len(endPoint) == 3:
                is_parametric = (
                    is_parametric
                    or startPoint[0].IsParametric()
                    or startPoint[1].IsParametric()
                    or endPoint[0].IsParametric()
                    or endPoint[1].IsParametric()
                    or endPoint[2].IsParametric()
                )
                arc = self._edb.geometry.arc_data(
                    self._pedb.point_data(startPoint[0].ToDouble(), startPoint[1].ToDouble()),
                    self._pedb.point_data(endPoint[0].ToDouble(), endPoint[1].ToDouble()),
                    endPoint[2].ToDouble(),
                )
                arcs.append(arc)
            elif len(endPoint) == 5:
                is_parametric = (
                    is_parametric
                    or startPoint[0].IsParametric()
                    or startPoint[1].IsParametric()
                    or endPoint[0].IsParametric()
                    or endPoint[1].IsParametric()
                    or endPoint[3].IsParametric()
                    or endPoint[4].IsParametric()
                )
                rotationDirection = self._edb.geometry.geometry.RotationDirection.Colinear
                if endPoint[2].ToString() == "cw":
                    rotationDirection = self._edb.geometry.geometry.RotationDirection.CW
                elif endPoint[2].ToString() == "ccw":
                    rotationDirection = self._edb.geometry.geometry.RotationDirection.CCW
                else:
                    self._logger.error("Invalid rotation direction %s is specified.", endPoint[2])
                    return None
                arc = self._edb.geometry.arc_data(
                    self._pedb.point_data(startPoint[0].ToDouble(), startPoint[1].ToDouble()),
                    self._pedb.point_data(endPoint[0].ToDouble(), endPoint[1].ToDouble()),
                    rotationDirection,
                    self._pedb.point_data(endPoint[3].ToDouble(), endPoint[4].ToDouble()),
                )
                arcs.append(arc)
        polygon = self._edb.geometry.polygon_data.create_from_arcs(arcs, True)
        if not is_parametric:
            return polygon
        else:
            k = 0
            for pt in points:
                point = [self._get_edb_value(i) for i in pt]
                new_points = self._edb.geometry.point_data(point[0], point[1])
                if len(point) > 2:
                    k += 1
                polygon.SetPoint(k, new_points)
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
        if not self._validatePoint(shape.pointA, False) or not self._validatePoint(shape.pointB, False):
            return None
        pointA = self._edb.geometry.point_data(
            self._get_edb_value(shape.pointA[0]), self._get_edb_value(shape.pointA[1])
        )
        pointB = self._edb.geometry.point_data(
            self._get_edb_value(shape.pointB[0]), self._get_edb_value(shape.pointB[1])
        )
        return self._edb.geometry.polygon_data.create_from_bbox((pointA, pointB))

    class Shape(object):
        """Shape class.

        Parameters
        ----------
        type : str, optional
            Type of the shape. Options are ``"circle"``, ``"rectangle"``, and ``"polygon"``.
            The default is ``"unknown``.
        pointA : optional
            Lower-left corner when ``type="rectangle"``. The default is ``None``.
        pointB : optional
            Upper-right corner when ``type="rectangle"``. The default is ``None``.
        centerPoint : optional
            Center point when ``type="circle"``. The default is ``None``.
        radius : optional
            Radius when ``type="circle"``. The default is ``None``.
        points : list, optional
            List of points when ``type="polygon"``. The default is ``None``.
        properties : dict, optional
            Dictionary of properties associated with the shape. The default is ``{}``.
        """

        def __init__(
            self,
            type="unknown",  # noqa
            pointA=None,
            pointB=None,
            centerPoint=None,
            radius=None,
            points=None,
            properties={},
        ):  # noqa
            self.type = type
            self.pointA = pointA
            self.pointB = pointB
            self.centerPoint = centerPoint
            self.radius = radius
            self.points = points
            self.properties = properties

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
            var_server = False
            for p in self.paths:
                if p.net.name == net_name:
                    if not layers_name:
                        if not var_server:
                            if not variable_value:
                                variable_value = p.width
                            result, var_server = self._pedb.add_design_variable(
                                parameter_name, variable_value, is_parameter=True
                            )
                        p.width = self._pedb.edb_value(parameter_name)
                    elif p.layer.name in layers_name:
                        if not var_server:
                            if not variable_value:
                                variable_value = p.width
                            result, var_server = self._pedb.add_design_variable(
                                parameter_name, variable_value, is_parameter=True
                            )
                        p.width = self._pedb.edb_value(parameter_name)
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
            self._logger.info("Uniting Objects on layer %s.", lay)
            poly_by_nets = {}
            all_voids = []
            list_polygon_data = []
            delete_list = []
            if lay in list(self.polygons_by_layer.keys()):
                for poly in self.polygons_by_layer[lay]:
                    poly = poly._edb_object
                    if not poly.GetNet().GetName() in list(poly_by_nets.keys()):
                        if poly.GetNet().GetName():
                            poly_by_nets[poly.GetNet().GetName()] = [poly]
                    else:
                        if poly.GetNet().GetName():
                            poly_by_nets[poly.GetNet().GetName()].append(poly)
            for net in poly_by_nets:
                if net in net_names_list or not net_names_list:
                    for i in poly_by_nets[net]:
                        list_polygon_data.append(i.GetPolygonData())
                        delete_list.append(i)
                        all_voids.append(i.Voids)
            a = self._edb.geometry.polygon_data.unite(convert_py_list_to_net_list(list_polygon_data))
            for item in a:
                for v in all_voids:
                    for void in v:
                        if int(item.GetIntersectionType(void.GetPolygonData())) == 2:
                            item.AddHole(void.GetPolygonData())
                self.create_polygon(item, layer_name=lay, voids=[], net_name=net)
            for v in all_voids:
                for void in v:
                    for poly in poly_by_nets[net]:  # pragma no cover
                        if int(void.GetPolygonData().GetIntersectionType(poly.GetPolygonData())) >= 2:
                            try:
                                id = delete_list.index(poly)
                            except ValueError:
                                id = -1
                            if id >= 0:
                                delete_list.pop(id)
            for poly in delete_list:
                poly.Delete()

        if delete_padstack_gemometries:
            self._logger.info("Deleting Padstack Definitions")
            for pad in self._pedb.padstacks.definitions:
                p1 = self._pedb.padstacks.definitions[pad].edb_padstack.GetData()
                if len(p1.GetLayerNames()) > 1:
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
        poly_data = poly.polygon_data
        new_poly = poly_data._edb_object.Defeature(tolerance)
        poly._edb_object.SetPolygonData(new_poly)
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
        stat_model = EDBStatistics()
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
                        if prim.type == "Path":
                            surface += prim.length * prim.width
                        if prim.type == "Polygon":
                            surface += prim.polygon_data._edb_object.Area()
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
        bondwire_type="jedec4",
        start_cell_instance_name=None,
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
        start_cell_instance_name : None
            Added for grpc compatibility.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.primitive.BondwireDotNet`
            Bondwire object created.
        """
        if start_cell_instance_name:
            self._pedb.logger.warning(f"start_cell_instance_name {start_cell_instance_name} is only valid with grpc.")
        return Bondwire(
            pedb=self._pedb,
            bondwire_type=bondwire_type,
            definition_name=definition_name,
            placement_layer=placement_layer,
            width=self._pedb.edb_value(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=self._pedb.edb_value(start_x),
            start_y=self._pedb.edb_value(start_y),
            end_layer_name=end_layer_name,
            end_x=self._pedb.edb_value(end_x),
            end_y=self._pedb.edb_value(end_y),
            net=self._pedb.nets[net]._edb_object,
        )

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
        pins = {}
        if pins_by_id:
            if isinstance(pins_by_id, int):
                pins_by_id = [pins_by_id]
            for p in pins_by_id:
                edb_pin = self._pedb.layout.find_object_by_id(p)
                if edb_pin and not p in pins:
                    pins[p] = edb_pin._edb_object
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
                pin.id: pin._edb_object
                for pin in p_inst
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
        obj = self._edb.cell.hierarchy.pin_group.Create(
            self._pedb.active_layout, name, convert_py_list_to_net_list(pins)
        )
        if obj.IsNull():
            raise RuntimeError(f"Failed to create pin group {name}.")
        else:
            net_obj = [i.GetNet() for i in pins if not i.GetNet().IsNull()]
            if net_obj:
                obj.SetNet(net_obj[0])
        return self._pedb.siwave.pin_groups[name]

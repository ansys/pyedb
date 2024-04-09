"""
This module contains these classes: `EdbLayout` and `Shape`.
"""
import math
import warnings

import ansys.edb.core.geometry as geometry
import ansys.edb.core.geometry.arc_data as arcdata
import ansys.edb.core.primitive as primitive
from ansys.edb.core.primitive import Bondwire
import ansys.edb.core.utility as utility

# from ansys.edb.geometry.point_data import PointData
# from ansys.edb.geometry.polygon_data import PolygonData
# from ansys.edb.geometry.arc_data import ArcData
from pyedb.generic.general_methods import pyedb_function_handler

# from ansys.edb.primitive import Circle
# from ansys.edb.primitive import Path
# from ansys.edb.primitive import Polygon
# from ansys.edb.primitive import Rectangle
from pyedb.grpc.edb_core.edb_data.primitives_data import EDBPrimitives, cast
from pyedb.grpc.edb_core.edb_data.utilities import EDBStatistics

# from ansys.edb.primitive.primitive import PathEndCapType, PathCornerType
# from ansys.edb.utility.value import Value
# from ansys.edb.primitive.primitive import RectangleRepresentationType
# from ansys.edb.geometry.arc_data import RotationDirection


class EdbLayout(object):
    """Manages EDB methods for primitives management accessible from `Edb.modeler` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.modeler
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _edb(self):
        return self._pedb

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _edbutils(self):
        return self._pedb.edbutils

    @property
    def _active_layout(self):
        return self._layout

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

    @property
    def primitives(self):
        """Primitives.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of primitives.
        """
        _prims = []
        if self._layout:
            for lay_obj in self._layout.primitives:
                _prims.append(cast(lay_obj, self._pedb))
        return _prims

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
        for i in self._layout.primitives:
            lay = i.layer.name
            if not lay:
                continue
            _primitives_by_layer[lay].append(cast(i, self._pedb))
        return _primitives_by_layer

    @property
    def rectangles(self):
        """Rectangles.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of rectangles.

        """
        return [prim for prim in self.primitives if prim.type == "Rectangle"]

    @property
    def circles(self):
        """Circles.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of circles.

        """
        return [prim for prim in self.primitives if prim.type == "Circle"]

    @property
    def paths(self):
        """Paths.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of paths.
        """
        return [prim for prim in self.primitives if prim.type == "Path"]

    @property
    def bondwires(self):
        """Bondwires.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of bondwires.
        """
        return [prim for prim in self.primitives if prim.type == "Bondwire"]

    @property
    def polygons(self):
        """Polygons.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            List of polygons.
        """
        return [prim for prim in self.primitives if prim.type == "Polygon"]

    @pyedb_function_handler()
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

    @pyedb_function_handler()
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
        >>> poly = edb_core.modeler.get_polygons_by_layer("GND")
        >>> bounding = edb_core.modeler.get_polygon_bounding_box(poly[0])
        """
        bounding = []
        try:
            bounding_box = polygon.polygon_data().bbox
            bounding = [
                bounding_box[0].x.value,
                bounding_box[0].y.value,
                bounding_box[1].x.value,
                bounding_box[1].y.value,
            ]
        except:
            pass
        return bounding

    @pyedb_function_handler()
    def get_polygon_points(self, polygon):
        """Retrieve polygon points.

        .. note::
           For arcs, one point is returned.

        Parameters
        ----------
        polygon :
            class: `pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`

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

        >>> poly = edb_core.modeler.get_polygons_by_layer("GND")
        >>> points  = edb_core.modeler.get_polygon_points(poly[0])

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

    @pyedb_function_handler()
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
        bound_center = polygon_data.bounding_circle()
        bound_center2 = selection_polygon_data.bounding_circle()
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
                    check_inside = selection_polygon_data.in_polygon(point)
                    if check_inside:
                        xcoeff, ycoeff = calc_slope([point.x.value, point.x.value], origin)

                        new_points = (
                            str(point.x.value) + "{}*{}".format(xcoeff, offset_name),
                            str(point.y.value) + "{}*{}".format(ycoeff, offset_name),
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

    @pyedb_function_handler()
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
        path_list : :class:`pyaedt.edb_core.layout.Shape`
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
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            ``True`` when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if start_cap_style.lower() == "round":
            start_cap_style = primitive.PathEndCapType.ROUND
        elif start_cap_style.lower() == "extended":
            start_cap_style = primitive.PathEndCapType.EXTENDED
        else:
            start_cap_style = primitive.PathEndCapType.FLAT
        if end_cap_style.lower() == "round":
            end_cap_style = primitive.PathEndCapType.ROUND
        elif end_cap_style.lower() == "extended":
            end_cap_style = primitive.PathEndCapType.EXTENDED
        else:
            end_cap_style = primitive.PathEndCapType.FLAT
        if corner_style.lower() == "round":
            corner_style = primitive.PathCornerType.ROUND
        elif corner_style.lower() == "sharp":
            corner_style = primitive.PathCornerType.SHARP
        else:
            corner_style = primitive.PathCornerType.MITER

        pointlists = [geometry.PointData(i[0], i[1]) for i in path_list.points]
        polygonData = geometry.PolygonData(pointlists, False)
        polygon = primitive.Path.create(
            self._active_layout,
            layer_name,
            net,
            utility.Value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData,
        )
        if polygon.is_null:  # pragma: no cover
            self._logger.error("Null path created")
            return False
        return cast(polygon, self._pedb)

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
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

    @pyedb_function_handler()
    def create_polygon(self, main_shape, layer_name, voids=[], net_name=""):
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

        Returns
        -------
        bool, :class:`pyaedt.edb_core.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if isinstance(main_shape, list):
            arcs = []
            for _ in range(len(main_shape)):
                arcs.append(geometry.ArcData(geometry.PointData(), geometry.PointData()))
            polygonData = geometry.PolygonData(arcs, False)

            for idx, i in enumerate(main_shape):
                pdata_0 = utility.Value(i[0])
                pdata_1 = utility.Value(i[1])
                new_points = geometry.PointData(pdata_0, pdata_1)
                polygonData.points[idx] = new_points

        elif isinstance(main_shape, EdbLayout.Shape):
            polygonData = self.shape_to_polygon_data(main_shape)
        else:
            polygonData = main_shape
        if polygonData is False or polygonData is None or polygonData.is_null:
            self._logger.error("Failed to create main shape polygon data")
            return False
        for void in voids:
            if isinstance(void, list):
                void = self.Shape("polygon", points=void)
                voidPolygonData = self.shape_to_polygon_data(void)
            elif isinstance(void, EdbLayout.Shape):
                voidPolygonData = self.shape_to_polygon_data(void)
            else:
                voidPolygonData = void
            if voidPolygonData is False or voidPolygonData is None or voidPolygonData.is_null:
                self._logger.error("Failed to create void polygon data")
                return False
            polygonData.holes.append(voidPolygonData)
        polygon = primitive.Polygon.create(self._active_layout, layer_name, net, polygonData)
        if polygon.is_null or polygonData is False:  # pragma: no cover
            self._logger.error("Null polygon created")
            return False
        else:
            return cast(polygon, self._pedb)

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        warnings.warn(
            "Use :func:`create_polygon` method instead. It now supports point lists as arguments.", DeprecationWarning
        )
        return self.create_polygon(point_list, layer_name, net_name=net_name)

    @pyedb_function_handler()
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
         :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            Rectangle when successful, ``False`` when failed.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)
        if representation_type == "LowerLeftUpperRight":
            rep_type = primitive.RectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT
            rect = primitive.Rectangle.create(
                self._active_layout,
                layer_name,
                edb_net.net_obj,
                rep_type,
                utility.Value(lower_left_point[0]),
                utility.Value(lower_left_point[1]),
                utility.Value(upper_right_point[0]),
                utility.Value(upper_right_point[1]),
                utility.Value(corner_radius),
                utility.Value(rotation),
            )
        else:
            rep_type = primitive.RectangleRepresentationType.CENTER_WIDTH_HEIGHT
            rect = primitive.Rectangle.create(
                self._active_layout,
                layer_name,
                edb_net.net_obj,
                rep_type,
                utility.Value(center_point[0]),
                utility.Value(center_point[1]),
                utility.Value(width),
                utility.Value(height),
                utility.Value(corner_radius),
                utility.Value(rotation),
            )
        if rect:
            return cast(rect, self._pedb)
        return False  # pragma: no cover

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
            Objects of the circle created when successful.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)

        circle = primitive.Circle.create(
            self._active_layout,
            layer_name,
            edb_net,
            utility.Value(x),
            utility.Value(y),
            utility.Value(radius),
        )
        if circle:
            return cast(circle, self._pedb)
        return False  # pragma: no cover

    @pyedb_function_handler
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

    @pyedb_function_handler()
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

    @pyedb_function_handler()
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
            ) = void_circle.primitive_object.get_parameters()

            cloned_circle = primitive.Circle.create(
                self._active_layout,
                void_circle.layer_name,
                void_circle.net,
                utility.Value(center_x),
                utility.Value(center_y),
                utility.Value(radius),
            )
            if res:
                cloned_circle.is_negative = True
                void_circle.delete()
        return True

    @pyedb_function_handler()
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
        if isinstance(shape, EDBPrimitives):
            shape = shape.primitive_object
        if not isinstance(void_shape, list):
            void_shape = [void_shape]
        for void in void_shape:
            if isinstance(void, EDBPrimitives):
                flag = shape.add_void(void.primitive_object)
            else:
                flag = shape.add_void(void)
            if not flag:
                return flag
        return True

    @pyedb_function_handler()
    def shape_to_polygon_data(self, shape):
        """Convert a shape to polygon data.

        Parameters
        ----------
        shape : :class:`pyaedt.edb_core.layout.EdbLayout.Shape`
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

    @pyedb_function_handler()
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
            startPoint = [utility.Value(i) for i in startPoint]
            endPoint = [utility.Value(i) for i in endPoint]
            if len(endPoint) == 2:
                is_parametric = (
                    is_parametric
                    or startPoint[0].is_parametric
                    or startPoint[1].is_parametric
                    or endPoint[0].is_parametric
                    or endPoint[1].is_parametric
                )
                arc = geometry.ArcData(
                    geometry.PointData(startPoint[0].value, startPoint[1].value),
                    geometry.PointData(endPoint[0].value, endPoint[1].value),
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
                arc = geometry.ArcData(
                    geometry.PointData(startPoint[0].value, startPoint[1].value),
                    geometry.PointData(endPoint[0].value, endPoint[1].value, endPoint[2].value),
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
                rotationDirection = arcdata.RotationDirection.CO_LINEAR
                if str(endPoint[2].value) == "cw":
                    rotationDirection = arcdata.RotationDirection.CW
                elif str(endPoint[2].value) == "ccw":
                    rotationDirection = arcdata.RotationDirection.CCW
                else:
                    self._logger.error("Invalid rotation direction %s is specified.", endPoint[2])
                    return None
                arc = geometry.ArcData(
                    geometry.PointData(startPoint[0].value, startPoint[1].value),
                    geometry.PointData(endPoint[0].value, endPoint[1].value),
                    rotationDirection,
                    geometry.PointData(endPoint[3].value, endPoint[4].value),
                )
                arcs.append(arc)
        polygon = geometry.PolygonData(arcs, True)
        if not is_parametric:
            return polygon
        else:
            k = 0
            for pt in points:
                point = [utility.Value(i) for i in pt]
                new_points = geometry.PointData(point[0], point[1])
                if len(point) > 2:
                    k += 1
                polygon.points[k] = new_points
                k += 1
        return polygon

    @pyedb_function_handler()
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
        pointA = geometry.PointData(utility.Value(shape.pointA[0]), utility.Value(shape.pointA[1]))
        pointB = geometry.PointData(utility.Value(shape.pointB[0]), utility.Value(shape.pointB[1]))
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

    @pyedb_function_handler()
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
        for net in nets_name:
            selected_paths = [p for p in self.paths if p.net_name == net]
            ind = 0
            for path in selected_paths:
                parameter_name = f"{net}_{str(ind)}"
                if not layers_name:
                    variable_value = path.width
                    param = self._pedb.add_design_variable(parameter_name, variable_value, is_parameter=True)
                    path.width = param
                elif path.layer.name in layers_name:
                    variable_value = path.width
                    param = self._pedb.add_design_variable(parameter_name, variable_value, is_parameter=True)
                    path.width = param
                ind += 1
        return True

    @pyedb_function_handler()
    def unite_polygons_on_layer(self, layer_name=None, delete_padstack_gemometries=False):
        """Try to unite all Polygons on specified layer.

        Parameters
        ----------
        layer_name : str, optional
            Layer Name on which unite objects. If ``None``, all layers will be taken.
        delete_padstack_gemometries : bool, optional
            ``True`` to delete all padstack geometry.

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
            if lay in list(self.polygons_by_layer.keys()):
                for poly in self.polygons_by_layer[lay]:
                    if not poly.net.name in list(poly_by_nets.keys()):
                        if poly.net.name:
                            poly_by_nets[poly.net.name] = [poly]
                    else:
                        if poly.net.name:
                            poly_by_nets[poly.net.name].append(poly)
            for net in poly_by_nets:
                list_polygon_data = [i.polygon_data() for i in poly_by_nets[net]]
                all_voids = [i.voids for i in poly_by_nets[net]]
                a = geometry.PolygonData.unite(list_polygon_data)
                for item in a:
                    for v in all_voids:
                        for void in v:
                            if int(item.intersection_type(void.polygon_data)) == 2:
                                item.add_hole(void.polygon_data)
                    poly = primitive.Polygon.create(self._active_layout, lay, self._pedb.nets.nets[net], item)
                list_to_delete = [i for i in poly_by_nets[net]]
                for v in all_voids:
                    for void in v:
                        for poly in poly_by_nets[net]:
                            if int(void.polygon_data.intersection_type(poly.polygon_data)) >= 2:
                                try:
                                    id = list_to_delete.index(poly)
                                except ValueError:
                                    id = -1
                                if id >= 0:
                                    list_to_delete.pop(id)

                [i.Delete() for i in list_to_delete]

        if delete_padstack_gemometries:
            self._logger.info("Deleting Padstack Definitions")
            for pad in self._pedb.padstacks.definitions:
                p1 = self._pedb.padstacks.definitions[pad].edb_padstack.data
                if len(p1.layer_names) > 1:
                    self._pedb.padstacks.remove_pads_from_padstack(pad)
        return True

    @pyedb_function_handler()
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
        new_poly = poly_data.defeature(tolerance)
        poly.polygon_data = new_poly
        return True

    @pyedb_function_handler()
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
        stat_model.num_layers = len(list(self._pedb.stackup.stackup_layers.values()))
        stat_model.num_capacitors = len(self._pedb.components.capacitors)
        stat_model.num_resistors = len(self._pedb.components.resistors)
        stat_model.num_inductors = len(self._pedb.components.inductors)
        bbox = self._pedb._hfss.get_layout_bounding_box(self._active_layout)
        stat_model._layout_size = bbox[2] - bbox[0], bbox[3] - bbox[1]
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
        stat_model.stackup_thickness = self._pedb.stackup.get_layout_thickness()
        if evaluate_area:
            if net_list:
                netlist = list(self._pedb.nets.nets.keys())
                _poly = self._pedb.get_conformal_polygon_from_netlist(netlist)
            else:
                _poly = self._pedb.get_conformal_polygon_from_netlist()
            stat_model.occupying_surface = _poly.area
            outline_surface = stat_model.layout_size[0] * stat_model.layout_size[1]
            stat_model.occupying_ratio = stat_model.occupying_surface / outline_surface
        return stat_model

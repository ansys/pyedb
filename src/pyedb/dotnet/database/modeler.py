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

import math
import warnings

from pyedb.dotnet.clr_module import Tuple
from pyedb.dotnet.database.cell.primitive.bondwire import Bondwire
from pyedb.dotnet.database.dotnet.primitive import CircleDotNet, PathDotNet, RectangleDotNet
from pyedb.dotnet.database.edb_data.primitives_data import EdbPolygon, Primitive, cast
from pyedb.dotnet.database.edb_data.utilities import EDBStatistics
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.misc.decorators import deprecate_argument_name, deprecated, deprecated_property


class Modeler:
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
        raise ValueError(f"Primitive {name} not found.")

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    @deprecated_property("use layout.primitives property instead.")
    def primitives(self):
        """Primitives.

        .. deprecated:: 0.70.0
           Use layout.primitives instead.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives.
        """
        return self._pedb.layout.primitives

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
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Round
        elif start_cap_style.lower() == "extended":
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Extended  # pragma: no cover
        else:
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Flat  # pragma: no cover
        if end_cap_style.lower() == "round":
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Round  # pragma: no cover
        elif end_cap_style.lower() == "extended":
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Extended  # pragma: no cover
        else:
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Flat
        if corner_style.lower() == "round":
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.RoundCorner
        elif corner_style.lower() == "sharp":
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.SharpCorner  # pragma: no cover
        else:
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.MiterCorner  # pragma: no cover

        pointlists = [self._pedb.point_data(i[0], i[1]) for i in path_list.points]
        polygonData = self._edb.Geometry.PolygonData(convert_py_list_to_net_list(pointlists), False)
        polygon = self._edb.Cell.Primitive.Path.Create(
            self._active_layout,
            layer_name,
            net._edb_object,
            self._get_edb_value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData,
        )

        if polygon.IsNull():  # pragma: no cover
            raise RuntimeError("Failed to create path.")
        polygon = self._pedb.layout.find_object_by_id(polygon.GetId())
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

    @deprecate_argument_name({"main_shape": "points"})
    def create_polygon(
        self,
        points=None,
        layer_name="",
        voids=[],
        net_name="",
    ):
        """Create a polygon based on a list of points and voids.

        Parameters
        ----------
        points : list of points or PolygonData or ``modeler.Shape``
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
        bool, :class:`dotnet.database.edb_data.primitives.Primitive`
            Polygon when successful, ``False`` when failed.
        """
        from pyedb.dotnet.database.geometry.polygon_data import PolygonData

        net = self._pedb.nets.find_or_create_net(net_name)

        if isinstance(points, list):
            arcs = []
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

        elif isinstance(points, Modeler.Shape):
            polygonData = self.shape_to_polygon_data(points)
        else:
            polygonData = points
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
            if isinstance(polygonData, PolygonData):
                polygonData = polygonData._edb_object
            polygonData.AddHole(voidPolygonData)
        if isinstance(polygonData, PolygonData):
            polygonData = polygonData._edb_object
        polygon = self._pedb._edb.Cell.Primitive.Polygon.Create(
            self._active_layout, layer_name, net._edb_object, polygonData
        )
        if polygon.IsNull() or polygonData is False:  # pragma: no cover
            raise RuntimeError("Null polygon created")
        else:
            return cast(polygon, self._pedb)

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
            rep_type = self._edb.Cell.Primitive.RectangleRepresentationType.LowerLeftUpperRight
            rect = self._edb.Cell.Primitive.Rectangle.Create(
                self._active_layout,
                layer_name,
                edb_net._edb_object,
                rep_type,
                self._get_edb_value(lower_left_point[0]),
                self._get_edb_value(lower_left_point[1]),
                self._get_edb_value(upper_right_point[0]),
                self._get_edb_value(upper_right_point[1]),
                self._get_edb_value(corner_radius),
                self._get_edb_value(rotation),
            )
        else:
            rep_type = self._edb.Cell.Primitive.RectangleRepresentationType.CenterWidthHeight
            rect = self._edb.Cell.Primitive.Rectangle.Create(
                self._active_layout,
                layer_name,
                edb_net._edb_object,
                rep_type,
                self._get_edb_value(center_point[0]),
                self._get_edb_value(center_point[1]),
                self._get_edb_value(width),
                self._get_edb_value(height),
                self._get_edb_value(corner_radius),
                self._get_edb_value(rotation),
            )
        if not rect.IsNull():
            return self._pedb.layout.find_object_by_id(rect.GetId())
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

        circle = self._edb.Cell.Primitive.Circle.Create(
            self._active_layout,
            layer_name,
            edb_net._edb_object,
            self._get_edb_value(x),
            self._get_edb_value(y),
            self._get_edb_value(radius),
        )
        if not circle.IsNull():
            return self._pedb.layout.find_object_by_id(circle.GetId())
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

            cloned_circle = self._edb.Cell.Primitive.Circle.Create(
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
                arc = self._edb.Geometry.ArcData(
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
                arc = self._edb.Geometry.Arc_data(
                    self._pedb.point_data(startPoint[0].ToDouble(), startPoint[1].ToDouble()),
                    self._pedb.point_data(endPoint[0].ToDouble(), endPoint[1].ToDouble()),
                    # endPoint[2].ToDouble(),  # This argument is never used in the original code. There might be a bug.
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
                if endPoint[2].ToString() == "cw":
                    rotationDirection = self._edb.geometry.geometry.RotationDirection.CW
                elif endPoint[2].ToString() == "ccw":
                    rotationDirection = self._edb.geometry.geometry.RotationDirection.CCW
                else:
                    raise ValueError("Invalid rotation direction %s is specified.", endPoint[2])
                arc = self._edb.Geometry.ArcData(
                    self._pedb.point_data(startPoint[0].ToDouble(), startPoint[1].ToDouble()),
                    self._pedb.point_data(endPoint[0].ToDouble(), endPoint[1].ToDouble()),
                    rotationDirection,
                    self._pedb.point_data(endPoint[3].ToDouble(), endPoint[4].ToDouble()),
                )
                arcs.append(arc)
        polygon = self._edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)
        if not is_parametric:
            return polygon
        else:
            k = 0
            for pt in points:
                point = [self._get_edb_value(i) for i in pt]
                new_points = self._edb.Geometry.PointData(point[0], point[1])
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
        pointA = self._edb.Geometry.PointData(
            self._get_edb_value(shape.pointA[0]), self._get_edb_value(shape.pointA[1])
        )
        pointB = self._edb.Geometry.PointData(
            self._get_edb_value(shape.pointB[0]), self._get_edb_value(shape.pointB[1])
        )
        points = Tuple[self._pedb.core.Geometry.PointData, self._pedb.core.Geometry.PointData](pointA, pointB)
        return self._edb.Geometry.PolygonData.CreateFromBBox(points)

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
                            _, var_server = self._pedb.add_design_variable(
                                parameter_name, variable_value, is_parameter=True
                            )
                        p.width = self._pedb.edb_value(parameter_name)
                    elif p.layer.name in layers_name:
                        if not var_server:
                            if not variable_value:
                                variable_value = p.width
                            _, var_server = self._pedb.add_design_variable(
                                parameter_name, variable_value, is_parameter=True
                            )
                        p.width = self._pedb.edb_value(parameter_name)
        return True

    def unite_polygons_on_layer(self, layer_name=None, delete_padstack_gemometries=False, net_names_list=None):
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

        def unite_polygons(polygons: list):
            """Unite a list of polygons.

            Parameters
            ----------
            polygons
            """
            if len(polygons) < 2:
                raise ValueError("At least two polygons are required to unite.")
            layer = set([i.layer_name for i in polygons])
            if len(layer) > 1:
                raise ValueError("Polygons must be on the same layer.")
            layer = list(layer)[0]

            new_polygon_data = self._pedb.core.Geometry.PolygonData.Unite(
                convert_py_list_to_net_list([i.polygon_data._edb_object for i in polygons])
            )
            voids = []
            for i in polygons:
                voids.extend(i.voids)

            new_polygons = []
            for pdata in new_polygon_data:
                voids_ = [i for i in voids if int(pdata.GetIntersectionType(i.polygon_data._edb_object)) == 2]

                new_polygons.append(self.create_polygon(pdata, layer, voids_, polygons[0].net_name))

            for i in polygons:
                i.delete()
            return new_polygons

        if not layer_name:
            layers = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layers = [layer_name]
        else:
            layers = layer_name

        for layer in layers:
            self._logger.info("Uniting Objects on layer %s.", layer)
            if net_names_list:
                polygons = [
                    i
                    for i in self._pedb.layout.find_primitive(layer_name=layer, net_name=net_names_list)
                    if i.primitive_type == "polygon"
                ]
            else:
                polygons = [
                    i for i in self._pedb.layout.find_primitive(layer_name=layer) if i.primitive_type == "polygon"
                ]
            if len(polygons) > 1:
                unite_polygons(polygons)

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

    def get_layout_statistics(self, evaluate_area=False, net_list=False) -> EDBStatistics:
        """Return EDBStatistics object from a layout.

        Parameters
        ----------

        evaluate_area : optional bool
            When True evaluates the layout metal surface, can take time-consuming,
            avoid using this option on large design.
        net_list: optional bool
            list of net names to evaluate area for, if None all nets will be evaluated.
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
        ----------
        name : str
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
                    if id not in pins:
                        pins[id] = pin
        if not pins:
            self._logger.error("No pin found.")
            return False
        pins = list(pins.values())
        obj = self._edb.Cell.Hierarchy.PinGroup.Create(
            self._pedb.active_layout, name, convert_py_list_to_net_list(pins)
        )
        if obj.IsNull():
            raise RuntimeError(f"Failed to create pin group {name}.")
        else:
            net_obj = [i.GetNet() for i in pins if not i.GetNet().IsNull()]
            if net_obj:
                obj.SetNet(net_obj[0])
        return self._pedb.siwave.pin_groups[name]

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
    @deprecated_property("use stackup.layers property instead.")
    def layers(self):
        """Dictionary of layers.

        .. deprecated:: 0.70.0
           Use stackup.layers instead.

        Returns
        -------
        dict
            Dictionary of layers.
        """
        return self._pedb.stackup.layers

    @deprecated("Use layout.find_object_by_id method instead.")
    def get_primitive(self, primitive_id):
        """Retrieve primitive from give id.

        .. deprecated:: 0.70.0
           Use layout.find_object_by_id method instead.

        Parameters
        ----------
        primitive_id : int
            Primitive id.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of primitives.
        """
        return self._pedb.layout.find_object_by_id(primitive_id)

    @property
    @deprecated_property("use layout.polygons_by_layer property instead.")
    def polygons_by_layer(self) -> dict[str, list[EdbPolygon]]:
        """Primitives with layer names as keys.

        .. deprecated:: 0.70.0
           Use layout.polygons_by_layer instead.

        Returns
        -------
        dict
            Dictionary of primitives with layer names as keys.
        """
        return self._pedb.layout.polygons_by_layer

    @property
    @deprecated_property("use layout.primitives_by_net property instead.")
    def primitives_by_net(self) -> dict[str, Primitive]:
        """Primitives with net names as keys.

        .. deprecated:: 0.70.0
           Use layout.primitives_by_net instead.

        Returns
        -------
        dict
            Dictionary of primitives with nat names as keys.
        """
        return self._pedb.layout.primitives_by_net

    @property
    @deprecated_property("use layout.primitives_by_layer property instead.")
    def primitives_by_layer(self) -> dict[str, list[Primitive]]:
        """Primitives with layer names as keys.

        .. deprecated:: 0.70.0
           Use :attr: layout.primitives_by_layer instead.

        Returns
        -------
        dict
            Dictionary of primitives with layer names as keys.
        """
        return self._pedb.layout.primitives_by_layer

    @property
    @deprecated_property("Use layout.rectangles property instead.")
    def rectangles(self) -> list[RectangleDotNet]:
        """Rectangles.

        .. deprecated:: 0.70.0
           Use :attr: layout.rectangles instead.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of rectangles.

        """
        return self._pedb.layout.rectangles

    @property
    @deprecated_property("Use layout.circles property instead.")
    def circles(self) -> list[CircleDotNet]:
        """Circles.

        .. deprecated:: 0.70.0
           Use :attr: layout.circles instead.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of circles.

        """
        return self._pedb.layout.circles

    @property
    @deprecated_property("Use layout.paths property instead.")
    def paths(self) -> list[PathDotNet]:
        """Paths.

        .. deprecated:: 0.70.0
           Use :attr: layout.paths instead.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of paths.
        """
        return self._pedb.layout.paths

    @property
    @deprecated_property("use layout.polygons property instead.")
    def polygons(self) -> list[EdbPolygon]:
        """Polygons.

        .. deprecated:: 0.70.0
           Use :attr: layout.polygons instead.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
            List of polygons.
        """
        return self._pedb.layout.polygons

    @deprecated("Use layout.get_polygons_by_layer method instead.")
    def get_polygons_by_layer(self, layer_name, net_list=None) -> list[EdbPolygon]:
        """Retrieve polygons by a layer.

        .. deprecated:: 0.70.0
           Use :func: layout.get_polygons_by_layer method instead.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        net_list : list, optional
            List of net names.

        Returns
        -------
        list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon`
        """
        return self._pedb.layout.get_polygons_by_layer(layer_name=layer_name, net_list=net_list)

    @deprecated("Use layout.get_primitive_by_layer_and_point method instead.")
    def get_primitive_by_layer_and_point(self, point=None, layer=None, nets=None):
        """Return primitive given coordinate point [x, y], layer name and nets.

        .. deprecated :: 0.70.0
           Use :func: layout.get_primitive_by_layer_and_point method instead.

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
        return self._pedb.layout.get_primitive_by_layer_and_point(point=point, layer=layer, nets=nets)

    @deprecated("Use layout.get_polygons_by_layer method instead.")
    def get_polygon_bounding_box(self, polygon):
        """Retrieve a polygon bounding box.

        .. deprecated:: 0.70.0
           Use :func: layout.get_polygon_bounding_box method instead.

        Parameters
        ----------
        polygon :
            Name of the polygon.

        Returns
        -------
        list
            List of bounding box coordinates in the format ``[-x, -y, +x, +y]``.
        """
        return self._pedb.layout.get_polygon_bounding_box(polygon)

    @deprecated("Use layout.get_polygons_by_layer method instead.")
    def get_polygon_points(self, polygon) -> list[float]:
        """Retrieve polygon points.

        .. deprecated :: 0.70.0
           Use :func: layout.get_polygon_points method instead.

        """
        return self._pedb.layout.get_polygon_points(polygon)

    @deprecated("Use layout.filter_primitives method instead.")
    def get_primitives(self, net_name=None, layer_name=None, prim_type=None, is_void=False) -> list[Primitive]:
        """Get primitives by conditions.

        .. deprecated:: 0.70.0
           Use :func: layout.filter_primitives method instead.

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
        list
            List of filtered primitives
        """
        return self._pedb.layout.filter_primitives(
            net_name=net_name,
            layer_name=layer_name,
            prim_type=prim_type,
            is_void=is_void,
        )

    @staticmethod
    def clear_cache():
        """Force reload of all primitives and reset indexes."""
        warnings.warn("Redundant methods. Not use.", DeprecationWarning)

    def create_taper(
        self,
        start_point: tuple[str | float, str | float, str | float, str | float],
        end_point: tuple[str | float, str | float, str | float, str | float],
        start_width: str | float,
        end_width: str | float,
        layer_name: str = "",
        voids: list | None = None,
        net_name: str = "",
    ) -> bool:
        """
        Create RF trace taper.
        (y)
         ↑
         |              <─      End Width      ─>
         |              ─────── End Point ───────
         |             /           |             \
         |            /            |              \
         |           /             |               \
         |          ────────── Start Point ─────────
         |          <─         Start Width        ─>
         +──────────────────────────────────────→ (x)

        Parameters
        ----------
        start_point : tuple[str | float, str | float, str | float, str | float]
            start point of the taper.
        end_point : tuple[str | float, str | float, str | float, str | float]
            end point of the taper.
        start_width : str | float
            start width of the taper.
        end_width : str | float
            end width of the taper.
        layer_name : str, optional
            Layer of the taper. Default is ``""``.
        voids : list, optional
            Voids of the taper. Default is ``None``.
        net_name : str, optional
            Netname of the taper. Default is ``""``.

        """

        p0_x, p0_y = self._pedb.value(start_point[0]), self._pedb.value(start_point[1])
        p1_x, p1_y = self._pedb.value(end_point[0]), self._pedb.value(end_point[1])
        angle = ((p1_y - p0_y) / (p1_x - p0_x)).atan()
        w0 = self._pedb.value(start_width)
        w1 = self._pedb.value(end_width)

        h = ((p0_x - p1_x) ** 2 + (p0_y - p1_y) ** 2) ** 0.5

        t_p0_y = w0 / 2
        t_p1_y = w0 / -2
        t_p0_x = t_p1_x = 0

        t_p2_y = w1 / -2
        t_p3_y = w1 / 2
        t_p2_x = t_p3_x = h

        point_data = []
        for i in [
            [t_p0_x, t_p0_y],
            [t_p1_x, t_p1_y],
            [t_p2_x, t_p2_y],
            [t_p3_x, t_p3_y],
        ]:
            temp = PointData.create(self._pedb, x=str(i[0]), y=str(i[1]))
            temp = temp.rotate(angle=str(angle), center=(0, 0))
            temp = temp.move(p0_x, p0_y)
            point_data.append(temp)
            poly_data = PolygonData.create(self._pedb, point_data, closed=True)
        _voids = [] if voids is None else voids
        return self.create_polygon(poly_data, layer_name=layer_name, voids=_voids, net_name=net_name)

    def open_solder_mask(self,
                         open_components:bool=True,
                         component_filter:list[str] | None = None,
                         components_opening_offset:float|str=0.0,
                         open_voids:bool=True,
                         voids_opening_offset:float|str=0.0,
                         open_traces:bool=True,
                         traces_offset:float|str=0.0,
                         open_traces_net_filter:list[str] | None = None,
                         solder_mask_layer_name:str="Solder",
                         solder_mask_thickness:float|str="30um",
                         solder_mask_material:str="",
                         reference_signal_layer:str="",
                         open_top:bool=True) -> bool:
        """
        Create solder mask openings for components, voids, and traces.

        This method creates a solder mask dielectric layer with openings (negative geometries) for:

        - Component pads and bodies
        - Polygon voids (cutouts) in power/ground planes
        - PCB traces (transmission lines)

        The solder mask is created as a negative layer (inverted copper representation) in EDB,
        and openings are implemented as rectangular or polygonal shapes placed on this layer.
        A default solder mask material (εᵣ = 4) is created automatically if no material is specified.

        Parameters
        ----------
        open_components : bool, optional
            Enable creation of solder mask openings for component pads and bodies.
            If ``True`` and ``component_filter`` is ``None``, openings are created for all
            components on the reference signal layer. The default is ``True``.
        component_filter : list[str], optional
            Reference designators (RefDes) of specific components to open (e.g., ``["C1", "R2"]``).
            If specified, only these components receive solder mask openings.
            If ``None``, all components on the reference layer are opened. The default is ``None``.
        components_opening_offset : float or str, optional
            Offset distance (in layout units or string with units) to expand component
            opening rectangles beyond the component bounding box. Use positive values to
            expand the opening, negative values to shrink it. The default is ``0.0``.
            Example: ``"0.1mm"`` or ``0.0001`` (in default unit).
        open_voids : bool, optional
            Enable creation of solder mask openings for polygon voids (cutouts in planes).
            When enabled, iterates all polygons on the reference layer and extracts nested
            voids to create corresponding mask openings. The default is ``True``.
        voids_opening_offset : float or str, optional
            Scaling factor for void opening polygons. Positive values expand the void,
            negative values shrink it (relative scaling, not absolute offset). The default is ``0.0``.
        open_traces : bool, optional
            Enable creation of solder mask openings for traces (paths) on the reference layer.
            When enabled, all path primitives are converted to polygonal mask openings. The default is ``True``.
        traces_offset : float or str, optional
            Scaling factor for trace opening polygons. The default is ``0.0``.
        open_traces_net_filter : list[str], optional
            Net name filter to select only specific traces for mask openings (e.g., ``["GND", "SIG1"]``).
            If ``None``, all traces on the reference layer are opened. The default is ``None``.
        solder_mask_layer_name : str, optional
            Name of the solder mask layer to create or reuse. If a layer with this name
            already exists in the stackup, it is reused; otherwise, a new layer is created.
            The default is ``"Solder"``.
        solder_mask_thickness : float or str, optional
            Thickness of the solder mask layer (in layout units or string with units).
            The default is ``"30um"``.
        solder_mask_material : str, optional
            Name of the dielectric material for the solder mask layer. If the material
            does not exist in the database, a default solder mask material with εᵣ = 4
            is created and a warning is logged. The default is ``""`` (empty string triggers
            default creation).
        reference_signal_layer : str, optional
            Name of the signal layer to reference for component placement and primitive
            filtering. If not specified, the topmost signal layer is used when ``open_top=True``,
            or the bottommost signal layer when ``open_top=False``. The default is ``""``.
        open_top : bool, optional
            If ``True``, the solder mask layer is placed on top of the board and references
            the topmost signal layer. If ``False``, the mask is placed on the bottom and
            references the bottommost signal layer. The default is ``True``.

        Returns
        -------
        bool
            ``True`` if the solder mask layer and all openings were created successfully.
            Raises ``ValueError`` if ``component_filter`` specifies RefDes values that do
            not exist in the design.

        Raises
        ------
        ValueError
            If any reference designator in ``component_filter`` is not found in the design.

        Notes
        -----
        - Solder mask layers are created as negative layers in EDB (inverted copper model).
        - All opening geometries inherit the solder mask layer name and are assigned
          to the default net (empty net name ``""``).
        - Component openings are rectangular bounding-box-based; for non-rectangular pads,
          consider using padstack opening geometries instead.
        - Void and trace openings are polygon-based and inherit the exact geometry of the
          original plane cutout or trace path.
        - Offset/scaling parameters use EDB unit system (typically millimeters).

        Examples
        --------
        Create a standard solder mask with all openings on the top side:

        >>> edb = Edb("design.aedb")
        >>> edb.modeler.open_solder_mask()

        Create openings only for specific components with a 0.1 mm margin:

        >>> edb.modeler.open_solder_mask(
        ...     component_filter=["U1", "U2"],
        ...     components_opening_offset="0.1mm",
        ...     open_voids=False,
        ...     open_traces=False,
        ... )

        Create a bottom-side solder mask with custom material and thickness:

        >>> edb.modeler.open_solder_mask(
        ...     solder_mask_layer_name="BottomSolder",
        ...     solder_mask_material="CustomMask",
        ...     solder_mask_thickness="50um",
        ...     open_top=False,
        ... )

        See Also
        --------
        :meth:`stackup.add_layer` : Add a dielectric layer to the stackup
        :meth:`create_rectangle` : Create a rectangular primitive
        :meth:`create_polygon` : Create a polygonal primitive
        """
        if not solder_mask_material in self._pedb.materials:
            solder_mask_material = "SolderMask"
            self._pedb.materials.add_dielectric(permittivity=4, name=solder_mask_material)
            self._pedb.logger.warning(f"No Material name provided or found for {solder_mask_material}.")
            self._pedb.logger.warning(f"Creating default solder mask material {solder_mask_material} with epsr=4.")
        if not reference_signal_layer:
            if open_top:
                reference_signal_layer = list(self._pedb.stackup.signal_layers.values())[0].name
            else:
                reference_signal_layer = list(self._pedb.stackup.signal_layers.values())[-1].name
        if solder_mask_layer_name is self._pedb.stackup.layers:
            layer = self._pedb.stackup.layers[solder_mask_layer_name]
        else:
            if open_top:
                method = "add_on_top"
            else:
                method = "add_below"
            self._pedb.stackup.add_layer(layer_name=solder_mask_layer_name,
                                                 layer_type="signal",
                                                 material=solder_mask_material,
                                                 base_layer=reference_signal_layer,
                                                 thickness=solder_mask_thickness,
                                                 method=method,
                                                 is_negative=True,
                                                 filling_material="AIR"
                                                 )
        if open_components:
            if component_filter:
                components = [component for ref_des, component in self._pedb.components.instances.items()
                              if ref_des in component_filter]
                if not components:
                    raise ValueError(f"No components found for {component_filter}.")
            else:
                components = [component for component in list(self._pedb.components.instances.values())
                              if component.placement_layer == reference_signal_layer]
            for component in components:
                comp_box = component.bounding_box
                x1 = comp_box[0] - components_opening_offset
                y1 = comp_box[1] + components_opening_offset
                x2 = comp_box[2] - components_opening_offset
                y2 = comp_box[3] + components_opening_offset
                self.create_rectangle(layer_name=solder_mask_layer_name,
                                      lower_left_point=(x1, y1),
                                      upper_right_point=(x2, y2))
        if open_voids:
            for polygon in self._pedb.layout.find_primitive(prim_type="polygon", layer_name=reference_signal_layer):
                if not polygon.has_voids:
                    continue
                for void in polygon.voids:
                    polygon_data = void.polygon_data
                    if voids_opening_offset:
                        polygon_data = polygon_data.scale(voids_opening_offset)
                    self.create_polygon(polygon_data, layer_name=solder_mask_layer_name, net_name="")
        if open_traces:
            traces = self._pedb.layout.find_primitive(prim_type="path", layer_name=reference_signal_layer,
                                                      net_name=open_traces_net_filter)
            for trace in traces:
                polygon_data = trace.polygon_data
                if traces_offset:
                    polygon_data = polygon_data.scale(traces_offset)
                self.create_polygon(polygon_data, layer_name=solder_mask_layer_name, net_name="")
        return True
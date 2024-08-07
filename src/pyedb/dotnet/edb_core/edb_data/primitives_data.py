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

import math

from pyedb.dotnet.edb_core.cell.primitive import Primitive
from pyedb.dotnet.edb_core.dotnet.primitive import (
    BondwireDotNet,
    CircleDotNet,
    PathDotNet,
    PolygonDataDotNet,
    RectangleDotNet,
    TextDotNet,
)
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.modeler.geometry_operators import GeometryOperators


def cast(raw_primitive, core_app):
    """Cast the primitive object to correct concrete type.

    Returns
    -------
    Primitive
    """
    prim_type = raw_primitive.GetPrimitiveType()
    if prim_type == prim_type.Rectangle:
        return EdbRectangle(raw_primitive, core_app)
    elif prim_type == prim_type.Polygon:
        return EdbPolygon(raw_primitive, core_app)
    elif prim_type == prim_type.Path:
        return EdbPath(raw_primitive, core_app)
    elif prim_type == prim_type.Bondwire:
        return EdbBondwire(raw_primitive, core_app)
    elif prim_type == prim_type.Text:
        return EdbText(raw_primitive, core_app)
    elif prim_type == prim_type.Circle:
        return EdbCircle(raw_primitive, core_app)
    else:
        return None


class EdbPath(Primitive, PathDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, core_app, raw_primitive)
        PathDotNet.__init__(self, core_app, raw_primitive)

    @property
    def width(self):
        """Path width.

        Returns
        -------
        float
            Path width or None.
        """
        if self.type == "Path":
            return self.primitive_object.GetWidth()
        return

    @width.setter
    def width(self, value):
        if self.type == "Path":
            if isinstance(value, (int, str, float)):
                self.primitive_object.SetWidth(self._app.edb_value(value))
            else:
                self.primitive_object.SetWidth(value)

    @property
    def length(self):
        """Path length in meters.

        Returns
        -------
        float
            Path length in meters.
        """
        center_line_arcs = list(self.api_object.GetCenterLine().GetArcData())
        path_length = 0.0
        for arc in center_line_arcs:
            path_length += arc.GetLength()
        if self.end_cap_style[0]:
            if not self.end_cap_style[1].value__ == 1:
                path_length += self.width / 2
            if not self.end_cap_style[2].value__ == 1:
                path_length += self.width / 2
        return path_length

    def add_point(self, x, y, incremental=False):
        """Add a point at the end of the path.

        Parameters
        ----------
        x: str, int, float
            X coordinate.
        y: str, in, float
            Y coordinate.
        incremental: bool
            Add point incrementally. If True, coordinates of the added point is incremental to the last point.
            The default value is ``False``.

        Returns
        -------
        bool
        """
        center_line = PolygonDataDotNet(self._pedb, self._edb_object.GetCenterLine())
        center_line.add_point(x, y, incremental)
        return self._edb_object.SetCenterLine(center_line.edb_api)

    def get_center_line(self, to_string=False):
        """Get the center line of the trace.

        Parameters
        ----------
        to_string : bool, optional
            Type of return. The default is ``"False"``.

        Returns
        -------
        list

        """
        if to_string:
            return [[p.X.ToString(), p.Y.ToString()] for p in list(self.primitive_object.GetCenterLine().Points)]
        else:
            return [[p.X.ToDouble(), p.Y.ToDouble()] for p in list(self.primitive_object.GetCenterLine().Points)]

    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        center_line = self.center_line
        width = self.width
        corner_style = self.corner_style
        end_cap_style = self.end_cap_style
        cloned_path = self._app.edb_api.cell.primitive.path.create(
            self._app.active_layout,
            self.layer_name,
            self.net,
            width,
            end_cap_style[1],
            end_cap_style[2],
            corner_style,
            center_line,
        )
        if cloned_path:
            return cloned_path

    #

    def create_edge_port(
        self,
        name,
        position="End",
        port_type="Wave",
        reference_layer=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """

        Parameters
        ----------
        name : str
            Name of the port.
        position : str, optional
            Position of the port. The default is ``"End"``, in which case the port is created at the end of the trace.
            Options are ``"Start"`` and ``"End"``.
        port_type : str, optional
            Type of the port. The default is ``"Wave"``, in which case a wave port is created. Options are ``"Wave"``
             and ``"Gap"``.
        reference_layer : str, optional
            Name of the references layer. The default is ``None``. Only available for gap port.
        horizontal_extent_factor : int, optional
            Horizontal extent factor of the wave port. The default is ``5``.
        vertical_extent_factor : int, optional
            Vertical extent factor of the wave port. The default is ``3``.
        pec_launch_width : float, str, optional
            Perfect electrical conductor width of the wave port. The default is ``"0.01mm"``.

        Returns
        -------
            :class:`dotnet.edb_core.edb_data.sources.ExcitationPorts`

        Examples
        --------
        >>> edbapp = pyedb.dotnet.Edb("myproject.aedb")
        >>> sig = appedb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
        >>> sig.create_edge_port("pcb_port", "end", "Wave", None, 8, 8)

        """
        center_line = self.get_center_line()
        pos = center_line[-1] if position.lower() == "end" else center_line[0]

        if port_type.lower() == "wave":
            return self._app.hfss.create_wave_port(
                self.id, pos, name, 50, horizontal_extent_factor, vertical_extent_factor, pec_launch_width
            )
        else:
            return self._app.hfss.create_edge_port_vertical(self.id, pos, name, 50, reference_layer)

    def create_via_fence(self, distance, gap, padstack_name, net_name="GND"):
        """Create via fences on both sides of the trace.

        Parameters
        ----------
        distance: str, float
            Distance between via fence and trace center line.
        gap: str, float
            Gap between vias.
        padstack_name: str
            Name of the via padstack.
        net_name: str, optional
            Name of the net.

        Returns
        -------
        """

        def getAngle(v1, v2):  # pragma: no cover
            v1_mag = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            v2_mag = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            dotsum = v1[0] * v2[0] + v1[1] * v2[1]
            if v1[0] * v2[1] - v1[1] * v2[0] > 0:
                scale = 1
            else:
                scale = -1
            dtheta = scale * math.acos(dotsum / (v1_mag * v2_mag))

            return dtheta

        def getLocations(line, gap):  # pragma: no cover
            location = [line[0]]
            residual = 0

            for n in range(len(line) - 1):
                x0, y0 = line[n]
                x1, y1 = line[n + 1]
                length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                dx, dy = (x1 - x0) / length, (y1 - y0) / length
                x = x0 - dx * residual
                y = y0 - dy * residual
                length = length + residual
                while length >= gap:
                    x += gap * dx
                    y += gap * dy
                    location.append((x, y))
                    length -= gap

                residual = length
            return location

        def getParalletLines(pts, distance):  # pragma: no cover
            leftline = []
            rightline = []

            x0, y0 = pts[0]
            x1, y1 = pts[1]
            vector = (x1 - x0, y1 - y0)
            orientation1 = getAngle((1, 0), vector)

            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x0 + distance * math.cos(leftturn), y0 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x0 + distance * math.cos(righrturn), y0 + distance * math.sin(righrturn))
            rightline.append(rightPt)

            for n in range(1, len(pts) - 1):
                x0, y0 = pts[n - 1]
                x1, y1 = pts[n]
                x2, y2 = pts[n + 1]

                v1 = (x1 - x0, y1 - y0)
                v2 = (x2 - x1, y2 - y1)
                dtheta = getAngle(v1, v2)
                orientation1 = getAngle((1, 0), v1)

                leftturn = orientation1 + dtheta / 2 + math.pi / 2
                righrturn = orientation1 + dtheta / 2 - math.pi / 2

                distance2 = distance / math.sin((math.pi - dtheta) / 2)
                leftPt = (x1 + distance2 * math.cos(leftturn), y1 + distance2 * math.sin(leftturn))
                leftline.append(leftPt)
                rightPt = (x1 + distance2 * math.cos(righrturn), y1 + distance2 * math.sin(righrturn))
                rightline.append(rightPt)

            x0, y0 = pts[-2]
            x1, y1 = pts[-1]

            vector = (x1 - x0, y1 - y0)
            orientation1 = getAngle((1, 0), vector)
            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x1 + distance * math.cos(leftturn), y1 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x1 + distance * math.cos(righrturn), y1 + distance * math.sin(righrturn))
            rightline.append(rightPt)
            return leftline, rightline

        distance = self._pedb.edb_value(distance).ToDouble()
        gap = self._pedb.edb_value(gap).ToDouble()
        center_line = self.get_center_line()
        leftline, rightline = getParalletLines(center_line, distance)
        for x, y in getLocations(rightline, gap) + getLocations(leftline, gap):
            self._pedb.padstacks.place([x, y], padstack_name, net_name=net_name)


class EdbRectangle(Primitive, RectangleDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, core_app,raw_primitive)
        RectangleDotNet.__init__(self, core_app, raw_primitive)


class EdbCircle(Primitive, CircleDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self,core_app, raw_primitive)
        CircleDotNet.__init__(self, self._app, raw_primitive)


class EdbPolygon(Primitive):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, core_app, raw_primitive)

    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        return self._pedb.modeler.create_polygon(
            main_shape=self.polygon_data._edb_object,
            layer_name=self.layer_name,
            net_name=self.net_name,
            voids=self.voids
        )

    @property
    def has_self_intersections(self):
        """Check if Polygon has self intersections.

        Returns
        -------
        bool
        """
        return self.polygon_data.edb_api.HasSelfIntersections()

    def fix_self_intersections(self):
        """Remove self intersections if they exists.

        Returns
        -------
        list
            All new polygons created from the removal operation.
        """
        new_polys = []
        if self.has_self_intersections:
            new_polygons = list(self.polygon_data.edb_api.RemoveSelfIntersections())
            self.polygon_data = new_polygons[0]
            for p in new_polygons[1:]:
                cloned_poly = self._app.edb_api.cell.primitive.polygon.create(
                    self._app.active_layout, self.layer_name, self.net, p
                )
                new_polys.append(cloned_poly)
        return new_polys

    def duplicate_across_layers(self, layers):
        """Duplicate across layer a primitive object.

        Parameters:

        layers: list
            list of str, with layer names

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for layer in layers:
            if layer in self._pedb.stackup.layers:
                duplicate_polygon = self._app.edb_api.cell.primitive.polygon.create(
                    self._app.active_layout, layer, self.net, self.polygon_data.edb_api
                )
                if duplicate_polygon:
                    for void in self.voids:
                        duplicate_void = self._app.edb_api.cell.primitive.polygon.create(
                            self._app.active_layout, layer, self.net, void.polygon_data.edb_api
                        )
                        duplicate_polygon.prim_obj.AddVoid(duplicate_void.prim_obj)
            else:
                return False
        return True

    def move(self, vector):
        """Move polygon along a vector.

        Parameters
        ----------
        vector : List of float or str [x,y].

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edbapp = pyaedt.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.move(vector=["2mm", "100um"])
        """
        if vector and isinstance(vector, list) and len(vector) == 2:
            _vector = self._edb.Geometry.PointData(
                self._edb.Utility.Value(vector[0]), self._edb.Utility.Value(vector[1])
            )
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(self.polygon_data.edb_api.GetArcData(), True)
            polygon_data.Move(_vector)
            return self.api_object.SetPolygonData(polygon_data)
        return False

    def rotate(self, angle, center=None):
        """Rotate polygon around a center point by an angle.

        Parameters
        ----------
        angle : float
            Value of the rotation angle in degree.
        center : List of float or str [x,y], optional
            If None rotation is done from polygon center.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edbapp = pyaedt.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.rotate(angle=45)
        """
        if angle:
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(self.polygon_data.edb_api.GetArcData(), True)
            if not center:
                center = polygon_data.GetBoundingCircleCenter()
                if center:
                    polygon_data.Rotate(angle * math.pi / 180, center)
                    return self.api_object.SetPolygonData(polygon_data)
            elif isinstance(center, list) and len(center) == 2:
                center = self._edb.Geometry.PointData(
                    self._edb.Utility.Value(center[0]), self._edb.Utility.Value(center[1])
                )
                polygon_data.Rotate(angle * math.pi / 180, center)
                return self.api_object.SetPolygonData(polygon_data)
        return False

    def move_layer(self, layer):
        """Move polygon to given layer.

        Parameters
        ----------
        layer : str
            layer name.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.
        """
        if layer and isinstance(layer, str) and layer in self._pedb.stackup.signal_layers:
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(self.polygon_data.edb_api.GetArcData(), True)
            moved_polygon = self._pedb.modeler.create_polygon(
                main_shape=polygon_data, net_name=self.net_name, layer_name=layer
            )
            if moved_polygon:
                self.delete()
                return True
        return False

    def in_polygon(
        self,
        point_data,
        include_partial=True,
    ):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        point_data : PointData Object or list of float
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(point_data, list):
            point_data = self._app.edb_api.geometry.point_data(
                self._app.edb_value(point_data[0]), self._app.edb_value(point_data[1])
            )
        int_val = int(self.polygon_data._edb_object.PointInPolygon(point_data))

        # Intersection type:
        # 0 = objects do not intersect
        # 1 = this object fully inside other (no common contour points)
        # 2 = other object fully inside this
        # 3 = common contour points 4 = undefined intersection
        if int_val == 0:
            return False
        elif include_partial:
            return True
        elif int_val < 3:
            return True
        else:
            return False

    #
    # def add_void(self, point_list):
    #     """Add a void to current primitive.
    #
    #     Parameters
    #     ----------
    #     point_list : list or  :class:`dotnet.edb_core.edb_data.primitives_data.Primitive` or EDB Primitive Object
    #         Point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.
    #
    #     Returns
    #     -------
    #     bool
    #         ``True`` if successful, either  ``False``.
    #     """
    #     if isinstance(point_list, list):
    #         plane = self._app.modeler.Shape("polygon", points=point_list)
    #         _poly = self._app.modeler.shape_to_polygon_data(plane)
    #         if _poly is None or _poly.IsNull() or _poly is False:
    #             self._logger.error("Failed to create void polygon data")
    #             return False
    #         prim = self._app.edb_api.cell.primitive.polygon.create(
    #             self._app.active_layout, self.layer_name, self.primitive_object.GetNet(), _poly
    #         )
    #     elif isinstance(point_list, Primitive):
    #         prim = point_list.primitive_object
    #     else:
    #         prim = point_list
    #     return self.add_void(prim)


class EdbText(Primitive, TextDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, raw_primitive, core_app)
        TextDotNet.__init__(self, raw_primitive, self._app)


class EdbBondwire(Primitive, BondwireDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, raw_primitive, core_app)
        BondwireDotNet.__init__(self, raw_primitive, self._app)


class EDBArcs(object):
    """Manages EDB Arc Data functionalities.
    It Inherits EDB primitives arcs properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> prim_arcs = edb.modeler.primitives[0].arcs
    >>> prim_arcs.center # arc center
    >>> prim_arcs.points # arc point list
    >>> prim_arcs.mid_point # arc mid point
    """

    def __init__(self, app, arc):
        self._app = app
        self.arc_object = arc

    @property
    def start(self):
        """Get the coordinates of the starting point.

        Returns
        -------
        list
            List containing the X and Y coordinates of the starting point.


        Examples
        --------
        >>> appedb = Edb(fpath, edbversion="2024.1")
        >>> start_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].start
        >>> print(start_coordinate)
        [x_value, y_value]
        """
        point = self.arc_object.Start
        return [point.X.ToDouble(), point.Y.ToDouble()]

    @property
    def end(self):
        """Get the coordinates of the ending point.

        Returns
        -------
        list
            List containing the X and Y coordinates of the ending point.

        Examples
        --------
        >>> appedb = Edb(fpath, edbversion="2024.1")
        >>> end_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].end
        """
        point = self.arc_object.End
        return [point.X.ToDouble(), point.Y.ToDouble()]

    @property
    def height(self):
        """Get the height of the arc.

        Returns
        -------
        float
            Height of the arc.


        Examples
        --------
        >>> appedb = Edb(fpath, edbversion="2024.1")
        >>> arc_height = appedb.nets["V1P0_S0"].primitives[0].arcs[0].height
        """
        return self.arc_object.Height

    @property
    def center(self):
        """Arc center.

        Returns
        -------
        list
        """
        cent = self.arc_object.GetCenter()
        return [cent.X.ToDouble(), cent.Y.ToDouble()]

    @property
    def length(self):
        """Arc length.

        Returns
        -------
        float
        """
        return self.arc_object.GetLength()

    @property
    def mid_point(self):
        """Arc mid point.

        Returns
        -------
        float
        """
        return self.arc_object.GetMidPoint()

    @property
    def radius(self):
        """Arc radius.

        Returns
        -------
        float
        """
        return self.arc_object.GetRadius()

    @property
    def is_segment(self):
        """Either if it is a straight segment or not.

        Returns
        -------
        bool
        """
        return self.arc_object.IsSegment()

    @property
    def is_point(self):
        """Either if it is a point or not.

        Returns
        -------
        bool
        """
        return self.arc_object.IsPoint()

    @property
    def is_ccw(self):
        """Test whether arc is counter clockwise.

        Returns
        -------
        bool
        """
        return self.arc_object.IsCCW()

    @property
    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        list
            Edb Points.
        """
        return list(self.arc_object.GetPointData())

    @property
    def points(self, arc_segments=6):
        """Return the list of points with arcs converted to segments.

        Parameters
        ----------
        arc_segments : int
            Number of facets to convert an arc. Default is `6`.

        Returns
        -------
        list, list
            x and y list of points.
        """
        try:
            my_net_points = self.points_raw
            xt, yt = self._app._get_points_for_plot(my_net_points, arc_segments)
            if not xt:
                return []
            x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
            return x, y
        except:
            x = []
            y = []
        return x, y

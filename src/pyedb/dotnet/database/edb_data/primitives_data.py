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

import math

from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.dotnet.primitive import (
    BondwireDotNet,
    CircleDotNet,
    RectangleDotNet,
    TextDotNet,
)
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
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
    elif prim_type == prim_type.Bondwire:
        return EdbBondwire(raw_primitive, core_app)
    elif prim_type == prim_type.Text:
        return EdbText(raw_primitive, core_app)
    elif prim_type == prim_type.Circle:
        return EdbCircle(raw_primitive, core_app)
    else:
        return None


class EdbRectangle(Primitive, RectangleDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, core_app, raw_primitive)
        RectangleDotNet.__init__(self, core_app, raw_primitive)


class EdbCircle(Primitive, CircleDotNet):
    def __init__(self, raw_primitive, core_app):
        Primitive.__init__(self, core_app, raw_primitive)
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
            voids=self.voids,
        )

    @property
    def has_self_intersections(self):
        """Check if Polygon has self intersections.

        Returns
        -------
        bool
        """
        return self.polygon_data._edb_object.HasSelfIntersections()

    def fix_self_intersections(self):
        """Remove self intersections if they exists.

        Returns
        -------
        list
            All new polygons created from the removal operation.
        """
        new_polys = []
        if self.has_self_intersections:
            new_polygons = list(self.polygon_data._edb_object.RemoveSelfIntersections())
            self._edb_object.SetPolygonData(new_polygons[0])
            for p in new_polygons[1:]:
                cloned_poly = self._app.core.Cell.primitive.polygon.create(
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
                duplicate_polygon = self._pedb.modeler.create_polygon(
                    self.polygon_data._edb_object, layer, net_name=self.net.name
                )
                if duplicate_polygon:
                    for void in self.voids:
                        duplicate_void = self._pedb.modeler.create_polygon(
                            void.polygon_data._edb_object,
                            layer,
                            net_name=self.net.name,
                        )
                        duplicate_polygon._edb_object.AddVoid(duplicate_void._edb_object)
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
        >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.move(vector=["2mm", "100um"])
        """
        if vector and isinstance(vector, list) and len(vector) == 2:
            _vector = self._edb.Geometry.PointData(
                self._edb.Utility.Value(vector[0]), self._edb.Utility.Value(vector[1])
            )
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(
                self.polygon_data._edb_object.GetArcData(), True
            )
            polygon_data.Move(_vector)
            return self._edb_object.SetPolygonData(polygon_data)
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
        >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.rotate(angle=45)
        """
        if angle:
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(
                self.polygon_data._edb_object.GetArcData(), True
            )
            if not center:
                center = polygon_data.GetBoundingCircleCenter()
                if center:
                    polygon_data.Rotate(angle * math.pi / 180, center)
                    return self._edb_object.SetPolygonData(polygon_data)
            elif isinstance(center, list) and len(center) == 2:
                center = self._edb.Geometry.PointData(
                    self._edb.Utility.Value(center[0]), self._edb.Utility.Value(center[1])
                )
                polygon_data.Rotate(angle * math.pi / 180, center)
                return self._edb_object.SetPolygonData(polygon_data)
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
            polygon_data = self._edb.Geometry.PolygonData.CreateFromArcs(
                self.polygon_data._edb_object.GetArcData(), True
            )
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
            point_data = self._app.pedb_class.database.geometry.point_data.PointData.create_from_xy(
                self._app, self._app.edb_value(point_data[0]), self._app.edb_value(point_data[1])
            )
        int_val = int(self.polygon_data._edb_object.PointInPolygon(point_data._edb_object))

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
    #     point_list : list or  :class:`dotnet.database.edb_data.primitives_data.Primitive` or EDB Primitive Object
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
    #         prim = self._app.core.Cell.primitive.polygon.create(
    #             self._app.active_layout, self.layer_name, self.primitive_object.GetNet(), _poly
    #         )
    #     elif isinstance(point_list, Primitive):
    #         prim = point_list.primitive_object
    #     else:
    #         prim = point_list
    #     return self.add_void(prim)

    @property
    def polygon_data(self):
        """:class:`pyedb.dotnet.database.dotnet.database.PolygonDataDotNet`: Outer contour of the Polygon object."""
        return PolygonData(self._pedb, self._edb_object.GetPolygonData())

    @polygon_data.setter
    def polygon_data(self, poly):
        self._edb_object.SetPolygonData(poly._edb_object)

    def expand(self, offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001):
        """Expand the polygon shape by an absolute value in all direction.
        Offset can be negative for negative expansion.

        Parameters
        ----------
        offset : float, optional
            Offset value in meters.
        tolerance : float, optional
            Tolerance in meters.
        round_corners : bool, optional
            Whether to round corners or not.
            If True, use rounded corners in the expansion otherwise use straight edges (can be degenerate).
        maximum_corner_extension : float, optional
            The maximum corner extension (when round corners are not used) at which point the corner is clipped.
        """
        pd = self.polygon_data
        pd.expand(offset, tolerance, round_corners, maximum_corner_extension)
        self.polygon_data = pd
        return pd


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
    >>> prim_arcs.center  # arc center
    >>> prim_arcs.points  # arc point list
    >>> prim_arcs.mid_point  # arc mid point
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
        >>> appedb = Edb(fpath, edbversion="2024.2")
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
        >>> appedb = Edb(fpath, edbversion="2024.2")
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
        >>> appedb = Edb(fpath, edbversion="2024.2")
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
            xt, yt = self._app._active_cell.primitive._get_points_for_plot(my_net_points, arc_segments)
            if not xt:
                return []
            x, y = list(GeometryOperators.orient_polygon(xt, yt, clockwise=True))
            return [x, y]
        except:
            x = []
            y = []
        return [x, y]

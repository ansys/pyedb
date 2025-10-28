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
from typing import Union
import warnings

from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData
from pyedb.dotnet.database.utilities.obj_base import BBox


class PolygonData:
    """Polygon Data."""

    def __init__(
        self,
        pedb,
        edb_object=None,
        create_from_points=None,
        create_from_circle=None,
        create_from_rectangle=None,
        create_from_bounding_box=None,
        **kwargs,
    ):
        self._pedb = pedb

        if create_from_points:
            self._edb_object = self.create_from_points(**kwargs)
        elif create_from_circle:
            x_center, y_center, radius = kwargs
        elif create_from_rectangle:
            x_lower_left, y_lower_left, x_upper_right, y_upper_right = kwargs
        elif create_from_bounding_box:
            self._edb_object = self.create_from_bounding_box(**kwargs)
        else:  # pragma: no cover
            self._edb_object = edb_object

    @property
    def bounding_box(self):
        """Bounding box.

        Returns
        -------
        List[float]
            List of coordinates for the component's bounding box, with the list of
            coordinates in this order: [X lower left corner, Y lower left corner,
            X upper right corner, Y upper right corner].
        """
        return BBox(self._pedb, self._edb_object.GetBBox()).corner_points

    @property
    def arcs(self):
        """Get the Primitive Arc Data."""
        from pyedb.dotnet.database.edb_data.primitives_data import EDBArcs

        arcs = [EDBArcs(self._pedb, i) for i in self._edb_object.GetArcData()]
        return arcs

    @property
    def points(self):
        """Get all points in polygon.

        Returns
        -------
        list[list[float]]
        """
        return [
            (self._pedb.edb_value(i.X).ToDouble(), self._pedb.edb_value(i.Y).ToDouble())
            for i in list(self._edb_object.Points)
        ]

    @property
    def points_without_arcs(self):
        points = list(self._edb_object.GetPolygonWithoutArcs().Points)
        return [(pt.X.ToDouble(), pt.Y.ToDouble()) for pt in points]

    def create_from_points(self, points, closed=True):
        list_of_point_data = []
        for pt in points:
            list_of_point_data.append(PointData.create_from_xy(self._pedb, x=pt[0], y=pt[1])._edb_object)
        return self._pedb.core.Geometry.PolygonData(convert_py_list_to_net_list(list_of_point_data), closed)

    @property
    def area(self):
        """Get the area of the polygon."""
        return self._edb_object.Area()

    def create_from_bounding_box(self, points):
        bbox = BBox(self._pedb, point_1=points[0], point_2=points[1])
        return self._pedb.core.Geometry.PolygonData.CreateFromBBox(bbox._edb_object)

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
        new_poly = self._edb_object.Expand(offset, tolerance, round_corners, maximum_corner_extension)
        self._edb_object = new_poly[0]
        return True

    def create_from_arcs(self, arcs, flag):
        """Edb Dotnet Api Database `Edb.Geometry.CreateFromArcs`.

        Parameters
        ----------
        arcs : list or `Edb.Geometry.ArcData`
            List of ArcData.
        flag : bool
        """
        if isinstance(arcs, list):
            arcs = convert_py_list_to_net_list(arcs)
        poly = self._edb_object.CreateFromArcs(arcs, flag)
        return PolygonData(self._pedb, poly)

    def is_inside(self, x: Union[str, float], y: Union[str, float] = None) -> bool:
        """Determines whether a point is inside the polygon."""
        if isinstance(x, list) and len(x) == 2:
            y = x[1]
            x = x[0]
        return self._edb_object.PointInPolygon(self._pedb.point_data(x, y))

    def point_in_polygon(self, x: Union[str, float], y: Union[str, float] = None) -> bool:
        """Determines whether a point is inside the polygon.

        ..deprecated:: 0.48.0
           Use: func:`is_inside` instead.
        """
        warnings.warn("Use method is_inside instead", DeprecationWarning)
        return self.is_inside(x, y)

    def get_point(self, index):
        """Gets the point at the index as a PointData object."""
        edb_object = self._edb_object.GetPoint(index)
        return self._pedb.pedb_class.database.geometry.point_data.PointData(self._pedb, edb_object)

    def set_point(self, index, point_data):
        """Sets the point at the index from a PointData object."""
        self._edb_object.SetPoint(index, point_data)

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


from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData

from pyedb.grpc.database.geometry.arc_data import ArcData
from pyedb.grpc.database.utility.value import Value


class PolygonData:
    """Class managing Polygon Data."""

    def __init__(
        self,
        edb_object=None,
        create_from_points=None,
        create_from_circle=None,
        create_from_rectangle=None,
        create_from_bounding_box=None,
        **kwargs,
    ):
        if create_from_points:
            self.core = self.create_from_points(**kwargs)
        elif create_from_circle:
            x_center, y_center, radius = kwargs
        elif create_from_rectangle:
            x_lower_left, y_lower_left, x_upper_right, y_upper_right = kwargs
        elif create_from_bounding_box:
            self.core = self.create_from_bounding_box(**kwargs)
        else:  # pragma: no cover
            self.core = edb_object

    @property
    def bounding_box(self) -> list[float]:
        """Bounding box.

        Returns
        -------
        List[float]
            List of coordinates for the component's bounding box, with the list of
            coordinates in this order: [X lower left corner, Y lower left corner,
            X upper right corner, Y upper right corner].
        """
        bbox = self.core.bbox()
        return [Value(bbox[0].x), Value(bbox[0].y), Value(bbox[1].x), Value(bbox[1].y)]

    @property
    def arcs(self) -> list[ArcData]:
        """Get the Primitive Arc Data.

        Returns
        -------
        List[:class:`ArcData <pyedb.grpc.database.geometry.arc_data.ArcData>`]
        """
        return [ArcData(i) for i in self.core.arc_data]

    @property
    def is_closed(self) -> bool:
        """Check if polygon is closed.

        Returns
        -------
        bool
        """
        return self.core.is_closed

    @property
    def sense(self) -> any:
        """Get the polygon sense type.

        Returns
        -------
        :class: `PolygonSenseType <ansys.edb.core.geometry.polygon_data.PolygonSenseType>`
        """
        return self.core.sense

    @property
    def holes(self):
        """Get all holes in polygon.

        Returns
        -------
        list[:class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`]
        """
        return [PolygonData(i) for i in self.core.holes]

    @property
    def points(self) -> list[list[float]]:
        """Get all points in polygon.

        Returns
        -------
        list[list[float]]
        """
        return [[Value(i.x), Value(i.y)] for i in list(self.core.points)]

    @classmethod
    def create_from_points(cls, points, closed=True):
        if not isinstance(points, list):
            raise TypeError("Points must be provided as a list of PointData objects.")
        list_of_point_data = []
        for pt in points:
            list_of_point_data.append(GrpcPointData(pt))
        return cls(GrpcPolygonData(points=list_of_point_data, closed=closed))

    @classmethod
    def create_from_bounding_box(cls, points) -> GrpcPolygonData:
        """Create PolygonData from point list.

        Returns
        -------
        :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`

        """
        return cls(GrpcPolygonData(points=points))

    def expand(self, offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001) -> bool:
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

        Returns
        -------
        bool

        """
        new_poly = self.core.expand(offset, tolerance, round_corners, maximum_corner_extension)
        if not new_poly[0].points:
            return False
        self.core = new_poly[0]
        return True

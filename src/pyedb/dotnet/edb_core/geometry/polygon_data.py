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

from pyedb.dotnet.edb_core.geometry.point_data import PointData
from pyedb.dotnet.edb_core.utilities.obj_base import BBox


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
    def points(self):
        """Get all points in polygon.

        Returns
        -------
        list[list[float]]
        """
        return [
            [self._pedb.edb_value(i.X).ToDouble(), self._pedb.edb_value(i.Y).ToDouble()]
            for i in list(self._edb_object.Points)
        ]

    def create_from_points(self, points, closed=True):
        list_of_point_data = []
        for pt in points:
            list_of_point_data.append(PointData(self._pedb, x=pt[0], y=pt[1]))
        return self._pedb.edb_api.geometry.api_class.PolygonData(list_of_point_data, closed)

    def create_from_bounding_box(self, points):
        bbox = BBox(self._pedb, point_1=points[0], point_2=points[1])
        return self._pedb.edb_api.geometry.api_class.PolygonData.CreateFromBBox(bbox._edb_object)

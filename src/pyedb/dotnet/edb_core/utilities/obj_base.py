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

from pyedb.dotnet.clr_module import Tuple
from pyedb.dotnet.edb_core.geometry.point_data import PointData


class BBox:
    """Bounding box."""

    def __init__(self, pedb, edb_object=None, point_1=None, point_2=None):
        self._pedb = pedb
        if edb_object:
            self._edb_object = edb_object
        else:
            point_1 = PointData(self._pedb, x=point_1[0], y=point_1[1])
            point_2 = PointData(self._pedb, x=point_2[0], y=point_2[1])
            self._edb_object = Tuple[self._pedb.edb_api.Geometry.PointData, self._pedb.edb_api.Geometry.PointData](
                point_1._edb_object, point_2._edb_object
            )

    @property
    def point_1(self):
        return [self._edb_object.Item1.X.ToDouble(), self._edb_object.Item1.Y.ToDouble()]

    @property
    def point_2(self):
        return [self._edb_object.Item2.X.ToDouble(), self._edb_object.Item2.Y.ToDouble()]

    @property
    def corner_points(self):
        return [self.point_1, self.point_2]


class ObjBase(object):
    """Manages EDB functionalities for a base object."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def is_null(self):
        """Flag indicating if this object is null."""
        return self._edb_object.IsNull()

    @property
    def type(self):
        """Type of the edb object."""
        try:
            return self._edb_object.GetType()
        except AttributeError:  # pragma: no cover
            return None

    @property
    def name(self):
        """Name of the definition."""
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        self._edb_object.SetName(value)

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

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
from typing import TYPE_CHECKING, Any
import warnings

from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData
from pyedb.dotnet.database.utilities.obj_base import BBox
from pyedb.misc.decorators import deprecated

if TYPE_CHECKING:  # pragma: no cover
    from pyedb.dotnet.database.edb_data.primitives_data import EDBArcs
    from pyedb.dotnet.edb import Edb


class PolygonData:
    """Polygon Data."""

    def __init__(
        self,
        pedb: "Edb",
        core: Any | None = None,
        create_from_points: Any | None = None,
        create_from_bounding_box: Any | None = None,
        **kwargs,
    ) -> None:
        self._pedb = pedb

        if core is not None:
            self.core = core
        elif create_from_points:
            self.core = self.create_from_points(**kwargs)
        elif create_from_bounding_box:
            self.core = self.create_from_bounding_box(**kwargs)
        else:
            self._pedb.logger.error(
                "PolygonData: No valid EDB object or creation method provided. "
                "Please provide either an 'edb_object', 'create_from_points', or 'create_from_bounding_box' argument."
            )

    @classmethod
    def create(cls, pedb, points: list[tuple[float, float]], closed: bool = True) -> Any:
        """Create a polygon from a list of points."""
        list_of_point_data = []
        for pt in points:
            if isinstance(pt, PointData):
                list_of_point_data.append(pt.core)
            else:
                list_of_point_data.append(PointData.create(pedb, x=pt[0], y=pt[1]).core)
        core = pedb.core.Geometry.PolygonData(convert_py_list_to_net_list(list_of_point_data), closed)
        return cls(pedb, core)

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
        return BBox(self._pedb, self.core.GetBBox()).corner_points

    @property
    def arcs(self) -> list["EDBArcs"]:
        """Get the Primitive Arc Data."""
        from pyedb.dotnet.database.edb_data.primitives_data import EDBArcs

        arcs = [EDBArcs(self._pedb, i) for i in self.core.GetArcData()]
        return arcs

    @property
    def points(self) -> list[tuple[float, float]]:
        """Get all points in polygon.

        Returns
        -------
        list[tuple[float, float]]
        """
        return [
            (self._pedb.edb_value(i.X).ToDouble(), self._pedb.edb_value(i.Y).ToDouble())
            for i in list(self.core.Points)
        ]

    @property
    def points_without_arcs(self) -> list[tuple[float, float]]:
        """Get all points in polygon without arcs."""
        points = list(self.core.GetPolygonWithoutArcs().Points)
        return [(pt.X.ToDouble(), pt.Y.ToDouble()) for pt in points]

    def create_from_points(self, points: list[tuple[float, float]], closed: bool = True) -> Any:
        """Create a polygon from a list of points."""
        list_of_point_data = []
        for pt in points:
            list_of_point_data.append(PointData.create_from_xy(self._pedb, x=pt[0], y=pt[1]).core)
        return self._pedb.core.Geometry.PolygonData(convert_py_list_to_net_list(list_of_point_data), closed)

    @property
    def area(self) -> float:
        """Get the area of the polygon."""
        return self.core.Area()

    def create_from_bounding_box(self, points: list[Any]) -> Any:
        """Create a polygon from a bounding box defined by two corner points."""
        bbox = BBox(self._pedb, point_1=points[0], point_2=points[1])
        return self._pedb.core.Geometry.PolygonData.CreateFromBBox(bbox.core)

    def expand(
        self,
        offset: float = 0.001,
        tolerance: float = 1e-12,
        round_corners: bool = True,
        maximum_corner_extension: float = 0.001,
    ) -> "PolygonData":
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
        new_poly = self.core.Expand(offset, tolerance, round_corners, maximum_corner_extension)
        self.core = new_poly[0]
        return self

    def create_from_arcs(self, arcs: list[Any], flag: bool) -> "PolygonData":
        """Edb Dotnet Api Database `Edb.Geometry.CreateFromArcs`.

        Parameters
        ----------
        arcs : list or `Edb.Geometry.ArcData`
            List of ArcData.
        flag : bool
        """
        if isinstance(arcs, list):
            arcs = convert_py_list_to_net_list(arcs)
        poly = self.core.CreateFromArcs(arcs, flag)
        return PolygonData(self._pedb, poly)

    # TODO: Shouldn't that method only work with x and y as input instead of
    # accepting that x can be a "point" (list of two values)?
    def is_inside(self, x: str | float | list[Any], y: str | float | None = None) -> bool:
        """Determines whether a point is inside the polygon."""
        if isinstance(x, list) and len(x) == 2:
            y = x[1]
            x = x[0]
        return self.core.PointInPolygon(self._pedb.point_data(x, y))

    # TODO: Same argument as above
    @deprecated("Use is_inside method instead.", category=None)
    def point_in_polygon(self, x: str | float | list[Any], y: str | float | None = None) -> bool:
        """Determines whether a point is inside the polygon.

        ..deprecated:: 0.48.0
           Use: func:`is_inside` instead.
        """
        warnings.warn("Use method is_inside instead", DeprecationWarning)
        return self.is_inside(x, y)

    def get_point(self, index: int) -> PointData:
        """Gets the point at the index as a PointData object."""
        edb_object = self.core.GetPoint(index)
        return self._pedb.pedb_class.database.geometry.point_data.PointData(self._pedb, edb_object)

    def set_point(self, index: int, point_data: PointData) -> None:
        """Sets the point at the index from a PointData object."""
        self.core.SetPoint(index, point_data)

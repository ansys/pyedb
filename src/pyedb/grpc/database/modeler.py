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
from typing import Any, Iterable, List, Optional, Union
import warnings

from ansys.edb.core.geometry.point_data import PointData as CorePointData
from ansys.edb.core.geometry.polygon_data import (
    PolygonData as CorePolygonData,
)

from pyedb.grpc.database.geometry.point_data import PointData
from pyedb.grpc.database.geometry.polygon_data import PolygonData
from pyedb.grpc.database.hierarchy.pingroup import PinGroup
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.primitive.text import Text
from pyedb.grpc.database.utility.layout_statistics import LayoutStatistics
from pyedb.misc.decorators import deprecate_argument_name, deprecated, deprecated_property


def normalize_pairs(points: Iterable[float]) -> List[List[float]]:
    """
    Convert any reasonable point description into [[x1, y1], [x2, y2], …]
    """
    pts = list(points)
    if not pts:  # empty input
        return []

    # Detect flat vs nested
    if isinstance(pts[0], (list, tuple)):
        # already nested – just ensure every item is a *list* (not tuple)
        return [list(pair) for pair in pts]
    else:
        if len(pts) % 2:
            raise ValueError("Odd number of coordinates supplied")
        return [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]


class Modeler(object):
    """Manages EDB methods for primitives management accessible from `Edb.modeler`.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.modeler
    """

    def __getitem__(self, name: Union[str, int]) -> Primitive:
        """Get a primitive by name or ID.

        Parameters
        ----------
        name : str or int
            Name or ID of the primitive.

        Returns
        -------
        :class:`pyedb.grpc.database.primitive.primitive.Primitive`
            Primitive instance if found, None otherwise.

        Raises
        ------
        TypeError
            If name is not str or int.
        """

        if isinstance(name, int):
            return self._pedb.layout.find_object_by_id(name)
        return self._pedb.layout.find_primitive(name=name)[0]

    def __init__(self, p_edb) -> None:
        """Initialize Modeler instance."""
        self._pedb = p_edb
        # Core cache
        self._primitives_by_name: dict[str, Primitive] | None = None
        self._primitives_by_net: dict[str, list[Primitive]] | None = None
        self._primitives_by_layer: dict[str, list[Primitive]] | None = None

        # ============================================================

    # Cache management
    # ============================================================

    def clear_cache(self):
        """Force reload of all primitives and reset indexes."""
        self._primitives_by_name = None
        self._primitives_by_net = None
        self._primitives_by_layer = None

    @property
    @deprecated_property("use edb.layout.primitives property instead.", category=None)
    def primitives(self):
        """Primitives.

        .. deprecated:: 0.70.0
           Use :attr:`edb.layout.primitives` instead.

        Returns
        -------
        list of :class:`pyedb.grpc.database.primitives.Primitive`
            List of primitives.
        """
        warnings.warn("Deprecated. Use `edb.layout.primitives` instead.", DeprecationWarning, stacklevel=2)
        return self._pedb.layout.primitives

    @property
    @deprecated_property("use layout.primitives_by_layer property instead.")
    def primitives_by_layer(self):
        """Primitives organized by layer names.

        .. deprecated:: 0.70.0
        use layout.primitives_by_layer property instead.

        """
        return self._pedb.layout.primitives_by_layer

    @deprecated("use layout.find_object_by_id instead.")
    def get_primitive(self, primitive_id: int) -> list[Primitive]:
        """Retrieve primitive from give id.

        .. deprecated:: 0.70.0
        use layout.find_object_by_id method instead.

        Parameters
        ----------
        primitive_id : int
            Primitive id.

        Returns
        -------
        list of :class:`pyedb.grpc.database.primitive.primitive.Primitive`
            List of primitives.
        """
        return self._pedb.layout.find_object_by_id(primitive_id)

    @property
    @deprecated_property("use layout.polygons_by_layer property instead.")
    def polygons_by_layer(self) -> dict[str, List[Polygon]]:
        """Primitives with layer names as keys.

        .. deprecated:: 0.70.0
        use layout.polygons_by_layer property instead.

        Returns
        -------
        dict
            Dictionary of polygons with layer names as keys.
        """
        return self._pedb.layout.polygons_by_layer

    @property
    @deprecated_property("use layout.rectangles property instead.")
    def rectangles(self) -> List[Union[Rectangle, Primitive]]:
        """All rectangle primitives.

        Returns
        -------
        list
            List of :class:`pyedb.grpc.database.edb_data.primitives_data.Rectangle` objects.
        """
        return self._pedb.layout.rectangles

    @property
    @deprecated_property("use layout.circles property instead.")
    def circles(self) -> List[Union[Circle, Primitive]]:
        """All circle primitives.

        .. deprecated:: 0.70.0
        use layout.circles instead.

        Returns
        -------
        list
            List of :class:`pyedb.grpc.database.edb_data.primitives_data.Circle` objects.
        """
        return self._pedb.layout.circles

    @property
    @deprecated_property("use layout.paths property instead.")
    def paths(self) -> List[Union[Path, Primitive]]:
        """All path primitives.

        .. deprecated:: 0.70.0
        use layout.paths instead.

        Returns
        -------
        list
            List of :class:`pyedb.grpc.database.edb_data.primitives_data.Path` objects.
        """
        return self._pedb.layout.paths

    @property
    def texts(self) -> List[Union[Text, Primitive]]:
        """All text primitives.

        Returns
        -------
        list
            List of :class:`pyedb.grpc.database.edb_data.primitives_data.Text` objects.
        """
        return [i for i in self._pedb.layout.primitives if i.primitive_type == "text"]

    @property
    @deprecated_property("use layout.polygons property instead.")
    def polygons(self) -> List[Union[Polygon, Primitive]]:
        """All polygon primitives.

        .. deprecated:: 0.70.0
        use layout.polygons instead.

        Returns
        -------
        list
            List of :class:`pyedb.grpc.database.primitive.polygon.Polygon` objects.
        """
        return self._pedb.layout.polygons

    @property
    @deprecated_property("use layout.primitives_by_net property instead.")
    def primitives_by_net(self) -> dict[str, List[Primitive]]:
        """Primitives with net names as keys.

        .. deprecated:: 0.70.0
        use layout.primitives_by_net instead.

        Returns
        -------
        dict
            Dictionary of primitives with net names as keys.
        """
        return self._pedb.layout.primitives_by_net

    @deprecated("use layout.get_polygons_by_layer method instead.")
    def get_polygons_by_layer(self, layer_name: str, net_list: Optional[List[str]] = None) -> List[Primitive]:
        """Retrieve polygons by layer.

        .. deprecated:: 0.70.0
        use layout.get_polygons_by_layer method instead.

        Parameters
        ----------
        layer_name : str
            Layer name.
        net_list : list, optional
            List of net names to filter by.

        Returns
        -------
        list
            List of polygon objects.
        """
        return self._pedb.layout.get_polygons_by_layer(layer=layer_name, nets=net_list)

    @deprecated("use layout.get_primitive_by_layer_and_point method instead.")
    def get_primitive_by_layer_and_point(
        self,
        point: Optional[List[float]] = None,
        layer: Optional[Union[str, List[str]]] = None,
        nets: Optional[Union[str, List[str]]] = None,
    ) -> List[Primitive]:
        """Get primitive at specified point on layer.

        Parameters
        ----------
        point : list, optional
            [x, y] coordinate point.
        layer : str or list, optional
            Layer name(s) to filter by.
        nets : str or list, optional
            Net name(s) to filter by.

        Returns
        -------
        list
            List of primitive objects at the point.

        Raises
        ------
        ValueError
            If point is invalid.
        """
        return self._pedb.layout.get_primitive_by_layer_and_point(point=point, layer=layer, nets=nets)

    @deprecated("use layout.get_polygon_bounding_box method instead.")
    def get_polygon_bounding_box(self, polygon: Primitive) -> List[float]:
        """Get bounding box of polygon.

        .. deprecated:: 0.70.0
        use layout.get_polygon_bounding_box method instead.

        Parameters
        ----------
        polygon : :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Polygon primitive.

        Returns
        -------
        list
            Bounding box coordinates [min_x, min_y, max_x, max_y].
        """
        return self._pedb.layout.get_polygon_bounding_box(polygon)

    @deprecated("use layout.get_polygon_points method instead.")
    def get_polygon_points(self, polygon) -> List[List[float]]:
        """Get points defining a polygon.

        .. deprecated:: 0.70.0
        use layout.get_polygon_points method instead.

        Parameters
        ----------
        polygon : :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Polygon primitive.

        Returns
        -------
        list
            List of point coordinates.
        """
        return self._pedb.layout.get_polygon_points(polygon)

    def parametrize_polygon(self, polygon, selection_polygon, offset_name="offsetx", origin=None) -> bool:
        """Parametrize polygon points based on another polygon.

        Parameters
        ----------
        polygon : :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Polygon to parametrize.
        selection_polygon : :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Polygon used for selection.
        offset_name : str, optional
            Name of offset parameter.
        origin : list, optional
            [x, y] origin point for vector calculation.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        bound_center = polygon_data.bounding_circle()[0]
        bound_center2 = selection_polygon_data.bounding_circle()[0]
        center = [self._pedb.value(bound_center[0]), self._pedb.value(bound_center[1])]
        center2 = [self._pedb.value(bound_center2[0]), self._pedb.value(bound_center2[1])]
        x1, y1 = calc_slope(center2, center)

        if not origin:
            origin = [center[0] + float(x1) * 10000, center[1] + float(y1) * 10000]
        self._pedb.add_design_variable(offset_name, 0.0)
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = polygon_data.points[i]
                if prev_point != point:
                    check_inside = selection_polygon_data.is_inside(point)
                    if check_inside:
                        xcoeff, ycoeff = calc_slope([self._pedb.value(point.x), self._pedb.value(point.x)], origin)

                        new_points = CorePointData(
                            [
                                self._pedb.value(str(self._pedb.value(point.x) + f"{xcoeff}*{offset_name}")),
                                self._pedb.value(str(self._pedb.value(point.y)) + f"{ycoeff}*{offset_name}"),
                            ]
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

    def _create_path(
        self,
        points,
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
        points: .:class:`dotnet.database.layout.Shape`
            List of points.
        layer_name : str
            Name of the layer on which to create the path.
        width : float, optional
            Width of the path. The default is ``1``.
        net_name: str, optional
            Name of the net. The default is ``""``.
        start_cap_style : str, optional
            Style of the cap at its start. Options are ``"Round"``,
            ``"Extended", `` and ``"Flat"``. The default is
            ``"Round".
        end_cap_style : str, optional
            Style of the cap at its end. Options are ``"Round"``,
            ``"Extended", `` and ``"Flat"``. The default is
            ``"Round".
        corner_style : str, optional
            Style of the corner. Options are ``"Round"``,
            ``"Sharp"`` and ``"Mitered"``. The default is ``"Round".

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            ``True`` when successful, ``False`` when failed.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        _points = []
        if isinstance(points, (list, tuple)):
            points = normalize_pairs(points)
            for pt in points:
                _pt = []
                for coord in pt:
                    coord = self._pedb.value(coord)
                    _pt.append(coord)
                _points.append(_pt)
            points = _points
            width = self._pedb.value(width)
            polygon_data = CorePolygonData(points)
        elif isinstance(points, CorePolygonData):
            polygon_data = points
        else:
            raise TypeError("Points must be a list of points or a PolygonData object.")
        path = Path.create(
            layout=self._pedb.active_layout,
            layer=layer_name,
            net=net,
            width=width,
            end_cap1=start_cap_style,
            end_cap2=end_cap_style,
            corner_style=corner_style,
            points=polygon_data,
        )
        if path.is_null:  # pragma: no cover
            self._pedb.logger.error("Null path created")
            return False
        return path

    def create_trace(
        self,
        path_list: Union[Iterable[float], CorePolygonData],
        layer_name: str,
        width: float = 1,
        net_name: str = "",
        start_cap_style: str = "Round",
        end_cap_style: str = "Round",
        corner_style: str = "Round",
    ) -> Optional[Primitive]:
        """Create trace path.

        Parameters
        ----------
        path_list : Iterable
            List of points [x,y] or [[x, y], ...]
            or [(x, y)...].
        layer_name : str
            Layer name.
        width : float, optional
            Trace width.
        net_name : str, optional
            Associated net name.
        start_cap_style : str, optional
            Start cap style ("Round", "Extended", "Flat").
        end_cap_style : str, optional
            End cap style ("Round", "Extended", "Flat").
        corner_style : str, optional
            Corner style ("Round", "Sharp", "Mitered").

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Path` or bool
            Path object if created, False otherwise.
        """

        primitive = self._create_path(
            points=path_list,
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
        points: Union[List[List[float]], CorePolygonData],
        layer_name: str,
        voids: Optional[List[Any]] = [],
        net_name: str = "",
    ) -> Union[Optional[Primitive], bool]:
        """Create polygon primitive.

        Parameters
        ----------
        points : list or :class:`ansys.edb.core.geometry.polygon_data.PolygonData`
            Polygon points or PolygonData object.
        layer_name : str
            Layer name.
        voids : list, optional
            List of void shapes or points.
        net_name : str, optional
            Associated net name.

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Polygon` or bool
            Polygon object if created, False otherwise.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if isinstance(points, list):
            new_points = []
            for idx, i in enumerate(points):
                new_points.append(CorePointData([self._pedb.value(i[0]), self._pedb.value(i[1])]))
            polygon_data = CorePolygonData(points=new_points)

        elif isinstance(points, CorePolygonData):
            polygon_data = points
        else:
            polygon_data = points
        if not polygon_data.points:
            raise RuntimeError("Failed to create main shape polygon data")
        for void in voids:
            if isinstance(void, list):
                void_polygon_data = CorePolygonData(points=void)
            elif isinstance(void, CorePolygonData):
                void_polygon_data = void
            elif isinstance(void, PolygonData):
                void_polygon_data = void.core
            elif isinstance(void, Polygon | Rectangle | Circle | Primitive):
                void_polygon_data = void.polygon_data.core
            else:
                raise TypeError("Unsupported void format.")
            if not void_polygon_data.points:
                raise RuntimeError("Failed to create void polygon data")
            polygon_data.holes.append(void_polygon_data)
        polygon = Polygon.create(layout=self._pedb.active_layout, layer=layer_name, net=net, polygon_data=polygon_data)
        if polygon.is_null or polygon_data is False:  # pragma: no cover
            raise RuntimeError("Null polygon created")
        return polygon

    def create_rectangle(
        self,
        layer_name: str,
        net_name: str = "",
        lower_left_point: str = "",
        upper_right_point: str = "",
        center_point: str = "",
        width: Union[str, float] = "",
        height: Union[str, float] = "",
        representation_type: str = "lower_left_upper_right",
        corner_radius: str = "0mm",
        rotation: str = "0deg",
    ) -> Optional[Primitive]:
        """Create rectangle primitive.

        Parameters
        ----------
        layer_name : str
            Layer name.
        net_name : str, optional
            Associated net name.
        lower_left_point : list
            Required for representation type: "lower_left_upper_right"
            [x,y] lower left point.
        upper_right_point : list
            Required for representation type: "lower_left_upper_right"
            [x,y] upper right point.
        center_point : list
            Required for representation type: "center_width_height"
            [x,y] center point.
        width : str or float, optional
            Required for representation type: "center_width_height"
            Rectangle width.
        height : str or float, optional
             Required for representation type: "center_width_height"
            Rectangle height.
        representation_type : str, optional
            "lower_left_upper_right" or "center_width_height". Default value is "lower_left_upper_right".
        corner_radius : str, optional
            Corner radius with units.
        rotation : str, optional
            Rotation angle with units.

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Rectangle` or bool
            Rectangle object if created, False otherwise.
        """
        net = self._pedb.nets.find_or_create_net(net_name)
        if representation_type == "lower_left_upper_right":
            rect = Rectangle(self._pedb).create(
                layout=self._pedb.active_layout,
                layer=layer_name,
                net=net.core,
                rep_type=representation_type,
                param1=self._pedb.value(lower_left_point[0]),
                param2=self._pedb.value(lower_left_point[1]),
                param3=self._pedb.value(upper_right_point[0]),
                param4=self._pedb.value(upper_right_point[1]),
                corner_rad=self._pedb.value(corner_radius),
                rotation=self._pedb.value(rotation),
            )
        else:
            rep_type = "center_width_height"
            if isinstance(width, str):
                if width in self._pedb.variables:
                    width = self._pedb.value(width, self._pedb.active_cell)
                else:
                    width = self._pedb.value(width)
            else:
                width = self._pedb.value(width)
            if isinstance(height, str):
                if height in self._pedb.variables:
                    height = self._pedb.value(height, self._pedb.active_cell)
                else:
                    height = self._pedb.value(width)
            else:
                height = self._pedb.value(width)
            rect = Rectangle.create(
                layout=self._pedb.active_layout,
                layer=layer_name,
                net=net.core,
                rep_type=rep_type,
                param1=self._pedb.value(center_point[0]),
                param2=self._pedb.value(center_point[1]),
                param3=self._pedb.value(width),
                param4=self._pedb.value(height),
                corner_rad=self._pedb.value(corner_radius),
                rotation=self._pedb.value(rotation),
            )
        if not rect.is_null:
            return rect
        return False

    def create_circle(
        self, layer_name: str, x: Union[float, str], y: Union[float, str], radius: Union[float, str], net_name: str = ""
    ) -> Optional[Primitive]:
        """Create circle primitive.

        Parameters
        ----------
        layer_name : str
            Layer name.
        x : float
            Center x-coordinate.
        y : float
            Center y-coordinate.
        radius : float
            Circle radius.
        net_name : str, optional
            Associated net name.

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Circle` or bool
            Circle object if created, False otherwise.
        """
        edb_net = self._pedb.nets.find_or_create_net(net_name)

        circle = Circle(self._pedb).create(
            layout=self._pedb.active_layout,
            layer=layer_name,
            net=edb_net,
            center_x=self._pedb.value(x),
            center_y=self._pedb.value(y),
            radius=self._pedb.value(radius),
        )
        if not circle.is_null:
            return circle
        return False

    def create_text(
        self, layer_name: str, x: Union[float, str], y: Union[float, str], text: str
    ) -> Optional[Primitive]:
        """Create text primitive.

        Parameters
        ----------
        layer_name : str
            Layer name.
        x : float
            Center x-coordinate.
        y : float
            Center y-coordinate.
        text : str
            Text of the displayed object.

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Text` or bool
            Text object if created, False otherwise.
        """
        text = Text.create(
            layout=self._pedb.active_layout,
            layer=layer_name,
            center_x=self._pedb.value(x),
            center_y=self._pedb.value(y),
            text=text,
        )
        if not text.is_null:
            return text
        return False

    def delete_primitives(self, net_names: Union[str, List[str]]) -> bool:
        """Delete primitives by net name(s).

        Parameters
        ----------
        net_names : str or list
            Net name(s).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p in self.primitives[:]:
            if p.net_name in net_names:
                p.delete()
        return True

    def get_primitives(
        self,
        net_name: Optional[str] = None,
        layer_name: Optional[str] = None,
        prim_type: Optional[str] = None,
        is_void: Optional[bool] = None,
    ) -> List[Primitive]:
        """Get primitives with filtering.

        Parameters
        ----------
        net_name : str, optional
            Net name filter.
        layer_name : str, optional
            Layer name filter.
        prim_type : str, optional
            Primitive type filter.
        is_void : bool, optional
            Void primitive filter. When ``None``, both standard primitives and voids are returned.

        Returns
        -------
        list
            List of filtered primitives.
        """
        return self._pedb.layout.filter_primitives(
            net_name=net_name,
            layer_name=layer_name,
            prim_type=prim_type,
            is_void=is_void,
        )

    def fix_circle_void_for_clipping(self) -> bool:
        """Fix circle void clipping issues.

        Returns
        -------
        bool
            True if changes made, False otherwise.
        """
        for void_circle in self.circles:
            if not void_circle.is_void:
                continue
            circ_params = void_circle.get_parameters()

            cloned_circle = Circle.create(
                layout=self._pedb.active_layout,
                layer=void_circle.layer_name,
                net=void_circle.net,
                center_x=self._pedb.value(circ_params[0]),
                center_y=self._pedb.value(circ_params[1]),
                radius=self._pedb.value(circ_params[2]),
            )
            if not cloned_circle.is_null:
                cloned_circle.is_negative = True
                void_circle.delete()
        return True

    def _validatePoint(self, point, allowArcs=True):
        if len(point) == 2:
            if not isinstance(point[0], (int, float, str)):
                self._pedb.logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):
                self._pedb.logger.error("Point Y value must be a number.")
                return False
            return True
        elif len(point) == 3:
            if not allowArcs:  # pragma: no cover
                self._pedb.logger.error("Arc found but arcs are not allowed in _validatePoint.")
                return False
            if not isinstance(point[0], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Point Y value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Invalid point height.")
                return False
            return True
        elif len(point) == 5:
            if not allowArcs:  # pragma: no cover
                self._pedb.logger.error("Arc found but arcs are not allowed in _validatePoint.")
                return False
            if not isinstance(point[0], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Point Y value must be a number.")
                return False
            if not isinstance(point[2], str) or point[2] not in ["cw", "ccw"]:
                self._pedb.logger.error("Invalid rotation direction {} is specified.")
                return False
            if not isinstance(point[3], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Arc center point X value must be a number.")
                return False
            if not isinstance(point[4], (int, float, str)):  # pragma: no cover
                self._pedb.logger.error("Arc center point Y value must be a number.")
                return False
            return True
        else:  # pragma: no cover
            self._pedb.logger.error("Arc point descriptor has incorrect number of elements (%s)", len(point))
            return False

    def parametrize_trace_width(
        self,
        nets_name: Union[str, List[str]],
        layers_name: Optional[Union[str, List[str]]] = None,
        parameter_name: str = "trace_width",
        variable_value: Optional[Union[float, str]] = None,
    ) -> bool:
        """Parametrize trace width.

        Parameters
        ----------
        nets_name : str or list
            Net name(s).
        layers_name : str or list, optional
            Layer name(s) filter.
        parameter_name : str, optional
            Parameter name prefix.
        variable_value : float or str, optional
            Initial parameter value.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(nets_name, str):
            nets_name = [nets_name]
        if isinstance(layers_name, str):
            layers_name = [layers_name]
        for net_name in nets_name:
            for p in self.paths:
                _parameter_name = f"{parameter_name}_{p.id}"
                if not p.net.is_null:
                    if p.net.name == net_name:
                        if not layers_name:
                            if not variable_value:
                                variable_value = p.width
                            self._pedb.active_cell.add_variable(
                                name=_parameter_name, value=self._pedb.value(variable_value), is_param=True
                            )
                            p.width = self._pedb.value(_parameter_name)
                        elif p.layer.name in layers_name:
                            if not variable_value:
                                variable_value = p.width
                            self._pedb.add_design_variable(parameter_name, variable_value, True)
                            p.width = self._pedb.value(_parameter_name)
        return True

    def unite_polygons_on_layer(
        self,
        layer_name: Optional[Union[str, List[str]]] = None,
        delete_padstack_gemometries: bool = False,
        net_names_list: Optional[List[str]] = None,
    ) -> bool:
        """Unite polygons on layer.

        Parameters
        ----------
        layer_name : str or list, optional
            Layer name(s) to process.
        delete_padstack_gemometries : bool, optional
            Whether to delete padstack geometries.
        net_names_list : list, optional
            Net names filter.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(layer_name, str):
            layer_name = [layer_name]
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        if net_names_list is None:
            net_names_list = []

        for lay in layer_name:
            self._pedb.logger.info(f"Uniting Objects on layer {lay}.")
            poly_by_nets = {}
            all_voids = []
            list_polygon_data = []
            delete_list = []
            for poly in self.polygons_by_layer.get(lay, []):
                if poly.net_name:
                    poly_by_nets.setdefault(poly.net_name, []).append(poly)
            for net, polys in poly_by_nets.items():
                if net in net_names_list or not net_names_list:
                    for p in polys:
                        list_polygon_data.append(p.core.polygon_data)
                        delete_list.append(p)
                        all_voids.extend([v for v in p.voids])
            united = CorePolygonData.unite(list_polygon_data)
            for item in united:
                _added_voids = []
                for void in all_voids:
                    if item.intersection_type(void.core.polygon_data).value == 2:
                        _added_voids.append(void)
                self.create_polygon(item, layer_name=lay, voids=_added_voids, net_name=net)
            for void in all_voids:
                for poly in poly_by_nets[net]:  # pragma no cover
                    if void.core.polygon_data.intersection_type(poly.core.polygon_data).value >= 2:
                        try:
                            id = delete_list.index(poly)
                        except ValueError:
                            id = -1
                        if id >= 0:
                            delete_list.pop(id)
            self.clear_cache()
            for poly in delete_list:
                poly.delete()
        if delete_padstack_gemometries:
            self._pedb.logger.info("Deleting Padstack Definitions")
            for pad in self._pedb.padstacks.definitions:
                p1 = self._pedb.padstacks.definitions[pad].edb_padstack.data
                if len(p1.get_layer_names()) > 1:
                    self._pedb.padstacks.remove_pads_from_padstack(pad)
        self.clear_cache()
        return True

    def defeature_polygon(self, poly: Polygon, tolerance: float = 0.001) -> bool:
        """Defeature polygon.

        Parameters
        ----------
        poly : :class:`pyedb.grpc.database.edb_data.primitives_data.Polygon`
            Polygon to defeature.
        tolerance : float, optional
            Maximum surface deviation tolerance.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        new_poly = poly.polygon_data.core.defeature(tol=tolerance)
        if not new_poly.points:
            self._pedb.logger.error(
                f"Defeaturing on polygon {poly.id} returned empty polygon, tolerance threshold might too large. "
            )
            return False
        poly.core.polygon_data = new_poly
        return True

    def get_layout_statistics(
        self, evaluate_area: bool = False, net_list: Optional[List[str]] = None
    ) -> LayoutStatistics:
        """Get layout statistics.

        Parameters
        ----------
        evaluate_area : bool, optional
            Whether to compute metal area statistics.
        net_list : list, optional
            Net list for area computation.

        Returns
        -------
        :class:`LayoutStatistics`
            Layout statistics object.
        """
        stat_model = LayoutStatistics()
        stat_model.num_layers = len(list(self._pedb.stackup.layers.values()))
        stat_model.num_capacitors = len(self._pedb.components.capacitors)
        stat_model.num_resistors = len(self._pedb.components.resistors)
        stat_model.num_inductors = len(self._pedb.components.inductors)
        bbox = self._pedb._hfss.get_layout_bounding_box(self._pedb.active_layout)
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
                        if prim.primitive_type.name == "PATH":
                            surface += Path(self._pedb, prim).length * self._pedb.value(prim.cast().width)
                        if prim.primitive_type.name == "POLYGON":
                            surface += prim.polygon_data.area()
                            stat_model.occupying_surface[layer] = round(surface, 6)
                            stat_model.occupying_ratio[layer] = round(surface / outline_surface, 6)
        return stat_model

    def create_bondwire(
        self,
        definition_name: str,
        placement_layer: str,
        width: Union[float, str],
        material: str,
        start_layer_name: str,
        start_x: Union[float, str],
        start_y: Union[float, str],
        end_layer_name: str,
        end_x: Union[float, str],
        end_y: Union[float, str],
        net: str,
        start_cell_instance_name: Optional[str] = None,
        end_cell_instance_name: Optional[str] = None,
        bondwire_type: str = "jedec4",
    ) -> Bondwire:
        """Create bondwire.

        Parameters
        ----------
        definition_name : str
            Bondwire definition name.
        placement_layer : str
            Placement layer name.
        width : float or str
            Bondwire width.
        material : str
            Material name.
        start_layer_name : str
            Start layer name.
        start_x : float or str
            Start x-coordinate.
        start_y : float or str
            Start y-coordinate.
        end_layer_name : str
            End layer name.
        end_x : float or str
            End x-coordinate.
        end_y : float or str
            End y-coordinate.
        net : str
            Associated net name.
        start_cell_instance_name : str, optional
            Start cell instance name.
        end_cell_instance_name : str, optional
            End cell instance name.
        bondwire_type : str, optional
            Bondwire type ("jedec4", "jedec5", "apd").

        Returns
        -------
        :class:`pyedb.grpc.database.edb_data.primitives_data.Bondwire` or bool
            Bondwire object if created, False otherwise.
        """

        from ansys.edb.core.hierarchy.cell_instance import (
            CellInstance as GrpcCellInstance,
        )

        start_cell_inst = None
        end_cell_inst = None
        cell_instances = {cell_inst.name: cell_inst for cell_inst in self._pedb.active_layout.core.cell_instances}
        if start_cell_instance_name:
            if start_cell_instance_name not in cell_instances:
                start_cell_inst = GrpcCellInstance.create(
                    self._pedb.active_layout.core, start_cell_instance_name, ref=self._pedb.active_layout.core
                )
            else:
                start_cell_inst = cell_instances[start_cell_instance_name]
                cell_instances = {cell_inst.name: cell_inst for cell_inst in self._pedb.active_layout.cell_instances}
        if end_cell_instance_name:
            if end_cell_instance_name not in cell_instances:
                end_cell_inst = GrpcCellInstance.create(
                    self._pedb.active_layout, end_cell_instance_name, ref=self._pedb.active_layout
                )
            else:
                end_cell_inst = cell_instances[end_cell_instance_name]
        bw = Bondwire.create(
            layout=self._pedb.active_layout,
            bondwire_type=bondwire_type,
            definition_name=definition_name,
            placement_layer=placement_layer,
            width=self._pedb.value(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=self._pedb.value(start_x),
            start_y=self._pedb.value(start_y),
            end_layer_name=end_layer_name,
            end_x=self._pedb.value(end_x),
            end_y=self._pedb.value(end_y),
            net=net,
            end_cell_inst=end_cell_inst,
            start_cell_inst=start_cell_inst,
        )
        return bw

    def create_pin_group(
        self,
        name: str,
        pins_by_id: Optional[List[int]] = None,
        pins_by_aedt_name: Optional[List[str]] = None,
        pins_by_name: Optional[List[str]] = None,
    ) -> bool:
        """Create pin group.

        Parameters
        ----------
        name : str
            Pin group name.
        pins_by_id : list, optional
            List of pin IDs.
        pins_by_aedt_name : list, optional
            List of pin AEDT names.
        pins_by_name : list, optional
            List of pin names.

        Returns
        -------
        :class:`pyedb.grpc.database.siwave.pin_group.PinGroup` or bool
            PinGroup object if created, False otherwise.
        """
        # TODO move this method to components and merge with existing one
        pins = {}
        if pins_by_id:
            if isinstance(pins_by_id, int):
                pins_by_id = [pins_by_id]
            for p in pins_by_id:
                edb_pin = None
                if p in self._pedb.padstacks.instances:
                    edb_pin = self._pedb.padstacks.instances[p]
                if edb_pin and not p in pins:
                    pins[p] = edb_pin
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
            _pins = {pin.id: pin for pin in p_inst if pin.aedt_name in pins_by_aedt_name or pin.name in pins_by_name}
            if not pins:
                pins = _pins
            else:
                for id, pin in _pins.items():
                    if not id in pins:
                        pins[id] = pin
        if not pins:
            self._pedb.logger.error("No pin found.")
            return False
        pins = list(pins.values())
        obj = PinGroup.create(layout=self._pedb.active_layout, name=name, padstack_instances=pins)
        if obj.is_null:
            raise RuntimeError(f"Failed to create pin group {name}.")
        else:
            net_obj = [i.net for i in pins if not i.net.is_null]
            if net_obj:
                obj.net = net_obj[0]
        return self._pedb.siwave.pin_groups[name]

    @staticmethod
    def add_void(shape: "Primitive", void_shape: Union["Primitive", List["Primitive"]]) -> bool:
        """Add void to shape.

        Parameters
        ----------
        shape : :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Main shape.
        void_shape : list or :class:`pyedb.grpc.database.edb_data.primitives_data.Primitive`
            Void shape(s).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not isinstance(void_shape, list):
            void_shape = [void_shape]
        for void in void_shape:
            if isinstance(void, Primitive):
                shape.core.add_void(void.core)
                flag = True
            else:
                shape.core.add_void(void.core)
                flag = True
            if not flag:
                return flag
        return True

    def insert_layout_instance_on_layer(
        self,
        cell_name: str,
        placement_layer: str,
        rotation: Union[float, str] = 0.0,
        rotation_x: float | str = 0,
        rotation_y: float | str = 0,
        x: float | str = 0,
        y: float | str = 0,
        place_on_bottom: bool = False,
        local_origin_x: float | str | None = 0,
        local_origin_y: float | str | None = 0,
    ) -> Any:
        """Insert a layout instance into the active layout.

        Parameters
        ----------
        cell_name: str
            Name of the layout to insert.
        placement_layer: str
            Placement Layer.
        rotation : float or str
            Rotation angle around Z-axis, specified counter-clockwise in radians.
        rotation_x : float or str
            Rotation angle around X-axis, specified counter-clockwise in radians.
        rotation_y : float or str
            Rotation angle around Y-axis, specified counter-clockwise in radians.
        x : float or str
            X offset.
        y : float or str
            Y offset.
        place_on_bottom : bool
            Whether to place the layout instance on the bottom of the layer.
        local_origin_x: float or str
            Local origin X coordinate.
        local_origin_y: float or str
            Local origin Y coordinate.
        """

        placement_layer = self._pedb.stackup.layers[placement_layer]
        if not place_on_bottom:
            cell_inst = self.insert_layout_instance_placement_3d(
                cell_name=cell_name,
                x=x,
                y=y,
                z=placement_layer.upper_elevation,
                rotation_x=rotation_x,
                rotation_y=rotation_y,
                rotation_z=rotation,
                local_origin_x=local_origin_x,
                local_origin_y=local_origin_y,
            )
        else:
            cell_inst = self.insert_layout_instance_placement_3d(
                cell_name=cell_name,
                x=x,
                y=y,
                z=placement_layer.lower_elevation,
                rotation_x=self._pedb.value(rotation_x) + self._pedb.value("180deg"),
                rotation_y=rotation_y,
                rotation_z=rotation,
                local_origin_x=local_origin_x,
                local_origin_y=local_origin_y,
            )
        return cell_inst

    def insert_layout_instance_placement_3d(
        self,
        cell_name: Union[str, Path],
        x: Union[float, str] = 0.0,
        y: Union[float, str] = 0.0,
        z: Union[float, str] = 0.0,
        rotation_x: Union[float, str] = 0.0,
        rotation_y: Union[float, str] = 0.0,
        rotation_z: Union[float, str] = 0.0,
        local_origin_x: Union[float, str] = 0.0,
        local_origin_y: Union[float, str] = 0.0,
        local_origin_z: Union[float, str] = 0.0,
    ) -> Any:
        """Insert a 3D component placement into the active layout.

        Parameters
        ----------
        cell_name: str
            Name of the layout to insert.
        x: float or str
            X coordinate.
        y: float or str
            Y coordinate.
        z: float or str
            Z coordinate.
        rotation_x: float or str
            Rotation angle around X-axis, specified counter-clockwise in radians.
        rotation_y: float or str
            Rotation angle around Y-axis, specified counter-clockwise in radians.
        rotation_z: float or str
            Rotation angle around Z-axis, specified counter-clockwise in radians.
        local_origin_x: float or str
            Local origin X coordinate.
        local_origin_y: float or str
            Local origin Y coordinate.
        local_origin_z: float or str
            Local origin Z coordinate.
        """

        from ansys.edb.core.geometry.point3d_data import Point3DData as GrpcPoint3DData
        from ansys.edb.core.hierarchy.cell_instance import CellInstance as GrpcCellInstance
        from ansys.edb.core.layout.cell import Cell, CellType

        from pyedb.generic.general_methods import generate_unique_name

        x_ = self._pedb.value(x)
        y_ = self._pedb.value(y)
        z_ = self._pedb.value(z)
        rotation_x_ = self._pedb.value(rotation_x)
        rotation_y_ = self._pedb.value(rotation_y)
        rotation_z_ = self._pedb.value(rotation_z)
        local_origin_x_ = self._pedb.value(local_origin_x)
        local_origin_y_ = self._pedb.value(local_origin_y)
        local_origin_z_ = self._pedb.value(local_origin_z)

        instance_name = generate_unique_name(cell_name, n=2)
        edb_cell = Cell.find(self._pedb._db, CellType.CIRCUIT_CELL, cell_name)
        cell_inst = GrpcCellInstance.create(self._pedb.active_layout.core, instance_name, edb_cell.layout)
        cell_inst.placement_3d = True
        t3d = cell_inst.transform3d

        # offsets
        location = GrpcPoint3DData(
            (local_origin_x_.core * -1),
            (local_origin_y_.core * -1),
            (local_origin_z_.core * -1),
        )
        t3d_offset = t3d.create_from_offset(offset=location)
        t3d = t3d + t3d_offset

        # Rotation X
        t3d_rotation_x = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(1.0, 0.0, 0.0), angle=self._pedb.value(rotation_x_)
        )
        t3d = t3d + t3d_rotation_x

        # Rotation Y
        t3d_rotation_y = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(0.0, 1.0, 0.0), angle=self._pedb.value(rotation_y_)
        )
        t3d = t3d + t3d_rotation_y

        # Rotation Z
        t3d_rotation_z = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(0.0, 0.0, 1.0), angle=self._pedb.value(rotation_z_)
        )
        t3d = t3d + t3d_rotation_z

        # Place
        location = GrpcPoint3DData(x_.core, y_.core, z_.core)
        t3d_offset = t3d.create_from_offset(offset=location)
        t3d = t3d + t3d_offset

        # Set transform3d back into instance
        cell_inst.transform3d = t3d
        return cell_inst

    def insert_3d_component_placement_3d(
        self,
        a3dcomp_path: Union[str, Path],
        x: Union[float, str] = 0.0,
        y: Union[float, str] = 0.0,
        z: Union[float, str] = 0.0,
        rotation_x: Union[float, str] = 0.0,
        rotation_y: Union[float, str] = 0.0,
        rotation_z: Union[float, str] = 0.0,
        local_origin_x: Union[float, str] = 0.0,
        local_origin_y: Union[float, str] = 0.0,
        local_origin_z: Union[float, str] = 0.0,
    ) -> Any:
        """Insert a 3D component placement into the active layout.

        Parameters
        ----------
        a3dcomp_path: str or Path
            File path to the 3D component.
        x: float or str
            X coordinate.
        y: float or str
            Y coordinate.
        z: float or str
            Z coordinate.
        rotation_x: float or str
            Rotation angle around X-axis, specified counter-clockwise in radians.
        rotation_y: float or str
            Rotation angle around Y-axis, specified counter-clockwise in radians.
        rotation_z: float or str
            Rotation angle around Z-axis, specified counter-clockwise in radians.
        local_origin_x: float or str
            Local origin X coordinate.
        local_origin_y: float or str
            Local origin Y coordinate.
        local_origin_z: float or str
            Local origin Z coordinate.
        """
        from ansys.edb.core.geometry.point3d_data import Point3DData as GrpcPoint3DData
        from ansys.edb.core.layout.mcad_model import McadModel as GrpcMcadModel

        x_ = self._pedb.value(x)
        y_ = self._pedb.value(y)
        z_ = self._pedb.value(z)
        rotation_x_ = self._pedb.value(rotation_x)
        rotation_y_ = self._pedb.value(rotation_y)
        rotation_z_ = self._pedb.value(rotation_z)
        local_origin_x_ = self._pedb.value(local_origin_x)
        local_origin_y_ = self._pedb.value(local_origin_y)
        local_origin_z_ = self._pedb.value(local_origin_z)

        mcad_model = GrpcMcadModel.create_3d_comp(layout=self._pedb.active_layout.core, filename=str(a3dcomp_path))
        cell_inst = mcad_model.cell_instance
        cell_inst.placement_3d = True
        t3d = cell_inst.transform3d

        # offsets
        location = GrpcPoint3DData(
            (local_origin_x_ * -1).core,
            (local_origin_y_ * -1).core,
            (local_origin_z_ * -1).core,
        )
        t3d_offset = t3d.create_from_offset(offset=location)
        t3d = t3d + t3d_offset

        # Rotation X
        t3d_rotation_x = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(1.0, 0.0, 0.0), angle=self._pedb.value(rotation_x_)
        )
        t3d = t3d + t3d_rotation_x

        # Rotation Y
        t3d_rotation_y = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(0.0, 1.0, 0.0), angle=self._pedb.value(rotation_y_)
        )
        t3d = t3d + t3d_rotation_y

        # Rotation Z
        t3d_rotation_z = t3d.create_from_axis_and_angle(
            axis=GrpcPoint3DData(0.0, 0.0, 1.0), angle=self._pedb.value(rotation_z_)
        )
        t3d = t3d + t3d_rotation_z

        # Place
        location = GrpcPoint3DData(x_.core, y_.core, z_.core)
        t3d_offset = t3d.create_from_offset(offset=location)
        t3d = t3d + t3d_offset

        # Set transform3d back into instance
        cell_inst.transform3d = t3d
        return cell_inst

    def insert_3d_component_on_layer(
        self,
        a3dcomp_path: str | Path,
        placement_layer: str,
        rotation: float | str = 0,
        rotation_x: float | str = 0,
        rotation_y: float | str = 0,
        x: float | str = 0,
        y: float | str = 0,
        place_on_bottom: bool = False,
        local_origin_x: float | str | None = 0,
        local_origin_y: float | str | None = 0,
        local_origin_z: float | str | None = 0,
    ) -> Any:
        """Insert a layout instance into the active layout.

        Parameters
        ----------
        a3dcomp_path: str or Path
            File path to the 3D component.
        placement_layer: str
            Placement Layer.
        rotation : float or str
            Rotation angle, specified counter-clockwise in radians.
        rotation_x : float or str
            Rotation angle, specified counter-clockwise in radians.
        rotation_y : float or str
            Rotation angle, specified counter-clockwise in radians.
        x : float or str
            X offset.
        y : float or str
            Y offset.
        place_on_bottom : bool
            Whether to place the layout instance on the bottom of the layer.
        local_origin_x: float or str
            Local origin X coordinate.
        local_origin_y: float or str
            Local origin Y coordinate.
        local_origin_z: float or str
            Local origin Z coordinate.
        """

        placement_layer = self._pedb.stackup.layers[placement_layer]
        if not place_on_bottom:
            cell_inst = self.insert_3d_component_placement_3d(
                a3dcomp_path=a3dcomp_path,
                x=x,
                y=y,
                z=placement_layer.upper_elevation,
                rotation_x=rotation_x,
                rotation_y=rotation_y,
                rotation_z=rotation,
                local_origin_x=local_origin_x,
                local_origin_y=local_origin_y,
                local_origin_z=local_origin_z,
            )
        else:
            cell_inst = self.insert_3d_component_placement_3d(
                a3dcomp_path=a3dcomp_path,
                x=x,
                y=y,
                z=placement_layer.lower_elevation,
                rotation_x=self._pedb.value(rotation_x) + self._pedb.value("180deg"),
                rotation_y=rotation_y,
                rotation_z=rotation,
                local_origin_x=local_origin_x,
                local_origin_y=local_origin_y,
                local_origin_z=local_origin_z,
            )
        return cell_inst

    def create_taper(
        self,
        start_point: tuple[str | float, str | float, str | float, str | float],
        end_point: tuple[str | float, str | float, str | float, str | float],
        start_width: str | float,
        end_width: str | float,
        layer_name: str = "",
        voids: list | None = None,
        net_name: str = "",
    ) -> Polygon:
        """Create an RF trace taper polygon between two points.

        The taper is a trapezoidal polygon with ``start_width`` at ``start_point``
        and ``end_width`` at ``end_point``, rotated to match the direction between
        the two points.

        .. code-block:: text

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
        start_point : tuple[str or float, str or float]
            Start point coordinates as ``(x, y)``.
        end_point : tuple[str or float, str or float]
            End point coordinates as ``(x, y)``.
        start_width : str or float
            Width of the taper at the start point.
        end_width : str or float
            Width of the taper at the end point.
        layer_name : str, optional
            Name of the layer on which to create the taper. The default is ``""``.
        voids : list, optional
            List of void polygons to subtract from the taper. The default is ``None``.
        net_name : str, optional
            Net name to assign to the taper polygon. The default is ``""``.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
            Created taper polygon object.
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
            # [t_p0_x, t_p0_y],
        ]:
            temp = PointData.create(self._pedb, x=str(i[0]), y=str(i[1]))
            temp = temp.rotate(angle=str(angle), center=(0, 0))
            temp = temp.move(p0_x, p0_y)
            point_data.append(temp)
            poly_data = PolygonData.create(self._pedb, point_data, closed=True)
        _voids = [] if voids is None else voids
        return self.create_polygon(poly_data, layer_name=layer_name, voids=_voids, net_name=net_name)

    def open_solder_mask(
        self,
        open_components: bool = True,
        component_filter: list[str] | None = None,
        components_opening_offset: float | str = 0.0,
        open_voids: bool = True,
        voids_opening_offset: float | str = 0.0,
        open_traces: bool = True,
        traces_offset: float | str = 0.0,
        open_traces_net_filter: list[str] | None = None,
        solder_mask_layer_name: str = "Solder",
        solder_mask_thickness: float | str = "30um",
        solder_mask_material: str = "",
        reference_signal_layer: str = "",
        open_top: bool = True,
    ) -> bool:
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
        if not solder_mask_layer_name in self._pedb.stackup.layers:
            if open_top:
                method = "add_on_top"
            else:
                method = "add_below"
            self._pedb.stackup.add_layer(
                layer_name=solder_mask_layer_name,
                layer_type="signal",
                material=solder_mask_material,
                base_layer=reference_signal_layer,
                thickness=solder_mask_thickness,
                method=method,
                is_negative=True,
                filling_material="AIR",
            )
        if open_components:
            if component_filter:
                components = [
                    component
                    for ref_des, component in self._pedb.components.instances.items()
                    if ref_des in component_filter
                ]
                if not components:
                    raise ValueError(f"No components found for {component_filter}.")
            else:
                components = [
                    component
                    for component in list(self._pedb.components.instances.values())
                    if component.placement_layer == reference_signal_layer
                ]
            for component in components:
                comp_box = component.bounding_box
                x1 = comp_box[0] - self._pedb.value(components_opening_offset)
                y1 = comp_box[1] + self._pedb.value(components_opening_offset)
                x2 = comp_box[2] - self._pedb.value(components_opening_offset)
                y2 = comp_box[3] + self._pedb.value(components_opening_offset)
                self.create_rectangle(
                    layer_name=solder_mask_layer_name, lower_left_point=(x1, y1), upper_right_point=(x2, y2)
                )
        if open_voids:
            for primitive in self._pedb.layout.find_primitive(prim_type="polygon", layer_name=reference_signal_layer):
                if not primitive.has_voids:
                    continue
                for void in primitive.voids:
                    polygon_data = void.polygon_data
                    if voids_opening_offset:
                        polygon_data = polygon_data.expand(self._pedb.value(voids_opening_offset))
                    self.create_polygon(polygon_data, layer_name=solder_mask_layer_name, net_name="")
        if open_traces:
            traces = self._pedb.layout.find_primitive(
                prim_type="path", layer_name=reference_signal_layer, net_name=open_traces_net_filter
            )
            for trace in traces:
                polygon_data = trace.polygon_data
                if traces_offset:
                    polygon_data = polygon_data.expand(self._pedb.value(traces_offset))
                self.create_polygon(polygon_data, layer_name=solder_mask_layer_name, net_name="")
        return True

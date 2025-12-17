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
from typing import Any

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.layer.layer import LayerType as GrpcLayerType
from ansys.edb.core.primitive.circle import Circle as GrpcCircle

from pyedb.grpc.database.geometry.polygon_data import PolygonData
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.utilities import compute_arc_points
from pyedb.modeler.geometry_operators import GeometryOperators

layer_type_mapping = {
    "conducting": GrpcLayerType.CONDUCTING_LAYER,
    "air_lines": GrpcLayerType.AIRLINES_LAYER,
    "errors": GrpcLayerType.ERRORS_LAYER,
    "symbol": GrpcLayerType.SYMBOL_LAYER,
    "measure": GrpcLayerType.MEASURE_LAYER,
    "assembly": GrpcLayerType.ASSEMBLY_LAYER,
    "silkscreen": GrpcLayerType.SILKSCREEN_LAYER,
    "solder_mask": GrpcLayerType.SOLDER_MASK_LAYER,
    "solder_paste": GrpcLayerType.SOLDER_PASTE_LAYER,
    "glue": GrpcLayerType.GLUE_LAYER,
    "wirebond": GrpcLayerType.WIREBOND_LAYER,
    "user": GrpcLayerType.USER_LAYER,
    "siwave_hfss_solver_regions": GrpcLayerType.SIWAVE_HFSS_SOLVER_REGIONS,
    "postprocessing": GrpcLayerType.POST_PROCESSING_LAYER,
    "outline": GrpcLayerType.OUTLINE_LAYER,
    "layer_types_count": GrpcLayerType.LAYER_TYPES_COUNT,
    "undefined_layer_type": GrpcLayerType.UNDEFINED_LAYER_TYPE,
}


class Primitive:
    """Manages EDB functionalities for a primitives.
    It inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2025.2", grpc=True)
    >>> edb_prim = edb.modeler.primitives[0]
    """

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb
        self._core_stackup = pedb.stackup
        self._core_net = pedb.nets
        self._object_instance = None

    @property
    def type(self) -> str:
        """Type of the primitive.

        Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

        Returns
        -------
        str
        """
        return self.core.primitive_type.name.lower()

    @property
    def layout(self):
        """Layout object.

        Returns
        -------
        :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`

        """
        return self._pedb.layout

    @property
    def polygon_data(self):
        """Polygon data.

        Returns
        -------
        :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`

        """
        primitive = self.core.cast()
        return PolygonData(primitive.polygon_data) if hasattr(primitive, "polygon_data") else None

    @polygon_data.setter
    def polygon_data(self, value):
        """Set polygon data.

        Parameters
        ----------
        value : :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`

        """
        primitive = self.core.cast()
        if hasattr(primitive, "polygon_data"):
            if hasattr(value, "core"):
                primitive.polygon_data = value.core
            else:
                primitive.polygon_data = value

    @property
    def object_instance(self):
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`

        """
        if not self._object_instance:
            self._object_instance = self.core.layout.layout_instance.get_layout_obj_instance_in_context(self, None)
        return self._object_instance

    @property
    def net_name(self) -> str:
        """Net name.

        Returns
        -------
        str
            Net name.

        """
        if not self.core.net.is_null:
            return self.net.name

    @net_name.setter
    def net_name(self, value):
        if value in self._pedb.nets.nets:
            self.core.net = self._pedb.nets.nets[value]

    @property
    def layer_name(self) -> str:
        """Layer name.

        Returns
        -------
        str
            Layer name.
        """
        return self.core.layer.name

    @layer_name.setter
    def layer_name(self, value):
        if value in self._pedb.stackup.layers:
            self.core.layer = self._pedb.stackup.layers[value].core

    @property
    def voids(self) -> list[Any]:
        """Primitive voids.

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`

        """
        return [Primitive(self._pedb, prim) for prim in self.core.voids]

    @property
    def has_voids(self):
        """Check if primitive has voids.

        Returns
        -------
        bool
        """
        return self.core.has_voids

    @property
    def is_negative(self) -> bool:
        """Check if primitive is negative.

        Returns
        -------
        bool
        """
        return self.core.is_negative

    @is_negative.setter
    def is_negative(self, value: bool):
        """Set primitive as negative.

        Parameters
        ----------
        value : bool
            Either to set primitive as negative or not.

        """
        self.core.is_negative = value

    @property
    def is_parameterized(self) -> bool:
        """Check if any primitive is parameterized.

        Returns
        -------
        bool
            True if any primitive is parameterized, False otherwise.
        """
        return self.core.is_parameterized

    @property
    def is_zone_primitive(self) -> bool:
        """Check if primitive is a zone primitive.

        Returns
        -------
        bool
            True if primitive is a zone primitive, False otherwise.
        """
        return self.core.is_zone_primitive

    @property
    def can_be_zone_primitive(self):
        """Check if primitive can be a zone primitive.

        Returns
        -------
        bool
            True if primitive can be a zone primitive, False otherwise.
        """
        return self.core.can_be_zone_primitive

    @property
    def aedt_name(self) -> str:
        """Name to be visualized in AEDT.

        Returns
        -------
        str
            Name.
        """
        try:
            name = self.core.get_product_property(GrpcProductIdType.DESIGNER, 1)
            name = name.strip("'")
        except:
            name = ""
        if not name:
            if self.core.primitive_type.name.lower() == "path":
                ptype = "line"
            elif self.core.primitive_type.name.lower() == "rectangle":
                ptype = "rect"
            elif self.core.primitive_type.name.lower() == "polygon":
                ptype = "poly"
            elif self.core.primitive_type.name.lower() == "bondwire":
                ptype = "bwr"
            else:
                ptype = self.core.primitive_type.name.lower()
            name = "{}_{}".format(ptype, self.core.edb_uid)
            self.aedt_name = name
        return name

    @aedt_name.setter
    def aedt_name(self, value):
        self.core.set_product_property(GrpcProductIdType.DESIGNER, 1, value)

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]

        """
        return self._pedb.get_connected_objects(self.object_instance)

    def area(self, include_voids=True) -> float:
        """Return the total area.

        Parameters
        ----------
        include_voids : bool, optional
            Either if the voids have to be included in computation.
            The default value is ``True``.

        Returns
        -------
        float
        """
        area = self.core.cast().polygon_data.area()
        if include_voids:
            for el in self.voids:
                area -= el.polygon_data.area()
        return area

    def _get_points_for_plot(self, my_net_points, num):
        """
        Get the points to be plotted.
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            if not point.is_arc:
                x.append(Value(point.x))
                y.append(Value(point.y))
            else:
                arc_h = Value(point.arc_height)
                p1 = [Value(my_net_points[i - 1].x), Value(my_net_points[i - 1].y)]
                if i + 1 < len(my_net_points):
                    p2 = [Value(my_net_points[i + 1].x), Value(my_net_points[i + 1].y)]
                else:
                    p2 = [Value(my_net_points[0].x), Value(my_net_points[0].y)]
                x_arc, y_arc = compute_arc_points(p1, p2, arc_h, num)
                x.extend(x_arc)
                y.extend(y_arc)
        # fmt: on
        return x, y

    @property
    def center(self) -> tuple[float, float]:
        """Return the primitive bounding box center coordinate.

        Returns
        -------
        List[float, float]
            [x, y]

        """
        center = self.core.cast().polygon_data.bounding_circle()[0]
        return Value(center.x), Value(center.y)

    def get_connected_object_id_set(self) -> list[int]:
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        List[int]
            Found connected objects IDs with Layout object.
        """
        layout_inst = self.core.layout.layout_instance
        layout_obj_inst = layout_inst.get_layout_obj_instance_in_context(self.core, None)  # 2nd arg was []
        return [loi.layout_obj.id for loi in layout_inst.get_connected_objects(layout_obj_inst)]

    @property
    def bbox(self) -> list[float]:
        """Return the primitive bounding box points. Lower left corner, upper right corner.

        Returns
        -------
        List[float, float, float, float]
            [lower_left x, lower_left y, upper right x, upper right y]

        """
        bbox = self.core.cast().polygon_data.bbox()
        return [Value(bbox[0].x), Value(bbox[0].y), Value(bbox[1].x), Value(bbox[1].y)]

    def convert_to_polygon(self):
        """Convert path to polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
            Polygon when successful, ``False`` when failed.

        """
        if self.type == "path":
            polygon = self._pedb.modeler.create_polygon(self.polygon_data, self.layer_name, [], self.net.name)
            self.core.delete()
            self._pedb.modeler._reload_all()
            return polygon
        else:
            return False

    def intersection_type(self, primitive):
        """Get intersection type between actual primitive and another primitive or polygon data.

        Parameters
        ----------
        primitive : :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>>` or `PolygonData`

        Returns
        -------
        int
            Intersection type:
            0 - objects do not intersect,
            1 - this object fully inside other (no common contour points),
            2 - other object fully inside this,
            3 - common contour points,
            4 - undefined intersection.
        """
        if self.type in ["path, polygon"]:
            poly = primitive.polygon_data
            return self.polygon_data.intersection_type(poly).value
        else:
            return 4

    def is_intersecting(self, primitive) -> bool:
        """Check if actual primitive and another primitive or polygon data intesects.

        Parameters
        ----------
        primitive : :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>>` or `PolygonData`

        Returns
        -------
        bool
        """
        return True if self.intersection_type(primitive) >= 1 else False

    def get_closest_point(self, point) -> list[float]:
        """Get the closest point of the primitive to the input data.

        Parameters
        ----------
        point : list of float or PointData

        Returns
        -------
        List[float, float]
            [x, y].

        """
        if isinstance(point, (list, tuple)):
            point = GrpcPointData(point)

        p0 = self.core.cast().polygon_data.closest_point(point)
        return [Value(p0.x), Value(p0.y)]

    @property
    def arcs(self):
        """Get the Primitive Arc Data.

        Returns
        -------
        :class:`ArcData <ansys.edb.core.geometry.arc_data.ArcData>`
        """
        from pyedb.grpc.database.geometry.arc_data import ArcData

        return [ArcData(arc) for arc in self.polygon_data.core.arc_data]

    @property
    def longest_arc(self) -> float:
        """Longest arc.

        Returns
        -------
        float
            Arc length.
        """
        len = 0
        arc = None
        for i in self.arcs:
            if i.is_segment and i.length > len:
                arc = i
                len = i.length
        return arc

    def rotate(self, angle, center=None) -> bool:
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
        """
        if angle and hasattr(self, "polygon_data"):
            if center is None:
                center = self.core.cast().polygon_data.bounding_circle()[0]
            self.core.cast().polygon_data = self.polygon_data.rotate(angle * math.pi / 180, center)
            return True
        return False

    def move(self, vector) -> bool:
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
            _vector = [Value(pt) for pt in vector]
            self.core.cast().polygon_data = self.polygon_data.move(_vector)
            return True
        return False

    def scale(self, factor, center=None) -> bool:
        """Scales the polygon relative to a center point by a factor.

        Parameters
        ----------
        factor : float
            Scaling factor.
        center : List of float or str [x,y], optional
            If None scaling is done from polygon center.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(factor, str) and hasattr(self, "polygon_data"):
            factor = float(factor)
            if not center:
                center = self.core.cast().polygon_data.bounding_circle()[0]
            elif isinstance(center, list) and len(center) == 2:
                center = GrpcPointData([Value(center[0]), Value(center[1])])
            else:
                self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            self.cast().polygon_data = self.polygon_data.scale(factor, center)
            return True
        return False

    def subtract(self, primitives) -> list[Any]:
        """Subtract active primitive with one or more primitives.

        Parameters
        ----------
        primitives : :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
         or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
         or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
            List of Primitive objects.

        """
        poly = self.core.cast().polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        voids_of_prims = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.core.cast().polygon_data)
                for void in prim.voids:
                    voids_of_prims.append(void.cast().polygon_data)
            else:
                try:
                    primi_polys.append(prim.cast().polygon_data)
                except:
                    primi_polys.append(prim)
        for v in self.voids[:]:
            primi_polys.append(v.polygon_data)
        primi_polys = poly.unite(primi_polys)
        p_to_sub = poly.unite([poly] + voids_of_prims)
        list_poly = poly.subtract(p_to_sub, primi_polys)
        new_polys = []
        if list_poly:
            for p in list_poly:
                if not p.points:
                    continue
                new_polys.append(
                    self._pedb.modeler.create_polygon(p, self.layer_name, net_name=self.net.name, voids=[]),
                )
        self.core.delete()
        for prim in primitives:
            if isinstance(prim, Primitive):
                prim.core.delete()
        self._pedb.modeler._reload_all()
        return new_polys

    def intersect(self, primitives) -> list[Any]:
        """Intersect active primitive with one or more primitives.

        Parameters
        ----------
         primitives :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
         or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
         or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
            List of Primitive objects.

        """
        poly = self.core.cast().polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.polygon_data)
            else:
                if isinstance(prim, GrpcCircle):
                    primi_polys.append(prim.polygon_data)
                else:
                    primi_polys.append(prim.polygon_data)
        list_poly = poly.intersect([poly], primi_polys)
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if not p.points:
                    continue
                list_void = []
                void_to_subtract = []
                if voids:
                    for void in voids:
                        void_pdata = void.polygon_data
                        int_data2 = p.intersection_type(void_pdata).value
                        if int_data2 > 2 or int_data2 == 1:
                            void_to_subtract.append(void_pdata)
                        elif int_data2 == 2:
                            list_void.append(void_pdata)
                    if void_to_subtract:
                        polys_cleans = p.subtract(p, void_to_subtract)
                        for polys_clean in polys_cleans:
                            if polys_clean.points:
                                void_to_append = [v for v in list_void if polys_clean.intersection_type(v) == 2]
                        new_polys.append(
                            self._pedb.modeler.create_polygon(
                                polys_clean, self.layer_name, net_name=self.core.net.name, voids=void_to_append
                            )
                        )
                    else:
                        new_polys.append(
                            self._pedb.modeler.create_polygon(
                                p, self.layer_name, net_name=self.core.net.name, voids=list_void
                            )
                        )
                else:
                    new_polys.append(
                        self._pedb.modeler.create_polygon(
                            p, self.layer_name, net_name=self.core.net.name, voids=list_void
                        )
                    )
        self.core.delete()
        for prim in primitives:
            prim.delete()
        return new_polys

    def unite(self, primitives) -> list[Any]:
        """Unite active primitive with one or more primitives.

        Parameters
        ----------
         primitives : :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
         or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
         or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
            List of Primitive objects.

        """
        poly = self.polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.polygon_data)
            else:
                primi_polys.append(prim.polygon_data)
                primi_polys.append(prim)
        list_poly = poly.unite([poly] + primi_polys)
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if not p.points:
                    continue
                list_void = []
                if voids:
                    for void in voids:
                        void_pdata = void.polygon_data
                        int_data2 = p.intersection_type(void_pdata)
                        if int_data2 > 1:
                            list_void.append(void_pdata)
                new_polys.append(
                    self._pedb.modeler.create_polygon(p, self.layer_name, net_name=self.net.name, voids=list_void),
                )
        self.core.delete()
        for prim in primitives:
            if isinstance(prim, Primitive):
                prim.core.delete()
            else:
                try:
                    prim.delete()
                except AttributeError:
                    continue
        return new_polys

    def get_closest_arc_midpoint(self, point) -> list[float]:
        """Get the closest arc midpoint of the primitive to the input data.

        Parameters
        ----------
        point : List[float] or List[:class:`PointData <ansys.edb.core.geometry.point_data.PointData>`]

        Returns
        -------
        LIst[float, float]
            [x, y].
        """

        if isinstance(point, GrpcPointData):
            point = [Value(point.x), Value(point.y)]
        dist = 1e12
        out = None
        for arc in self.arcs:
            mid_point = arc.midpoint
            if GeometryOperators.points_distance(mid_point, point) < dist:
                out = arc.midpoint
                dist = GeometryOperators.points_distance(mid_point, point)
        return [Value(out[0]), Value(out[1])]

    @property
    def shortest_arc(self) -> float:
        """Longest arc.

        Returns
        -------
        float
            Arc length.
        """
        len = 1e12
        arc = None
        for i in self.arcs:
            if i.is_segment and i.length < len:
                arc = i
                len = i.length
        return arc

    def add_void(self, point_list) -> bool:
        """Add a void to current primitive.

        Parameters
        ----------
        point_list : list or :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>` \
            or point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

        Returns
        -------
        bool
            ``True`` if successful, either  ``False``.
        """
        if isinstance(point_list, list):
            plane = self._pedb.modeler.Shape("polygon", points=point_list)
            _poly = self._pedb.modeler.shape_to_polygon_data(plane)
            if _poly is None or _poly.is_null or _poly is False:
                self._pedb.logger.error("Failed to create void polygon data")
                return False
            void_poly = self._pedb.modeler.create_polygon(
                _poly, layer_name=self.layer_name, net_name=self.core.net.name
            )
        return self.add_void(void_poly)

    def points(self, arc_segments=6) -> tuple[float, float]:
        """Return the list of points with arcs converted to segments.

        Parameters
        ----------
        arc_segments : int
            Number of facets to convert an arc. Default is `6`.

        Returns
        -------
        tuple(float, float)
            (X, Y).
        """
        xt, yt = self._get_points_for_plot(self.polygon_data.core.points, arc_segments)
        if not xt:
            return []
        x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
        return x, y

    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        List[:class:`PointData <ansys.edb.core.geometry.point_data.PointData>`]

        """

        return self.polygon_data.points_raw

    @property
    def id(self):
        return self.core.edb_uid

    @property
    def edb_uid(self):
        return self.core.edb_uid

    @property
    def primitive_type(self):
        return self.core.primitive_type.name.lower()

    @property
    def net(self):
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.net)

    @net.setter
    def net(self, value):
        from pyedb.grpc.database.net.net import Net

        if isinstance(value, Net):
            self.core.net = value.core
        elif isinstance(value, Net):
            self.core.net = value
        elif isinstance(value, str):
            if value in self._pedb.nets:
                self.core.net = self._pedb.nets[value].core
        else:
            raise TypeError("Net must be an instance of Net or str")

    @property
    def is_void(self):
        """Check if the primitive is a void.

        Returns
        -------
        bool
            ``True`` if the primitive is a void, ``False`` otherwise.
        """
        return self.core.is_void

    @property
    def is_null(self):
        """Check if the primitive is null.

        Returns
        -------
        bool
            ``True`` if the primitive is null, ``False`` otherwise.
        """
        return self.core.is_null

    @property
    def layer(self):
        """Get the layer object of the primitive.

        Returns
        -------
        :class:`Layer <pyedb.grpc.database.stackup.layer.Layer>`
            Layer object.
        """
        return self.core.layer

    def expand(self, offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001) -> list[Any]:
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

        Return
        ------
        List:[:class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`]

        """
        return self.core.polygon_data.expand(
            offset=offset, round_corner=round_corners, max_corner_ext=maximum_corner_extension, tol=tolerance
        )

    def scale(self, factor, center=None) -> bool:
        """Scales the polygon relative to a center point by a factor.

        Parameters
        ----------
        factor : float
            Scaling factor.
        center : List of float or str [x,y], optional
            If None scaling is done from polygon center.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(factor, str):
            factor = float(factor)
            from ansys.edb.core.geometry.polygon_data import (
                PolygonData as GrpcPolygonData,
            )

            polygon_data = GrpcPolygonData(points=self.core.cast().polygon_data.points)
            if not center:
                center = polygon_data.bounding_circle()[0]
                if center:
                    polygon_data.scale(factor, center)
                    self.core.cast().polygon_data = polygon_data
                    return True
                else:
                    self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            elif isinstance(center, list) and len(center) == 2:
                center = GrpcPointData(center)
                polygon_data.scale(factor, center)
                self.core.cast().polygon_data = polygon_data
                return True
        return False

    def plot(self, plot_net=False, show=True, save_plot=None):
        """Plot the current polygon on matplotlib.

        Parameters
        ----------
        plot_net : bool, optional
            Whether if plot the entire net or only the selected polygon. Default is ``False``.
        show : bool, optional
            Whether if show the plot or not. Default is ``True``.
        save_plot : str, optional
            Save the plot path.

        Returns
        -------
        (ax, fig)
            Matplotlib ax and figures.
        """
        import matplotlib.pyplot as plt
        from shapely.geometry import Polygon
        from shapely.plotting import plot_polygon

        dpi = 100.0
        figsize = (2000 / dpi, 1000 / dpi)
        if plot_net and self.net_name:
            fig, ax = self._pedb.nets.plot([self.net_name], color_by_net=True, show=False, show_legend=False)
        else:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(1, 1, 1)
        xt, yt = self.points()
        p1 = [(i, j) for i, j in zip(xt[::-1], yt[::-1])]

        holes = []
        for void in self.voids:
            xvt, yvt = void.points(arc_segments=3)
            h1 = [(i, j) for i, j in zip(xvt, yvt)]
            holes.append(h1)
        poly = Polygon(p1, holes)
        plot_polygon(poly, add_points=False, color=(1, 0, 0))
        ax.grid(False)
        ax.set_axis_off()
        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])
        message = f"Polygon {self.id} on net {self.net_name}"
        plt.title(message, size=20)
        if save_plot:
            plt.savefig(save_plot)
        elif show:
            plt.show()
        return ax, fig

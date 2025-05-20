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

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.primitive.circle import Circle as GrpcCircle
from ansys.edb.core.primitive.primitive import Primitive as GrpcPrimitive

from pyedb.misc.utilities import compute_arc_points
from pyedb.modeler.geometry_operators import GeometryOperators


class Primitive(GrpcPrimitive):
    """Manages EDB functionalities for a primitives.
    It inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.modeler.primitives[0]
    >>> edb_prim.is_void # Class Property
    >>> edb_prim.IsVoid() # EDB Object Property
    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._edb_object = edb_object
        self._core_stackup = pedb.stackup
        self._core_net = pedb.nets
        self._object_instance = None

    @property
    def type(self):
        """Type of the primitive.

        Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

        Returns
        -------
        str
        """
        return super().primitive_type.name.lower()

    @property
    def polygon_data(self):
        """Polygon data.

        Returns
        -------
        :class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        """
        return self.cast().polygon_data

    @property
    def object_instance(self):
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`

        """
        if not self._object_instance:
            self._object_instance = self.layout.layout_instance.get_layout_obj_instance_in_context(self, None)
        return self._object_instance

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Net name.

        """
        if not self.net.is_null:
            return self.net.name

    @net_name.setter
    def net_name(self, value):
        if value in self._pedb.nets.nets:
            self.net = self._pedb.nets.nets[value]

    @property
    def layer_name(self):
        """Layer name.

        Returns
        -------
        str
            Layer name.
        """
        return self.layer.name

    @layer_name.setter
    def layer_name(self, value):
        if value in self._pedb.stackup.layers:
            self.layer = self._pedb.stackup.layers[value]

    @property
    def voids(self):
        """Primitive voids.

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`

        """
        return [Primitive(self._pedb, prim) for prim in super().voids]

    @property
    def aedt_name(self):
        """Name to be visualized in AEDT.

        Returns
        -------
        str
            Name.
        """
        try:
            name = self.get_product_property(GrpcProductIdType.DESIGNER, 1)
            name = name.strip("'")
        except:
            name = ""
        if not name:
            if self.primitive_type.name.lower() == "path":
                ptype = "line"
            elif self.primitive_type.name.lower() == "rectangle":
                ptype = "rect"
            elif self.primitive_type.name.lower() == "polygon":
                ptype = "poly"
            elif self.primitive_type.name.lower() == "bondwire":
                ptype = "bwr"
            else:
                ptype = self.primitive_type.name.lower()
            name = "{}_{}".format(ptype, self.edb_uid)
            self.aedt_name = name
        return name

    @aedt_name.setter
    def aedt_name(self, value):
        self.set_product_property(GrpcProductIdType.DESIGNER, 1, value)

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]

        """
        return self._pedb.get_connected_objects(self.object_instance)

    def area(self, include_voids=True):
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
        area = self.cast().polygon_data.area()
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
                x.append(point.x.value)
                y.append(point.y.value)
            else:
                arc_h = point.arc_height.value
                p1 = [my_net_points[i - 1].x.value, my_net_points[i - 1].y.value]
                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].x.value, my_net_points[i + 1].y.value]
                else:
                    p2 = [my_net_points[0].x.value, my_net_points[0].y.value]
                x_arc, y_arc = compute_arc_points(p1, p2, arc_h, num)
                x.extend(x_arc)
                y.extend(y_arc)
        # fmt: on
        return x, y

    @property
    def center(self):
        """Return the primitive bounding box center coordinate.

        Returns
        -------
        List[float, float]
            [x, y]

        """
        center = self.cast().polygon_data.bounding_circle()[0]
        return [center.x.value, center.y.value]

    def get_connected_object_id_set(self):
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        List[int]
            Found connected objects IDs with Layout object.
        """
        layout_inst = self.layout.layout_instance
        layout_obj_inst = layout_inst.get_layout_obj_instance_in_context(self._edb_object, None)  # 2nd arg was []
        return [loi.layout_obj.id for loi in layout_inst.get_connected_objects(layout_obj_inst)]

    @property
    def bbox(self):
        """Return the primitive bounding box points. Lower left corner, upper right corner.

        Returns
        -------
        List[float, float, float, float]
            [lower_left x, lower_left y, upper right x, upper right y]

        """
        bbox = self.cast().polygon_data.bbox()
        return [
            round(bbox[0].x.value, 6),
            round(bbox[0].y.value, 6),
            round(bbox[1].x.value, 6),
            round(bbox[1].y.value, 6),
        ]

    def convert_to_polygon(self):
        """Convert path to polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
            Polygon when successful, ``False`` when failed.

        """
        if self.type == "path":
            polygon = self._pedb.modeler.create_polygon(self.polygon_data, self.layer_name, [], self.net.name)
            self.delete()
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

    def is_intersecting(self, primitive):
        """Check if actual primitive and another primitive or polygon data intesects.

        Parameters
        ----------
        primitive : :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>>` or `PolygonData`

        Returns
        -------
        bool
        """
        return True if self.intersection_type(primitive) >= 1 else False

    def get_closest_point(self, point):
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

        p0 = self.cast().polygon_data.closest_point(point)
        return [p0.x.value, p0.y.value]

    @property
    def arcs(self):
        """Get the Primitive Arc Data.

        Returns
        -------
        :class:`ArcData <ansys.edb.core.geometry.arc_data.ArcData>`
        """
        return self.polygon_data.arc_data

    @property
    def longest_arc(self):
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

    def subtract(self, primitives):
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
        poly = self.cast().polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        voids_of_prims = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.cast().polygon_data)
                for void in prim.voids:
                    voids_of_prims.append(void.cast().polygon_data)
            else:
                try:
                    primi_polys.append(prim.cast().polygon_data)
                except:
                    primi_polys.append(prim)
        for v in self.voids[:]:
            primi_polys.append(v.cast().polygon_data)
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
        self.delete()
        for prim in primitives:
            if isinstance(prim, Primitive):
                prim.delete()
            else:
                try:
                    prim.Delete()
                except AttributeError:
                    continue
        return new_polys

    def intersect(self, primitives):
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
        poly = self.cast().polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            prim = prim.cast()
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
                                polys_clean, self.layer_name, net_name=self.net.name, voids=void_to_append
                            )
                        )
                    else:
                        new_polys.append(
                            self._pedb.modeler.create_polygon(
                                p, self.layer_name, net_name=self.net.name, voids=list_void
                            )
                        )
                else:
                    new_polys.append(
                        self._pedb.modeler.create_polygon(p, self.layer_name, net_name=self.net.name, voids=list_void)
                    )
        self.delete()
        for prim in primitives:
            prim.delete()
        return new_polys

    def unite(self, primitives):
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
        self.delete()
        for prim in primitives:
            if isinstance(prim, Primitive):
                prim.delete()
            else:
                try:
                    prim.delete()
                except AttributeError:
                    continue
        return new_polys

    def get_closest_arc_midpoint(self, point):
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
            point = [point.x.value, point.y.value]
        dist = 1e12
        out = None
        for arc in self.arcs:
            mid_point = arc.midpoint
            mid_point = [mid_point.x.value, mid_point.y.value]
            if GeometryOperators.points_distance(mid_point, point) < dist:
                out = arc.midpoint
                dist = GeometryOperators.points_distance(mid_point, point)
        return [out.x.value, out.y.value]

    @property
    def shortest_arc(self):
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

    def add_void(self, point_list):
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
            void_poly = self._pedb.modeler.create_polygon(_poly, layer_name=self.layer_name, net_name=self.net.name)
        return self.add_void(void_poly)

    def points(self, arc_segments=6):
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
        xt, yt = self._get_points_for_plot(self.polygon_data.points, arc_segments)
        if not xt:
            return []
        x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
        return x, y

    @property
    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        List[:class:`PointData <ansys.edb.core.geometry.point_data.PointData>`]

        """

        return self.polygon_data.points

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

        Return
        ------
        List:[:class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`]

        """
        return self.cast().polygon_data.expand(
            offset=offset, round_corner=round_corners, max_corner_ext=maximum_corner_extension, tol=tolerance
        )

    def scale(self, factor, center=None):
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

            polygon_data = GrpcPolygonData(points=self.cast().polygon_data.points)
            if not center:
                center = polygon_data.bounding_circle()[0]
                if center:
                    polygon_data.scale(factor, center)
                    self.cast().polygon_data = polygon_data
                    return True
                else:
                    self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            elif isinstance(center, list) and len(center) == 2:
                center = GrpcPointData(center)
                polygon_data.scale(factor, center)
                self.cast().polygon_data = polygon_data
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

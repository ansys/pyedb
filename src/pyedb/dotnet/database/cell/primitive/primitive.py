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
import re

from System import String

from pyedb.dotnet.database.cell.connectable import Connectable
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.misc.utilities import compute_arc_points
from pyedb.modeler.geometry_operators import GeometryOperators


class Primitive(Connectable):
    """Manages EDB functionalities for a primitives.
    It inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.modeler.primitives[0]
    >>> edb_prim.is_void  # Class Property
    >>> edb_prim.IsVoid()  # EDB Object Property
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._app = self._pedb
        self.primitive_object = self._edb_object

        bondwire_type = self._pedb._edb.Cell.Primitive.BondwireType
        self._bondwire_type = {
            "invalid": bondwire_type.Invalid,
            "apd": bondwire_type.ApdBondwire,
            "jedec_4": bondwire_type.Jedec4Bondwire,
            "jedec4": bondwire_type.Jedec4Bondwire,
            "jedec_5": bondwire_type.Jedec5Bondwire,
            "jedec5": bondwire_type.Jedec5Bondwire,
            "num_of_bondwire_type": bondwire_type.NumOfBondwireType,
        }
        bondwire_cross_section_type = self._pedb._edb.Cell.Primitive.BondwireCrossSectionType
        self._bondwire_cross_section_type = {
            "invalid": bondwire_cross_section_type.Invalid,
            "round": bondwire_cross_section_type.BondwireRound,
            "rectangle": bondwire_cross_section_type.BondwireRectangle,
        }

    @property
    def _core_stackup(self):
        return self._app.stackup

    @property
    def _core_net(self):
        return self._app.nets

    @property
    def type(self):
        """Return the type of the primitive.

        Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

        Returns
        -------
        str
        """
        try:
            return self._edb_object.GetPrimitiveType().ToString()
        except AttributeError:  # pragma: no cover
            return ""

    @property
    def primitive_type(self):
        """Return the type of the primitive.

        Expected output is among ``"circle"``, ``"rectangle"``,``"polygon"``,``"path"`` or ``"bondwire"``.

        Returns
        -------
        str
        """
        return self._edb_object.GetPrimitiveType().ToString().lower()

    @property
    def layer(self):
        """Get the primitive edb layer object."""
        obj = self._edb_object.GetLayer()
        if obj.IsNull():
            return None
        else:
            return self._pedb.stackup.find_layer_by_name(obj.GetName())

    @property
    def layer_name(self):
        """Get the primitive layer name.

        Returns
        -------
        str
        """
        try:
            return self._edb_object.GetLayer().GetName()
        except (KeyError, AttributeError):  # pragma: no cover
            return None

    @layer_name.setter
    def layer_name(self, val):
        layer_list = list(self._core_stackup.layers.keys())
        if isinstance(val, str) and val in layer_list:
            layer = self._core_stackup.layers[val]._edb_layer
            if layer:
                self.primitive_object.SetLayer(layer)
            else:
                raise AttributeError("Layer {} not found.".format(val))
        elif isinstance(val, type(self._core_stackup.layers[layer_list[0]])):
            try:
                self.primitive_object.SetLayer(val._edb_layer)
            except:
                raise AttributeError("Failed to assign new layer on primitive.")
        else:
            raise AttributeError("Invalid input value")

    @property
    def is_void(self):
        """Either if the primitive is a void or not.

        Returns
        -------
        bool
        """
        return self._edb_object.IsVoid()

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
        if "GetPolygonData" not in dir(self._edb_object):
            return 0
        area = self._edb_object.GetPolygonData().Area()
        if include_voids:
            for el in self._edb_object.Voids:
                area -= el.GetPolygonData().Area()
        return area

    @property
    def is_negative(self):
        """Determine whether this primitive is negative.

        Returns
        -------
        bool
            True if it is negative, False otherwise.
        """
        return self._edb_object.GetIsNegative()

    @is_negative.setter
    def is_negative(self, value):
        self._edb_object.SetIsNegative(value)

    def _get_points_for_plot(self, my_net_points, num):
        """
        Get the points to be plotted.
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            if not self.is_arc(point):
                x.append(point.X.ToDouble())
                y.append(point.Y.ToDouble())
                # i += 1
            else:
                arc_h = point.GetArcHeight().ToDouble()
                p1 = [my_net_points[i - 1].X.ToDouble(), my_net_points[i - 1].Y.ToDouble()]
                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].X.ToDouble(), my_net_points[i + 1].Y.ToDouble()]
                else:
                    p2 = [my_net_points[0].X.ToDouble(), my_net_points[0].Y.ToDouble()]
                x_arc, y_arc = compute_arc_points(p1, p2, arc_h, num)
                x.extend(x_arc)
                y.extend(y_arc)
                # i += 1
        # fmt: on
        return x, y

    @property
    def center(self):
        """Return the primitive bounding box center coordinate.

        Returns
        -------
        list
            [x, y]

        """
        bbox = self.bbox
        return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]

    def is_arc(self, point):
        """Either if a point is an arc or not.

        Returns
        -------
        bool
        """
        return point.IsArc()

    @property
    def bbox(self):
        """Return the primitive bounding box points. Lower left corner, upper right corner.

        Returns
        -------
        list
            [lower_left x, lower_left y, upper right x, upper right y]

        """
        bbox = self.polygon_data._edb_object.GetBBox()
        return [
            round(bbox.Item1.X.ToDouble(), 9),
            round(bbox.Item1.Y.ToDouble(), 9),
            round(bbox.Item2.X.ToDouble(), 9),
            round(bbox.Item2.Y.ToDouble(), 9),
        ]

    def convert_to_polygon(self):
        """Convert path to polygon.

        Returns
        -------
        bool, :class:`dotnet.database.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed.

        """
        if self.type == "Path":
            polygon_data = self._edb_object.GetPolygonData()
            polygon = self._app.modeler.create_polygon(polygon_data, self.layer_name, [], self.net_name)
            self._edb_object.Delete()
            return polygon
        else:
            return False

    def intersection_type(self, primitive):
        """Get intersection type between actual primitive and another primitive or polygon data.

        Parameters
        ----------
        primitive : :class:`pyaeedt.database.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

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
        poly = primitive
        try:
            poly = primitive.polygon_data
        except AttributeError:
            pass
        return int(self.polygon_data._edb_object.GetIntersectionType(poly._edb_object))

    def is_intersecting(self, primitive):
        """Check if actual primitive and another primitive or polygon data intesects.

        Parameters
        ----------
        primitive : :class:`pyaeedt.database.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

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
        list of float
        """
        if isinstance(point, (list, tuple)):
            point = self._app.core.geometry.point_data(self._app.edb_value(point[0]), self._app.edb_value(point[1]))

        p0 = self.polygon_data._edb_object.GetClosestPoint(point)
        return [p0.X.ToDouble(), p0.Y.ToDouble()]

    @property
    def arcs(self):
        """Get the Primitive Arc Data."""
        return self.polygon_data.arcs

    @property
    def longest_arc(self):
        """Get the longest arc."""
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
        primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`dotnet.database.edb_data.EDBPrimitives`
        """
        poly = self.primitive_object.GetPolygonData()
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        voids_of_prims = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.primitive_object.GetPolygonData())
                for void in prim.voids:
                    voids_of_prims.append(void.polygon_data._edb_object)
            else:
                try:
                    primi_polys.append(prim.GetPolygonData())
                except:
                    primi_polys.append(prim)
        for v in self.voids[:]:
            primi_polys.append(v.polygon_data._edb_object)
        primi_polys = poly.Unite(convert_py_list_to_net_list(primi_polys))
        p_to_sub = poly.Unite(convert_py_list_to_net_list([poly] + voids_of_prims))
        list_poly = poly.Subtract(p_to_sub, primi_polys)
        new_polys = []
        if list_poly:
            for p in list_poly:
                if p.IsNull():
                    continue
            new_polys.append(
                self._app.modeler.create_polygon(p, self.layer_name, net_name=self.net_name, voids=[]),
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
        primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`dotnet.database.edb_data.EDBPrimitives`
        """
        poly = self._edb_object.GetPolygonData()
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.primitive_object.GetPolygonData())
            else:
                primi_polys.append(prim._edb_object.GetPolygonData())
                # primi_polys.append(prim)
        list_poly = poly.Intersect(convert_py_list_to_net_list([poly]), convert_py_list_to_net_list(primi_polys))
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if p.IsNull():
                    continue
                list_void = []
                void_to_subtract = []
                if voids:
                    for void in voids:
                        void_pdata = void._edb_object.GetPolygonData()
                        int_data2 = p.GetIntersectionType(void_pdata)
                        if int_data2 > 2 or int_data2 == 1:
                            void_to_subtract.append(void_pdata)
                        elif int_data2 == 2:
                            list_void.append(void_pdata)
                    if void_to_subtract:
                        polys_cleans = p.Subtract(
                            convert_py_list_to_net_list(p), convert_py_list_to_net_list(void_to_subtract)
                        )
                        for polys_clean in polys_cleans:
                            if not polys_clean.IsNull():
                                void_to_append = [v for v in list_void if polys_clean.GetIntersectionType(v) == 2]
                        new_polys.append(
                            self._app.modeler.create_polygon(
                                polys_clean, self.layer_name, net_name=self.net_name, voids=void_to_append
                            )
                        )
                    else:
                        new_polys.append(
                            self._app.modeler.create_polygon(
                                p, self.layer_name, net_name=self.net_name, voids=list_void
                            )
                        )
                else:
                    new_polys.append(
                        self._app.modeler.create_polygon(p, self.layer_name, net_name=self.net_name, voids=list_void)
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

    def unite(self, primitives):
        """Unite active primitive with one or more primitives.

        Parameters
        ----------
        primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`dotnet.database.edb_data.EDBPrimitives`
        """
        poly = self._edb_object.GetPolygonData()
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, Primitive):
                primi_polys.append(prim.primitive_object.GetPolygonData())
            else:
                try:
                    primi_polys.append(prim.GetPolygonData())
                except:
                    primi_polys.append(prim)
        list_poly = poly.Unite(convert_py_list_to_net_list([poly] + primi_polys))
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if p.IsNull():
                    continue
                list_void = []
                if voids:
                    for void in voids:
                        void_pdata = void.primitive_object.GetPolygonData()
                        int_data2 = p.GetIntersectionType(void_pdata)
                        if int_data2 > 1:
                            list_void.append(void_pdata)
                new_polys.append(
                    self._app.modeler.create_polygon(p, self.layer_name, net_name=self.net_name, voids=list_void),
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

    def get_closest_arc_midpoint(self, point):
        """Get the closest arc midpoint of the primitive to the input data.

        Parameters
        ----------
        point : list of float or PointData

        Returns
        -------
        list of float
        """
        if isinstance(point, self._app.core.Geometry.PointData):
            point = [point.X.ToDouble(), point.Y.ToDouble()]
        dist = 1e12
        out = None
        for arc in self.arcs:
            mid_point = arc.mid_point
            mid_point = [mid_point.X.ToDouble(), mid_point.Y.ToDouble()]
            if GeometryOperators.points_distance(mid_point, point) < dist:
                out = arc.mid_point
                dist = GeometryOperators.points_distance(mid_point, point)
        return [out.X.ToDouble(), out.Y.ToDouble()]

    @property
    def voids(self):
        """:obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>`: List of void\
        primitive objects inside the primitive.

        Read-Only.
        """
        return [self._pedb.layout.find_object_by_id(void.GetId()) for void in self._edb_object.Voids]

    @property
    def shortest_arc(self):
        """Get the longest arc."""
        len = 1e12
        arc = None
        for i in self.arcs:
            if i.is_segment and i.length < len:
                arc = i
                len = i.length
        return arc

    @property
    def aedt_name(self):
        """Name to be visualized in AEDT.

        Returns
        -------
        str
            Name.
        """
        val = String("")

        _, name = self._edb_object.GetProductProperty(self._pedb._edb.ProductId.Designer, 1, val)
        name = str(name).strip("'")
        if name == "":
            if str(self.primitive_type).lower() == "path":
                ptype = "line"
            elif str(self.primitive_type).lower() == "rectangle":
                ptype = "rect"
            elif str(self.primitive_type).lower() == "polygon":
                ptype = "poly"
            elif str(self.primitive_type).lower() == "bondwire":
                ptype = "bwr"
            else:
                ptype = str(self.primitive_type).lower()
            name = "{}__{}".format(ptype, self.id)
            self._edb_object.SetProductProperty(self._pedb._edb.ProductId.Designer, 1, name)
        return name

    @aedt_name.setter
    def aedt_name(self, value):
        self._edb_object.SetProductProperty(self._pedb._edb.ProductId.Designer, 1, value)

    @property
    def polygon_data(self):
        """:class:`pyedb.dotnet.database.dotnet.database.PolygonDataDotNet`: Outer contour of the Polygon object."""
        return PolygonData(self._pedb, self._edb_object.GetPolygonData())

    def add_void(self, point_list):
        """Add a void to current primitive.

        Parameters
        ----------
        point_list : list or :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives` \
            or EDB Primitive Object. Point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

        Returns
        -------
        bool
            ``True`` if successful, either  ``False``.
        """
        if isinstance(point_list, list):
            plane = self._pedb.modeler.Shape("polygon", points=point_list)
            _poly = self._pedb.modeler.shape_to_polygon_data(plane)
            if _poly is None or _poly.IsNull() or _poly is False:
                self._logger.error("Failed to create void polygon data")
                return False
            point_list = self._pedb.modeler.create_polygon(
                _poly, layer_name=self.layer_name, net_name=self.net.name
            )._edb_object
        elif "_edb_object" in dir(point_list):
            point_list = point_list._edb_object
        elif "primitive_obj" in dir(point_list):
            point_list = point_list.primitive_obj
        return self._edb_object.AddVoid(point_list)

    @property
    def api_class(self):
        return self._pedb._edb.Cell.Primitive

    def set_hfss_prop(self, material, solve_inside):
        """Set HFSS properties.

        Parameters
        ----------
        material : str
            Material property name to be set.
        solve_inside : bool
            Whether to do solve inside.
        """
        self._edb_object.SetHfssProp(material, solve_inside)

    @property
    def has_voids(self):
        """:obj:`bool`: If a primitive has voids inside.

        Read-Only.
        """
        return self._edb_object.HasVoids()

    @property
    def owner(self):
        """:class:`Primitive <ansys.edb.primitive.Primitive>`: Owner of the primitive object.

        Read-Only.
        """
        pid = self._edb_object.GetOwner().GetId()
        return self._pedb.layout.self.find_object_by_id(pid)

    @property
    def is_parameterized(self):
        """:obj:`bool`: Primitive's parametrization.

        Read-Only.
        """
        return self._edb_object.IsParameterized()

    def get_hfss_prop(self):
        """
        Get HFSS properties.

        Returns
        -------
        material : str
            Material property name.
        solve_inside : bool
            If solve inside.
        """
        material = ""
        solve_inside = True
        self._edb_object.GetHfssProp(material, solve_inside)
        return material, solve_inside

    def remove_hfss_prop(self):
        """Remove HFSS properties."""
        self._edb_object.RemoveHfssProp()

    @property
    def is_zone_primitive(self):
        """:obj:`bool`: If primitive object is a zone.

        Read-Only.
        """
        return self._edb_object.IsZonePrimitive()

    @property
    def can_be_zone_primitive(self):
        """:obj:`bool`: If a primitive can be a zone.

        Read-Only.
        """
        return True

    def make_zone_primitive(self, zone_id):
        """Make primitive a zone primitive with a zone specified by the provided id.

        Parameters
        ----------
        zone_id : int
            Id of zone primitive will use.

        """
        self._edb_object.MakeZonePrimitive(zone_id)

    def points(self, arc_segments=6):
        """Return the list of points with arcs converted to segments.

        Parameters
        ----------
        arc_segments : int
            Number of facets to convert an arc. Default is `6`.

        Returns
        -------
        tuple
            The tuple contains 2 lists made of X and Y points coordinates.
        """
        my_net_points = list(self._edb_object.GetPolygonData().Points)
        xt, yt = self._get_points_for_plot(my_net_points, arc_segments)
        if not xt:
            return []
        x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
        return x, y

    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        list
            Edb Points.
        """
        points = []
        my_net_points = list(self._edb_object.GetPolygonData().Points)
        for point in my_net_points:
            points.append(point)
        return points

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
            polygon_data = self.polygon_data.create_from_arcs(self.polygon_data._edb_object.GetArcData(), True)
            if not center:
                center = self.polygon_data._edb_object.GetBoundingCircleCenter()
                if center:
                    polygon_data._edb_object.Scale(factor, center)
                    self.polygon_data = polygon_data
                    return True
                else:
                    self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            elif isinstance(center, list) and len(center) == 2:
                center = self._edb.Geometry.PointData(
                    self._edb.Utility.Value(center[0]), self._edb.Utility.Value(center[1])
                )
                polygon_data._edb_object.Scale(factor, center)
                self.polygon_data = polygon_data
                return True
        return False

    @property
    def _em_properties(self):
        """Get EM properties."""
        default = (
            r"$begin 'EM properties'\n"
            r"\tType('Mesh')\n"
            r"\tDataId='EM properties1'\n"
            r"\t$begin 'Properties'\n"
            r"\t\tGeneral=''\n"
            r"\t\tModeled='true'\n"
            r"\t\tUnion='true'\n"
            r"\t\t'Use Precedence'='false'\n"
            r"\t\t'Precedence Value'='1'\n"
            r"\t\tPlanarEM=''\n"
            r"\t\tRefined='true'\n"
            r"\t\tRefineFactor='1'\n"
            r"\t\tNoEdgeMesh='false'\n"
            r"\t\tHFSS=''\n"
            r"\t\t'Solve Inside'='false'\n"
            r"\t\tSIwave=''\n"
            r"\t\t'DCIR Equipotential Region'='false'\n"
            r"\t$end 'Properties'\n"
            r"$end 'EM properties'\n"
        )

        pid = self._pedb.core.ProductId.Designer
        _, p = self._edb_object.GetProductProperty(pid, 18, "")
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = self._pedb.core.ProductId.Designer
        self._edb_object.SetProductProperty(pid, 18, em_prop)

    @property
    def dcir_equipotential_region(self):
        """Check whether dcir equipotential region is enabled.

        Returns
        -------
        bool
        """
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        em_pp = self._em_properties
        result = re.search(pattern, em_pp).group(1)
        if result == "true":
            return True
        else:
            return False

    @dcir_equipotential_region.setter
    def dcir_equipotential_region(self, value):
        """Set dcir equipotential region."""
        pp = r"'DCIR Equipotential Region'='true'" if value else r"'DCIR Equipotential Region'='false'"
        em_pp = self._em_properties
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        new_em_pp = re.sub(pattern, pp, em_pp)
        self._em_properties = new_em_pp

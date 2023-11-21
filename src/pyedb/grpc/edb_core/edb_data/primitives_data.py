import math

import ansys.edb.primitive as primitive
import ansys.edb.utility as utility
import ansys.edb.net as net
from pyedb.generic.general_methods import generate_unique_name
# from ansys.edb.primitive.primitive import Bondwire
# from ansys.edb.primitive.primitive import Circle
# from ansys.edb.primitive.primitive import Path
# from ansys.edb.primitive.primitive import Polygon
# from ansys.edb.primitive.primitive import Rectangle
# from ansys.edb.primitive.primitive import Text
# from ansys.edb.primitive.primitive import PrimitiveType
# from ansys.edb.utility.value import Value
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.modeler.geometry_operators import GeometryOperators


def cast(raw_primitive, core_app):
    """Cast the primitive object to correct concrete type.

    Returns
    -------
    Primitive
    """
    if isinstance(raw_primitive, primitive.Rectangle):
        return EdbRectangle(raw_primitive, core_app)
    elif isinstance(raw_primitive, primitive.Polygon):
        return EdbPolygon(raw_primitive, core_app)
    elif isinstance(raw_primitive, primitive.Path):
        return EdbPath(raw_primitive, core_app)
    elif isinstance(raw_primitive, primitive.Bondwire):
        return EdbBondwire(raw_primitive, core_app)
    elif isinstance(raw_primitive, primitive.Text):
        return EdbText(raw_primitive, core_app)
    elif isinstance(raw_primitive, primitive.Circle):
        return EdbCircle(raw_primitive, core_app)
    else:
        try:
            prim_type = raw_primitive.primitive_type
            if prim_type == primitive.PrimitiveType.RECTANGLE:
                return EdbRectangle(raw_primitive, core_app)
            elif prim_type == primitive.PrimitiveType.POLYGON:
                return EdbPolygon(raw_primitive, core_app)
            elif prim_type == primitive.PrimitiveType.PATH:
                return EdbPath(raw_primitive, core_app)
            elif prim_type == primitive.PrimitiveType.BONDWIRE:
                return EdbBondwire(raw_primitive, core_app)
            elif prim_type == primitive.PrimitiveType.TEXT:
                return EdbText(raw_primitive, core_app)
            elif prim_type == primitive.PrimitiveType.CIRCLE:
                return EdbCircle(raw_primitive, core_app)
            else:
                return None
        except:
            return None


class EDBPrimitivesMain:
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb.grpc.edb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.modeler.primitives[0]
    >>> edb_prim.is_void # Class Property
    >>> edb_prim.IsVoid() # EDB Object Property
    """

    def __init__(self, raw_primitive, core_app):
        # super().__init__(core_app, raw_primitive)
        # self._app = self._pedb
        self._app = core_app
        self._stackup = core_app.stackup
        self._net = core_app.nets
        # self.primitive_object = self._edb_object
        self.primitive_object = raw_primitive
        self._edb_object = raw_primitive
        self._layer = None
        self.net = None

    @property
    def type(self):
        """Return the type of the primitive.
        Allowed outputs are ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

        Returns
        -------
        str
        """
        types = ["CIRCLE", "PATH", "POLYGON", "RECTANGLE", "BONDWIRE"]
        str_type = str(self.primitive_object.primitive_type).split(".")
        if str_type[-1] in types:
            return f"{str_type[-1][0]}{str_type[-1][1:].lower()}"
        return None

    @property
    def id(self):
        return self.primitive_object.id

    @property
    def net(self):
        if self.net_name:
            return self._app.nets.nets[self.net_name]
        return False

    @net.setter
    def net(self, value):
        if isinstance(value, net.Net):
            self._edb_object.net = value
        elif isinstance(value, str):
            layout_net = net.Net.find_by_name(self._app.layout, value)
            if not layout_net.is_null:
                self._edb_object.net = layout_net
            else:
                self._edb_object.net = net.Net.create(self._app.layout, value)

    @property
    def net_name(self):
        """Get or Set the primitive net name.

        Returns
        -------
        str
        """
        if not self.primitive_object.net.is_null:
            return self.primitive_object.net.name
        return False

    @net_name.setter
    def net_name(self, name):
        if isinstance(name, str):
            self.primitive_object.name = name
        else:
            try:
                self.net = name
            except:
                self._app.logger.error("Failed to set net name.")

    @property
    def layer(self):
        """Get the primitive edb layer object."""
        if self.primitive_object.obj_type.name == "PADSTACK_INSTANCE":
            self._layer = None
            return self._layer
        else:
            self._layer = self.primitive_object.layer
            return self._layer

    @property
    def layer_name(self):
        """Get or Set the primitive layer name.

        Returns
        -------
        str
        """
        if self._layer:
            return self._layer.name

    @layer_name.setter
    def layer_name(self, val):
        if isinstance(val, str) and val in list(self._stackup.layers.keys()):
            lay = self._stackup.layers["TOP"]._edb_layer
            if lay:
                self.primitive_object.layer = lay
            else:
                raise AttributeError("Layer {} not found in layer".format(val))
        elif isinstance(val, type(self._stackup.layers["TOP"])):
            try:
                self.primitive_object.layer = val._edb_layer
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
        if self._edb_object.layout_obj_type in [primitive.PrimitiveType.CIRCLE,
                                                primitive.PrimitiveType.POLYGON,
                                                primitive.PrimitiveType.RECTANGLE]:
            return self._edb_object.is_void
        else:
            return False


class EDBPrimitives(EDBPrimitivesMain):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.modeler.primitives[0]
    >>> edb_prim.is_void # Class Property
    >>> edb_prim.IsVoid() # EDB Object Property
    """

    def __init__(self, raw_primitive, core_app):
        EDBPrimitivesMain.__init__(self, raw_primitive, core_app)

    @pyedb_function_handler()
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
        area = self.primitive_object.polygon_data.area
        if include_voids:
            for el in self.primitive_object.voids:
                area -= el.polygon_data.area
        return area

    @property
    def polygon_data(self):
        if self.primitive_object.primitive_type.name == "PATH":
            return self.primitive_object.center_line
        else:
            return self.primitive_object.polygon_data

    @property
    def is_negative(self):
        """Determine whether this primitive is negative.

        Returns
        -------
        bool
            True if it is negative, False otherwise.
        """
        return self.primitive_object.is_negative

    @is_negative.setter
    def is_negative(self, value):
        if isinstance(value, bool):
            self.primitive_object.is_negative = value

    @staticmethod
    def _eval_arc_points(p1, p2, h, n=6, tol=1e-12):
        """Get the points of the arc

        Parameters
        ----------
        p1 : list
            Arc starting point.
        p2 : list
            Arc ending point.
        h : float
            Arc height.
        n : int
            Number of points to generate along the arc.
        tol : float
            Geometric tolerance.

        Returns
        -------
        list, list
            Points generated along the arc.
        """
        # fmt: off
        if abs(h) < tol:
            return [], []
        elif h > 0:
            reverse = False
            x1 = p1[0]
            y1 = p1[1]
            x2 = p2[0]
            y2 = p2[1]
        else:
            reverse = True
            x1 = p2[0]
            y1 = p2[1]
            x2 = p1[0]
            y2 = p1[1]
            h *= -1
        xa = (x2 - x1) / 2
        ya = (y2 - y1) / 2
        xo = x1 + xa
        yo = y1 + ya
        a = math.sqrt(xa ** 2 + ya ** 2)
        if a < tol:
            return [], []
        r = (a ** 2) / (2 * h) + h / 2
        if abs(r - a) < tol:
            b = 0
            th = 2 * math.asin(1)  # chord angle
        else:
            b = math.sqrt(r ** 2 - a ** 2)
            th = 2 * math.asin(a / r)  # chord angle

        # center of the circle
        xc = xo + b * ya / a
        yc = yo - b * xa / a

        alpha = math.atan2((y1 - yc), (x1 - xc))
        xr = []
        yr = []
        for i in range(n):
            i += 1
            dth = (float(i) / (n + 1)) * th
            xi = xc + r * math.cos(alpha - dth)
            yi = yc + r * math.sin(alpha - dth)
            xr.append(xi)
            yr.append(yi)

        if reverse:
            xr.reverse()
            yr.reverse()
        # fmt: on
        return xr, yr

    def _get_points_for_plot(self, my_net_points, num):
        """
        Get the points to be plotted.
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            if not self.is_arc(point):
                x.append(point.x.value)
                y.append(point.y.value)
                # i += 1
            else:
                arc_h = point.arc_height.value
                p1 = [my_net_points[i - 1].x.value, my_net_points[i - 1].y.value]
                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].x.value, my_net_points[i + 1].y.value]
                else:
                    p2 = [my_net_points[0].x.value, my_net_points[0].y.value]
                x_arc, y_arc = self._eval_arc_points(p1, p2, arc_h, num)
                x.extend(x_arc)
                y.extend(y_arc)
                # i += 1
        # fmt: on
        return x, y

    @property
    def bbox(self):
        """Return the primitive bounding box points. Lower left corner, upper right corner.

        Returns
        -------
        list
            [lower_left x, lower_left y, upper right x, upper right y]

        """
        bbox = self.polygon_data.bbox()
        return [bbox[0].x.value, bbox[0].y.value, bbox[1].x.value, bbox[1].y.value]

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

    @pyedb_function_handler()
    def is_arc(self, point):
        """Either if a point is an arc or not.

        Returns
        -------
        bool
        """
        return point.IsArc()

    @pyedb_function_handler()
    def get_connected_object_id_set(self):
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        list
            Found connected objects IDs with Layout object.
        """
        layout_inst = self.primitive_object.layout.layout_instance
        layout_obj_inst = layout_inst.layout_obj_instance(self.primitive_object, None)
        return [loi.layout_obj.id for loi in layout_inst.get_connected_objects(layout_obj_inst)]

    @pyedb_function_handler()
    def _get_connected_object_obj_set(self):
        layout_inst = self.primitive_object.layout.layout_instance
        layout_obj_inst = layout_inst.layout_obj_instance(self.primitive_object, None)
        return [loi.layout_obj for loi in layout_inst.get_connected_objects(layout_obj_inst)]

    @pyedb_function_handler()
    def convert_to_polygon(self):
        """Convert path to polygon.

        Returns
        -------
        Converted polygon.

        """
        if self.type == "Path":
            polygon_data = self.primitive_object.polygon_data
            polygon = self._app.modeler.create_polygon(polygon_data, self.layer_name, [], self.net_name)
            self.primitive_object.delete()
            return polygon

    @pyedb_function_handler()
    def subtract(self, primitives):
        """Subtract active primitive with one or more primitives.

        Parameters
        ----------
        primitives : :class:`pyaedt.edb_core.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`pyaedt.edb_core.edb_data.EDBPrimitives`
        """
        poly = self.primitive_object.polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        voids_of_prims = []
        for prim in primitives:
            if isinstance(prim, EDBPrimitives):
                primi_polys.append(prim.primitive_object.polygon_data)
                for void in prim.voids:
                    voids_of_prims.append(void.polygon_data)
            else:
                try:
                    primi_polys.append(prim.polygon_data)
                except:
                    primi_polys.append(prim)
        for v in self.voids[:]:
            primi_polys.append(v.polygon_data.edb_api)
        primi_polys = poly.unite(primi_polys)
        p_to_sub = poly.unite([poly] + voids_of_prims)
        list_poly = poly.subtract(p_to_sub, primi_polys)
        new_polys = []
        if list_poly:
            for p in list_poly:
                if p.is_null:
                    continue
            new_polys.append(
                cast(
                    self._app.modeler.create_polygon(p, self.layer_name, net_name=self.net_name, voids=[]),
                    self._app,
                )
            )
        self.delete()
        for prim in primitives:
            try:
                prim.delete()
            except AttributeError:
                continue
        return new_polys

    @pyedb_function_handler()
    def intersect(self, primitives):
        """Intersect active primitive with one or more primitives.

        Parameters
        ----------
        primitives : :class:`pyaedt.edb_core.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`pyaedt.edb_core.edb_data.EDBPrimitives`
        """
        poly = self.primitive_object.polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, EDBPrimitives):
                primi_polys.append(prim.primitive_object.polygon_data)
            else:
                try:
                    primi_polys.append(prim.polygon_data)
                except:
                    primi_polys.append(prim)
        list_poly = poly.Intersect([poly], primi_polys)
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if p.is_null:
                    continue
                list_void = []
                void_to_subtract = []
                if voids:
                    for void in voids:
                        void_pdata = void.prim_obj.polygon_data
                        int_data2 = p.intersection_type(void_pdata)
                        if int_data2 > 2 or int_data2 == 1:
                            void_to_subtract.append(void_pdata)
                        elif int_data2 == 2:
                            list_void.append(void_pdata)
                    if void_to_subtract:
                        polys_cleans = p.subtract(p, void_to_subtract)
                        for polys_clean in polys_cleans:
                            if not polys_clean.is_null:
                                void_to_append = [v for v in list_void if polys_clean.tntersection_type(v) == 2]
                        new_polys.append(
                            cast(
                                self._app.modeler.create_polygon(
                                    polys_clean, self.layer_name, net_name=self.net_name, voids=void_to_append
                                ),
                                self._app,
                            )
                        )
                    else:
                        new_polys.append(
                            cast(
                                self._app.modeler.create_polygon(
                                    p, self.layer_name, net_name=self.net_name, voids=list_void
                                ),
                                self._app,
                            )
                        )
                else:
                    new_polys.append(
                        cast(
                            self._app.modeler.create_polygon(
                                p, self.layer_name, net_name=self.net_name, voids=list_void
                            ),
                            self._app,
                        )
                    )
        self.delete()
        for prim in primitives:
            try:
                prim.delete()
            except AttributeError:
                continue
        return new_polys

    @pyedb_function_handler()
    def unite(self, primitives):
        """Unite active primitive with one or more primitives.

        Parameters
        ----------
        primitives : :class:`pyaedt.edb_core.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

        Returns
        -------
        List of :class:`pyaedt.edb_core.edb_data.EDBPrimitives`
        """
        poly = self.primitive_object.polygon_data
        if not isinstance(primitives, list):
            primitives = [primitives]
        primi_polys = []
        for prim in primitives:
            if isinstance(prim, EDBPrimitives):
                primi_polys.append(prim.primitive_object.polygon_data)
            else:
                try:
                    primi_polys.append(prim.polygon_data)
                except:
                    primi_polys.append(prim)
        list_poly = poly.unite([poly] + primi_polys)
        new_polys = []
        if list_poly:
            voids = self.voids
            for p in list_poly:
                if p.is_null:
                    continue
                list_void = []
                if voids:
                    for void in voids:
                        void_pdata = void.primitive_object.polygon_data
                        int_data2 = p.intersection_type(void_pdata)
                        if int_data2 > 1:
                            list_void.append(void_pdata)
                new_polys.append(
                    cast(
                        self._app.modeler.create_polygon(p, self.layer_name, net_name=self.net_name, voids=list_void),
                        self._app,
                    )
                )
        self.delete()
        for prim in primitives:
            try:
                prim.Delete()
            except AttributeError:
                continue
        return new_polys

    @pyedb_function_handler()
    def intersection_type(self, primitive):
        """Get intersection type between actual primitive and another primitive or polygon data.

        Parameters
        ----------
        primitive : :class:`pyaeedt.edb_core.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

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
        return int(self.polygon_data.intersection_type(poly))

    @pyedb_function_handler()
    def is_intersecting(self, primitive):
        """Check if actual primitive and another primitive or polygon data intesects.

        Parameters
        ----------
        primitive : :class:`pyaeedt.edb_core.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

        Returns
        -------
        bool
        """
        return True if self.intersection_type(primitive) >= 1 else False

    @pyedb_function_handler()
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
            point = self._app.geometry.point_data(Value(point[0]), Value(point[1]))

        p0 = self.polygon_data.closest_points(point)
        return [p0.x.value, p0.y.value]

    @pyedb_function_handler()
    def get_closest_arc_midpoint(self, point):
        """Get the closest arc midpoint of the primitive to the input data.

        Parameters
        ----------
        point : list of float or PointData

        Returns
        -------
        list of float
        """
        if isinstance(point, self._app.geometry.geometry.PointData):
            point = [point.x.value, point.y.value]
        dist = 1e12
        out = None
        for arc in self.arcs:
            mid_point = arc.mid_point
            mid_point = [mid_point.x.value, mid_point.y.value]
            if GeometryOperators.points_distance(mid_point, point) < dist:
                out = arc.mid_point
                dist = GeometryOperators.points_distance(mid_point, point)
        return [out.x.value, out.y.value]

    @property
    def arcs(self):
        """Get the Primitive Arc Data."""
        arcs = [EDBArcs(self, i) for i in self.polygon_data.arc_data]
        return arcs

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


class EdbPath(EDBPrimitives):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)

    @property
    def width(self):
        """Path width.

        Returns
        -------
        float
            Path width or None.
        """
        if self.type == "Path":
            return self.primitive_object.width.value
        return

    @width.setter
    def width(self, value):
        if self.type == "Path":
            self.primitive_object.width = utility.Value(value)

    @property
    def length(self):
        """Path length in meters.

        Returns
        -------
        float
            Path length in meters.
        """
        center_line = self.get_center_line()
        length = 0
        for pt_ind in range(len(center_line)):
            if pt_ind < len(center_line) - 1:
                length += GeometryOperators.points_distance(center_line[pt_ind], center_line[pt_ind + 1])
        return length

    @pyedb_function_handler
    def get_center_line(self, to_string=False):
        """Get the center line of the trace.

        Parameters
        ----------
        to_string : bool, optional
            Type of return. The default is ``"False"``.
        Returns
        -------
        list

        """
        if to_string:
            return [[str(p.x.value), str(p.y.value)] for p in list(self.primitive_object.center_line.points)]
        else:
            return [[p.x.value, p.y.value] for p in list(self.primitive_object.center_line.points)]

    @pyedb_function_handler
    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        center_line = self.center_line
        width = self.width
        corner_style = self.corner_style
        end_cap_style = self.end_cap_style
        cloned_path = self._app.edb_api.cell.primitive.path.create(
            self._app.active_layout,
            self.layer_name,
            self.net,
            width,
            end_cap_style[1],
            end_cap_style[2],
            corner_style,
            center_line,
        )
        if cloned_path:
            return cloned_path

    # @pyedb_function_handler()
    @pyedb_function_handler
    def create_edge_port(
            self,
            name,
            position="End",
            port_type="Wave",
            reference_layer=None,
            horizontal_extent_factor=5,
            vertical_extent_factor=3,
            pec_launch_width="0.01mm",
    ):
        """

        Parameters
        ----------
        name : str
            Name of the port.
        position : str, optional
            Position of the port. The default is ``"End"``, in which case the port is created at the end of the trace.
            Options are ``"Start"`` and ``"End"``.
        port_type : str, optional
            Type of the port. The default is ``"Wave"``, in which case a wave port is created. Options are ``"Wave"``
             and ``"Gap"``.
        reference_layer : str, optional
            Name of the references layer. The default is ``None``. Only available for gap port.
        horizontal_extent_factor : int, optional
            Horizontal extent factor of the wave port. The default is ``5``.
        vertical_extent_factor : int, optional
            Vertical extent factor of the wave port. The default is ``3``.
        pec_launch_width : float, str, optional
            Perfect electrical conductor width of the wave port. The default is ``"0.01mm"``.

        Returns
        -------
            :class:`pyaedt.edb_core.edb_data.sources.ExcitationPorts`

        Examples
        --------
        >>> edbapp = pyedb.Edb("myproject.aedb")
        >>> sig = appedb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
        >>> sig.create_edge_port("pcb_port", "end", "Wave", None, 8, 8)

        """
        center_line = self.get_center_line()
        pos = center_line[-1] if position.lower() == "end" else center_line[0]

        if port_type.lower() == "wave":
            return self._app.hfss.create_wave_port(
                self.id, pos, name, 50, horizontal_extent_factor, vertical_extent_factor, pec_launch_width
            )
        else:
            return self._app.hfss.create_edge_port_vertical(self.id, pos, name, 50, reference_layer)

    @pyedb_function_handler()
    def create_via_fence(self, distance, gap, padstack_name):
        """Create via fences on both sides of the trace.
        Parameters
        ----------
        distance: str, float
            Distance between via fence and trace center line.
        gap: str, float
            Gap between vias.
        padstack_name: str
            Name of the via padstack.
        Returns
        -------
        """

        def get_angle(v1, v2):  # pragma: no cover
            v1_mag = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            v2_mag = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            dotsum = v1[0] * v2[0] + v1[1] * v2[1]
            if v1[0] * v2[1] - v1[1] * v2[0] > 0:
                scale = 1
            else:
                scale = -1
            dtheta = scale * math.acos(dotsum / (v1_mag * v2_mag))

            return dtheta

        def get_locations(line, gap):  # pragma: no cover
            location = [line[0]]
            residual = 0

            for n in range(len(line) - 1):
                x0, y0 = line[n]
                x1, y1 = line[n + 1]
                length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                dx, dy = (x1 - x0) / length, (y1 - y0) / length
                x = x0 - dx * residual
                y = y0 - dy * residual
                length = length + residual
                while length >= gap:
                    x += gap * dx
                    y += gap * dy
                    location.append((x, y))
                    length -= gap

                residual = length
            return location

        def get_parallet_lines(pts, distance):  # pragma: no cover
            leftline = []
            rightline = []

            x0, y0 = pts[0]
            x1, y1 = pts[1]
            vector = (x1 - x0, y1 - y0)
            orientation1 = get_angle((1, 0), vector)

            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x0 + distance * math.cos(leftturn), y0 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x0 + distance * math.cos(righrturn), y0 + distance * math.sin(righrturn))
            rightline.append(rightPt)

            for n in range(1, len(pts) - 1):
                x0, y0 = pts[n - 1]
                x1, y1 = pts[n]
                x2, y2 = pts[n + 1]

                v1 = (x1 - x0, y1 - y0)
                v2 = (x2 - x1, y2 - y1)
                dtheta = get_angle(v1, v2)
                orientation1 = get_angle((1, 0), v1)

                leftturn = orientation1 + dtheta / 2 + math.pi / 2
                righrturn = orientation1 + dtheta / 2 - math.pi / 2

                distance2 = distance / math.sin((math.pi - dtheta) / 2)
                leftPt = (x1 + distance2 * math.cos(leftturn), y1 + distance2 * math.sin(leftturn))
                leftline.append(leftPt)
                rightPt = (x1 + distance2 * math.cos(righrturn), y1 + distance2 * math.sin(righrturn))
                rightline.append(rightPt)

            x0, y0 = pts[-2]
            x1, y1 = pts[-1]

            vector = (x1 - x0, y1 - y0)
            orientation1 = get_angle((1, 0), vector)
            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x1 + distance * math.cos(leftturn), y1 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x1 + distance * math.cos(righrturn), y1 + distance * math.sin(righrturn))
            rightline.append(rightPt)
            return leftline, rightline

        distance = utility.Value(distance).value
        gap = utility.Value(gap).value
        center_line = self.get_center_line()
        leftline, rightline = get_parallet_lines(center_line, distance)
        for x, y in get_locations(rightline, gap) + get_locations(leftline, gap):
            self._app.padstacks.place(position=[x, y], definition_name=padstack_name,
                                                          via_name=generate_unique_name(padstack_name))

class EdbRectangle(EDBPrimitives):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)


class EdbCircle(EDBPrimitives):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)


class EdbPolygon(EDBPrimitives):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)

    @pyedb_function_handler
    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        cloned_poly = self._app.cell.primitive.polygon.create(
            self._app.active_layout, self.layer_name, self.net, self.polygon_data
        )
        if cloned_poly:
            for void in self.voids:
                cloned_void = self._app.cell.primitive.polygon.create(
                    self._app.active_layout, self.layer_name, self.net, void.polygon_data
                )
                # cloned_void
                cloned_poly.prim_obj.add_void(cloned_void.prim_obj)
            return cloned_poly
        return False

    @pyedb_function_handler()
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
            point_data = self._app.geometry.point_data(Value(point_data[0]), Value(point_data[1])
                                                       )
        int_val = int(self.polygon_data.in_polygon(point_data))

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


class EdbText(EDBPrimitivesMain):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)


class EdbBondwire(EDBPrimitivesMain):
    def __init__(self, raw_primitive, core_app):
        EDBPrimitives.__init__(self, raw_primitive, core_app)


class EDBArcs(object):
    """Manages EDB Arc Data functionalities.
    It Inherits EDB primitives arcs properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2024.1")
    >>> prim_arcs = edb.modeler.primitives[0].arcs
    >>> prim_arcs.center # arc center
    >>> prim_arcs.points # arc point list
    >>> prim_arcs.mid_point # arc mid point
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
        >>> appedb = Edb(fpath, edbversion="2023.2")
        >>> start_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].start
        >>> print(start_coordinate)
        [x_value, y_value]
        """
        point = self.arc_object.start
        return [point.x.value, point.y.value]

    @property
    def end(self):
        """Get the coordinates of the ending point.

        Returns
        -------
        list
            List containing the X and Y coordinates of the ending point.

        Examples
        --------
        >>> appedb = Edb(fpath, edbversion="2023.2")
        >>> end_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].end
        """
        point = self.arc_object.end
        return [point.x.value, point.y.value]

    @property
    def height(self):
        """Get the height of the arc.

        Returns
        -------
        float
            Height of the arc.


        Examples
        --------
        >>> appedb = Edb(fpath, edbversion="2023.2")
        >>> arc_height = appedb.nets["V1P0_S0"].primitives[0].arcs[0].height
        """
        return self.arc_object.height

    @property
    def center(self):
        """Arc center.

        Returns
        -------
        list
        """
        cent = self.arc_object.center
        return [cent.x.value, cent.y.value]

    @property
    def length(self):
        """Arc length.

        Returns
        -------
        float
        """
        return self.arc_object.length

    @property
    def mid_point(self):
        """Arc mid point.

        Returns
        -------
        float
        """
        mid_point = self.arc_object.midpoint
        return [mid_point.x.value, mid_point.y.value]

    @property
    def radius(self):
        """Arc radius.

        Returns
        -------
        float
        """
        return self.arc_object.radius

    @property
    def is_segment(self):
        """Either if it is a straight segment or not.

        Returns
        -------
        bool
        """
        return self.arc_object.is_segment()

    @property
    def is_point(self):
        """Either if it is a point or not.

        Returns
        -------
        bool
        """
        return self.arc_object.is_point()

    @property
    def is_ccw(self):
        """Test whether arc is counter clockwise.

        Returns
        -------
        bool
        """
        return self.arc_object.is_ccw()

    @property
    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        list
            Edb Points.
        """
        return self.arc_object.points

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
            xt, yt = self._app._get_points_for_plot(my_net_points, arc_segments)
            if not xt:
                return []
            x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
            return x, y
        except:
            x = []
            y = []
        return x, y

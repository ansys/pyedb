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

import math
import re

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.point_data import PointData as GrpcPolygonData
from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.primitive.primitive import PadstackInstance as GrpcPadstackInstance
from ansys.edb.core.terminal.terminals import PinGroupTerminal as GrpcPinGroupTerminal
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.edb_core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.modeler.geometry_operators import GeometryOperators


class PadstackInstance(GrpcPadstackInstance):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstackinstance :

    _pedb :
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, pedb, edb_instance):
        super().__init__(edb_instance.msg)
        self._edb_object = edb_instance
        self._bounding_box = []
        self._object_instance = None
        self._position = []
        self._pdef = None
        self._pedb = pedb

    @property
    def terminal(self):
        """Terminal."""
        from pyedb.grpc.edb_core.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = PadstackInstanceTerminal(self._pedb, self._edb_object)
        return term if not term.is_null else None

    def create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        if not name:
            name = self.name
        term = PadstackInstanceTerminal.create(
            layout=self.layout,
            name=name,
            padstack_instance=self,
            layer=self.get_layer_range()[0],
            net=self.net,
            is_ref=False,
        )
        return PadstackInstanceTerminal(self._pedb, term)

    def get_terminal(self, create_new_terminal=True):
        inst_term = self.get_padstack_instance_terminal()
        if inst_term.is_null and create_new_terminal:
            inst_term = self.create_terminal()
        return PadstackInstanceTerminal(self._pedb, inst_term)

    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port."""
        port = self.create_port(name)
        port.radial_extent_factor = radial_extent_factor
        return port

    def create_port(self, name=None, reference=None, is_circuit_port=False):
        """Create a port on the padstack instance.

        Parameters
        ----------
        name : str, optional
            Name of the port. The default is ``None``, in which case a name is automatically assigned.
        reference : reference net or pingroup  optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port.
        """
        if not reference:
            return self.create_terminal(name)
        else:
            positive_terminal = self.create_terminal()
            if positive_terminal.is_null:
                self._pedb.logger(
                    f"Positive terminal on padsatck instance {self.name} is null. Make sure a terminal"
                    f"is not already defined."
                )
            negative_terminal = None
            if isinstance(reference, list):
                pg = GrpcPinGroup.create(self.layout, name=f"pingroup_{self.name}_ref", padstack_instances=reference)
                negative_terminal = GrpcPinGroupTerminal.create(
                    layout=self.layout,
                    name=f"pingroup_term{self.name}_ref)",
                    pin_group=pg,
                    net=reference[0].net,
                    is_ref=True,
                )
                is_circuit_port = True
            else:
                if isinstance(reference, PadstackInstance):
                    negative_terminal = reference.create_terminal()
                elif isinstance(reference, str):
                    if reference in self._pedb.padstacks.instances:
                        reference = self._pedb.padstacks.instances[reference]
                    else:
                        pin_groups = [pg for pg in self._pedb.active_layout.pin_groups if pg.name == reference]
                        if pin_groups:
                            reference = pin_groups[0]
                        else:
                            self._pedb.logger.error(f"No reference found for {reference}")
                            return False
                    negative_terminal = reference.create_terminal()
            if negative_terminal:
                positive_terminal.reference_terminal = negative_terminal
            else:
                self._pedb.logger.error("No reference terminal created")
                return False
            positive_terminal.is_circuit_port = is_circuit_port
            negative_terminal.is_circuit_port = is_circuit_port
            return positive_terminal

    @property
    def _em_properties(self):
        """Get EM properties."""
        from ansys.edb.core.database import ProductIdType

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

        _, p = self.get_product_property(ProductIdType.DESIGNER, 18, "")
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = self._pedb.edb_api.ProductId.Designer
        self.set_product_property(pid, 18, em_prop)

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

    @property
    def object_instance(self):
        """Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object."""
        if not self._object_instance:
            self._object_instance = self.layout.layout_instance.get_layout_obj_instance_in_context(self, None)
        return self._object_instance

    @property
    def bounding_box(self):
        """Get bounding box of the padstack instance.
        Because this method is slow, the bounding box is stored in a variable and reused.

        Returns
        -------
        list of float
        """
        # TODO check to implement in grpc
        if self._bounding_box:
            return self._bounding_box
        return self._bounding_box

    def in_polygon(self, polygon_data, include_partial=True):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.
        simple_check : bool, optional
            Whether to perform a single check based on the padstack center or check the padstack bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        int_val = 1 if polygon_data.point_in_polygon(GrpcPointData(self.position)) else 0
        if int_val == 0:
            return False
        else:
            int_val = polygon_data.intersection_type(GrpcPolygonData(self.bounding_box))
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

    def get_back_drill_by_depth(self, from_bottom=True):
        """Get backdrill by depth.
        Parameters
        ----------
        from_bottom : bool
        Default value is ``True``.

        Return
        ------
        tuple(bool, (drill_depth, diameter))

        """
        res = self.get_back_drill_by_depth(from_bottom)
        if not res[0]:
            return False
        else:
            return [p.value for p in res[1]]

    # TODO all backdrill

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        return self.get_layer_range()[0].name

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]
        start_layer = self._pedb.stackup.signal_layers[layer_name]
        self.set_layer_range(start_layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.get_layer_range()[-1].name

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]
        stop_layer = self._pedb.stackup.signal_layers[layer_name]
        self.set_layer_range(start_layer, stop_layer)

    @property
    def layer_range_names(self):
        """List of all layers to which the padstack instance belongs."""
        start_layer, stop_layer = self.get_layer_range()
        started = False
        layer_list = []
        start_layer_name = start_layer.name
        stop_layer_name = stop_layer.name
        for layer_name in list(self._pedb.stackup.layers.keys()):
            if started:
                layer_list.append(layer_name)
                if layer_name == stop_layer_name or layer_name == start_layer_name:
                    break
            elif layer_name == start_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == stop_layer_name:
                    break
            elif layer_name == stop_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == start_layer_name:
                    break
        return layer_list

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        if self.is_null:
            return ""
        elif self.net.is_null:
            return ""
        else:
            return self.net.name

    @net_name.setter
    def net_name(self, val):
        if not self.is_null and self.net.is_null:
            self.net.name = val

    @property
    def layout_object_instance(self):
        obj_inst = [
            obj
            for obj in self._pedb.layout_instance.query_layout_obj_instances(
                spatial_filter=GrpcPointData(self.position)
            )
            if obj.layout_obj.id == self.id
        ]
        return obj_inst[0] if obj_inst else None

    @property
    def is_pin(self):
        """Determines whether this padstack instance is a layout pin.

        Returns
        -------
        bool
            True if this padstack type is a layout pin, False otherwise.
        """
        return self.is_layout_pin

    @is_pin.setter
    def is_pin(self, value):
        self.is_layout_pin = value

    @property
    def component(self):
        """Component."""
        from pyedb.grpc.edb_core.hierarchy.component import Component

        comp = Component(self._pedb, super().component)
        return comp if not comp.is_null else False

    @property
    def position(self):
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]`` coordinates for the padstack instance position.
        """
        position = self.get_position_and_rotation()
        if self.component:
            out2 = self.component.transform.transform_point(GrpcPointData(position[:2]))
            self._position = [round(out2[0].value, 6), round(out2[1].value, 6)]
        else:
            self._position = [round(pt.value, 6) for pt in position[:2]]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(GrpcValue(v))
            else:
                pos.append(v)
        point_data = GrpcPointData(pos[0], pos[1])
        self.set_position_and_rotation(point_data, GrpcValue(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        return self.get_position_and_rotation()[-1].value

    @property
    def name(self):
        """Padstack Instance Name. If it is a pin, the syntax will be like in AEDT ComponentName-PinName."""
        if self.is_pin:
            return self.aedt_name
        else:
            return super().name

    @name.setter
    def name(self, value):
        self.name = value
        self.set_product_property(GrpcProductIdType.DESIGNER, 11, value)

    @property
    def metal_volume(self):
        """Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

        Returns
        -------
        float
            Metal volume of the via hole instance.

        """
        # TODO fix when backdrills are done
        volume = 0
        if not self.start_layer == self.stop_layer:
            start_layer = self.start_layer
            stop_layer = self.stop_layer
            if self.backdrill_top:  # pragma no cover
                start_layer = self.backdrill_top[0]
            if self.backdrill_bottom:  # pragma no cover
                stop_layer = self.backdrill_bottom[0]
            padstack_def = self._pedb.padstacks.definitions[self.padstack_definition]
            hole_diam = 0
            try:  # pragma no cover
                hole_diam = padstack_def.hole_properties[0]
            except:  # pragma no cover
                pass
            if hole_diam:  # pragma no cover
                hole_finished_size = padstack_def.hole_finished_size
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
                volume = (math.pi * (hole_diam / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def component_pin(self):
        """Get component pin."""
        return self.name

    @property
    def aedt_name(self):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.padstacks.instances[111].get_aedt_pin_name()

        """

        name = self.get_product_property(GrpcProductIdType.DESIGNER, 11)
        return str(name).strip("'")

    def parametrize_position(self, prefix=None):
        """Parametrize the instance position.

        Parameters
        ----------
        prefix : str, optional
            Prefix for the variable name. Default is ``None``.
            Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

        Returns
        -------
        List
            List of variables created.
        """
        p = self.position
        if not prefix:
            var_name = "${}_pos".format(self.name)
        else:
            var_name = "${}".format(prefix)
        self._pedb.add_project_variable(var_name + "X", p[0])
        self._pedb.add_project_variable(var_name + "Y", p[1])
        self.position = [var_name + "X", var_name + "Y"]
        return [var_name + "X", var_name + "Y"]

    def in_voids(self, net_name=None, layer_name=None):
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked. Default is ``None``.
        layer_name : str
            Layer name of the voids to be checked. Default is ``None``.

        Returns
        -------
        list
            List of the voids that include this padstack instance.
        """
        x_pos = GrpcValue(self.position[0])
        y_pos = GrpcValue(self.position[1])
        point_data = GrpcPointData([x_pos, y_pos])

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
            if prim.polygon_data.point_in_polygon(point_data):
                voids.append(prim)
        return voids

    @property
    def pingroups(self):
        """Pin groups that the pin belongs to.

        Returns
        -------
        list
            List of pin groups that the pin belongs to.
        """
        return self.pin_groups

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self.component.placement_layer

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self._pedb.stackup.layers[self.component.placement_layer].lower_elevation

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self._pedb.stackup.layers[self.component.placement_layer].upper_elevation

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer.

            * 0 Top associated.
            * 1 No association.
            * 2 Bottom associated.
            * 4 Number of top/bottom association type.
            * -1 Undefined.
        """
        return self._pedb.stackup.layers[self.component.placement_layer].top_bottom_association.value

    def create_rectangle_in_pad(self, layer_name, return_points=False, partition_max_order=16):
        """Create a rectangle inscribed inside a padstack instance pad.

        The rectangle is fully inscribed in the pad and has the maximum area.
        It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.
        return_points : bool, optional
            If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
            Default is `False`.
        partition_max_order : float, optional
            Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
            Default is ``16``.

        Returns
        -------
        bool, List,  :class:`pyedb.dotnet.edb_core.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.modeler
        >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """
        # TODO check if still used anf fix if yes.
        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack = self._pedb.padstacks.definitions[self.padstack_def]
        try:
            padstack_pad = padstack.pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = padstack.pad_by_layer[padstack.via_start_layer]
            except KeyError:  # pragma: no cover
                return False

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad.polygon_data

        def _rotate(p):
            x = p[0] * math.cos(rotation) - p[1] * math.sin(rotation)
            y = p[0] * math.sin(rotation) + p[1] * math.cos(rotation)
            return [x, y]

        def _translate(p):
            x = p[0] + padstack_center[0]
            y = p[1] + padstack_center[1]
            return [x, y]

        rect = None

        if pad_shape == 1:
            # Circle
            diameter = params[0]
            r = diameter * 0.5
            p1 = [r, 0.0]
            p2 = [0.0, r]
            p3 = [-r, 0.0]
            p4 = [0.0, -r]
            rect = [_translate(p1), _translate(p2), _translate(p3), _translate(p4)]
        elif pad_shape == 2:
            # Square
            square_size = params[0]
            s2 = square_size * 0.5
            p1 = [s2, s2]
            p2 = [-s2, s2]
            p3 = [-s2, -s2]
            p4 = [s2, -s2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 3:
            # Rectangle
            x_size = float(params[0])
            y_size = float(params[1])
            sx2 = x_size * 0.5
            sy2 = y_size * 0.5
            p1 = [sx2, sy2]
            p2 = [-sx2, sy2]
            p3 = [-sx2, -sy2]
            p4 = [sx2, -sy2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 4:
            # Oval
            x_size = params[0]
            y_size = params[1]
            corner_radius = float(params[2])
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-sx - k, sy + k]
            p3 = [-sx - k, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 5:
            # Bullet
            x_size = params[0]
            y_size = params[1]
            corner_radius = params[2]
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-x_size * 0.5, sy + k]
            p3 = [-x_size * 0.5, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 6:
            # N-Sided Polygon
            size = params[0]
            num_sides = params[1]
            ext_radius = size * 0.5
            apothem = ext_radius * math.cos(math.pi / num_sides)
            p1 = [apothem, 0.0]
            p2 = [0.0, apothem]
            p3 = [-apothem, 0.0]
            p4 = [0.0, -apothem]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 0 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < polygon_data.edb_api.Count:
                point = polygon_data.edb_api.GetPoint(i)
                i += 1
                if point.IsArc():
                    continue
                else:
                    points.append([point.X.ToDouble(), point.Y.ToDouble()])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.modeler.Shape("polygon", points=rect)
        pdata = self._pedb.modeler.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self.component.transform.transform_point(point)
            new_rect.append([p_transf.X.ToDouble(), p_transf.Y.ToDouble()])
        if return_points:
            return new_rect
        else:
            path = self._pedb.modeler.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    def get_reference_pins(self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True):
        """Search for reference pins using given criteria.

        Parameters
        ----------
        reference_net : str, optional
            Reference net. The default is ``"GND"``.
        search_radius : float, optional
            Search radius for finding padstack instances. The default is ``5e-3``.
        max_limit : int, optional
            Maximum limit for the padstack instances found. The default is ``0``, in which
            case no limit is applied. The maximum limit value occurs on the nearest
            reference pins from the positive one that is found.
        component_only : bool, optional
            Whether to limit the search to component padstack instances only. The
            default is ``True``. When ``False``, the search is extended to the entire layout.

        Returns
        -------
        list
            List of :class:`dotnet.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.

        Examples
        --------
        >>> edbapp = Edb("target_path")
        >>> pin = edbapp.components.instances["J5"].pins["19"]
        >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
        >>> component_only=True)
        """
        return self._pedb.padstacks.get_reference_pins(
            positive_pin=self,
            reference_net=reference_net,
            search_radius=search_radius,
            max_limit=max_limit,
            component_only=component_only,
        )

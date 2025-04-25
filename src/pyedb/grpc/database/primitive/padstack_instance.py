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
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.primitive.padstack_instance import (
    PadstackInstance as GrpcPadstackInstance,
)
from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as GrpcPinGroupTerminal,
)
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.modeler.geometry_operators import GeometryOperators


class PadstackInstance(GrpcPadstackInstance):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    :class:`PadstackInstance <pyedb.grpc.dataybase.primitive.PadstackInstance>`
        PadstackInstance object.

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
        self._position = []
        self._pdef = None
        self._pedb = pedb
        self._object_instance = None

    @property
    def definition(self):
        """Padstack definition.

        Returns
        -------
        :class:`PadstackDef`<pyedb.grpc.database.definition.padstack_def.PadstackDef>`
        """
        return PadstackDef(self._pedb, self.padstack_def)

    @property
    def padstack_definition(self):
        """Padstack definition name.

        Returns
        -------
        str
            Padstack definition name.

        """
        return self.padstack_def.name

    @property
    def terminal(self):
        """PadstackInstanceTerminal.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.
        """
        from pyedb.grpc.database.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = self.get_padstack_instance_terminal()
        if not term.is_null:
            term = PadstackInstanceTerminal(self._pedb, term)
        return term if not term.is_null else None

    def create_terminal(self, name=None):
        """Create a padstack instance terminal.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.

        """
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
        """Returns padstack instance terminal.

        Parameters
        ----------
        create_new_terminal : bool, optional
            If terminal instance is not created,
            and value is ``True``, a new PadstackInstanceTerminal is created.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.

        """
        inst_term = self.get_padstack_instance_terminal()
        if inst_term.is_null and create_new_terminal:
            inst_term = self.create_terminal()
        return PadstackInstanceTerminal(self._pedb, inst_term)

    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port.

        Parameters
        ----------
        name : str, optional.
            Port name, the default is ``None``, in which case a name is automatically assigned.
        radial_extent_factor : int, float, optional
            Radial extent of coaxial port.

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
            Port terminal.
        """
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

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
            Port terminal.
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

        p = self.get_product_property(ProductIdType.DESIGNER, 18)
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
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance import.LayoutObjInstance>`

        """
        if not self._object_instance:
            self._object_instance = self.layout.layout_instance.get_layout_obj_instance_in_context(self, None)
        return self._object_instance

    @property
    def bounding_box(self):
        """Padstack instance bounding box.
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
        """List of all layers to which the padstack instance belongs.

        Returns
        -------
        List[str]
            List of layer names.

        """
        start_layer, stop_layer = self.get_layer_range()
        started = False
        layer_list = []
        start_layer_name = start_layer.name
        stop_layer_name = stop_layer.name
        for layer_name in list(self._pedb.stackup.signal_layers.keys()):
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
        if not self.is_null and not self.net.is_null:
            self.net = self._pedb.nets.nets[val]

    @property
    def layout_object_instance(self):
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`

        """
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
        """Component.

        Returns
        -------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`

        """
        from pyedb.grpc.database.hierarchy.component import Component

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
                pos.append(GrpcValue(v, self._pedb.active_cell))
            else:
                pos.append(v)
        point_data = GrpcPointData(pos[0], pos[1])
        self.set_position_and_rotation(
            x=point_data.x, y=point_data.y, rotation=GrpcValue(self.rotation, self._pedb.active_cell)
        )

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
        """Padstack Instance Name.

        Returns
        -------
        str
            If it is a pin, the syntax will be like in AEDT ComponentName-PinName.

        """
        if not super().name:
            return self.aedt_name
        else:
            return super().name

    @name.setter
    def name(self, value):
        super(PadstackInstance, self.__class__).name.__set__(self, value)
        self.set_product_property(GrpcProductIdType.DESIGNER, 11, value)

    @property
    def backdrill_type(self):
        """Backdrill type.


        Returns
        -------
        str
            Backdrill type.

        """
        return self.get_backdrill_type()

    @property
    def backdrill_top(self):
        if self.get_back_drill_type(False).value == 0:
            return False
        else:
            try:
                if self.get_back_drill_by_layer(from_bottom=False):
                    return True
            except:
                return False

    @property
    def backdrill_bottom(self):
        """Check is backdrill is starting at bottom.


        Returns
        -------
        bool

        """
        if self.get_back_drill_type(True).value == 0:
            return False
        else:
            try:
                if self.get_back_drill_by_layer(True):
                    return True
            except:
                return False

    @property
    def metal_volume(self):
        """Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

        Returns
        -------
        float
            Metal volume of the via hole instance.

        """
        volume = 0
        if not self.start_layer == self.stop_layer:
            start_layer = self.start_layer
            stop_layer = self.stop_layer
            via_length = (
                self._pedb.stackup.signal_layers[start_layer].upper_elevation
                - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
            )
            if self.get_backdrill_type == "layer_drill":
                layer, _, _ = self.get_back_drill_by_layer()
                start_layer = self._pedb.stackup.signal_layers[0]
                stop_layer = self._pedb.stackup.signal_layers[layer.name]
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
            elif self.get_backdrill_type == "depth_drill":
                drill_depth, _ = self.get_back_drill_by_depth()
                start_layer = self._pedb.stackup.signal_layers[0]
                via_length = self._pedb.stackup.signal_layers[start_layer].upper_elevation - drill_depth
            padstack_def = self._pedb.padstacks.definitions[self.padstack_def.name]
            hole_diameter = padstack_def.hole_diameter
            if hole_diameter:
                hole_finished_size = padstack_def.hole_finished_size
                volume = (math.pi * (hole_diameter / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def component_pin(self):
        """Component pin.

        Returns
        -------
        str
            Component pin name.

        """
        return self.name

    @property
    def aedt_name(self):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.name`.

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

    @aedt_name.setter
    def aedt_name(self, value):
        self.set_product_property(GrpcProductIdType.DESIGNER, 11, value)

    def get_backdrill_type(self, from_bottom=True):
        """Return backdrill type
        Parameters
        ----------
        from_bottom : bool, optional
            default value is `True.`

        Return
        ------
        str
            Back drill type, `"layer_drill"`,`"depth_drill"`, `"no_drill"`.

        """
        return super().get_back_drill_type(from_bottom).name.lower()

    def get_back_drill_by_layer(self, from_bottom=True):
        """Get backdrill by layer.

        Parameters
        ----------
        from_bottom : bool, optional.
         Default value is `True`.

         Return
         ------
         tuple (layer, offset, diameter) (str, [float, float], float).

        """
        back_drill = super().get_back_drill_by_layer(from_bottom)
        layer = back_drill[0].name
        offset = round(back_drill[1].value, 9)
        diameter = round(back_drill[2].value, 9)
        return layer, offset, diameter

    def get_back_drill_by_depth(self, from_bottom=True):
        """Get back drill by depth parameters
        Parameters
        ----------
        from_bottom : bool, optional
            Default value is `True`.

        Return
        ------
        tuple (drill_depth, drill_diameter) (float, float)
        """
        back_drill = super().get_back_drill_by_depth(from_bottom)
        drill_depth = back_drill[0].value
        drill_diameter = back_drill[1].value
        return drill_depth, drill_diameter

    def set_back_drill_by_depth(self, drill_depth, diameter, from_bottom=True):
        """Set back drill by depth.

        Parameters
        ----------
        drill_depth : str, float
            drill depth value
        diameter : str, float
            drill diameter
        from_bottom : bool, optional
            Default value is `True`.
        """
        super().set_back_drill_by_depth(
            drill_depth=GrpcValue(drill_depth), diameter=GrpcValue(diameter), from_bottom=from_bottom
        )

    def set_back_drill_by_layer(self, drill_to_layer, offset, diameter, from_bottom=True):
        """Set back drill layer.

        Parameters
        ----------
        drill_to_layer : str, Layer
            Layer to drill to.
        offset : str, float
            Offset value
        diameter : str, float
            Drill diameter
        from_bottom : bool, optional
            Default value is `True`
        """
        if isinstance(drill_to_layer, str):
            drill_to_layer = self._pedb.stackup.layers[drill_to_layer]
        super().set_back_drill_by_layer(
            drill_to_layer=drill_to_layer,
            offset=GrpcValue(offset),
            diameter=GrpcValue(diameter),
            from_bottom=from_bottom,
        )

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
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
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
        List[:class:`PinGroup <ansys.edb.core.hierarchy.pin_group>`]
            List of pin groups that the pin belongs to.
        """
        return self.pin_groups

    @property
    def placement_layer(self):
        """Placement layer name.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self.component.placement_layer

    @property
    def layer(self):
        """Placement layer object.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
           Placement layer.
        """
        return self.component.layer

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
        bool, List, :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`
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
        # padstack = self._pedb.padstacks.definitions[self.padstack_def.name]
        try:
            padstack_pad = PadstackDef(self._pedb, self.padstack_def).pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = PadstackDef(self._pedb, self.padstack_def).pad_by_layer[
                    PadstackDef(self._pedb, self.padstack_def).start_layer
                ]
            except KeyError:  # pragma: no cover
                return False

        try:
            pad_shape = padstack_pad.geometry_type
            params = padstack_pad.parameters_values
            polygon_data = padstack_pad.polygon_data
        except:
            self._pedb.logger.warning(f"No pad defined on padstack definition {self.padstack_def.name}")
            return False

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
        elif pad_shape == 7 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < len(polygon_data.points):
                point = polygon_data.points[i]
                i += 1
                if point.is_arc:
                    continue
                else:
                    points.append([point.x.value, point.y.value])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        # if rect is None or len(rect) != 4:
        #     return False
        rect = [GrpcPointData(pt) for pt in rect]
        path = GrpcPolygonData(rect)
        new_rect = []
        for point in path.points:
            if self.component:
                p_transf = self.component.transform.transform_point(point)
                new_rect.append([p_transf.x.value, p_transf.y.value])
        if return_points:
            return new_rect
        else:
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
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]

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

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]
        """
        return self._pedb.get_connected_objects(self.object_instance)

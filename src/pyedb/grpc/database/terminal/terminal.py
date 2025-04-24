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

import re

from ansys.edb.core.terminal.edge_terminal import EdgeType as GrpcEdgeType
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType
from ansys.edb.core.terminal.terminal import Terminal as GrpcTerminal
from ansys.edb.core.terminal.terminal import TerminalType as GrpcTerminalType
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.primitives_data import cast


class Terminal(GrpcTerminal):
    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._reference_object = None
        self.edb_object = edb_object

        self._boundary_type_mapping = {
            "port": GrpcBoundaryType.PORT,
            "pec": GrpcBoundaryType.PEC,
            "rlc": GrpcBoundaryType.RLC,
            "current_source": GrpcBoundaryType.CURRENT_SOURCE,
            "voltage_source": GrpcBoundaryType.VOLTAGE_SOURCE,
            "nexxim_ground": GrpcBoundaryType.NEXXIM_GROUND,
            "nxxim_port": GrpcBoundaryType.NEXXIM_PORT,
            "dc_terminal": GrpcBoundaryType.DC_TERMINAL,
            "voltage_probe": GrpcBoundaryType.VOLTAGE_PROBE,
        }

        self._terminal_type_mapping = {
            "edge": GrpcTerminalType.EDGE,
            "point": GrpcTerminalType.POINT,
            "terminal_instance": GrpcTerminalType.TERM_INST,
            "padstack_instance": GrpcTerminalType.PADSTACK_INST,
            "bundle": GrpcTerminalType.BUNDLE,
            "pin_group": GrpcTerminalType.PIN_GROUP,
        }

    @property
    def _hfss_port_property(self):
        """HFSS port property."""
        hfss_prop = re.search(r"HFSS\(.*?\)", self._edb_properties)
        p = {}
        if hfss_prop:
            hfss_type = re.search(r"'HFSS Type'='([^']+)'", hfss_prop.group())
            orientation = re.search(r"'Orientation'='([^']+)'", hfss_prop.group())
            horizontal_ef = re.search(r"'Horizontal Extent Factor'='([^']+)'", hfss_prop.group())
            vertical_ef = re.search(r"'Vertical Extent Factor'='([^']+)'", hfss_prop.group())
            radial_ef = re.search(r"'Radial Extent Factor'='([^']+)'", hfss_prop.group())
            pec_w = re.search(r"'PEC Launch Width'='([^']+)'", hfss_prop.group())

            p["HFSS Type"] = hfss_type.group(1) if hfss_type else ""
            p["Orientation"] = orientation.group(1) if orientation else ""
            p["Horizontal Extent Factor"] = float(horizontal_ef.group(1)) if horizontal_ef else ""
            p["Vertical Extent Factor"] = float(vertical_ef.group(1)) if vertical_ef else ""
            p["Radial Extent Factor"] = float(radial_ef.group(1)) if radial_ef else ""
            p["PEC Launch Width"] = pec_w.group(1) if pec_w else ""
        else:
            p["HFSS Type"] = ""
            p["Orientation"] = ""
            p["Horizontal Extent Factor"] = ""
            p["Vertical Extent Factor"] = ""
            p["Radial Extent Factor"] = ""
            p["PEC Launch Width"] = ""
        return p

    @property
    def ref_terminal(self):
        """Reference terminal.

        Returns
        -------
        :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

        """
        return self.reference_terminal

    @ref_terminal.setter
    def ref_terminal(self, value):
        self.reference_terminal = value

    @_hfss_port_property.setter
    def _hfss_port_property(self, value):
        txt = []
        for k, v in value.items():
            txt.append("'{}'='{}'".format(k, v))
        txt = ",".join(txt)
        self._edb_properties = "HFSS({})".format(txt)

    @property
    def hfss_type(self):
        """HFSS port type."""
        return self._hfss_port_property["HFSS Type"]

    @hfss_type.setter
    def hfss_type(self, value):
        p = self._hfss_port_property
        p["HFSS Type"] = value
        self._hfss_port_property = p

    @property
    def layer(self):
        """Get layer of the terminal.

        Returns
        -------
        str : layer name.
        """
        return self.reference_layer.name

    @layer.setter
    def layer(self, value):
        from ansys.edb.core.layer.layer import Layer

        if isinstance(value, Layer):
            self.reference_layer = value
        if isinstance(value, str):
            self.reference_layer = self._pedb.stackup.layers[value]

    @property
    def do_renormalize(self):
        """Determine whether port renormalization is enabled.

        Returns
        -------
        bool

        """
        return self.port_post_processing_prop.do_renormalize

    @do_renormalize.setter
    def do_renormalize(self, value):
        self.port_post_processing_prop.do_renormalize = value

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Net name.
        """
        return self.net.name

    @property
    def terminal_type(self):
        """Terminal Type. Accepted values for setter: `"edge"`, `"point"`, `"terminal_instance"`,
        `"padstack_instance"`, `"bundle_terminal"`, `"pin_group"`.

        Returns
        -------
        str
        """
        return self.type.name.lower()

    @terminal_type.setter
    def terminal_type(self, value):
        self.type = self._terminal_type_mapping[value]

    @property
    def boundary_type(self):
        """Boundary type.

        Returns
        -------
        str
            port, pec, rlc, current_source, voltage_source, nexxim_ground, nexxim_pPort, dc_terminal, voltage_probe.
        """
        return super().boundary_type.name.lower()

    @boundary_type.setter
    def boundary_type(self, value):
        super(Terminal, self.__class__).boundary_type.__set__(self, self._boundary_type_mapping[value])

    @property
    def is_port(self):
        """Whether it is a port.

        Returns
        -------
        bool

        """
        return True if self.boundary_type == "port" else False

    @property
    def is_current_source(self):
        """Whether it is a current source.

        Returns
        -------
        bool

        """
        return True if self.boundary_type == "current_source" else False

    @property
    def is_voltage_source(self):
        """Whether it is a voltage source.

        Returns
        -------
        bool

        """
        return True if self.boundary_type == "voltage_source" else False

    @property
    def impedance(self):
        """Impedance of the port.

        Returns
        -------
        float : impedance value.

        """
        return self.impedance.value

    @impedance.setter
    def impedance(self, value):
        self.impedance = GrpcValue(value)

    @property
    def reference_object(self):  # pragma : no cover
        """This returns the object assigned as reference. It can be a primitive or a padstack instance.


        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>` or
        :class:`Primitive <pyedb.grpc.database.primitive.primitives.Primitive>`
        """
        if not self._reference_object:
            if self.terminal_type == "edge":
                edges = self.edges
                edgeType = edges[0].type
                if edgeType == GrpcEdgeType.PADSTACK:
                    self._reference_object = self.get_pad_edge_terminal_reference_pin()
                else:
                    self._reference_object = self.get_edge_terminal_reference_primitive()
            elif self.terminal_type == "pin_group":
                self._reference_object = self.get_pin_group_terminal_reference_pin()
            elif self.terminal_type == "point":
                self._reference_object = self.get_point_terminal_reference_primitive()
            elif self.terminal_type == "padstack_instance":
                self._reference_object = self.get_padstack_terminal_reference_pin()
            else:
                self._pedb.logger.warning("Invalid Terminal Type={}")
                return False

        return self._reference_object

    @property
    def reference_net_name(self):
        """Net name to which reference_object belongs.

        Returns
        -------
        str : net name.

        """
        if self.reference_object:
            return self.reference_object.net_name

        return ""

    def get_padstack_terminal_reference_pin(self, gnd_net_name_preference=None):  # pragma : no cover
        """Get a list of pad stacks instances and serves Coax wave ports,
        pingroup terminals, PadEdge terminals.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name.

        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
        """

        if self.is_circuit_port:
            return self.get_pin_group_terminal_reference_pin()
        _, padStackInstance, _ = self.get_parameters()

        # Get the pastack instance of the terminal
        pins = self._pedb.components.get_pin_from_component(self.component.name)
        return self._get_closest_pin(padStackInstance, pins, gnd_net_name_preference)

    def get_pin_group_terminal_reference_pin(self, gnd_net_name_preference=None):  # pragma : no cover
        """Return a list of pins and serves terminals connected to pingroups.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name.

        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
        """

        refTerm = self.reference_terminal
        if self.type == GrpcTerminalType.PIN_GROUP:
            padStackInstance = self.pin_group.pins[0]
            pingroup = refTerm.pin_group
            refPinList = pingroup.pins
            return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
        elif self.type == GrpcTerminalType.PADSTACK_INST:
            _, padStackInstance, _ = self.get_parameters()
            if refTerm.type == GrpcTerminalType.PIN_GROUP:
                pingroup = refTerm.pin_group
                refPinList = pingroup.pins
                return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
            else:
                try:
                    _, refTermPSI, _ = refTerm.get_parameters()
                    return EDBPadstackInstance(refTermPSI, self._pedb)
                except AttributeError:
                    return False
        return False

    def get_edge_terminal_reference_primitive(self):  # pragma : no cover
        """Check and return a primitive instance that serves Edge ports,
        wave-ports and coupled-edge ports that are directly connected to primitives.

        Returns
        -------
        :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`
        """

        ref_layer = self.reference_layer
        edges = self.edges
        _, _, point_data = edges[0].get_parameters()
        # shape_pd = self._pedb.edb_api.geometry.point_data(X, Y)
        layer_name = ref_layer.name
        for primitive in self._pedb.layout.primitives:
            if primitive.layer.name == layer_name:
                if primitive.polygon_data.point_in_polygon(point_data):
                    return cast(primitive, self._pedb)
        return None  # pragma: no cover

    def get_point_terminal_reference_primitive(self):  # pragma : no cover
        """Find and return the primitive reference for the point terminal or the padstack instance.

        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>` or
        :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`
        """

        ref_term = self.reference_terminal  # return value is type terminal
        _, point_data, layer = ref_term.get_parameters()
        # shape_pd = self._pedb.edb_api.geometry.point_data(X, Y)
        layer_name = layer.name
        for primitive in self._pedb.layout.primitives:
            if primitive.layer.name == layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if primitive.polygon_data.point_in_polygon(point_data):
                    return cast(primitive, self._pedb)
        for vias in self._pedb.padstacks.instances.values():
            if layer_name in vias.layer_range_names:
                plane = self._pedb.modeler.Shape(
                    "rectangle", pointA=vias.position, pointB=vias.padstack_definition.bounding_box[1]
                )
                rectangle_data = vias._pedb.modeler.shape_to_polygon_data(plane)
                if rectangle_data.point_in_polygon(point_data):
                    return vias
        return False

    def get_pad_edge_terminal_reference_pin(self, gnd_net_name_preference=None):
        """Get the closest pin padstack instances and serves any edge terminal connected to a pad.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name. Optianal, default is `None` which will auto compute the gnd name.

        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
        """
        comp_inst = self.component
        pins = self._pedb.components.get_pin_from_component(comp_inst.name)
        edges = self.edges
        _, pad_edge_pstack_inst, _, _ = edges[0].get_parameters()
        return self._get_closest_pin(pad_edge_pstack_inst, pins, gnd_net_name_preference)

    def _get_closest_pin(self, ref_pin, pin_list, gnd_net=None):
        _, pad_stack_inst_point, _ = ref_pin.position_and_rotation  # get the xy of the padstack
        if gnd_net is not None:
            power_ground_net_names = [gnd_net]
        else:
            power_ground_net_names = [net for net in self._pedb.nets.power.keys()]
        comp_ref_pins = [i for i in pin_list if i.net.name in power_ground_net_names]
        if len(comp_ref_pins) == 0:  # pragma: no cover
            self._pedb.logger.error(
                "Terminal with PadStack Instance Name {} component has no reference pins.".format(ref_pin.GetName())
            )
            return None
        closest_pin_distance = None
        pin_obj = None
        for pin in comp_ref_pins:  # find the distance to all the pins to the terminal pin
            if pin.name == ref_pin.name:  # skip the reference psi
                continue  # pragma: no cover
            _, pin_point, _ = pin.position_and_rotation
            distance = pad_stack_inst_point.distance(pin_point)
            if closest_pin_distance is None:
                closest_pin_distance = distance
                pin_obj = pin
            elif closest_pin_distance < distance:
                continue
            else:
                closest_pin_distance = distance
                pin_obj = pin
        if pin_obj:
            return EDBPadstackInstance(pin_obj, self._pedb)

    @property
    def magnitude(self):
        """Get the magnitude of the source.

        Returns
        -------
        float : source magnitude.
        """
        return self.source_amplitude.value

    @magnitude.setter
    def magnitude(self, value):
        self.source_amplitude = GrpcValue(value)

    @property
    def phase(self):
        """Get the phase of the source.

        Returns
        -------
        float : source phase.

        """
        return self.source_phase.value

    @phase.setter
    def phase(self, value):
        self.source_phase = GrpcValue(value)

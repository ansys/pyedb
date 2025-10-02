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
import warnings

from pyedb.dotnet.database.cell.connectable import Connectable
from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.primitives_data import cast


class Terminal(Connectable):
    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._reference_object = None

        self._boundary_type_mapping = {
            "InvalidBoundary": self._pedb.core.Cell.Terminal.BoundaryType.InvalidBoundary,
            "PortBoundary": self._pedb.core.Cell.Terminal.BoundaryType.PortBoundary,
            "PecBoundary": self._pedb.core.Cell.Terminal.BoundaryType.PecBoundary,
            "RlcBoundary": self._pedb.core.Cell.Terminal.BoundaryType.RlcBoundary,
            "kCurrentSource": self._pedb.core.Cell.Terminal.BoundaryType.kCurrentSource,
            "kVoltageSource": self._pedb.core.Cell.Terminal.BoundaryType.kVoltageSource,
            "kNexximGround": self._pedb.core.Cell.Terminal.BoundaryType.kNexximGround,
            "kNexximPort": self._pedb.core.Cell.Terminal.BoundaryType.kNexximPort,
            "kDcTerminal": self._pedb.core.Cell.Terminal.BoundaryType.kDcTerminal,
            "kVoltageProbe": self._pedb.core.Cell.Terminal.BoundaryType.kVoltageProbe,
        }

        self._terminal_type_mapping = {
            "InvalidTerminal": self._pedb.core.Cell.Terminal.TerminalType.InvalidTerminal,
            "EdgeTerminal": self._pedb.core.Cell.Terminal.TerminalType.EdgeTerminal,
            "PointTerminal": self._pedb.core.Cell.Terminal.TerminalType.PointTerminal,
            "TerminalInstanceTerminal": self._pedb.core.Cell.Terminal.TerminalType.TerminalInstanceTerminal,
            "PadstackInstanceTerminal": self._pedb.core.Cell.Terminal.TerminalType.PadstackInstanceTerminal,
            "BundleTerminal": self._pedb.core.Cell.Terminal.TerminalType.BundleTerminal,
            "PinGroupTerminal": self._pedb.core.Cell.Terminal.TerminalType.PinGroupTerminal,
        }

        self._source_term_to_ground_mapping = {
            "kNoGround": self._pedb.core.Cell.Terminal.SourceTermToGround.kNoGround,
            "kNegative": self._pedb.core.Cell.Terminal.SourceTermToGround.kNegative,
            "kPositive": self._pedb.core.Cell.Terminal.SourceTermToGround.kPositive,
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
        """Get layer of the terminal."""
        return self._pedb.logger.error("Cannot determine terminal layer")

    @property
    def is_circuit_port(self):
        """Whether it is a circuit port."""
        return self._edb_object.GetIsCircuitPort()

    @is_circuit_port.setter
    def is_circuit_port(self, value):
        self._edb_object.SetIsCircuitPort(value)

    @property
    def _port_post_processing_prop(self):
        """Get port post processing properties."""
        return self._edb_object.GetPortPostProcessingProp()

    @_port_post_processing_prop.setter
    def _port_post_processing_prop(self, value):
        self._edb_object.SetPortPostProcessingProp(value)

    @property
    def do_renormalize(self):
        """Determine whether port renormalization is enabled."""
        return self._port_post_processing_prop.DoRenormalize

    @do_renormalize.setter
    def do_renormalize(self, value):
        ppp = self._port_post_processing_prop
        ppp.DoRenormalize = value
        self._port_post_processing_prop = ppp

    @property
    def terminal_type(self):
        """Terminal Type.

        Returns
        -------
        int
        """
        return self._edb_object.GetTerminalType().ToString()

    @terminal_type.setter
    def terminal_type(self, value):
        self._edb_object.GetTerminalType(self._terminal_type_mapping[value])

    @property
    def boundary_type(self):
        """Boundary type.

        Returns
        -------
        str
            InvalidBoundary, PortBoundary, PecBoundary, RlcBoundary, kCurrentSource, kVoltageSource, kNexximGround,
            kNexximPort, kDcTerminal, kVoltageProbe
        """
        return self._edb_object.GetBoundaryType().ToString()

    @boundary_type.setter
    def boundary_type(self, value):
        self._edb_object.SetBoundaryType(self._boundary_type_mapping[value])

    @property
    def is_port(self):
        """Whether it is a port."""
        return True if self.boundary_type == "PortBoundary" else False

    @property
    def is_current_source(self):
        """Whether it is a current source."""
        return True if self.boundary_type == "kCurrentSource" else False

    @property
    def is_voltage_source(self):
        """Whether it is a voltage source."""
        return True if self.boundary_type == "kVoltageSource" else False

    @property
    def impedance(self):
        """Impedance of the port."""
        return self._edb_object.GetImpedance().ToDouble()

    @impedance.setter
    def impedance(self, value):
        self._edb_object.SetImpedance(self._pedb.edb_value(value))

    @property
    def is_reference_terminal(self):
        """Whether it is a reference terminal."""
        return self._edb_object.IsReferenceTerminal()

    @property
    def reference_terminal(self):
        """Adding grpc compatibility."""
        edb_terminal = self._edb_object.GetReferenceTerminal()
        if not edb_terminal.IsNull():
            return self._pedb.terminals[edb_terminal.GetName()]
        else:
            return None

    @reference_terminal.setter
    def reference_terminal(self, value):
        self._edb_object.SetReferenceTerminal(value._edb_object)

    @property
    def ref_terminal(self):
        """Get reference terminal.

        .deprecated:: pyedb 0.47.0
        Use: attribute:`reference_terminal` instead.

        """
        warnings.warn(
            "`ref_terminal` is deprecated, use `reference_terminal` instead.",
            DeprecationWarning,
        )
        return self.reference_terminal

    @ref_terminal.setter
    def ref_terminal(self, value):
        self.reference_terminal = value

    @property
    def reference_object(self):  # pragma : no cover
        """This returns the object assigned as reference. It can be a primitive or a padstack instance.


        Returns
        -------
        :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`
        """
        if not self._reference_object:
            term = self._edb_object

            if self.terminal_type == self._pedb.core.Cell.Terminal.TerminalType.EdgeTerminal:
                edges = self._edb_object.GetEdges()
                edgeType = edges[0].GetEdgeType()
                if edgeType == self._pedb.core.Cell.Terminal.EdgeType.PadEdge:
                    self._reference_object = self.get_pad_edge_terminal_reference_pin()
                else:
                    self._reference_object = self.get_edge_terminal_reference_primitive()
            elif self.terminal_type == "PinGroupTerminal":
                self._reference_object = self.get_pin_group_terminal_reference_pin()
            elif self.terminal_type == "PointTerminal":
                self._reference_object = self.get_point_terminal_reference_primitive()
            elif self.terminal_type == "PadstackInstanceTerminal":
                self._reference_object = self.get_padstack_terminal_reference_pin()
            else:
                self._pedb.logger.warning("Invalid Terminal Type={}".format(term.GetTerminalType()))

        return self._reference_object

    @property
    def reference_net_name(self):
        """Net name to which reference_object belongs."""
        ref_obj = self._reference_object if self._reference_object else self.reference_object
        if ref_obj:
            return ref_obj.net_name

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
        :class:`dotnet.database.edb_data.padstack_data.EDBPadstackInstance`
        """

        if self._edb_object.GetIsCircuitPort():
            return self.get_pin_group_terminal_reference_pin()
        _, padStackInstance, _ = self._edb_object.GetParameters()

        # Get the pastack instance of the terminal
        compInst = self._edb_object.GetComponent()
        pins = self._pedb.components.get_pin_from_component(compInst.GetName())
        return self._get_closest_pin(padStackInstance, pins, gnd_net_name_preference)

    def get_pin_group_terminal_reference_pin(self, gnd_net_name_preference=None):  # pragma : no cover
        """Return a list of pins and serves terminals connected to pingroups.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name.

        Returns
        -------
        :class:`dotnet.database.edb_data.padstack_data.EDBPadstackInstance`
        """

        refTerm = self._edb_object.GetReferenceTerminal()
        if self._edb_object.GetTerminalType() == self._pedb.core.Cell.Terminal.TerminalType.PinGroupTerminal:
            padStackInstance = self._edb_object.GetPinGroup().GetPins()[0]
            pingroup = refTerm.GetPinGroup()
            refPinList = pingroup.GetPins()
            return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
        elif self._edb_object.GetTerminalType() == self._pedb.core.Cell.Terminal.TerminalType.PadstackInstanceTerminal:
            _, padStackInstance, _ = self._edb_object.GetParameters()
            if refTerm.GetTerminalType() == self._pedb.core.Cell.Terminal.TerminalType.PinGroupTerminal:
                pingroup = refTerm.GetPinGroup()
                refPinList = pingroup.GetPins()
                return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
            else:
                try:
                    _, refTermPSI, _ = refTerm.GetParameters()
                    return EDBPadstackInstance(refTermPSI, self._pedb)
                except AttributeError:
                    return False
        return False

    def get_edge_terminal_reference_primitive(self):  # pragma : no cover
        """Check and  return a primitive instance that serves Edge ports,
        wave ports and coupled edge ports that are directly connedted to primitives.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`
        """

        ref_layer = self._edb_object.GetReferenceLayer()
        edges = self._edb_object.GetEdges()
        _, _, point_data = edges[0].GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.core.geometry.point_data(X, Y)
        layer_name = ref_layer.GetName()
        for primitive in self._pedb.layout.primitives:
            if primitive.GetLayer().GetName() == layer_name or not layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return cast(primitive, self._pedb)
        return None  # pragma: no cover

    def get_point_terminal_reference_primitive(self):  # pragma : no cover
        """Find and return the primitive reference for the point terminal or the padstack instance.

        Returns
        -------
        :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`
        """

        ref_term = self._edb_object.GetReferenceTerminal()  # return value is type terminal
        _, point_data, layer = ref_term.GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.core.geometry.point_data(X, Y)
        layer_name = layer.GetName()
        for primitive in self._pedb.layout.primitives:
            if primitive.GetLayer().GetName() == layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return cast(primitive, self._pedb)
        for vias in self._pedb.padstacks.instances.values():
            if layer_name in vias.layer_range_names:
                plane = self._pedb.modeler.Shape(
                    "rectangle", pointA=vias.position, pointB=vias.padstack_definition.bounding_box[1]
                )
                rectangle_data = vias._pedb.modeler.shape_to_polygon_data(plane)
                if rectangle_data.PointInPolygon(shape_pd):
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
        :class:`pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`
        """
        comp_inst = self._edb_object.GetComponent()
        pins = self._pedb.components.get_pin_from_component(comp_inst.GetName())
        try:
            edges = self._edb_object.GetEdges()
        except AttributeError:
            return False
        _, pad_edge_pstack_inst, _, _ = edges[0].GetParameters()
        return self._get_closest_pin(pad_edge_pstack_inst, pins, gnd_net_name_preference)

    def _get_closest_pin(self, ref_pin, pin_list, gnd_net=None):
        _, pad_stack_inst_point, _ = ref_pin.GetPositionAndRotation()  # get the xy of the padstack
        if gnd_net is not None:
            power_ground_net_names = [gnd_net]
        else:
            power_ground_net_names = [net for net in self._pedb.nets.power.keys()]
        pin_list = [
            EDBPadstackInstance(pin, self._pedb)
            for pin in pin_list
            if str(pin) == "Ansys.Ansoft.Edb.Cell.Primitive.PadstackInstance"
        ]
        comp_ref_pins = [i for i in pin_list if i.net_name in power_ground_net_names]
        if len(comp_ref_pins) == 0:  # pragma: no cover
            self._pedb.logger.error(
                "Terminal with PadStack Instance Name {} component has no reference pins.".format(ref_pin.GetName())
            )
            return None
        closest_pin_distance = None
        pin_obj = None
        for pin in comp_ref_pins:  # find the distance to all the pins to the terminal pin
            if pin.component_pin == ref_pin.GetName():  # skip the reference psi
                continue  # pragma: no cover
            _, pin_point, _ = pin._edb_object.GetPositionAndRotation()
            distance = pad_stack_inst_point.Distance(pin_point)
            if closest_pin_distance is None:
                closest_pin_distance = distance
                pin_obj = pin
            elif closest_pin_distance < distance:
                continue
            else:
                closest_pin_distance = distance
                pin_obj = pin
        if pin_obj:
            return pin_obj

    @property
    def magnitude(self):
        """Get the magnitude of the source."""
        return self._edb_object.GetSourceAmplitude().ToDouble()

    @magnitude.setter
    def magnitude(self, value):
        self._edb_object.SetSourceAmplitude(self._edb.Utility.Value(value))

    @property
    def phase(self):
        """Get the phase of the source."""
        return self._edb_object.GetSourcePhase().ToDouble()

    @phase.setter
    def phase(self, value):
        self._edb_object.SetSourcePhase(self._edb.Utility.Value(value))

    @property
    def amplitude(self):
        """Property added for grpc compatibility"""
        return self.magnitude

    @property
    def source_amplitude(self):
        """Property added for grpc compatibility"""
        return self.magnitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        self.magnitude = value

    @property
    def source_phase(self):
        """Property added for grpc compatibility"""
        return self.phase

    @source_phase.setter
    def source_phase(self, value):
        self.phase = value

    @property
    def terminal_to_ground(self):
        return self._edb_object.GetTerminalToGround().ToString()

    @terminal_to_ground.setter
    def terminal_to_ground(self, value):
        obj = self._source_term_to_ground_mapping[value]
        self._edb_object.SetTerminalToGround(obj)

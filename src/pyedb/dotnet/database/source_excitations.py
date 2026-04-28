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

import time
from typing import Set

from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import PadstackInstanceTerminal
from pyedb.dotnet.database.cell.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal
from pyedb.dotnet.database.cell.terminal.terminal import Terminal
from pyedb.dotnet.database.edb_data.nets_data import EDBNetsData
from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.ports import BundleWavePort, CircuitPort, CoaxPort, GapPort, WavePort
from pyedb.dotnet.database.edb_data.sources import (
    CircuitPortBuilder,
    CurrentSourceBuilder,
    ResistorSourceBuilder,
    SourceType,
    VoltageSourceBuilder,
)
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.generic.general_methods import _retry_ntimes, generate_unique_name
from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.misc.decorators import deprecated


class SourceExcitation:
    """Manage sources and excitations."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._edb = self._pedb._edb
        self._active_layout = self._pedb.active_layout

    def get_edge_from_port(self, port):
        res, primitive, point = port._edb_object.GetEdges()[0].GetParameters()

        primitive = Primitive(self._pedb, primitive)
        point = [point.X.ToString(), point.Y.ToString()]
        return res, primitive, point

    def _create_edge_terminal(self, prim_id, point_on_edge, terminal_name=None, is_ref=False):
        """
        Create an edge terminal.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        terminal_name : str, optional
            Name of the terminal. The default is ``None``, in which case the
            default name is assigned.
        is_ref : bool, optional
            Whether it is a reference terminal. The default is ``False``.

        Returns
        -------
        Edb.Cell.Terminal.EdgeTerminal

        """
        if not terminal_name:
            terminal_name = generate_unique_name("Terminal_")
        if isinstance(point_on_edge, (list, tuple)):
            if len(point_on_edge) > 2:
                point_on_edge = [
                    self._pedb._edb.Geometry.PointData(self._pedb.edb_value(pt[0]), self._pedb.edb_value(pt[1]))
                    for pt in point_on_edge
                ]
            else:
                point_on_edge = [
                    self._pedb._edb.Geometry.PointData(
                        self._pedb.edb_value(point_on_edge[0]), self._pedb.edb_value(point_on_edge[1])
                    )
                ]
        if hasattr(prim_id, "GetId"):
            prim = prim_id
        else:
            prim = self._pedb.layout.find_object_by_id(prim_id).core
        pos_edge = []
        for pt in point_on_edge:
            edge = self._pedb._edb.Cell.Terminal.PrimitiveEdge.Create(prim, pt)
            pos_edge.append(edge)
        # pos_edge = self._pedb._edb.Cell.Terminal.PrimitiveEdge.Create(prim, point_on_edge)
        pos_edge = convert_py_list_to_net_list(pos_edge, self._pedb._edb.Cell.Terminal.Edge)
        return self._pedb._edb.Cell.Terminal.EdgeTerminal.Create(
            prim.GetLayout(), prim.GetNet(), terminal_name, pos_edge, isRef=is_ref
        )

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """
        Create a circuit port on a pin.

        Parameters
        ----------
        pos_pin : Object
            Edb Pin
        neg_pin : Object
            Edb Pin
        impedance : float
            Port Impedance
        port_name : str, optional
            Port Name

        Returns
        -------
        str
            Port Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")

        """
        circuit_port = CircuitPortBuilder()
        if not isinstance(pos_pin, EDBPadstackInstance):
            pos_pin = EDBPadstackInstance(pos_pin, self._pedb)
        if not isinstance(neg_pin, EDBPadstackInstance):
            neg_pin = EDBPadstackInstance(neg_pin, self._pedb)
        circuit_port.positive_node.net = pos_pin.net_name
        circuit_port.negative_node.net = neg_pin.net_name
        circuit_port.impedance = impedance

        if not port_name:
            port_name = "Port_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_pin.component
        circuit_port.positive_node.node_pins = pos_pin
        circuit_port.negative_node.component_node = neg_pin.component
        circuit_port.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(circuit_port)

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """
        Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")

        """

        voltage_source = VoltageSourceBuilder()
        voltage_source.positive_node.net = pos_pin.net_name
        voltage_source.negative_node.net = neg_pin.net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        if not source_name:
            source_name = "VSource_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_pin.component
        voltage_source.positive_node.node_pins = pos_pin
        voltage_source.negative_node.component_node = neg_pin.component
        voltage_source.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(voltage_source)

    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """
        Create a current source.

        Parameters
        ----------
        pos_pin : Object
            Positive pin.
        neg_pin : Object
            Negative pin.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")

        """
        current_source = CurrentSourceBuilder()
        current_source.positive_node.net = pos_pin.net_name
        current_source.negative_node.net = neg_pin.net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        if not source_name:
            source_name = "ISource_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_pin.component
        current_source.positive_node.node_pins = pos_pin
        current_source.negative_node.component_node = neg_pin.component
        current_source.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(current_source)

    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """
        Create a Resistor boundary between two given pins..

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Name of the resistor.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_resistor_on_pin(pins[0], pins[1], 50, "res_name")

        """
        resistor = ResistorSourceBuilder()
        resistor.positive_node.net = pos_pin.net_name
        resistor.negative_node.net = neg_pin.net_name
        resistor.rvalue = rvalue
        if not resistor_name:
            resistor_name = "Res_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        resistor.name = resistor_name
        resistor.positive_node.component_node = pos_pin.component
        resistor.positive_node.node_pins = pos_pin
        resistor.negative_node.component_node = neg_pin.component
        resistor.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(resistor)

    def _check_gnd(self, component_name):
        negative_net_name = None
        if self._pedb.nets.is_net_in_component(component_name, "GND"):
            negative_net_name = "GND"
        elif self._pedb.nets.is_net_in_component(component_name, "PGND"):
            negative_net_name = "PGND"
        elif self._pedb.nets.is_net_in_component(component_name, "AGND"):
            negative_net_name = "AGND"
        elif self._pedb.nets.is_net_in_component(component_name, "DGND"):
            negative_net_name = "DGND"
        if not negative_net_name:
            raise ValueError("No GND, PGND, AGND, DGND found. Please setup the negative net name manually.")
        return negative_net_name

    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        impedance_value=50,
        port_name="",
    ):
        """
        Create a circuit port on a NET.

        It groups all pins belonging to the specified net and then applies the port on PinGroups.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            The name of the port.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.excitation_manager.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")

        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        circuit_port = CircuitPortBuilder()
        circuit_port.positive_node.net = positive_net_name
        circuit_port.negative_node.net = negative_net_name
        circuit_port.impedance = impedance_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)
        if port_name == "":
            port_name = "Port_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_node_cmp
        circuit_port.positive_node.node_pins = pos_node_pins
        circuit_port.negative_node.component_node = neg_node_cmp
        circuit_port.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(circuit_port)

    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        voltage_value=3.3,
        phase_value=0,
        source_name="",
    ):
        """
        Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitation_manager.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")

        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        voltage_source = VoltageSourceBuilder()
        voltage_source.positive_node.net = positive_net_name
        voltage_source.negative_node.net = negative_net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Vsource_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_node_cmp
        voltage_source.positive_node.node_pins = pos_node_pins
        voltage_source.negative_node.component_node = neg_node_cmp
        voltage_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(voltage_source)

    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """
        Create a current source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitation_manager.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")

        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        current_source = CurrentSourceBuilder()
        current_source.positive_node.net = positive_net_name
        current_source.negative_node.net = negative_net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Port_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_node_cmp
        current_source.positive_node.node_pins = pos_node_pins
        current_source.negative_node.component_node = neg_node_cmp
        current_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(current_source)

    def create_coax_port_on_component(self, ref_des_list, net_list, delete_existing_terminal=False):
        """
        Create a coaxial port on a component or component list on a net or net list.
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

        delete_existing_terminal : bool
            Only active with grpc version. This argument is added only to ensure compatibility between DotNet and grpc.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        coax = []
        if delete_existing_terminal:
            self._pedb.logger.warning(f"flag delete_existing_terminal is set to True but is only supported with grpc.")
        if not isinstance(ref_des_list, list):
            ref_des_list = [ref_des_list]
        if not isinstance(net_list, list):
            net_list = [net_list]
        for ref in ref_des_list:
            for _, py_inst in self._pedb.components.instances[ref].pins.items():
                if py_inst.net_name in net_list and py_inst.is_pin:
                    port_name = "{}_{}_{}".format(ref, py_inst.net_name, py_inst.pin.GetName())
                    (
                        res,
                        from_layer_pos,
                        to_layer_pos,
                    ) = py_inst.pin.GetLayerRange()
                    if (
                        res
                        and from_layer_pos
                        and self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
                            self._active_layout,
                            py_inst.pin.GetNet(),
                            port_name,
                            py_inst.pin,
                            to_layer_pos,
                        )
                    ):
                        coax.append(port_name)
        return coax

    def create_bundle_wave_port(
        self,
        primitives_id,
        points_on_edge,
        port_name=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """
        Create a bundle wave port.

        Parameters
        ----------
        primitives_id : list
            Primitive ID of the positive terminal.
        points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (port_name, pyedb.egacy.database.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.excitation_manager.create_bundle_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])

        """
        if not port_name:
            port_name = generate_unique_name("bundle_port")

        if isinstance(primitives_id[0], Primitive):
            primitives_id = [i.id for i in primitives_id]

        terminals = []
        _port_name = port_name
        for p_id, loc in list(zip(primitives_id, points_on_edge)):
            _, term = self.create_wave_port(
                p_id,
                loc,
                port_name=_port_name,
                horizontal_extent_factor=horizontal_extent_factor,
                vertical_extent_factor=vertical_extent_factor,
                pec_launch_width=pec_launch_width,
            )
            _port_name = None
            terminals.append(term)

        edb_list = convert_py_list_to_net_list([i._edb_object for i in terminals], self._edb.Cell.Terminal.Terminal)
        _edb_bundle_terminal = self._edb.Cell.Terminal.BundleTerminal.Create(edb_list)
        return BundleWavePort(self._pedb, _edb_bundle_terminal)

    def create_differential_wave_port(
        self,
        positive_primitive_id,
        positive_points_on_edge,
        negative_primitive_id,
        negative_points_on_edge,
        port_name=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """
        Create a differential wave port.

        Parameters
        ----------
        positive_primitive_id : int, EDBPrimitives
            Primitive ID of the positive terminal.
        positive_points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        negative_primitive_id : int, EDBPrimitives
            Primitive ID of the negative terminal.
        negative_points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (port_name, pyedb.dotnet.database.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.excitation_manager.create_differential_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])

        """
        if not port_name:
            port_name = generate_unique_name("diff")

        if isinstance(positive_primitive_id, Primitive):
            positive_primitive_id = positive_primitive_id.id

        if isinstance(negative_primitive_id, Primitive):
            negative_primitive_id = negative_primitive_id.id

        _, pos_term = self.create_wave_port(
            positive_primitive_id,
            positive_points_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        _, neg_term = self.create_wave_port(
            negative_primitive_id,
            negative_points_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        edb_list = convert_py_list_to_net_list(
            [pos_term._edb_object, neg_term._edb_object], self._edb.Cell.Terminal.Terminal
        )
        _edb_boundle_terminal = self._edb.Cell.Terminal.BundleTerminal.Create(edb_list)
        _edb_boundle_terminal.SetName(port_name)
        pos, neg = list(_edb_boundle_terminal.GetTerminals())
        pos.SetName(port_name + ":T1")
        neg.SetName(port_name + ":T2")
        return port_name, BundleWavePort(self._pedb, _edb_boundle_terminal)

    @deprecated("Use excitation_manager.create_edge_port method instead.")
    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """
        Create an HFSS port on a padstack.

        .. deprecated:: 0.70.0
           Use :func:`excitation_manager.create_edge_port` instead.

        Parameters
        ----------
        pinpos :
            Position of the pin.

        portname : str, optional
             Name of the port. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange()

        if not portname:
            portname = generate_unique_name("Port_" + pinpos.GetNet().GetName())
        edbpointTerm_pos = self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
            self._active_layout, pinpos.GetNet(), portname, pinpos, toLayer_pos
        )
        if edbpointTerm_pos:
            return True
        else:
            return False

    def create_port_between_pin_and_layer(
        self, component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0
    ):
        """
        Create circuit port between pin and a reference layer.

        Parameters
        ----------
        component_name : str
            Component name. The default is ``None``.
        pins_name : str
            Pin name or list of pin names. The default is ``None``.
        layer_name : str
            Layer name. The default is ``None``.
        reference_net : str
            Reference net name. The default is ``None``.
        impedance : float, optional
            Port impedance. The default is ``50.0`` in ohms.

        Returns
        -------
        PadstackInstanceTerminal
            Created terminal.

        """
        if not pins_name:
            pins_name = []
        if pins_name:
            if not isinstance(pins_name, list):  # pragma no cover
                pins_name = [pins_name]
            if not reference_net:
                self._pedb.logger.info("no reference net provided, searching net {} instead.".format(layer_name))
                reference_net = self._pedb.nets.get_net_by_name(layer_name)
                if not reference_net:  # pragma no cover
                    self._pedb.logger.error("reference net {} not found.".format(layer_name))
                    return False
            else:
                if not isinstance(reference_net, self._edb.Cell.Net):  # pragma no cover
                    reference_net = self._pedb.nets.get_net_by_name(reference_net)
                if not reference_net:
                    self._pedb.logger.error("Net {} not found".format(reference_net))
                    return False
            for pin_name in pins_name:  # pragma no cover
                pin = [
                    pin
                    for pin in self._pedb.padstacks.get_pinlist_from_component_and_net(component_name)
                    if pin.component_pin == pin_name
                ][0]
                term_name = "{}_{}_{}".format(pin.component.name, pin._edb_object.GetNet().GetName(), pin.component_pin)
                res, start_layer, stop_layer = pin._edb_object.GetLayerRange()
                if res:
                    pin_instance = pin._edb_padstackinstance
                    positive_terminal = self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
                        self._active_layout, pin_instance.GetNet(), term_name, pin_instance, start_layer
                    )
                    positive_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                    positive_terminal.SetImpedance(self._edb.Utility.Value(impedance))
                    positive_terminal.SetIsCircuitPort(True)
                    pos = self._pedb.components.get_pin_position(pin_instance)
                    position = self._edb.Geometry.PointData(
                        self._edb.Utility.Value(pos[0]), self._edb.Utility.Value(pos[1])
                    )
                    negative_terminal = self._edb.Cell.Terminal.PointTerminal.Create(
                        self._active_layout,
                        reference_net.net_obj,
                        "{}_ref".format(term_name),
                        position,
                        self._pedb.stackup.signal_layers[layer_name]._edb_layer,
                    )
                    negative_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                    negative_terminal.SetImpedance(self._edb.Utility.Value(impedance))
                    negative_terminal.SetIsCircuitPort(True)
                    if positive_terminal.SetReferenceTerminal(negative_terminal):
                        self._pedb.logger.info("Port {} successfully created".format(term_name))
                        return positive_terminal
            return False

    def _create_terminal_on_pins(
        self, source: VoltageSourceBuilder | CurrentSourceBuilder | CurrentSourceBuilder | ResistorSourceBuilder
    ):
        """
        Create a terminal on pins.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource or ResistorSource
            Name of the source.

        """
        if isinstance(source.positive_node.node_pins, EDBPadstackInstance):
            pos_pin = source.positive_node.node_pins._edb_padstackinstance
        else:
            pos_pin = source.positive_node.node_pins
        if isinstance(source.negative_node.node_pins, EDBPadstackInstance):
            neg_pin = source.negative_node.node_pins._edb_padstackinstance
        else:
            neg_pin = source.negative_node.node_pins

        res, fromLayer_pos, toLayer_pos = pos_pin.GetLayerRange()
        res, fromLayer_neg, toLayer_neg = neg_pin.GetLayerRange()

        pos_pingroup_terminal = _retry_ntimes(
            10,
            self._edb.Cell.Terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            pos_pin.GetNet(),
            pos_pin.GetName(),
            pos_pin,
            toLayer_pos,
        )
        time.sleep(0.5)
        neg_pingroup_terminal = _retry_ntimes(
            20,
            self._edb.Cell.Terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            neg_pin.GetNet(),
            neg_pin.GetName(),
            neg_pin,
            toLayer_neg,
        )
        if source.source_type in [SourceType.CoaxPort, SourceType.CircPort, SourceType.LumpedPort]:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetImpedance(self._pedb.edb_value(source.impedance))
            if source.source_type == SourceType.CircPort:
                pos_pingroup_terminal.SetIsCircuitPort(True)
                neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._pedb.logger.warning("%s already exists. Renaming to %s", source.name, name)
        elif source.source_type == SourceType.Isource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._pedb.edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._pedb.edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except Exception as e:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._pedb.logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Vsource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._pedb.edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._pedb.edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._pedb.logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Rlc:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._pedb.edb_value(source.rvalue))
            Rlc = self._edb.Utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = self._pedb.edb_value(source.rvalue)
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._pedb.logger.warning("%s already exists. Renaming to %s", source.name, name)
        else:
            pass
        return pos_pingroup_terminal.GetName()

    def create_padstack_instance_terminal(self, name="", padstack_instance_id=None, padstack_instance_name=None):
        pds = self._pedb.layout.find_padstack_instances(
            instance_id=padstack_instance_id,
            aedt_name=padstack_instance_name,
            component_name=None,
            component_pin_name=None,
        )
        if len(pds) == 0:
            raise ValueError(f"Padstack instance {padstack_instance_id} or {padstack_instance_name} not found.")
        else:
            pds = pds[0]

        _name = name if name else generate_unique_name(pds.aedt_name)
        terminal = pds.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: padstack_instance_id={padstack_instance_id}, "
                f"padstack_instance_name={padstack_instance_name}, name={name}."
            )
        return terminal

    def create_pin_group_terminal(self, pin_group):
        return self._pedb.siwave.create_pin_group_terminal(pin_group)

    def create_terminal_from_pin_group(self, pin_group, name=""):
        _name = name if name else generate_unique_name(pin_group)
        pg = self._pedb.siwave.pin_groups[pin_group]
        terminal = pg.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(f"Failed to create terminal. Input arguments: pin_group={pin_group}, name={name}.")
        return terminal

    def create_point_terminal(self, x, y, layer, net, name=""):
        from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal

        _name = name if name else f"point_{layer}_{x}_{y}"
        location = [x, y]
        point_terminal = PointTerminal(self._pedb)
        terminal = point_terminal.create(_name, net, location, layer)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: x={x}, y={y}, layer={layer}, net={net}, name={name}."
            )
        return terminal

    def create_edge_terminal(self, primitive_name, x, y, name=""):
        from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal

        _name = name if name else f"{primitive_name}_{x}_{y}"

        pt = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(self._pedb, x=x, y=y)
        primitive = self._pedb.layout.primitives_by_aedt_name[primitive_name]
        edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, pt.core)
        edge = convert_py_list_to_net_list(edge, self._pedb.core.Cell.Terminal.Edge)
        _terminal = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            _name,
            edge,
            isRef=False,
        )
        terminal = EdgeTerminal(self._pedb, _terminal)

        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: primitive_name={primitive_name}, x={x}, y={y},"
                f" name={name}."
            )
        return terminal

    def create_bundle_terminal(self, terminals, name=""):
        from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal

        _name = name if name else f"{generate_unique_name('bundle')}"

        terminal = BundleTerminal.create(self._pedb, _name, terminals)
        return terminal

    def create_edge_port(
        self,
        location,
        primitive_name,
        name,
        impedance=50,
        is_wave_port=True,
        horizontal_extent_factor=1,
        vertical_extent_factor=1,
        pec_launch_width=0.0001,
    ) -> WavePort:
        """
        Create an edge port on a primitive specific location.

        Parameters
        ----------
        location : list
            Port location.
        primitive_name : str
            Name of primitive.
        name : str
            Port name.
        impedance : float, optional
            Impedance.
        is_wave_port : bool, optional
            Whether if it is a wave port or gap port.
        horizontal_extent_factor : float, optional
            Horizontal extent factor for wave ports.
        vertical_extent_factor  : float, optional
            Vertical extent factor for wave ports.
        pec_launch_width : float, optional
            Pec launcher width for wave ports.

        """
        point_on_edge = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(
            self._pedb, self._pedb.value(location[0]), self._pedb.value(location[1])
        ).core
        primitive = self._pedb.layout.primitives_by_aedt_name[primitive_name]
        pos_edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, point_on_edge)
        pos_edge = convert_py_list_to_net_list(pos_edge, self._pedb.core.Cell.Terminal.Edge)
        edge_term = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            name,
            pos_edge,
            isRef=False,
        )
        edge_term.SetImpedance(self._pedb.edb_value(impedance))
        wave_port = WavePort(self._pedb, edge_term)
        wave_port.horizontal_extent_factor = horizontal_extent_factor
        wave_port.vertical_extent_factor = vertical_extent_factor
        wave_port.pec_launch_width = pec_launch_width
        if is_wave_port == "wave_port":
            wave_port.hfss_type = "Wave"
        else:
            wave_port.hfss_type = "Gap"
        wave_port.do_renormalize = True
        return wave_port

    def create_edge_port_on_polygon(
        self,
        polygon=None,
        reference_polygon=None,
        terminal_point=None,
        reference_point=None,
        reference_layer=None,
        port_name=None,
        port_impedance=50.0,
        force_circuit_port=False,
    ):
        """
        Create lumped port between two edges from two different polygons. Can also create a vertical port when
        the reference layer name is only provided. When a port is created between two edge from two polygons which don't
        belong to the same layer, a circuit port will be automatically created instead of lumped. To enforce the circuit
        port instead of lumped,use the boolean force_circuit_port.

        Parameters
        ----------
        polygon : The EDB polygon object used to assign the port.
            Edb.Cell.Primitive.Polygon object.

        reference_polygon : The EDB polygon object used to define the port reference.
            Edb.Cell.Primitive.Polygon object.

        terminal_point : The coordinate of the point to define the edge terminal of the port. This point must be
        located on the edge of the polygon where the port has to be placed. For instance taking the middle point
        of an edge is a good practice but any point of the edge should be valid. Taking a corner might cause unwanted
        port location.
            list[float, float] with values provided in meter.

        reference_point : same as terminal_point but used for defining the reference location on the edge.
            list[float, float] with values provided in meter.

        reference_layer : Name used to define port reference for vertical ports.
            str the layer name.

        port_name : Name of the port.
            str.

        port_impedance : port impedance value. Default value is 50 Ohms.
            float, impedance value.

        force_circuit_port ; used to force circuit port creation instead of lumped. Works for vertical and coplanar
        ports.

        Examples
        --------

        >>> edb_path = path_to_edb
        >>> edb = Edb(edb_path)
        >>> poly_list = [poly for poly in list(edb.layout.primitives) if poly.GetPrimitiveType() == 2]
        >>> port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
        >>> ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
        >>> port_location = [-65e-3, -13e-3]
        >>> ref_location = [-63e-3, -13e-3]
        >>> edb.excitation_manager.create_edge_port_on_polygon(polygon=port_poly, reference_polygon=ref_poly,
        >>> terminal_point=port_location, reference_point=ref_location)

        """
        if not polygon:
            self._pedb.logger.error("No polygon provided for port {} creation".format(port_name))
            return False
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
            if not reference_layer:
                self._pedb.logger.error("Specified layer for port {} creation was not found".format(port_name))
        if not isinstance(terminal_point, list):
            self._pedb.logger.error("Terminal point must be a list of float with providing the point location in meter")
            return False
        terminal_point = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(
            self._pedb, terminal_point[0], terminal_point[1]
        ).core

        if reference_point and isinstance(reference_point, list):
            reference_point = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(
                self._pedb, reference_point[0], reference_point[1]
            ).core
        if not port_name:
            port_name = generate_unique_name("Port_")
        edge = self._pedb._edb.Cell.Terminal.PrimitiveEdge.Create(polygon._edb_object, terminal_point)
        edges = convert_py_list_to_net_list(edge, self._pedb._edb.Cell.Terminal.Edge)
        edge_term = self._pedb._edb.Cell.Terminal.EdgeTerminal.Create(
            polygon._edb_object.GetLayout(), polygon._edb_object.GetNet(), port_name, edges, isRef=False
        )
        if force_circuit_port:
            edge_term.SetIsCircuitPort(True)
        else:
            edge_term.SetIsCircuitPort(False)

        if port_impedance:
            edge_term.SetImpedance(self._pedb.edb_value(port_impedance))
        edge_term.SetName(port_name)
        if reference_polygon and reference_point:
            ref_edge = self._pedb._edb.Cell.Terminal.PrimitiveEdge.Create(
                reference_polygon._edb_object, reference_point
            )
            ref_edges = convert_py_list_to_net_list(ref_edge, self._pedb._edb.Cell.Terminal.Edge)
            ref_edge_term = self._pedb._edb.Cell.Terminal.EdgeTerminal.Create(
                reference_polygon._edb_object.GetLayout(),
                reference_polygon._edb_object.GetNet(),
                port_name + "_ref",
                ref_edges,
                isRef=True,
            )
            if reference_layer:
                ref_edge_term.SetReferenceLayer(reference_layer)
            if force_circuit_port:
                ref_edge_term.SetIsCircuitPort(True)
            else:
                ref_edge_term.SetIsCircuitPort(False)

            if port_impedance:
                ref_edge_term.SetImpedance(self._pedb.edb_value(port_impedance))
            edge_term.SetReferenceTerminal(ref_edge_term)
        return True

    def create_horizontal_wave_port(
        self,
        void: int | Primitive,
        padstack_instances: list = None,
        pec_launch_width: str = "0.04mm",
        layer_alignment: str = "Lower",
    ) -> bool:
        """
        Create a horizontal wave port around one or more vias inside a void.

        A horizontal wave port is a higher-fidelity alternative to coaxial lumped
        ports for vertical interconnect excitation. Unlike a gap or lumped port,
        which assumes a uniform current distribution, a wave port solves the field
        distribution at the launch and therefore captures a more realistic
        characteristic impedance. This usually improves the evaluation of fringing
        fields and can noticeably affect results for differential pairs and other
        high-speed channel structures.

        Parameters
        ----------
        void : int | Primitive
            Void primitive, or void primitive ID, used to define the horizontal
            wave-port reference contour.
        padstack_instances : list[PadstackInstance], optional
            Padstack instances to connect to the horizontal wave port. When not
            provided, padstack instances are automatically detected from the vias
            intersecting the void polygon.
        pec_launch_width : str, optional
            PEC launch width assigned to the HFSS solver option. The default is
            ``"0.04mm"``.
        layer_alignment : str, optional
            HFSS layer alignment for the wave port. Typical values are
            ``"Lower"`` and ``"Upper"``. The default is ``"Lower"``.

        Returns
        -------
        bool | BundleTerminal
            Bundle terminal representing the created horizontal wave port. If no
            padstack instance is found inside the target void, ``False`` is
            returned.

        Notes
        -----
        Horizontal wave ports can be used in place of coaxial lumped ports when a
        more physical launch model is required. Because the wave port computes the
        electromagnetic field distribution, it produces a more realistic impedance
        than gap-port formulations that assume uniform current. This also improves
        fringing-field estimation and can have a significant impact on extracted
        results for differential links and other high-speed interconnect channels.

        """
        from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal

        port_number = len(self._pedb.ports) + 1
        terminals = []
        if isinstance(void, int):
            void = self._pedb.layout.get_object_by_id(void)
            if not void:
                raise Exception(f"No void found for given ID {void}")
        if not padstack_instances:
            # finding padstack instances included inside the void
            instance_ids = self._pedb.padstacks.get_padstack_instances_id_intersecting_polygon(
                points=void.polygon_data.points_without_arcs
            )
            padstack_instances = [self._pedb.padstacks.instances[inst_id] for inst_id in instance_ids]
            if not padstack_instances:
                self._pedb.logger.error(
                    f"No padstack instance find inside void primitive {void}, no horizontal wave port created."
                )
                return False
            self._pedb.logger.info(
                f"Creating horizontal wave port {void}, {len(padstack_instances)} padstack instances found "
                "inside the void."
            )
            self._pedb.logger.info(f"{len(padstack_instances)} padstack instances found inside the void.")

        # void terminal
        segments = void.polygon_data.arcs
        edges = [self._pedb._edb.Cell.Terminal.PrimitiveEdge.Create(void.core, seg.mid_point) for seg in segments]
        layout = self._pedb.layout.core
        net = void.net.net_object
        _edges = convert_py_list_to_net_list(edges, self._pedb._edb.Cell.Terminal.Edge)
        edge_term = self._pedb._edb.Cell.Terminal.EdgeTerminal.Create(layout, net, f"Ref_{void.id}", _edges, False)
        edge_term = EdgeTerminal(self._pedb, edge_term)

        symbol_def = self._pedb._edb.Definition.PadstackDef.FindByName(self._pedb.active_db, "Symbol")
        inst_ind = 0
        for via in padstack_instances:
            port_net = self._pedb.nets.find_or_create_net(f"Port{port_number}:{via.net.name}")
            inst_ind += 1
            symbol = self._pedb.padstacks.place(
                position=via.position,
                definition_name=symbol_def.GetName(),
                net_name=port_net.name,
                via_name=f"Port{port_number}_psi{inst_ind}",
                rotation=via.rotation,
                fromlayer=via.start_layer,
                tolayer=via.stop_layer,
            )
            symbol.is_layout_pin = True
            symbol.aedt_name = f"Port{port_number}:{via.net.name}"

            symbol.core.SetProductProperty(
                self._pedb.core.ProductId.Designer, 21, "$begin ''\n\tsid=3\n\tmat='copper'\n\tvs='Mesh'\n$end ''\n"
            )

            term = PadstackInstanceTerminal.create(
                edb=self._pedb, padstack_instance=symbol, name=symbol.aedt_name, layer=symbol.start_layer, is_ref=False
            )
            terminals.append(term)

        port_names_str = ", ".join(f"'{inst.aedt_name}'" for inst in padstack_instances)
        edge_term.core.SetProductProperty(
            self._pedb.core.ProductId.Designer,
            25,
            f"$begin ''\n\tType='Pad Port'\n\tArms=2\n\tHFSSLastType=8\n"
            f"\tHorizWavePort({port_names_str})\n\tHorizWavePrimary=true\n\tIsGapSource=true\n$end ''\n",
        )
        for term in terminals:
            term.core.SetProductProperty(
                self._pedb.core.ProductId.Designer,
                25,
                f"$begin ''\n\tType='Pad Port'\n\tArms=3\n\tHFSSLastType=8\n"
                f"\tHorizWavePort('{term.padstack_instance.aedt_name}')\n\tIsGapSource=true\n$end ''\n",
            )

        hfss_solver_str = (
            f"HFSS('HFSS Type'='Wave(coax)', Orientation='Horizontal', "
            f"'Layer Alignment'='{layer_alignment}', 'Horizontal Extent Factor'='5', "
            f"'Vertical Extent Factor'='3', 'Radial Extent Factor'='0', "
            f"'PEC Launch Width'='{pec_launch_width}', ReferenceName='')"
        )
        planar_em_str = "PlanarEM(Type='Pad Port Gap Source', PortSolver=true, 'Ignore Reference'=false)"
        siwave_str = "SIwave('Reference Net'='')"

        terminals.append(edge_term)
        for term in terminals:
            term.core.SetProductSolverOption(self._pedb.core.ProductId.Designer, "HFSS", hfss_solver_str)
            term.core.SetProductSolverOption(self._pedb.core.ProductId.Designer, "PlanarEM", planar_em_str)
            term.core.SetProductSolverOption(self._pedb.core.ProductId.Designer, "SIwave", siwave_str)

            pp = term.core.GetPortPostProcessingProp()
            pp.ExcitationVoltageMag = self._pedb.edb_value(1.0)
            pp.DoDeembed = True
            pp.DoRenormalize = True
            term.core.SetPortPostProcessingProp(pp)

        edb_list = convert_py_list_to_net_list(
            [term.core for term in terminals], self._pedb._edb.Cell.Terminal.Terminal
        )
        self._pedb._edb.Cell.Terminal.BundleTerminal.Create(edb_list)
        return True

    def create_wave_port(
        self,
        prim_id,
        point_on_edge,
        port_name=None,
        impedance=50,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """
        Create a wave port.

        Parameters
        ----------
        prim_id : int, Primitive
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (Port name, pyedb.dotnet.database.edb_data.sources.Excitation).

        Examples
        --------
        >>> edb.excitation_manager.create_wave_port(0, ["-50mm", "-0mm"])

        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")

        if isinstance(prim_id, Primitive):
            prim_id = prim_id.id

        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))

        wave_port = WavePort(self._pedb, pos_edge_term)
        wave_port.horizontal_extent_factor = horizontal_extent_factor
        wave_port.vertical_extent_factor = vertical_extent_factor
        wave_port.pec_launch_width = pec_launch_width
        wave_port.hfss_type = "Wave"
        wave_port.do_renormalize = True
        if pos_edge_term:
            return port_name, wave_port
        else:
            return False

    def create_edge_port_vertical(
        self,
        prim_id,
        point_on_edge,
        port_name=None,
        impedance=50,
        reference_layer=None,
        hfss_type="Gap",
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """
        Create a vertical edge port.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        reference_layer : str, optional
            Reference layer of the port. The default is ``None``.
        hfss_type : str, optional
            Type of the port. The default value is ``"Gap"``. Options are ``"Gap"``, ``"Wave"``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        radial_extent_factor : int, float, optional
            Radial extent factor. The default value is ``0``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        str
            Port name.

        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")
        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
            pos_edge_term.SetReferenceLayer(reference_layer)

        prop = ", ".join(
            [
                "HFSS('HFSS Type'='{}'".format(hfss_type),
                " Orientation='Vertical'",
                " 'Layer Alignment'='Upper'",
                " 'Horizontal Extent Factor'='{}'".format(horizontal_extent_factor),
                " 'Vertical Extent Factor'='{}'".format(vertical_extent_factor),
                " 'PEC Launch Width'='{}')".format(pec_launch_width),
            ]
        )
        pos_edge_term.SetProductSolverOption(
            self._pedb.core.ProductId.Designer,
            "HFSS",
            prop,
        )
        if pos_edge_term:
            return port_name, self._pedb.hfss.ports[port_name]
        else:
            return False

    def create_edge_port_horizontal(
        self,
        prim_id,
        point_on_edge,
        ref_prim_id=None,
        point_on_ref_edge=None,
        port_name=None,
        impedance=50,
        layer_alignment="Upper",
    ):
        """
        Create a horizontal edge port.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        ref_prim_id : int, optional
            Reference primitive ID. The default is ``None``.
        point_on_ref_edge : list, optional
            Coordinate of the point to define the reference edge
            terminal. The point must be on the target edge but not
            on the two ends of the edge. The default is ``None``.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        layer_alignment : str, optional
            Layer alignment. The default value is ``Upper``. Options are ``"Upper"``, ``"Lower"``.

        Returns
        -------
        str
            Name of the port.

        """
        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        neg_edge_term = self._create_edge_terminal(ref_prim_id, point_on_ref_edge, port_name + "_ref", is_ref=True)

        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))
        pos_edge_term.SetReferenceTerminal(neg_edge_term)
        if not layer_alignment == "Upper":
            layer_alignment = "Lower"
        pos_edge_term.SetProductSolverOption(
            self._pedb.core.ProductId.Designer,
            "HFSS",
            "HFSS('HFSS Type'='Gap(coax)', Orientation='Horizontal', 'Layer Alignment'='{}')".format(layer_alignment),
        )
        if pos_edge_term:
            return port_name
        else:
            return False

    def create_lumped_port_on_net(
        self, nets=None, reference_layer=None, return_points_only=False, digit_resolution=6, at_bounding_box=True
    ):
        """
        Create an edge port on nets. This command looks for traces and polygons on the
        nets and tries to assign vertical lumped port.

        Parameters
        ----------
        nets : list, optional
            List of nets, str or Edb net.

        reference_layer : str, Edb layer.
             Name or Edb layer object.

        return_points_only : bool, optional
            Use this boolean when you want to return only the points from the edges and not creating ports. Default
            value is ``False``.

        digit_resolution : int, optional
            The number of digits carried for the edge location accuracy. The default value is ``6``.

        at_bounding_box : bool
            When ``True`` will keep the edges from traces at the layout bounding box location. This is recommended when
             a cutout has been performed before and lumped ports have to be created on ending traces. Default value is
             ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = [self._pedb._edb.Cell.net.find_by_name(self._active_layout, nets)]
            elif isinstance(nets, self._pedb._edb.Cell.net.net):
                nets = [nets]
        else:
            temp_nets = []
            for nn in nets:
                if isinstance(nn, str):
                    temp_nets.append(self._pedb._edb.Cell.net.find_by_name(self._active_layout, nn))
                elif isinstance(nn, self._pedb._edb.Cell.net.net):
                    temp_nets.append(nn)
            nets = temp_nets
        port_created = False
        if nets:
            edges_pts = []
            if isinstance(reference_layer, str):
                try:
                    reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
                except:
                    raise Exception("Failed to get the layer {}".format(reference_layer))
            if not isinstance(reference_layer, self._pedb._edb.Cell.ILayerReadOnly):
                return False
            layout = nets[0].GetLayout()
            layout_bbox = self._pedb.get_conformal_polygon_from_netlist(self._pedb.nets.netlist)
            layout_extent_segments = [pt for pt in list(layout_bbox.GetArcData()) if pt.IsSegment()]
            first_pt = layout_extent_segments[0]
            layout_extent_points = [
                [first_pt.Start.X.ToDouble(), first_pt.End.X.ToDouble()],
                [first_pt.Start.Y.ToDouble(), first_pt.End.Y.ToDouble()],
            ]
            for segment in layout_extent_segments[1:]:
                end_point = (segment.End.X.ToDouble(), segment.End.Y.ToDouble())
                layout_extent_points[0].append(end_point[0])
                layout_extent_points[1].append(end_point[1])
            for net in nets:
                net_primitives = self._pedb.nets[net.name].primitives
                net_paths = [pp for pp in net_primitives if pp.type == "Path"]
                for path in net_paths:
                    trace_path_pts = list(path.center_line.Points)
                    port_name = "{}_{}".format(net.name, path.GetId())
                    for pt in trace_path_pts:
                        _pt = [
                            round(pt.X.ToDouble(), digit_resolution),
                            round(pt.Y.ToDouble(), digit_resolution),
                        ]
                        if at_bounding_box:
                            if GeometryOperators.point_in_polygon(_pt, layout_extent_points) == 0:
                                if return_points_only:
                                    edges_pts.append(_pt)
                                else:
                                    term = self._create_edge_terminal(path.id, pt, port_name)  # pragma no cover
                                    term.SetReferenceLayer(reference_layer)  # pragma no cover
                                    port_created = True
                        else:
                            if return_points_only:  # pragma: no cover
                                edges_pts.append(_pt)
                            else:
                                term = self._create_edge_terminal(path.id, pt, port_name)
                                term.SetReferenceLayer(reference_layer)
                                port_created = True
                net_poly = [pp for pp in net_primitives if pp.type == "Polygon"]
                for poly in net_poly:
                    poly_segment = [aa for aa in poly.arcs if aa.is_segment]
                    for segment in poly_segment:
                        if (
                            GeometryOperators.point_in_polygon(
                                [segment.mid_point.X.ToDouble(), segment.mid_point.Y.ToDouble()], layout_extent_points
                            )
                            == 0
                        ):
                            if return_points_only:
                                edges_pts.append(segment.mid_point)
                            else:
                                port_name = "{}_{}".format(net.name, poly.GetId())
                                term = self._create_edge_terminal(
                                    poly.id, segment.mid_point, port_name
                                )  # pragma no cover
                                term.SetReferenceLayer(reference_layer)  # pragma no cover
                                port_created = True
            if return_points_only:
                return edges_pts
        return port_created

    def create_vertical_circuit_port_on_clipped_traces(self, nets=None, reference_net=None, user_defined_extent=None):
        """
        Create an edge port on clipped signal traces.

        Parameters
        ----------
        nets : list, optional
            String of one net or EDB net or a list of multiple nets or EDB nets.

        reference_net : str, Edb net.
             Name or EDB reference net.

        user_defined_extent : [x, y], EDB PolygonData
            Use this point list or PolygonData object to check if ports are at this polygon border.

        Returns
        -------
        [[str]]
            Nested list of str, with net name as first value, X value for point at border, Y value for point at border,
            and terminal name.

        """
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = list(self._pedb.nets.signal.values())
        else:
            nets = [self._pedb.nets.signal[net] for net in nets]
        if nets:
            if isinstance(reference_net, str):
                reference_net = self._pedb.nets[reference_net]
            if not reference_net:
                self._pedb.logger.error("No reference net provided for creating port")
                return False
            if user_defined_extent:
                if isinstance(user_defined_extent, self._edb.Geometry.PolygonData):
                    _points = [pt for pt in list(user_defined_extent.Points)]
                    _x = []
                    _y = []
                    for pt in _points:
                        if pt.X.ToDouble() < 1e100 and pt.Y.ToDouble() < 1e100:
                            _x.append(pt.X.ToDouble())
                            _y.append(pt.Y.ToDouble())
                    user_defined_extent = [_x, _y]
            terminal_info = []
            for net in nets:
                net_polygons = [
                    pp
                    for pp in net.primitives
                    if pp._edb_object.GetPrimitiveType() == self._pedb._edb.Cell.Primitive.PrimitiveType.Polygon
                ]
                for poly in net_polygons:
                    mid_points = [[arc.mid_point.X.ToDouble(), arc.mid_point.Y.ToDouble()] for arc in poly.arcs]
                    for mid_point in mid_points:
                        if GeometryOperators.point_in_polygon(mid_point, user_defined_extent) == 0:
                            port_name = generate_unique_name("{}_{}".format(poly.net.name, poly.id))
                            term = self._create_edge_terminal(poly.id, mid_point, port_name)  # pragma no cover
                            if not term.IsNull():
                                self._pedb.logger.info("Terminal {} created".format(term.GetName()))
                                term.SetIsCircuitPort(True)
                                terminal_info.append([poly.net.name, mid_point[0], mid_point[1], term.GetName()])
                                mid_pt_data = self._edb.Geometry.PointData(
                                    self._edb.Utility.Value(mid_point[0]), self._edb.Utility.Value(mid_point[1])
                                )
                                ref_prim = [
                                    prim
                                    for prim in reference_net.primitives
                                    if prim.polygon_data._edb_object.PointInPolygon(mid_pt_data)
                                ]
                                if not ref_prim:
                                    self._pedb.logger.warning(
                                        "no reference primitive found, trying to extend scanning area"
                                    )
                                    scanning_zone = [
                                        (mid_point[0] - mid_point[0] * 1e-3, mid_point[1] - mid_point[1] * 1e-3),
                                        (mid_point[0] - mid_point[0] * 1e-3, mid_point[1] + mid_point[1] * 1e-3),
                                        (mid_point[0] + mid_point[0] * 1e-3, mid_point[1] + mid_point[1] * 1e-3),
                                        (mid_point[0] + mid_point[0] * 1e-3, mid_point[1] - mid_point[1] * 1e-3),
                                    ]
                                    for new_point in scanning_zone:
                                        mid_pt_data = self._edb.Geometry.PointData(
                                            self._edb.Utility.Value(new_point[0]), self._edb.Utility.Value(new_point[1])
                                        )
                                        ref_prim = [
                                            prim
                                            for prim in reference_net.primitives
                                            if prim.polygon_data.core.PointInPolygon(mid_pt_data)
                                        ]
                                        if ref_prim:
                                            self._pedb.logger.info("Reference primitive found")
                                            break
                                    if not ref_prim:
                                        self._pedb.logger.error(
                                            "Failed to collect valid reference primitives for terminal"
                                        )
                                if ref_prim:
                                    reference_layer = ref_prim[0].layer._edb_layer
                                    if term.SetReferenceLayer(reference_layer):  # pragma no cover
                                        self._pedb.logger.info("Port {} created".format(port_name))
            return terminal_info
        return False

    def create_rlc_boundary_on_pins(self, positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0):
        """
        Create hfss rlc boundary on pins.

        Parameters
        ----------
        positive_pin : Positive pin.
            Edb.Cell.Primitive.PadstackInstance

        negative_pin : Negative pin.
            Edb.Cell.Primitive.PadstackInstance

        rvalue : Resistance value

        lvalue : Inductance value

        cvalue . Capacitance value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if positive_pin and negative_pin:
            positive_pin_term = self._pedb.components._create_terminal(positive_pin)
            negative_pin_term = self._pedb.components._create_terminal(negative_pin)
            positive_pin_term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            negative_pin_term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            rlc = self._edb.Utility.Rlc()
            rlc.IsParallel = True
            rlc.REnabled = True
            rlc.LEnabled = True
            rlc.CEnabled = True
            rlc.R = self._pedb.edb_value(rvalue)
            rlc.L = self._pedb.edb_value(lvalue)
            rlc.C = self._pedb.edb_value(cvalue)
            positive_pin_term.SetRlcBoundaryParameters(rlc)
            term_name = "{}_{}_{}".format(
                positive_pin.GetComponent().GetName(), positive_pin.GetNet().GetName(), positive_pin.GetName()
            )
            positive_pin_term.SetName(term_name)
            negative_pin_term.SetName("{}_ref".format(term_name))
            positive_pin_term.SetReferenceTerminal(negative_pin_term)
            return True
        return False  # pragma no cover

    def create_circuit_port_on_pin_group(self, pos_pin_group_name, neg_pin_group_name, impedance=50, name=None):
        """
        Create a port between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        impedance : int, float, optional
            Impedance of the port. Default is ``50``.
        name : str, optional
            Port name.

        Returns
        -------
        bool

        """
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_port_terminal(impedance)
        if name:  # pragma: no cover
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("port")
            pos_terminal.SetName(name)
        neg_pin_group = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group.create_port_terminal(impedance)
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

    def create_current_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None
    ):
        """
        Create current source between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        magnitude : int, float, optional
            Magnitude of the source.
        phase : int, float, optional
            Phase of the source

        Returns
        -------
        bool

        """
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_current_source_terminal(magnitude, phase)
        if name:
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("isource")
            pos_terminal.SetName(name)
        neg_pin_group_name = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group_name.create_current_source_terminal()
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

    @property
    def pin_groups(self):
        """
        All Layout Pin groups.

        Returns
        -------
        list
            List of all layout pin groups.

        """
        _pingroups = {}
        for el in self._pedb.layout.pin_groups:
            _pingroups[el._edb_object.GetName()] = el
        return _pingroups

    def create_voltage_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001
    ):
        """
        Create voltage source between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        magnitude : int, float, optional
            Magnitude of the source.
        phase : int, float, optional
            Phase of the source

        Returns
        -------
        bool

        """
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_voltage_source_terminal(magnitude, phase, impedance)
        if name:
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("vsource")
            pos_terminal.SetName(name)
        neg_pin_group_name = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group_name.create_voltage_source_terminal(magnitude, phase)
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

    def create_voltage_probe_on_pin_group(self, probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000):
        """
        Create voltage probe between two pin groups.

        Parameters
        ----------
        probe_name : str
            Name of the probe.
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        impedance : int, float, optional
            Phase of the source.

        Returns
        -------
        bool

        """
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_voltage_probe_terminal(impedance)
        if probe_name:
            pos_terminal.SetName(probe_name)
        else:
            probe_name = generate_unique_name("vprobe")
            pos_terminal.SetName(probe_name)
        neg_pin_group = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group.create_voltage_probe_terminal()
        neg_terminal.SetName(probe_name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return not pos_terminal.IsNull()

    def create_port_on_component(
        self,
        component,
        net_list,
        port_type=SourceType.CoaxPort,
        do_pingroup=True,
        reference_net="gnd",
        port_name=None,
        solder_balls_height=None,
        solder_balls_size=None,
        solder_balls_mid_size=None,
        extend_reference_pins_outside_component=False,
    ):
        """
        Create ports on a component.

        Parameters
        ----------
        component : str or  self._pedb.component
            EDB component or str component name.
        net_list : str or list of string.
            List of nets where ports must be created on the component.
            If the net is not part of the component, this parameter is skipped.
        port_type : SourceType enumerator, CoaxPort or CircuitPort
            Type of port to create. ``CoaxPort`` generates solder balls.
            ``CircuitPort`` generates circuit ports on pins belonging to the net list.
        do_pingroup : bool
            True activate pingroup during port creation (only used with combination of CircPort),
            False will take the closest reference pin and generate one port per signal pin.
        refnet : string or list of string.
            list of the reference net.
        port_name : str
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.
        solder_balls_height : float, optional
            Solder balls height used for the component. When provided default value is overwritten and must be
            provided in meter.
        solder_balls_size : float, optional
            Solder balls diameter. When provided auto evaluation based on padstack size will be disabled.
        solder_balls_mid_size : float, optional
            Solder balls mid-diameter. When provided if value is different than solder balls size, spheroid shape will
            be switched.
        extend_reference_pins_outside_component : bool
            When no reference pins are found on the component extend the pins search with taking the closest one. If
            `do_pingroup` is `True` will be set to `False`. Default value is `False`.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> net_list = ["M_DQ<1>", "M_DQ<2>", "M_DQ<3>", "M_DQ<4>", "M_DQ<5>"]
        >>> edbapp.components.create_port_on_component(cmp="U2A5", net_list=net_list,
        >>> port_type=SourceType.CoaxPort, do_pingroup=False, refnet="GND")

        """
        # Adding grpc compatibility
        if not isinstance(port_type, int):
            if port_type == "circuit_port":
                port_type = SourceType.CircPort
            elif port_type in ["coaxial_port", "coax_port"]:
                port_type = SourceType.CoaxPort
            elif port_type == "lumped_port":
                port_type = SourceType.LumpedPort
            elif port_type == "rlc":
                port_type = SourceType.Rlc
            elif port_type == "current_source":
                port_type = SourceType.Isource
            elif port_type == "voltage_source":
                port_type = SourceType.Vsource
            elif port_type == "dc_terminal":
                port_type = SourceType.DcTerminal
            else:
                self._pedb.logger.error(f"Port type {port_type} seems to be for grpc version but is not compatible.")
                return False
        if isinstance(component, str):
            component = self._pedb.components.instances[component].edbcomponent

        nets = self._normalize_net_list(net_list)

        if not isinstance(reference_net, list):
            reference_net = [reference_net]
        ref_nets = self._normalize_net_list(reference_net)
        nets_to_remove = ref_nets.intersection(nets)
        if nets_to_remove:
            self._pedb.logger.warning(f"Removing reference nets {sorted(nets_to_remove)} from the positive net list.")
        nets -= nets_to_remove
        cmp_pins = [p for p in list(component.LayoutObjs) if int(p.GetObjType()) == 1 and p.GetNet().GetName() in nets]
        for p in cmp_pins:
            if not p.IsLayoutPin():
                p.SetIsLayoutPin(True)
        if len(cmp_pins) == 0:
            self._pedb.logger.info(
                "No pins found on component {}, searching padstack instances instead".format(component.GetName())
            )
            return False
        ref_pins = [
            p for p in list(component.LayoutObjs) if int(p.GetObjType()) == 1 and p.GetNet().GetName() in ref_nets
        ]
        pin_layers = cmp_pins[0].GetPadstackDef().GetData().GetLayerNames()
        if port_type == SourceType.CoaxPort:
            if not ref_pins:
                self._pedb.logger.error(
                    "No reference pins found on component. You might consider"
                    "using Circuit port instead since reference pins can be extended"
                    "outside the component when not found if argument extend_reference_pins_outside_component is True."
                )
                return False
            pad_params = self._pedb.padstacks.get_pad_parameters(pin=cmp_pins[0], layername=pin_layers[0], pad_type=0)

            if not solder_balls_height:
                solder_balls_height = self._pedb.components.instances[component.GetName()].solder_ball_height
            if not solder_balls_size:
                solder_balls_size = self._pedb.components.instances[component.GetName()].solder_ball_diameter[0]
            if not solder_balls_mid_size:
                solder_balls_mid_size = self._pedb.components.instances[component.GetName()].solder_ball_diameter[1]

            if not pad_params[0] == 7:
                if not solder_balls_size:  # pragma no cover
                    sball_diam = min([self._pedb.edb_value(val).ToDouble() for val in pad_params[1]])
                    sball_mid_diam = sball_diam
                else:  # pragma no cover
                    sball_diam = solder_balls_size
                    if solder_balls_mid_size:
                        sball_mid_diam = solder_balls_mid_size
                    else:
                        sball_mid_diam = solder_balls_size
                if not solder_balls_height:  # pragma no cover
                    solder_balls_height = 2 * sball_diam / 3
            else:  # pragma no cover
                if not solder_balls_size:
                    bbox = pad_params[1]
                    sball_diam = min([abs(bbox[2] - bbox[0]), abs(bbox[3] - bbox[1])]) * 0.8
                else:
                    sball_diam = solder_balls_size
                if not solder_balls_height:
                    solder_balls_height = 2 * sball_diam / 3
                if solder_balls_mid_size:
                    sball_mid_diam = solder_balls_mid_size
                else:
                    sball_mid_diam = sball_diam
            sball_shape = "Cylinder"
            if not sball_diam == sball_mid_diam:
                sball_shape = "Spheroid"
            self._pedb.components.set_solder_ball(
                component=component,
                sball_height=solder_balls_height,
                sball_diam=sball_diam,
                sball_mid_diam=sball_mid_diam,
                shape=sball_shape,
            )

            for pin in cmp_pins:
                self._pedb.padstacks.create_coax_port(padstackinstance=pin, name=port_name)

        elif port_type == SourceType.CircPort:
            for p in ref_pins:
                if not p.IsLayoutPin():
                    p.SetIsLayoutPin(True)
            if not ref_pins:
                self._pedb.logger.warning("No reference pins found on component")
                if not extend_reference_pins_outside_component:
                    self._pedb.logger.warning(
                        "Argument extend_reference_pins_outside_component is False. You might want "
                        "setting to True to extend the reference pin search outside the component"
                    )
                else:
                    do_pingroup = False
            if do_pingroup:
                if len(ref_pins) == 1:
                    ref_pins.is_pin = True
                    ref_pin_group_term = self._create_terminal(ref_pins[0])
                else:
                    for pin in ref_pins:
                        pin.is_pin = True
                    ref_pin_group = self._pedb.components.create_pingroup_from_pins(ref_pins)
                    if not ref_pin_group:
                        self._pedb.logger.error(
                            f"Failed to create reference pin group on component {component.GetName()}."
                        )
                        return False
                    ref_pin_group = self._pedb.siwave.pin_groups[ref_pin_group.GetName()]
                    ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group, isref=False)
                    if not ref_pin_group_term:
                        self._pedb.logger.error(
                            f"Failed to create reference pin group terminal on component {component.GetName()}"
                        )
                        return False
                for net in nets:
                    pins = [pin for pin in cmp_pins if pin.GetNet().GetName() == net]
                    if pins:
                        if len(pins) == 1:
                            pin_term = self._create_terminal(pins[0])
                            if pin_term:
                                pin_term.SetReferenceTerminal(ref_pin_group_term)
                        else:
                            pin_group = self._pedb.components.create_pingroup_from_pins(pins)
                            if not pin_group:
                                return False
                            pin_group = self._pedb.siwave.pin_groups[pin_group.GetName()]
                            pin_group_term = self._create_pin_group_terminal(pin_group)
                            if pin_group_term:
                                pin_group_term.SetReferenceTerminal(ref_pin_group_term)
                    else:
                        self._pedb.logger.info("No pins found on component {} for the net {}".format(component, net))
            else:
                for net in nets:
                    pins = [pin for pin in cmp_pins if pin.GetNet().GetName() == net]
                    for pin in pins:
                        if ref_pins:
                            self.create_port_on_pins(component, pin, ref_pins)
                        else:
                            if extend_reference_pins_outside_component:
                                _pin = EDBPadstackInstance(pin, self._pedb)
                                ref_pin = _pin.get_reference_pins(
                                    reference_net=reference_net[0],
                                    max_limit=1,
                                    component_only=False,
                                    search_radius=3e-3,
                                )
                                if ref_pin:
                                    self.create_port_on_pins(
                                        component,
                                        [EDBPadstackInstance(pin, self._pedb).name],
                                        [EDBPadstackInstance(ref_pin[0]._edb_object, self._pedb).id],
                                    )
                            else:
                                self._pedb.logger.error("Skipping port creation no reference pin found.")
        return True

    def _normalize_net_list(self, net_list) -> Set[str]:
        if not isinstance(net_list, list):
            net_list = [net_list]
        nets = set()
        for net in net_list:
            if isinstance(net, EDBNetsData):
                net_name = net.name
                if net_name != "":
                    nets.add(net_name)
            elif isinstance(net, str) and net != "":
                nets.add(net)
        return nets

    def _create_pin_group_terminal(self, pingroup, isref=False, term_name=None, term_type="circuit"):
        """
        Creates an EDB pin group terminal from a given EDB pin group.

        Parameters
        ----------
        pingroup : Edb pin group.

        isref : bool
        Specify if this terminal a reference terminal.

        term_name : Terminal name (Optional). If not provided default name is Component name, Pin name, Net name.
            str.

        term_type: Type of terminal, gap, circuit or auto.
        str.
        Returns
        -------
        Edb pin group terminal.

        """
        if not "Cell.Hierarchy.PinGroup" in str(pingroup):
            pingroup = pingroup._edb_object
        pin = list(pingroup.GetPins())[0]
        if term_name is None:
            term_name = "{}.{}.{}".format(pin.GetComponent().GetName(), pin.GetName(), pin.GetNet().GetName())
        for t in list(self._pedb.active_layout.Terminals):
            if t.GetName() == term_name:
                return t
        pingroup_term = self._edb.Cell.Terminal.PinGroupTerminal.Create(
            self._active_layout, pingroup.GetNet(), term_name, pingroup, isref
        )
        if term_type == "circuit":
            pingroup_term.SetIsCircuitPort(True)
        elif term_type == "auto":
            pingroup_term.SetIsAutoPort(True)
        return pingroup_term

    def create_pingroup_from_pins(self, pins, group_name=None):
        """
        Create a pin group on a component.

        Parameters
        ----------
        pins : list
            List of EDB pins.
        group_name : str, optional
            Name for the group. The default is ``None``, in which case
            a default name is assigned as follows: ``[component Name] [NetName]``.

        Returns
        -------
        tuple
            The tuple is structured as: (bool, pingroup).

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")

        """
        if len(pins) < 1:
            self._pedb.logger.error("No pins specified for pin group %s", group_name)
            return (False, None)
        if len([pin for pin in pins if isinstance(pin, EDBPadstackInstance)]):
            _pins = [pin._edb_padstackinstance for pin in pins]
            if _pins:
                pins = _pins
        if group_name is None:
            group_name = self._edb.Cell.Hierarchy.PinGroup.GetUniqueName(self._active_layout)
        for pin in pins:
            pin.SetIsLayoutPin(True)
        forbiden_car = "-><"
        group_name = group_name.translate({ord(i): "_" for i in forbiden_car})
        for pgroup in list(self._pedb.active_layout.PinGroups):
            if pgroup.GetName() == group_name:
                pin_group_exists = True
                if len(pgroup.GetPins()) == len(pins):
                    pnames = [i.GetName() for i in pins]
                    for p in pgroup.GetPins():
                        if p.GetName() in pnames:
                            continue
                        else:
                            group_name = self._edb.Cell.Hierarchy.PinGroup.GetUniqueName(
                                self._active_layout, group_name
                            )
                            pin_group_exists = False
                else:
                    group_name = self._edb.Cell.Hierarchy.PinGroup.GetUniqueName(self._active_layout, group_name)
                    pin_group_exists = False
                if pin_group_exists:
                    return pgroup
        pingroup = _retry_ntimes(
            10,
            self._edb.Cell.Hierarchy.PinGroup.Create,
            self._active_layout,
            group_name,
            convert_py_list_to_net_list(pins),
        )
        if pingroup.IsNull():
            return False
        else:
            pingroup.SetNet(pins[0].GetNet())
            return pingroup

    def create_port_on_pins(
        self,
        refdes,
        pins,
        reference_pins,
        impedance=50.0,
        port_name=None,
        pec_boundary=False,
        pingroup_on_single_pin=False,
    ):
        """
        Create circuit port between pins and reference ones.

        Parameters
        ----------
        refdes : Component reference designator
            str or EDBComponent object.
        pins : pin specifier(s) or instance(s) where the port terminal is to be created. Single pin name or a list of
        several can be provided. If several pins are provided a pin group will be created. Pin specifiers can be the
        global EDB object ID or padstack instance name or pin name on component with refdes ``refdes``. Pin instances
        can be provided as ``EDBPadstackInstance`` objects.
        For instance for the pin called ``Pin1`` located on component with refdes ``U1``: ``U1-Pin1``, ``Pin1`` with
        ``refdes=U1``, the pin's global EDB object ID, or the ``EDBPadstackInstance`` corresponding to the pin can be
        provided.
            Union[int, str, EDBPadstackInstance], List[Union[int, str, EDBPadstackInstance]]
        reference_pins : reference pin specifier(s) or instance(s) for the port reference terminal. Allowed values are
        the same as for the ``pins`` parameter.
            Union[int, str, EDBPadstackInstance], List[Union[int, str, EDBPadstackInstance]]
        impedance : Port impedance
            str, float
        port_name : str, optional
            Port name. The default is ``None``, in which case a name is automatically assigned.
        pec_boundary : bool, optional
        Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
        a perfect short is created between the pin and impedance is ignored. This
        parameter is only supported on a port created between two pins, such as
        when there is no pin group.
        pingroup_on_single_pin : bool
            If ``True`` force using pingroup definition on single pin to have the port created at the pad center. If
            ``False`` the port is created at the pad edge. Default value is ``False``.

        Returns
        -------
        EDB terminal created, or False if failed to create.

        Example:
        >>> from pyedb import Edb
        >>> edb = Edb(path_to_edb_file)
        >>> pin = "AJ6"
        >>> ref_pins = ["AM7", "AM4"]
        Or to take all reference pins
        >>> ref_pins = [pin for pin in list(edb.components["U2A5"].pins.values()) if pin.net_name == "GND"]
        >>> edb.components.create_port_on_pins(refdes="U2A5", pins=pin, reference_pins=ref_pins)
        >>> edb.save()
        >>> edb.close()

        """

        if isinstance(refdes, str):
            refdes = self._pedb.components.instances[refdes]
        elif isinstance(refdes, self._pedb._edb.Cell.Hierarchy.Component):
            from pyedb.dotnet.database.cell.hierarchy.component import EDBComponent

            refdes = EDBComponent(self._pedb, refdes)
        pins = self._pedb.components._get_pins_for_ports(pins, refdes)
        if not pins:  # pragma: no cover
            raise RuntimeError("No pins found during port creation. Port is not defined.")
        reference_pins = self._pedb.components._get_pins_for_ports(reference_pins, refdes)
        if not reference_pins:
            raise RuntimeError("No reference pins found during port creation. Port is not defined.")
        if not pins:
            raise RuntimeWarning("No pins found during port creation. Port is not defined.")
        if reference_pins:
            reference_pins = self._pedb.components._get_pins_for_ports(reference_pins, refdes)
            if not reference_pins:
                raise RuntimeWarning("No reference pins found during port creation. Port is not defined.")
        if refdes and any(refdes.rlc_values):
            return self._pedb.components.deactivate_rlc_component(component=refdes, create_circuit_port=True)
        if not port_name:
            port_name = f"Port_{pins[0].net_name}_{pins[0].aedt_name}".replace("-", "_")

        if len(pins) > 1 or pingroup_on_single_pin:
            if pec_boundary:
                pec_boundary = False
                self._pedb.logger.info(
                    "Disabling PEC boundary creation, this feature is supported on single pin "
                    f"ports only, {len(pins)} pins found (pingroup_on_single_pin: {pingroup_on_single_pin})."
                )
            group_name = "group_{}".format(port_name)
            pin_group = self.create_pingroup_from_pins(pins, group_name)
            term = self._create_pin_group_terminal(pingroup=pin_group, term_name=port_name)
        else:
            term = self._pedb.components._create_terminal(pins[0]._edb_object, term_name=port_name)
        term.SetIsCircuitPort(True)

        if len(reference_pins) > 1 or pingroup_on_single_pin:
            if pec_boundary:
                pec_boundary = False
                self._pedb.logger.info(
                    "Disabling PEC boundary creation. This feature is supported on single pin "
                    f"ports only, {len(reference_pins)} reference pins found "
                    f"(pingroup_on_single_pin: {pingroup_on_single_pin})."
                )
            ref_group_name = f"group_{port_name}_ref"
            ref_pin_group = self.create_pingroup_from_pins(reference_pins, ref_group_name)
            ref_term = self._create_pin_group_terminal(pingroup=ref_pin_group, term_name=port_name + "_ref")
        else:
            ref_term = self._pedb.components._create_terminal(
                reference_pins[0]._edb_object, term_name=port_name + "_ref"
            )
        ref_term.SetIsCircuitPort(True)

        term.SetImpedance(self._edb.Utility.Value(impedance))
        term.SetReferenceTerminal(ref_term)
        if pec_boundary:
            term.SetIsCircuitPort(False)
            ref_term.SetIsCircuitPort(False)
            term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PecBoundary)
            ref_term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PecBoundary)
            self._pedb.logger.info(
                f"PEC boundary created between pin {pins[0].name} and reference pin {reference_pins[0].name}"
            )

        return term or False

    def create_port(
        self,
        terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
        ref_terminal=None,
        is_circuit_port=False,
        name=None,
    ) -> CircuitPort | BundleWavePort | WavePort | CoaxPort | GapPort:
        """
        Create a port.

        Parameters
        ----------
        terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port. The default is ``False``.
        name: str, optional
            Name of the created port. The default is None, a random name is generated.
        Returns
        -------
        list: [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
            :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,].

        """

        terminal.boundary_type = "PortBoundary"
        terminal.is_circuit_port = is_circuit_port

        if ref_terminal:
            ref_terminal.boundary_type = "PortBoundary"
            terminal.reference_terminal = ref_terminal
        if name:
            terminal.name = name

        if terminal.is_circuit_port:
            port = CircuitPort(self._pedb, terminal._edb_object)
        elif terminal.terminal_type == "BundleTerminal":
            port = BundleWavePort(self._pedb, terminal._edb_object)
        elif terminal.hfss_type == "Wave":
            port = WavePort(self._pedb, terminal._edb_object)
        elif terminal.terminal_type == "PadstackInstanceTerminal":
            port = CoaxPort(self._pedb, terminal._edb_object)
        else:
            port = GapPort(self._pedb, terminal._edb_object)
        return port

    def create_voltage_probe(
        self,
        terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
        ref_terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
    ) -> Terminal:
        """
        Create a voltage probe.

        Parameters
        ----------
        terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Negative terminal of the probe.

        Returns
        -------
        pyedb.dotnet.database.edb_data.terminals.Terminal

        """
        term = Terminal(self._pedb, terminal._edb_object)
        term.boundary_type = "kVoltageProbe"

        ref_term = Terminal(self._pedb, ref_terminal._edb_object)
        ref_term.boundary_type = "kVoltageProbe"

        term.reference_terminal = ref_terminal
        return self._pedb.probes[term.name]

    def create_voltage_source(
        self,
        terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
        ref_terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
    ) -> Terminal:
        """
        Create a voltage source.

        Parameters
        ----------
        terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
            Positive terminal of the port.
        ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
            Negative terminal of the source.

        Returns
        -------
        class:`legacy.database.edb_data.ports.ExcitationSources`

        """
        term = Terminal(self._pedb, terminal._edb_object)
        term.boundary_type = "kVoltageSource"

        ref_term = Terminal(self._pedb, ref_terminal._edb_object)
        ref_term.boundary_type = "kVoltageSource"

        term.reference_terminal = ref_terminal
        return self._pedb.sources[term.name]

    def create_current_source(
        self,
        terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
        ref_terminal: EdgeTerminal | PadstackInstanceTerminal | PointTerminal | PinGroupTerminal,
    ) -> Terminal:
        """
        Create a current source.

        Parameters
        ----------
        terminal : :class:`legacy.database.edb_data.terminals.EdgeTerminal`,
            :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`legacy.database.edb_data.terminals.PointTerminal`,
            :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : class:`legacy.database.edb_data.terminals.EdgeTerminal`,
            :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`legacy.database.edb_data.terminals.PointTerminal`,
            :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
            Negative terminal of the source.

        Returns
        -------
        :class:`legacy.edb_core.edb_data.ports.ExcitationSources`

        """
        term = Terminal(self._pedb, terminal._edb_object)
        term.boundary_type = "kCurrentSource"

        ref_term = Terminal(self._pedb, ref_terminal._edb_object)
        ref_term.boundary_type = "kCurrentSource"

        term.reference_terminal = ref_terminal
        return self._pedb.sources[term.name]

    def get_point_terminal(self, name, net_name, location, layer) -> PointTerminal:
        """
        Place a voltage probe between two points.

        Parameters
        ----------
        name : str,
            Name of the terminal.
        net_name : str
            Name of the net.
        location : list
            Location of the terminal.
        layer : str,
            Layer of the terminal.

        Returns
        -------
        :class:`legacy.edb_core.edb_data.terminals.PointTerminal`

        """
        from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal

        point_terminal = PointTerminal(self._pedb)
        return point_terminal.create(name, net_name, location, layer)

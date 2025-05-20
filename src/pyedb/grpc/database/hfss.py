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

"""
This module contains the ``EdbHfss`` class.
"""
import math
import warnings

from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup,
)
from pyedb.grpc.database.utility.hfss_extent_info import HfssExtentInfo
from pyedb.modeler.geometry_operators import GeometryOperators


class Hfss(object):
    """Manages EDB method to configure Hfss setup accessible from `Edb.hfss` property."""

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def hfss_extent_info(self):
        """HFSS extent information."""
        return HfssExtentInfo(self._pedb)

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _layout(self):
        return self._pedb.layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.active_db

    @property
    def excitations(self):
        """Get all excitations."""
        return self._pedb.excitations

    @property
    def sources(self):
        """Get all sources."""
        return self._pedb.sources

    @property
    def probes(self):
        """Get all probes."""
        return self._pedb.probes

    def _create_edge_terminal(self, prim_id, point_on_edge, terminal_name=None, is_ref=False):
        """Create an edge terminal.

        . deprecated:: pyedb 0.28.0
        Use :func:`_create_edge_terminal` is move to pyedb.grpc.database.excitations._create_edge_terminal instead.

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
        warnings.warn(
            "`_create_edge_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_edge_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations._create_edge_terminal(
            prim_id=prim_id, point_on_edge=point_on_edge, terminal_name=terminal_name, is_ref=is_ref
        )

    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------<
        dict
            Dictionary of trace width data.
        """
        nets = {}
        for net in self._pedb.excitations_nets:
            nets[net] = self._pedb.nets.nets[net].get_smallest_trace_width()
        return nets

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create Circuit Port on Pin.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.

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

        """
        warnings.warn(
            "`create_circuit_port_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.

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
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_voltage_source_on_pin(pins[0], pins[1],50,"source_name")
        """
        warnings.warn(
            "`create_voltage_source_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_voltage_source_on_pin(
            pos_pin, neg_pin, voltage_value, phase_value, source_name
        )

    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
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
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_current_source_on_pin(pins[0], pins[1],50,"source_name")
        """
        warnings.warn(
            "`create_current_source_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_current_source_on_pin(
            pos_pin, neg_pin, current_value, phase_value, source_name
        )

    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.

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
            Name of the Resistor.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        warnings.warn(
            "`create_resistor_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        impedance_value=50,
        port_name="",
    ):
        """Create a circuit port on a NET.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_net` instead.

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
            Name of the negative net name. The default is ``"GND"``.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            The name of the port.
        """

        warnings.warn(
            "`create_circuit_port_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_circuit_port_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        voltage_value=3.3,
        phase_value=0,
        source_name="",
    ):
        """Create a voltage source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.

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
            Name of the negative net. The default is ``"GND"``.
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
        """

        warnings.warn(
            "`create_voltage_source_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """Create a current source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_current_source_on_net` instead.

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
            Name of the negative net. The default is ``"GND"``.
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
        """

        warnings.warn(
            "`create_current_source_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_current_source_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    def create_coax_port_on_component(self, ref_des_list, net_list, delete_existing_terminal=False):
        """Create a coaxial port on a component or component list on a net or net list.
           The name of the new coaxial port is automatically assigned.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_coax_port_on_component` instead.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn(
            "`create_coax_port_on_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_coax_port_on_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_coax_port_on_component(
            ref_des_list, net_list, delete_existing_terminal
        )

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
        """Create a differential wave port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_differential_wave_port` instead.

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

        """
        warnings.warn(
            "`create_differential_wave_port` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_differential_wave_port` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_differential_wave_port(
            positive_primitive_id,
            positive_points_on_edge,
            negative_primitive_id,
            negative_points_on_edge,
            port_name,
            horizontal_extent_factor,
            vertical_extent_factor,
            pec_launch_width,
        )

    def create_bundle_wave_port(
        self,
        primitives_id,
        points_on_edge,
        port_name=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """Create a bundle wave port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_bundle_wave_port` instead.

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
        """
        warnings.warn(
            "`create_bundle_wave_port` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_bundle_wave_port` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_bundle_wave_port(
            primitives_id, points_on_edge, port_name, horizontal_extent_factor, vertical_extent_factor, pec_launch_width
        )

    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """Create an HFSS port on a padstack.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_hfss_ports_on_padstack` instead.

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
        warnings.warn(
            "`create_hfss_ports_on_padstack` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_hfss_ports_on_padstack` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_hfss_ports_on_padstack(pinpos, portname)

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
        """Create lumped port between two edges from two different polygons. Can also create a vertical port when
        the reference layer name is only provided. When a port is created between two edge from two polygons which don't
        belong to the same layer, a circuit port will be automatically created instead of lumped. To enforce the circuit
        port instead of lumped,use the boolean force_circuit_port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_edge_port_on_polygon` instead.


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
        """

        warnings.warn(
            "`create_edge_port_on_polygon` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_edge_port_on_polygon` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_edge_port_on_polygon(
            polygon,
            reference_polygon,
            terminal_point,
            reference_point,
            reference_layer,
            port_name,
            port_impedance,
            force_circuit_port,
        )

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
        """Create a wave port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_wave_port` instead.

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

        """
        warnings.warn(
            "`create_source_on_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_source_on_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_wave_port(
            prim_id,
            point_on_edge,
            port_name,
            impedance,
            horizontal_extent_factor,
            vertical_extent_factor,
            pec_launch_width,
        )

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
        """Create a vertical edge port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_edge_port_vertical` instead.

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
        warnings.warn(
            "`create_edge_port_vertical` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_edge_port_vertical` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_edge_port_vertical(
            prim_id,
            point_on_edge,
            port_name,
            impedance,
            reference_layer,
            hfss_type,
            horizontal_extent_factor,
            vertical_extent_factor,
            pec_launch_width,
        )

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
        """Create a horizontal edge port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_edge_port_horizontal` instead.

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
        warnings.warn(
            "`create_edge_port_horizontal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_edge_port_horizontal` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_edge_port_horizontal(
            prim_id, point_on_edge, ref_prim_id, point_on_ref_edge, port_name, impedance, layer_alignment
        )

    def create_lumped_port_on_net(self, nets, reference_layer, return_points_only, digit_resolution, at_bounding_box):
        """Create an edge port on nets. This command looks for traces and polygons on the
        nets and tries to assign vertical lumped port.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_lumped_port_on_net` instead.

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
        warnings.warn(
            "`create_lumped_port_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_lumped_port_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_lumped_port_on_net(
            nets, reference_layer, return_points_only, digit_resolution, at_bounding_box
        )

    def create_vertical_circuit_port_on_clipped_traces(self, nets=None, reference_net=None, user_defined_extent=None):
        """Create an edge port on clipped signal traces.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_vertical_circuit_port_on_clipped_traces` instead.

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
        warnings.warn(
            "`create_source_on_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_source_on_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_vertical_circuit_port_on_clipped_traces(
            nets, reference_net, user_defined_extent
        )

    def get_layout_bounding_box(self, layout=None, digit_resolution=6):
        """Evaluate the layout bounding box.

        Parameters
        ----------
        layout :
            Edb layout.

        digit_resolution : int, optional
            Digit Resolution. The default value is ``6``.

        Returns
        -------
        list
            [lower left corner X, lower left corner, upper right corner X, upper right corner Y].
        """
        if not layout:
            layout = self._active_layout
        layout_obj_instances = layout.layout_instance.query_layout_obj_instances()
        tuple_list = []
        for lobj in layout_obj_instances:
            lobj_bbox = lobj.get_bbox()
            tuple_list.append(lobj_bbox)
        _bbox = GrpcPolygonData.bbox_of_polygons(tuple_list)
        layout_bbox = [
            round(_bbox[0].x.value, digit_resolution),
            round(_bbox[0].y.value, digit_resolution),
            round(_bbox[1].x.value, digit_resolution),
            round(_bbox[1].y.value, digit_resolution),
        ]
        return layout_bbox

    def configure_hfss_extents(self, simulation_setup=None):
        """Configure the HFSS extent box.

                . deprecated:: pyedb 0.28.0
        Use :func:`self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_extents`
        instead.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """
        warnings.warn(
            "`configure_hfss_extents` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_extents`"
            "instead.",
            DeprecationWarning,
        )
        return self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_extents(
            simulation_setup
        )

    def configure_hfss_analysis_setup(self, simulation_setup=None):
        """
        Configure HFSS analysis setup.

        . deprecated:: pyedb 0.28.0
        Use :func:
        `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_analysis_setup`
        instead.


        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """
        warnings.warn(
            "`configure_hfss_analysis_setup` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration."
            "configure_hfss_analysis_setup` instead.",
            DeprecationWarning,
        )
        self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_analysis_setup(
            simulation_setup
        )

    def _setup_decade_count_sweep(self, sweep, start_freq="1", stop_freq="1MHz", decade_count="10"):
        start_f = GeometryOperators.parse_dim_arg(start_freq)
        if start_f == 0.0:
            start_f = 10
            self._logger.warning("Decade Count sweep does not support DC value, defaulting starting frequency to 10Hz")

        stop_f = GeometryOperators.parse_dim_arg(stop_freq)
        decade_cnt = GeometryOperators.parse_dim_arg(decade_count)
        freq = start_f
        sweep.Frequencies.Add(str(freq))

        while freq < stop_f:
            freq = freq * math.pow(10, 1.0 / decade_cnt)
            sweep.Frequencies.Add(str(freq))

    def trim_component_reference_size(self, simulation_setup=None, trim_to_terminals=False):
        """Trim the common component reference to the minimally acceptable size.

        . deprecated:: pyedb 0.28.0
        Use :func:
        `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.trim_component_reference_size`
        instead.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        trim_to_terminals :
            bool.
                True, reduce the reference to a box covering only the active terminals (i.e. those with
        ports).
                False, reduce the reference to the minimal size needed to cover all pins

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        warnings.warn(
            "`trim_component_reference_size` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration."
            "trim_component_reference_size` instead.",
            DeprecationWarning,
        )
        self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.trim_component_reference_size(
            simulation_setup
        )

    def set_coax_port_attributes(self, simulation_setup=None):
        """Set coaxial port attribute with forcing default impedance to 50 Ohms and adjusting the coaxial extent radius.

        . deprecated:: pyedb 0.28.0
        Use :func:
        `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.set_coax_port_attributes`
        instead.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object.

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """
        warnings.warn(
            "`set_coax_port_attributes` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration."
            "set_coax_port_attributes` instead.",
            DeprecationWarning,
        )
        self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.set_coax_port_attributes(
            simulation_setup
        )

    def _get_terminals_bbox(self, comp, l_inst, terminals_only):
        terms_loi = []
        if terminals_only:
            term_list = []
            for pin in comp.pins:
                padstack_instance_term = pin.get_padstack_instance_terminal()
                if not padstack_instance_term.is_null:
                    term_list.append(padstack_instance_term)
            for tt in term_list:
                term_param = tt.get_parameters()
                if term_param:
                    loi = l_inst.get_layout_obj_instance(term_param[0], None)
                    terms_loi.append(loi)
        else:
            pin_list = comp.pins
            for pi in pin_list:
                loi = l_inst.get_layout_obj_instance(pi, None)
                terms_loi.append(loi)

        if len(terms_loi) == 0:
            return None

        terms_bbox = []
        for loi in terms_loi:
            # Need to account for the coax port dimension
            bb = loi.GetBBox()
            ll = [bb[0].x.value, bb[0].y.value]
            ur = [bb[1].x.value, bb[1].y.value]
            # dim = 0.26 * max(abs(UR[0]-LL[0]), abs(UR[1]-LL[1]))  # 0.25 corresponds to the default 0.5
            # Radial Extent Factor, so set slightly larger to avoid validation errors
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))  # 0.25 corresponds to the default 0.5
            terms_bbox.append(GrpcPolygonData([ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim]))
        return GrpcPolygonData.bbox_of_polygons(terms_bbox)

    def get_ports_number(self):
        """Return the total number of excitation ports in a layout.

        Parameters
        ----------
        None

        Returns
        -------
        int
           Number of ports.

        """
        warnings.warn(
            "`get_ports_number` is deprecated and is now located here "
            "`pyedb.grpc.core.excitation.get_ports_number` instead.",
            DeprecationWarning,
        )
        self._pedb.excitations.get_ports_number()

    def layout_defeaturing(self, simulation_setup=None):
        """Defeature the layout by reducing the number of points for polygons based on surface deviation criteria.

        . deprecated:: pyedb 0.28.0
        Use :func:
        `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.layout_defeaturing`
        instead.

        Parameters
        ----------
        simulation_setup : Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn(
            "`layout_defeaturing` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration."
            "layout_defeaturing` instead.",
            DeprecationWarning,
        )
        self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.layout_defeaturing(simulation_setup)

    def create_rlc_boundary_on_pins(self, positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0):
        """Create hfss rlc boundary on pins.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_rlc_boundary_on_pins` instead.

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
        warnings.warn(
            "`create_rlc_boundary_on_pins` is deprecated and is now located here "
            "`pyedb.grpc.core.create_rlc_boundary_on_pins.get_ports_number` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_rlc_boundary_on_pins(
            positive_pin, negative_pin, rvalue, lvalue, cvalue
        )

    def add_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
    ):
        """Add a HFSS analysis to EDB.

        Parameters
        ----------
        name : str, optional
            Setup name.
        Sweep type. `"interpolating"` or `"discrete"`.
        distribution : str, optional
            Type of the sweep. The default is `"linear"`. Options are:
            - `"linear"`
            - `"linear_count"`
            - `"decade_count"`
            - `"octave_count"`
            - `"exponential"`
        start_freq : str, float, optional
            Starting frequency. The default is ``0``.
        stop_freq : str, float, optional
            Stopping frequency. The default is ``20e9``.
        step_freq : str, float, int, optional
            Frequency step. The default is ``1e6``. or used for `"decade_count"`, "linear_count"`, "octave_count"`
            distribution. Must be integer in that case.
        discrete_sweep : bool, optional
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        :class:`HfssSimulationSetup`
            Setup object class.
        """
        from ansys.edb.core.simulation_setup.hfss_simulation_setup import (
            HfssSimulationSetup as GrpcHfssSimulationSetup,
        )
        from ansys.edb.core.simulation_setup.simulation_setup import (
            Distribution as GrpcDistribution,
        )
        from ansys.edb.core.simulation_setup.simulation_setup import (
            FrequencyData as GrpcFrequencyData,
        )
        from ansys.edb.core.simulation_setup.simulation_setup import (
            SweepData as GrpcSweepData,
        )

        if not name:
            name = generate_unique_name("HFSS_pyedb")
        if name in self._pedb.setups:
            self._pedb.logger.error(f"HFSS setup {name} already defined.")
            return False
        setup = GrpcHfssSimulationSetup.create(self._pedb.active_cell, name)
        start_freq = self._pedb.number_with_units(start_freq, "Hz")
        stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
        if distribution.lower() == "linear":
            distribution = "LIN"
        elif distribution.lower() == "linear_count":
            distribution = "LINC"
        elif distribution.lower() == "exponential":
            distribution = "ESTP"
        elif distribution.lower() == "decade_count":
            distribution = "DEC"
        elif distribution.lower() == "octave_count":
            distribution = "OCT"
        else:
            distribution = "LIN"
        sweep_name = f"sweep_{len(setup.sweep_data) + 1}"
        sweep_data = [
            GrpcSweepData(
                name=sweep_name,
                frequency_data=GrpcFrequencyData(
                    distribution=GrpcDistribution[distribution], start_f=start_freq, end_f=stop_freq, step=step_freq
                ),
            )
        ]
        if discrete_sweep:
            sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
        for sweep in setup.sweep_data:
            sweep_data.append(sweep)
        # TODO check bug #441 status
        # setup.sweep_data = sweep_data
        return HfssSimulationSetup(self._pedb, setup)

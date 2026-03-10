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

"""
This module contains the ``EdbHfss`` class.
"""

import math
from typing import Dict, Union

from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal
from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import PadstackInstanceTerminal
from pyedb.dotnet.database.cell.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal
from pyedb.dotnet.database.edb_data.hfss_extent_info import HfssExtentInfo
from pyedb.dotnet.database.edb_data.ports import (
    BundleWavePort,
    CircuitPort,
    CoaxPort,
    ExcitationSources,
    GapPort,
    WavePort,
)
from pyedb.dotnet.database.edb_data.primitives_data import Primitive
from pyedb.dotnet.database.general import (
    convert_py_list_to_net_list,
    convert_pytuple_to_nettuple,
)
from pyedb.generic.constants import RadiationBoxType, SweepType
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.misc.decorators import deprecated, deprecated_property


class EdbHfss(object):
    """Manages EDB method to configure Hfss setup accessible from `Edb.hfss` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edb_hfss = edb_3dedbapp.hfss
    """

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
        return self._pedb.core

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
    @deprecated_property
    def excitations(self) -> Dict[str, Union[BundleWavePort, GapPort, CircuitPort, CoaxPort, WavePort]]:
        """Get all ports.

        Returns
        -------
        port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]

        """
        return self.ports

    @property
    def ports(self) -> Dict[str, Union[BundleWavePort, GapPort, CircuitPort, CoaxPort, WavePort]]:
        """Get all ports.

        Returns
        -------
        port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]

        """
        return self._pedb.ports

    @property
    def sources(self) -> Dict[str, ExcitationSources]:
        """Get all sources."""
        return self._pedb.sources

    @property
    def probes(
        self,
    ) -> Dict[str, Union[PinGroupTerminal, PointTerminal, BundleTerminal, PadstackInstanceTerminal, EdgeTerminal]]:
        """Get all probes."""
        return self._pedb.probes

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------<
        dict
            Dictionary of trace width data.
        """
        nets = {}
        for net in self._pedb.excitations_nets:
            smallest = self._pedb.nets[net].get_smallest_trace_width()
            if smallest < 1e10:
                nets[net] = self._pedb.nets[net].get_smallest_trace_width()
        return nets

    @deprecated
    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create Circuit Port on Pin.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_circuit_port_on_pin` instead.

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

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")

        Returns
        -------
        str
            Port Name.

        """
        return self._pedb.excitation_manager.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    @deprecated
    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_voltage_source_on_pin` instead.

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
        return self._pedb.excitation_manager.create_voltage_source_on_pin(
            pos_pin, neg_pin, voltage_value, phase_value, source_name
        )

    @deprecated
    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_current_source_on_pin` instead.

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
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")
        """
        return self._pedb.excitation_manager.create_current_source_on_pin(
            pos_pin, neg_pin, current_value, phase_value, source_name
        )

    @deprecated
    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_resistor_on_pin` instead.

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
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation_manager.create_resistor_on_pin(pins[0], pins[1], 50, "res_name")
        """
        return self._pedb.excitation_manager.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    @deprecated
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
        It groups all pins belonging to the specified net and then applies the port on PinGroups.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_circuit_port_on_net` instead.

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

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.excitation_manager.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        return self._pedb.excitation_manager.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_voltage_source_on_net` instead.

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

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitation_manager.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")
        """
        return self._pedb.excitation_manager.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_current_source_on_net` instead.

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

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitation_manager.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        return self._pedb.excitation_manager.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    @deprecated
    def create_coax_port_on_component(self, ref_des_list, net_list, delete_existing_terminal=False):
        """Create a coaxial port on a component or component list on a net or net list.
           The name of the new coaxial port is automatically assigned.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_coax_port_on_component` instead.

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
        return self._pedb.excitation_manager.create_coax_port_on_component(
            ref_des_list=ref_des_list, net_list=net_list, delete_existing_terminal=delete_existing_terminal
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_differential_wave_port` instead.

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
        return self._pedb.excitation_manager.create_differential_wave_port(
            positive_primitive_id=positive_primitive_id,
            positive_points_on_edge=positive_points_on_edge,
            negative_primitive_id=negative_primitive_id,
            negative_points_on_edge=negative_points_on_edge,
            port_name=port_name,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_bundle_wave_port` instead.

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
        return self._pedb.excitation_manager.create_bundle_wave_port(
            primitives_id=primitives_id,
            points_on_edge=points_on_edge,
            port_name=port_name,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    @deprecated
    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """Create an HFSS port on a padstack.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_hfss_ports_on_padstack` instead.

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
        return self._pedb.excitation_manager.create_hfss_ports_on_padstack(pinpos=pinpos, portname=portname)

    @deprecated
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
        """Create an edge port on a primitive specific location.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.grpc.core.excitations.create_edge_port` instead.

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
        return self._pedb.excitation_manager.create_edge_port(
            location=location,
            primitive_name=primitive_name,
            name=name,
            impedance=impedance,
            is_wave_port=is_wave_port,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_edge_port_on_polygon` instead.

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
        return self._pedb.excitation_manager.create_edge_port_on_polygon(
            polygon=polygon,
            reference_polygon=reference_polygon,
            terminal_point=terminal_point,
            reference_point=reference_point,
            reference_layer=reference_layer,
            port_name=port_name,
            port_impedance=port_impedance,
            force_circuit_port=force_circuit_port,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_wave_port` instead.

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
        return self._pedb.excitation_manager.create_wave_port(
            prim_id=prim_id,
            point_on_edge=point_on_edge,
            port_name=port_name,
            impedance=impedance,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_edge_port_vertical` instead.

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
        return self._pedb.excitation_manager.create_edge_port_vertical(
            prim_id=prim_id,
            point_on_edge=point_on_edge,
            port_name=port_name,
            impedance=impedance,
            reference_layer=reference_layer,
            hfss_type=hfss_type,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    @deprecated
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

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_edge_port_horizontal` instead.

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
        return self._pedb.excitation_manager.create_edge_port_horizontal(
            prim_id=prim_id,
            point_on_edge=point_on_edge,
            ref_prim_id=ref_prim_id,
            point_on_ref_edge=point_on_ref_edge,
            port_name=port_name,
            impedance=impedance,
            layer_alignment=layer_alignment,
        )

    @deprecated
    def create_lumped_port_on_net(
        self, nets=None, reference_layer=None, return_points_only=False, digit_resolution=6, at_bounding_box=True
    ):
        """Create an edge port on nets. This command looks for traces and polygons on the
        nets and tries to assign vertical lumped port.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_lumped_port_on_net` instead.

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
        return self._pedb.excitation_manager.create_lumped_port_on_net(
            nets=nets,
            reference_layer=reference_layer,
            return_points_only=return_points_only,
            digit_resolution=digit_resolution,
            at_bounding_box=at_bounding_box,
        )

    @deprecated
    def create_vertical_circuit_port_on_clipped_traces(self, nets=None, reference_net=None, user_defined_extent=None):
        """Create an edge port on clipped signal traces.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_vertical_circuit_port_on_clipped_traces` instead.

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
        return self._pedb.excitation_manager.create_vertical_circuit_port_on_clipped_traces(
            nets=nets, reference_net=reference_net, user_defined_extent=user_defined_extent
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
        if layout is None:
            layout = self._active_layout
        layout_obj_instances = layout.GetLayoutInstance().GetAllLayoutObjInstances()
        tuple_list = []
        for lobj in layout_obj_instances.Items:
            lobj_bbox = lobj.GetLayoutInstanceContext().GetBBox(False)
            tuple_list.append(lobj_bbox)
        _bbox = self._edb.Geometry.PolygonData.GetBBoxOfBoxes(convert_py_list_to_net_list(tuple_list))
        layout_bbox = [
            round(_bbox.Item1.X.ToDouble(), digit_resolution),
            round(_bbox.Item1.Y.ToDouble(), digit_resolution),
            round(_bbox.Item2.X.ToDouble(), digit_resolution),
            round(_bbox.Item2.Y.ToDouble(), digit_resolution),
        ]
        return layout_bbox

    def add_setup(self, name=None):
        """Adding method for grpc compatibility"""
        return self._pedb.create_hfss_setup(name=name)

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

    def _get_terminals_bbox(self, comp, l_inst, terminals_only):
        terms_loi = []
        if terminals_only:
            term_list = [
                obj for obj in list(comp.LayoutObjs) if obj.GetObjType() == self._edb.Cell.LayoutObjectType.Terminal
            ]
            for tt in term_list:
                success, p_inst, lyr = tt.GetParameters()
                if success and lyr:
                    loi = l_inst.GetLayoutObjInstance(p_inst, None)
                    terms_loi.append(loi)
        else:
            pin_list = [
                obj
                for obj in list(comp.LayoutObjs)
                if obj.GetObjType() == self._edb.Cell.LayoutObjectType.PadstackInstance
            ]
            for pi in pin_list:
                loi = l_inst.GetLayoutObjInstance(pi, None)
                terms_loi.append(loi)

        if len(terms_loi) == 0:
            return None

        terms_bbox = []
        for loi in terms_loi:
            # Need to account for the coax port dimension
            bb = loi.GetBBox()
            ll = [bb.Item1.X.ToDouble(), bb.Item1.Y.ToDouble()]
            ur = [bb.Item2.X.ToDouble(), bb.Item2.Y.ToDouble()]
            # dim = 0.26 * max(abs(UR[0]-LL[0]), abs(UR[1]-LL[1]))  # 0.25 corresponds to the default 0.5
            # Radial Extent Factor, so set slightly larger to avoid validation errors
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))  # 0.25 corresponds to the default 0.5
            terms_bbox.append(
                self._edb.geometry.polygon_data.dotnetobj(ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim)
            )
        return self._edb.geometry.polygon_data.get_bbox_of_polygons(terms_bbox)

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
        terms = [term for term in self._layout.terminals if int(term._edb_object.GetBoundaryType()) == 0]
        return len([i for i in terms if not i.is_reference_terminal])

    @deprecated
    def create_rlc_boundary_on_pins(self, positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0):
        """Create hfss rlc boundary on pins.

        .. deprecated:: 0.70.0
            Use :func:`pyedb.excitation_manager.create_rlc_boundary_on_pins` instead.

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

        return self._pedb.excitation_manager.create_rlc_boundary_on_pins(
            positive_pin=positive_pin, negative_pin=negative_pin, rvalue=rvalue, lvalue=lvalue, cvalue=cvalue
        )

    def generate_auto_hfss_regions(self):
        """Generate auto HFSS regions.

        This method automatically identifies areas for use as HFSS regions in SIwave simulations.
        """
        if not self._pedb.active_cell.GenerateAutoHFSSRegions():
            raise RuntimeError("Failed to generate hfss regions.")

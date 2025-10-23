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
    """Manages EDB methods for HFSS setup configuration.

    Provides access to HFSS-specific operations including:
    - Excitation and port creation
    - Source and probe management
    - Simulation setup configuration
    - Boundary condition creation
    - Layout manipulation for simulation

    Accessed via `Edb.hfss` property.
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def hfss_extent_info(self) -> HfssExtentInfo:
        """HFSS extent information.

        Returns
        -------
        HfssExtentInfo
            Object containing HFSS extent configuration data.
        """
        return HfssExtentInfo(self._pedb)

    @property
    def _logger(self):
        """Logger instance for message handling.

        Returns
        -------
        logging.Logger
            Current logger instance.
        """
        return self._pedb.logger

    @property
    def _edb(self):
        """EDB API object.

        Returns
        -------
        Ansys.Ansoft.Edb
            EDB API instance.
        """
        return self._pedb

    @property
    def _active_layout(self):
        """Active layout object.

        Returns
        -------
        Edb.Cell.Layout
            Current active layout.
        """
        return self._pedb.active_layout

    @property
    def _layout(self):
        """Current layout object.

        Returns
        -------
        Edb.Cell.Layout
            Current layout.
        """
        return self._pedb.layout

    @property
    def _cell(self):
        """Current cell object.

        Returns
        -------
        Edb.Cell
            Current cell.
        """
        return self._pedb.cell

    @property
    def _db(self):
        """Active database object.

        Returns
        -------
        Edb.Database
            Active database.
        """
        return self._pedb.active_db

    @property
    def excitations(self):
        """All excitation definitions in the layout.

        Returns
        -------
        list
            List of excitation objects.
        """
        return self._pedb.excitations

    @property
    def sources(self):
        """All source definitions in the layout.

        Returns
        -------
        list
            List of source objects.
        """
        return self._pedb.sources

    @property
    def probes(self):
        """All probe definitions in the layout.

        Returns
        -------
        list
            List of probe objects.
        """
        return self._pedb.probes

    def _create_edge_terminal(self, prim_id, point_on_edge, terminal_name=None, is_ref=False):
        """Create an edge terminal (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations._create_edge_terminal` instead.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
        terminal_name : str, optional
            Name of the terminal.
        is_ref : bool, optional
            Whether it is a reference terminal.

        Returns
        -------
        Edb.Cell.Terminal.EdgeTerminal
            Created edge terminal.
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
        """Retrieve trace widths for traces with ports.

        Returns
        -------
        dict
            Dictionary mapping net names to smallest trace widths.

        Examples
        --------
        >>> widths = edb.hfss.get_trace_width_for_traces_with_ports()
        >>> for net_name, width in widths.items():
        ...     print(f"Net '{net_name}': Smallest width = {width}")
        """
        nets = {}
        for net in self._pedb.excitations_nets:
            nets[net] = self._pedb.nets.nets[net].get_smallest_trace_width()
        return nets

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create circuit port between two pins (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.

        Parameters
        ----------
        pos_pin : Edb.Cell.Primitive.PadstackInstance
            Positive pin.
        neg_pin : Edb.Cell.Primitive.PadstackInstance
            Negative pin.
        impedance : float, optional
            Port impedance.
        port_name : str, optional
            Port name.

        Returns
        -------
        str
            Port name.
        """
        warnings.warn(
            "`create_circuit_port_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.excitations.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create voltage source between two pins (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.

        Parameters
        ----------
        pos_pin : Edb.Cell.Primitive.PadstackInstance
            Positive pin.
        neg_pin : Edb.Cell.Primitive.PadstackInstance
            Negative pin.
        voltage_value : float, optional
            Voltage value.
        phase_value : float, optional
            Phase value.
        source_name : str, optional
            Source name.

        Returns
        -------
        str
            Source name.
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
        """Create current source between two pins (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.

        Parameters
        ----------
        pos_pin : Edb.Cell.Primitive.PadstackInstance
            Positive pin.
        neg_pin : Edb.Cell.Primitive.PadstackInstance
            Negative pin.
        current_value : float, optional
            Current value.
        phase_value : float, optional
            Phase value.
        source_name : str, optional
            Source name.

        Returns
        -------
        str
            Source name.
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
        """Create resistor between two pins (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.

        Parameters
        ----------
        pos_pin : Edb.Cell.Primitive.PadstackInstance
            Positive pin.
        neg_pin : Edb.Cell.Primitive.PadstackInstance
            Negative pin.
        rvalue : float, optional
            Resistance value.
        resistor_name : str, optional
            Resistor name.

        Returns
        -------
        str
            Resistor name.
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
        """Create circuit port on net (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_net` instead.

        Parameters
        ----------
        positive_component_name : str
            Positive component name.
        positive_net_name : str
            Positive net name.
        negative_component_name : str, optional
            Negative component name.
        negative_net_name : str, optional
            Negative net name.
        impedance_value : float, optional
            Port impedance.
        port_name : str, optional
            Port name.

        Returns
        -------
        str
            Port name.
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
        """Create voltage source on net (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.

        Parameters
        ----------
        positive_component_name : str
            Positive component name.
        positive_net_name : str
            Positive net name.
        negative_component_name : str, optional
            Negative component name.
        negative_net_name : str, optional
            Negative net name.
        voltage_value : float, optional
            Voltage value.
        phase_value : float, optional
            Phase value.
        source_name : str, optional
            Source name.

        Returns
        -------
        str
            Source name.
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
        """Create current source on net (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_current_source_on_net` instead.

        Parameters
        ----------
        positive_component_name : str
            Positive component name.
        positive_net_name : str
            Positive net name.
        negative_component_name : str, optional
            Negative component name.
        negative_net_name : str, optional
            Negative net name.
        current_value : float, optional
            Current value.
        phase_value : float, optional
            Phase value.
        source_name : str, optional
            Source name.

        Returns
        -------
        str
            Source name.
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
        """Create coaxial port on component (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_coax_port_on_component` instead.

        Parameters
        ----------
        ref_des_list : list, str
            Reference designator(s).
        net_list : list, str
            Net name(s).
        delete_existing_terminal : bool, optional
            Delete existing terminals.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Create differential wave port (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_differential_wave_port` instead.

        Parameters
        ----------
        positive_primitive_id : int, EDBPrimitives
            Positive primitive ID.
        positive_points_on_edge : list
            Point coordinates on positive edge.
        negative_primitive_id : int, EDBPrimitives
            Negative primitive ID.
        negative_points_on_edge : list
            Point coordinates on negative edge.
        port_name : str, optional
            Port name.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor.
        vertical_extent_factor : int, float, optional
            Vertical extent factor.
        pec_launch_width : str, optional
            PEC launch width.

        Returns
        -------
        tuple
            (Port name, ExcitationDifferential) tuple.
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
        """Create bundle wave port (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_bundle_wave_port` instead.

        Parameters
        ----------
        primitives_id : list
            Primitive IDs.
        points_on_edge : list
            Point coordinates on edges.
        port_name : str, optional
            Port name.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor.
        vertical_extent_factor : int, float, optional
            Vertical extent factor.
        pec_launch_width : str, optional
            PEC launch width.

        Returns
        -------
        tuple
            (Port name, ExcitationDifferential) tuple.
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
        """Create HFSS port on padstack (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_hfss_ports_on_padstack` instead.

        Parameters
        ----------
        pinpos :
            Pin position.
        portname : str, optional
            Port name.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Create edge port on polygon (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_edge_port_on_polygon` instead.

        Parameters
        ----------
        polygon : Edb.Cell.Primitive.Polygon, optional
            Port polygon.
        reference_polygon : Edb.Cell.Primitive.Polygon, optional
            Reference polygon.
        terminal_point : list, optional
            Terminal point coordinates.
        reference_point : list, optional
            Reference point coordinates.
        reference_layer : str, optional
            Reference layer name.
        port_name : str, optional
            Port name.
        port_impedance : float, optional
            Port impedance.
        force_circuit_port : bool, optional
            Force circuit port creation.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Create wave port (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_wave_port` instead.

        Parameters
        ----------
        prim_id : int, Primitive
            Primitive ID.
        point_on_edge : list
            Point coordinates on edge.
        port_name : str, optional
            Port name.
        impedance : int, float, optional
            Port impedance.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor.
        vertical_extent_factor : int, float, optional
            Vertical extent factor.
        pec_launch_width : str, optional
            PEC launch width.

        Returns
        -------
        tuple
            (Port name, Excitation) tuple.
        """
        warnings.warn(
            "`create_wave_port` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_wave_port` instead.",
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
        """Create vertical edge port (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_edge_port_vertical` instead.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Point coordinates on edge.
        port_name : str, optional
            Port name.
        impedance : int, float, optional
            Port impedance.
        reference_layer : str, optional
            Reference layer name.
        hfss_type : str, optional
            Port type ("Gap" or "Wave").
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor.
        vertical_extent_factor : int, float, optional
            Vertical extent factor.
        pec_launch_width : str, optional
            PEC launch width.

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
        """Create horizontal edge port (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_edge_port_horizontal` instead.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Point coordinates on edge.
        ref_prim_id : int, optional
            Reference primitive ID.
        point_on_ref_edge : list, optional
            Point coordinates on reference edge.
        port_name : str, optional
            Port name.
        impedance : int, float, optional
            Port impedance.
        layer_alignment : str, optional
            Layer alignment ("Upper" or "Lower").

        Returns
        -------
        str
            Port name.
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
        """Create lumped port on net (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_lumped_port_on_net` instead.

        Parameters
        ----------
        nets : list
            Net names or objects.
        reference_layer : str, Edb.Layer
            Reference layer name or object.
        return_points_only : bool
            Return points only without creating ports.
        digit_resolution : int
            Coordinate digit resolution.
        at_bounding_box : bool
            Use layout bounding box.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Create vertical circuit port on clipped traces (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_vertical_circuit_port_on_clipped_traces` instead.

        Parameters
        ----------
        nets : list, optional
            Net names or objects.
        reference_net : str, Edb.Net, optional
            Reference net name or object.
        user_defined_extent : list, PolygonData, optional
            User-defined extent polygon.

        Returns
        -------
        list
            List of port data [net_name, x, y, terminal_name].
        """
        warnings.warn(
            "`create_vertical_circuit_port_on_clipped_traces` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_vertical_circuit_port_on_clipped_traces` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_vertical_circuit_port_on_clipped_traces(
            nets, reference_net, user_defined_extent
        )

    def get_layout_bounding_box(self, layout=None, digit_resolution=6):
        """Calculate layout bounding box.

        Parameters
        ----------
        layout : Edb.Cell.Layout, optional
            Layout object (uses active layout if None).
        digit_resolution : int, optional
            Coordinate rounding precision.

        Returns
        -------
        list
            [min_x, min_y, max_x, max_y] coordinates.

        Examples
        --------
        >>> bbox = edb.hfss.get_layout_bounding_box()
        >>> print(f"Layout Bounding Box: {bbox}")
        >>>
        >>> # With custom parameters
        >>> custom_layout = edb.layouts["MyLayout"]
        >>> bbox = edb.hfss.get_layout_bounding_box(custom_layout, 5)
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
        """Configure HFSS extent box (deprecated).

        .. deprecated:: 0.28.0
            Use :func:
            `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_extents`
            instead.

        Parameters
        ----------
        simulation_setup : HfssSimulationSetup, optional
            Simulation setup object.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Configure HFSS analysis setup (deprecated).

        .. deprecated:: 0.28.0
            Use :func:
            `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.configure_hfss_analysis_setup`
            instead.

        Parameters
        ----------
        simulation_setup : HfssSimulationSetup, optional
            Simulation setup object.

        Returns
        -------
        bool
            True if successful, False otherwise.
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
        """Configure decade count sweep (internal).

        Parameters
        ----------
        sweep : SweepData
            Sweep data object.
        start_freq : str, float, optional
            Start frequency.
        stop_freq : str, float, optional
            Stop frequency.
        decade_count : str, float, optional
            Points per decade.
        """
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
        """Trim component reference size (deprecated).

        .. deprecated:: 0.28.0
            Use :func:
            `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.trim_component_reference_size`
            instead.

        Parameters
        ----------
        simulation_setup : HfssSimulationSetup, optional
            Simulation setup object.
        trim_to_terminals : bool, optional
            Trim to active terminals only.
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
        """Set coaxial port attributes (deprecated).

        .. deprecated:: 0.28.0
            Use :func:
            `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.set_coax_port_attributes`
            instead.

        Parameters
        ----------
        simulation_setup : HfssSimulationSetup, optional
            Simulation setup object.
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
        """Get component terminals bounding box (internal).

        Parameters
        ----------
        comp : Component
            Component object.
        l_inst : LayoutObjInstance
            Layout object instance.
        terminals_only : bool
            Consider only terminals.

        Returns
        -------
        PolygonData
            Bounding box polygon.
        """
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
            bb = loi.GetBBox()
            ll = [bb[0].x.value, bb[0].y.value]
            ur = [bb[1].x.value, bb[1].y.value]
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))
            terms_bbox.append(GrpcPolygonData([ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim]))
        return GrpcPolygonData.bbox_of_polygons(terms_bbox)

    def get_ports_number(self):
        """Get number of excitation ports.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitation.get_ports_number` instead.

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
        """Defeature layout polygons (deprecated).

        .. deprecated:: 0.28.0
            Use :func:
            `pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration.layout_defeaturing`
            instead.

        Parameters
        ----------
        simulation_setup : HfssSimulationSetup, optional
            Simulation setup object.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`layout_defeaturing` is deprecated and is now located here "
            "`pyedb.grpc.core.utility.simulation_configuration.ProcessSimulationConfiguration."
            "layout_defeaturing` instead.",
            DeprecationWarning,
        )
        self._pedb.utility.simulation_configuration.ProcessSimulationConfiguration.layout_defeaturing(simulation_setup)

    def create_rlc_boundary_on_pins(self, positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0):
        """Create RLC boundary on pins (deprecated).

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_rlc_boundary_on_pins` instead.

        Parameters
        ----------
        positive_pin : Edb.Cell.Primitive.PadstackInstance, optional
            Positive pin.
        negative_pin : Edb.Cell.Primitive.PadstackInstance, optional
            Negative pin.
        rvalue : float, optional
            Resistance value.
        lvalue : float, optional
            Inductance value.
        cvalue : float, optional
            Capacitance value.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`create_rlc_boundary_on_pins` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_rlc_boundary_on_pins` instead.",
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
    ) -> HfssSimulationSetup:
        """Add HFSS analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
            Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.

        Returns
        -------
        HfssSimulationSetup
            Created setup object.

        Examples
        --------
        >>> hfss_setup = edb.hfss.add_setup(
        ...     name="MySetup",
        ...     distribution="linear_count",
        ...     start_freq=1e9,
        ...     stop_freq=10e9,
        ...     step_freq=100,
        ... )
        """
        from ansys.edb.core.simulation_setup.hfss_simulation_setup import (
            HfssSimulationSetup as GrpcHfssSimulationSetup,
        )
        from ansys.edb.core.simulation_setup.simulation_setup import (
            Distribution as GrpcDistribution,
            FrequencyData as GrpcFrequencyData,
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

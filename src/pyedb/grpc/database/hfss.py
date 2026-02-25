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
from typing import Optional
import warnings

from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup,
)
from pyedb.grpc.database.utility.hfss_extent_info import HfssExtentInfo


class Hfss:
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

    def get_trace_width_for_traces_with_ports(self):
        """Retrieve trace widths for traces with ports.

        Returns
        -------
        dict
            Dictionary mapping net names to smallest trace widths.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_aedb")
        >>> widths = edb.hfss.get_trace_width_for_traces_with_ports()
        >>> for net_name, width in widths.items():
        ...     print(f"Net '{net_name}': Smallest width = {width}")
        """
        nets = {}
        for net in self._pedb.excitations_nets:
            nets[net] = self._pedb.nets.nets[net].get_smallest_trace_width()
        return nets

    def get_edge_from_port(self, port):
        _, primitive, point = port._edb_object.GetEdges()[0].GetParameters()

        primitive = Primitive(self._pedb, primitive)
        point = PointData(self._pedb, point)

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
    ):
        warnings.warn(
            "`create_edge_port` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_edge_port` instead.",
            DeprecationWarning,
        )
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
        >>> from pyedb import Edb
        >>> edb = Edb("my_aedb")
        >>> bbox = edb.hfss.get_layout_bounding_box()
        >>> print(f"Layout Bounding Box: {bbox}")
        >>> custom_layout = edb.active_layout
        >>> bbox = edb.hfss.get_layout_bounding_box(custom_layout, 5)
        """
        if not layout:
            layout = self._active_layout
        layout_obj_instances = layout.layout_instance.query_layout_obj_instances()
        tuple_list = []
        for lobj in layout_obj_instances:
            lobj_bbox = lobj.get_bbox()
            tuple_list.append(lobj_bbox)
        _bbox = CorePolygonData.bbox_of_polygons(tuple_list)
        layout_bbox = [
            round(_bbox[0].x.value, digit_resolution),
            round(_bbox[0].y.value, digit_resolution),
            round(_bbox[1].x.value, digit_resolution),
            round(_bbox[1].y.value, digit_resolution),
        ]
        return layout_bbox

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
            terms_bbox.append(CorePolygonData([ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim]))
        return CorePolygonData.bbox_of_polygons(terms_bbox)

    def add_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=None,
        stop_freq=None,
        step_freq=None,
        discrete_sweep=False,
    ) -> Optional[HfssSimulationSetup]:
        """
        .. deprecated pyedb 0.67.0

        Add HFSS analysis setup (deprecated).
        use :func:`create_simulation_setup` instead.

        """
        warnings.warn("add_setup is deprecated use create_simulation_setup instead", DeprecationWarning)

        return self._pedb.simulation_setups.create_hfss_setup(
            name, distribution, start_freq, stop_freq, step_freq, discrete_sweep
        )

    def generate_auto_hfss_regions(self):
        """Generate auto HFSS regions.

        This method automatically identifies areas for use as HFSS regions in SIwave simulations.
        """
        self._pedb.active_cell.generate_auto_hfss_regions()

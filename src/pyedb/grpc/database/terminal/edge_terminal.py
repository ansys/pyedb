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
from typing import TYPE_CHECKING

from ansys.edb.core.terminal.bundle_terminal import BundleTerminal as GrpcBundleTerminal
from ansys.edb.core.terminal.edge_terminal import EdgeTerminal as GrpcEdgeTerminal

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.component import Component


class EdgeTerminal:
    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb
        self._hfss_type = "Gap"

    @classmethod
    def create(cls, layout, name, edge, net, is_ref=False):
        """Create an edge terminal.

        Parameters
        ----------
        layout : :class:`pyedb.grpc.database.layout.layout.Layout`
            Layout object.
        name : str
            Terminal name.
        edge : :class:`.Edge`
            Edge object.
        net : :class:`.Net` or str, optional
            Net object or net name. If None, the terminal will not be assigned to any net.
        is_ref : bool, optional
            Whether the terminal is a reference terminal. Default is False.

        Returns
        -------
        :class:`EdgeTerminal <pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal>`
            Edge terminal object.
        """
        if net is None:
            raise Exception("Net must be specified to create an Edge Terminal.")
        grpc_edge_terminal = GrpcEdgeTerminal.create(
            layout.core,
            name,
            edge,
            net.core,
            is_ref,
        )
        return cls(layout._pedb, grpc_edge_terminal)

    @property
    def component(self):
        """Component.

        Returns
        -------
        Component object.
            :class:`Component <pyedb.grpc.database.component.Component>`.
        """
        from pyedb.grpc.database.hierarchy.component import Component

        return Component(self._pedb, self.core.component)

    @property
    def name(self):
        """Terminal name.

        Returns
        -------
        str : terminal name.
        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def source_amplitude(self):
        """Source amplitude.

        Returns
        -------
        float : source amplitude.
        """
        return self.core.source_amplitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        """Source amplitude."""
        self.core.source_amplitude = self._pedb.value(value)

    @property
    def source_phase(self):
        """Source phase.

        Returns
        -------
        float : source phase.
        """
        return self.core.source_phase

    @property
    def impedance(self):
        """Impedance.

        Returns
        -------
        float : impedance.
        """
        return self.core.impedance

    @impedance.setter
    def impedance(self, value):
        self.core.impedance = self._pedb.value(value)

    @source_phase.setter
    def source_phase(self, value):
        self.core.source_phase = self._pedb.value(value)

    @property
    def boundary_type(self) -> str:
        """Boundary type.

        Returns
        -------
        str : boundary type.
        """
        return self.core.boundary_type.name.lower()

    @property
    def reference_terminal(self):
        """Reference terminal.

        Returns
        -------
        EdgeTerminal object.
        """

        return EdgeTerminal(self._pedb, self.core.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        if isinstance(value, EdgeTerminal):
            self.core.reference_terminal = value.core

    @property
    def is_circuit_port(self) -> bool:
        """Is circuit port.

        Returns
        -------
        bool : circuit port.
        """
        return self.core.is_circuit_port

    @is_circuit_port.setter
    def is_circuit_port(self, value):
        self.core.is_circuit_port = value

    @property
    def port_post_processing_prop(self):
        """Port post-processing property."""
        return self.core.port_post_processing_prop

    @port_post_processing_prop.setter
    def port_post_processing_prop(self, value):
        self.core.port_post_processing_prop = value

    @property
    def _edb_properties(self):
        from ansys.edb.core.database import ProductIdType as GrpcProductIdType

        try:
            p = self.core.get_product_property(GrpcProductIdType.DESIGNER, 1)
        except:
            p = ""
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        from ansys.edb.core.database import ProductIdType as GrpcProductIdType

        self.core.set_product_property(GrpcProductIdType.DESIGNER, 1, value)

    @property
    def is_wave_port(self) -> bool:
        if self._hfss_port_property:
            return True
        return False

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
    def is_null(self) -> bool:
        """Added for dotnet compatibility

        Returns
        -------
        bool
        """
        return self.core.is_null

    @property
    def is_reference_terminal(self) -> bool:
        """Added for dotnet compatibility

        Returns
        -------
        bool
        """
        return self.core.is_reference_terminal

    def set_product_solver_option(self, product_id, solver_name, option):
        """Set product solver option."""
        self.core.set_product_solver_option(product_id, solver_name, option)

    def couple_ports(self, port):
        """Create a bundle wave port.

        Parameters
        ----------
        port : :class:`Waveport <pyedb.grpc.database.ports.ports.WavePort>`,
        :class:`GapPOrt <pyedb.grpc.database.ports.ports.GapPort>`, list, optional
            Ports to be added.

        Returns
        -------
        :class:`BundleWavePort <pyedb.grpc.database.ports.ports.BundleWavePort>`
        """
        if not isinstance(port, (list, tuple)):
            port = [port]
        temp = [self]
        temp.extend([i for i in port])
        bundle_terminal = GrpcBundleTerminal.create(temp)
        return self._pedb.ports[bundle_terminal.name]

    @property
    def is_port(self) -> bool:
        """Added for dotnet compatibility"""
        return True

    @property
    def ref_terminal(self) -> any:
        """Return refeference terminal.

        ..deprecated:: 0.44.0
           Use: func:`reference_terminal` property instead.

        """
        self._pedb.logger.warning("ref_terminal is deprecated, use reference_terminal property instead.")
        return self.core.reference_terminal

    @ref_terminal.setter
    def ref_terminal(self, value):
        self._pedb.logger.warning("ref_terminal is deprecated, use reference_terminal property instead.")
        self.core.reference_terminal = value

    @property
    def hfss_type(self) -> str:
        return self._hfss_type

    @hfss_type.setter
    def hfss_type(self, value):
        self._hfss_type = value

    @property
    def terminal_type(self) -> str:
        return "EdgeTerminal"

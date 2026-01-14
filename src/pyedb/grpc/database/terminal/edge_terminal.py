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

import re
from typing import TYPE_CHECKING

from ansys.edb.core.terminal.bundle_terminal import BundleTerminal as GrpcBundleTerminal
from ansys.edb.core.terminal.edge_terminal import EdgeTerminal as GrpcEdgeTerminal

from pyedb.grpc.database.terminal.terminal import Terminal

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.component import Component


class EdgeTerminal(Terminal):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
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
    def is_wave_port(self) -> bool:
        if self._hfss_port_property:
            return True
        return False

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

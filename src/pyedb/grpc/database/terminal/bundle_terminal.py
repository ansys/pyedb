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

from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.ports.ports import WavePort
from ansys.edb.core.terminal.bundle_terminal import BundleTerminal as GrpcBundleTerminal
from ansys.edb.core.terminal.terminal import (
    HfssPIType as GrpcHfssPIType,
    SourceTermToGroundType as GrpcSourceTermToGroundType,
)

from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.terminal.terminal import Terminal
from pyedb.grpc.database.utility.rlc import Rlc


class BundleTerminal(Terminal):
    """Manages bundle terminal properties.

    Parameters
    ----------
    pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
        EDB object.
    edb_object : :class:`BundleTerminal <ansys.edb.core.terminal.terminals.BundleTerminal>`
        BundleTerminal instance from EDB.
    """

    def __init__(self, pedb, core):
        if isinstance(core, GrpcBundleTerminal):
            super().__init__(pedb, core.terminals[0])
        self.core = core

    @classmethod
    def create(cls, pedb, name: str, terminals: list[Union[Terminal, WavePort, str]]) -> BundleTerminal:
        """Create a bundle terminal.

        Parameters
        ----------
        name : str
            Bundle terminal name.
        terminals : list[Union[Terminal, WavePort]]
            List of terminals to bundle.

        Returns
        -------
        BundleTerminal
            The created bundle terminal.
        """
        if not isinstance(terminals, list):
            raise TypeError("Terminals must be a list of Terminal objects.")
        if not terminals:
            raise ValueError("Terminals list cannot be empty.")
        _terminals = []
        for terminal in terminals:
            if isinstance(terminal, str):
                term = pedb.terminals.get(terminal, None)
                if term is None:
                    raise ValueError(f"Terminal '{terminal}' not found in the design.")
                _terminals.append(term)
        if _terminals and len(_terminals) == len(terminals):
            terminals = _terminals
        terminals = [term.core for term in terminals]
        grpc_term = GrpcBundleTerminal.create(terminals=terminals)
        bundle_terminal = cls(pedb, grpc_term)
        bundle_terminal.name = name
        index = 1
        for terminal in bundle_terminal.terminals:
            terminal.name = f"{name}:T{index}"
            index += 1
        return bundle_terminal

    @property
    def is_reference_terminal(self) -> bool:
        """Check if the bundle terminal is a reference terminal.

        Returns
        -------
        bool
        """
        return self.core.is_reference_terminal

    def decouple(self) -> bool:
        """Ungroup a bundle of terminals.

        Returns
        -------
        bool
        """
        return self.core.ungroup()

    @property
    def component(self) -> Component:
        """Component.

        Returns
        -------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component`
        """

        return Component(self._pedb, self.core.component)

    @property
    def net(self) -> Net:
        """Returns Net object.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
        """

        return Net(self._pedb, self.core.net)

    @property
    def hfss_pi_type(self) -> str:
        """Returns HFSS PI type.

        Returns
        -------
        str
        """
        return self.core.hfss_pi_type.name.lower()

    @hfss_pi_type.setter
    def hfss_pi_type(self, value):
        if value.upper() == "DEFAULT":
            self.core.hfss_pi_type = GrpcHfssPIType.DEFAULT
        elif value.upper() == "COAXIAL_OPEN":
            self.core.hfss_pi_type = GrpcHfssPIType.COAXIAL_OPEN
        elif value.upper() == "COAXIAL_SHORTENED":
            self.core.hfss_pi_type = GrpcHfssPIType.COAXIAL_SHORTENED
        elif value.upper() == "GAP":
            self.core.hfss_pi_type = GrpcHfssPIType.GAP
        elif value.upper() == "LUMPED":
            self.core.hfss_pi_type = GrpcHfssPIType.LUMPED

    @property
    def rlc_boundary_parameters(self) -> Rlc:
        """Returns Rlc parameters

        Returns
        -------
        :class:`Rlc <pyedb.grpc.database.utility.rlc.Rlc>`
        """
        return Rlc(self._pedb, self.core.rlc)

    @property
    def term_to_ground(self) -> str:
        """Returns terminal to ground.

        Returns
        -------
        str
            Terminal name.
        """
        return self.core.term_to_ground.name

    @term_to_ground.setter
    def term_to_ground(self, value):
        if value.upper() == "NO_GROUND":
            self.core.term_to_ground = GrpcSourceTermToGroundType.NO_GROUND
        elif value.upper() == "NEGATIVE":
            self.core.term_to_ground = GrpcSourceTermToGroundType.NEGATIVE
        elif value.upper() == "POSITIVE":
            self.core.term_to_ground = GrpcSourceTermToGroundType.POSITIVE

    @property
    def terminals(self) -> list[Terminal]:
        from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal

        """Returns terminals list.

        Returns
        -------
        List[:class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
        """
        return [EdgeTerminal(self._pedb, terminal) for terminal in self.core.terminals]

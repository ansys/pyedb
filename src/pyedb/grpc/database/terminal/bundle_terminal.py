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


class BundleTerminal:
    """Manages bundle terminal properties.

    Parameters
    ----------
    pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
        EDB object.
    edb_object : :class:`BundleTerminal <ansys.edb.core.terminal.terminals.BundleTerminal>`
        BundleTerminal instance from EDB.
    """

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @classmethod
    def create(cls, terminals: list[Union[Terminal, WavePort]]) -> BundleTerminal:
        """Create a bundle terminal.

        Parameters
        ----------
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
        pedb = terminals[0]._pedb
        for term in terminals[1:]:
            if term._pedb is not pedb:
                raise ValueError("All terminals must belong to the same EDB.")
        terminals = [term.core for term in terminals]
        term = GrpcBundleTerminal.create(terminals=terminals)
        return cls(pedb, term)

    @property
    def boundary_type(self) -> str:
        """Boundary type.

        Returns
        -------
        str : boundary type.
        """
        return self.core.boundary_type.name.lower()

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
    def impedance(self) -> float:
        """Impedance value.

        Returns
        -------
        float
            Impedance value.
        """
        return self.core.impedance.value

    @impedance.setter
    def impedance(self, value):
        self.core.impedance = self._pedb.value(value)

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
    def reference_layer(self) -> Layer:
        """Returns reference layer.

        Returns
        -------
        :class:`Layer <pyedb.grpc.database.layers.layer.Layer>`
        """
        return Layer(self._pedb, self.core.reference_layer)

    @reference_layer.setter
    def reference_layer(self, value):
        if isinstance(value, Layer):
            self.core.reference_layer = value.core
        elif isinstance(value, str):
            self.core.reference_layer = self._pedb.stackup.signal_layer[value].core

    @property
    def reference_terminal(self) -> Terminal:
        """Returns reference terminal.

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
        """
        return Terminal(self._pedb, self.core.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        if isinstance(value, Terminal):
            self.core.reference_terminal = value.core

    @property
    def rlc_boundary_parameters(self) -> Rlc:
        """Returns Rlc parameters

        Returns
        -------
        :class:`Rlc <pyedb.grpc.database.utility.rlc.Rlc>`
        """
        return Rlc(self._pedb, self.core.rlc)

    @property
    def source_amplitude(self) -> float:
        """Returns source amplitude.

        Returns
        -------
        float
        """
        return self.core.source_amplitude.value

    @source_amplitude.setter
    def source_amplitude(self, value):
        self.core.source_amplitude = self._pedb.value(value)

    @property
    def source_phase(self) -> float:
        """Returns source phase.

        Returns
        -------
        float
        """
        return self.core.source_phase.value

    @source_phase.setter
    def source_phase(self, value):
        self.core.source_phase = self._pedb.value(value)

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
        """Returns terminals list.

        Returns
        -------
        List[:class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
        """
        return [Terminal(self._pedb, terminal) for terminal in self.core.terminals]

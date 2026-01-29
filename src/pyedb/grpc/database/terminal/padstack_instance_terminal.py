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

from typing import TYPE_CHECKING

from ansys.edb.core.terminal.padstack_instance_terminal import PadstackInstanceTerminal as CorePadstackInstanceTerminal

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.terminal.terminal import Terminal
from pyedb.grpc.database.utility.value import Value


class PadstackInstanceTerminal(Terminal):
    """Manages bundle terminal properties."""

    def __init__(self, pedb, core):
        super().__init__(pedb, core)

    @classmethod
    def create(cls, layout, name, padstack_instance, layer, is_ref=False, net=None) -> "PadstackInstanceTerminal":
        """Create a padstack instance terminal.
        Parameters
        ----------
        layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
            Layout object associated with the terminal.
        name : str
            Terminal name.
        padstack_instance : PadstackInstance
            Padstack instance object.
        layer : str
            Layer name.
        is_ref : bool, optional
            Whether the terminal is a reference terminal. Default is False.
        Returns
        -------
        PadstackInstanceTerminal
            Padstack instance terminal object.
        """
        if net is None:
            net = padstack_instance.net
        edb_terminal_inst = CorePadstackInstanceTerminal.create(
            layout=layout.core,
            name=name,
            padstack_instance=padstack_instance.core,
            layer=layer,
            net=net.core,
            is_ref=is_ref,
        )
        return cls(layout._pedb, edb_terminal_inst)

    @property
    def is_circuit_port(self) -> bool:
        """Check if the terminal is a circuit port.

        Returns
        -------
        bool
            True if the terminal is a circuit port, False otherwise.
        """
        return self.core.is_circuit_port

    @is_circuit_port.setter
    def is_circuit_port(self, value: bool):
        """Set whether the terminal is a circuit port.

        Parameters
        ----------
        value : bool
            True to set the terminal as a circuit port, False otherwise.
        """
        self.core.is_circuit_port = value

    @property
    def is_reference_terminal(self) -> bool:
        """Check if the terminal is a reference terminal.

        Returns
        -------
        bool
            True if the terminal is a reference terminal, False otherwise.
        """
        return self.core.is_reference_terminal

    @property
    def id(self) -> int:
        """Terminal ID.

        Returns
        -------
        int
            Terminal ID.
        """
        return self.core.edb_uid

    @property
    def edb_uid(self) -> int:
        """Terminal EDB UID.

        Returns
        -------
        int
            Terminal EDB UID.
        """
        return self.core.edb_uid

    @property
    def net(self) -> Net:
        """Net.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
            Terminal net.
        """
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.net)

    @property
    def position(self) -> tuple[float, float]:
        """Terminal position.

        Returns
        -------
        Position [x,y] : [float, float]
        """
        pos_x, pos_y, rotation = self.padstack_instance.core.get_position_and_rotation()
        return Value(pos_x.value), Value(pos_y.value)

    @property
    def padstack_instance(self) -> PadstackInstance:
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        return PadstackInstance(self._pedb, self.core.padstack_instance)

    @property
    def component(self) -> Component:
        from pyedb.grpc.database.hierarchy.component import Component

        return Component(self._pedb, self.core.component)

    @property
    def location(self) -> tuple[float, float]:
        """Terminal position.

        Returns
        -------
        Position [x,y] : [float, float]
        """
        p_inst, _ = self.core.params
        pos_x, pos_y, _ = p_inst.get_position_and_rotation()
        return Value(pos_x), Value(pos_y)

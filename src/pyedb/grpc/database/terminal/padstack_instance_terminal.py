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

from typing import TYPE_CHECKING

from ansys.edb.core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal as GrpcPadstackInstanceTerminal,
)
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecated_property


class PadstackInstanceTerminal:
    """Manages bundle terminal properties."""

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

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
        edb_terminal_inst = GrpcPadstackInstanceTerminal.create(
            layout=layout.core,
            name=name,
            padstack_instance=padstack_instance.core,
            layer=layer,
            net=net.core,
            is_ref=is_ref,
        )
        return cls(layout._pedb, edb_terminal_inst)

    @property
    def name(self) -> str:
        """Terminal name.

        Returns
        -------
        str
            Terminal name.
        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def is_null(self) -> bool:
        """Check if the terminal is null.

        Returns
        -------
        bool
            True if the terminal is null, False otherwise.
        """
        return self.core.is_null

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

    @property
    def net_name(self) -> str:
        """Net name.

        Returns
        -------
        str : name of the net.
        """
        if self.core.is_null:
            return ""
        elif self.core.net.is_null:
            return ""
        else:
            return self.core.net.name

    @net_name.setter
    def net_name(self, val):
        if not self.core.is_null and self.core.net.is_null:
            self.core.net.name = val

    @property
    def magnitude(self) -> float:
        """Source amplitude.

        Returns
        -------
        float : amplitude value.
        """
        return self.source_amplitude

    @magnitude.setter
    def magnitude(self, value):
        self.source_amplitude = value

    @property
    def phase(self) -> float:
        """Source phase.

        Returns
        -------
        float : phase value.
        """
        return self.core.source_phase

    @phase.setter
    def phase(self, value):
        self.core.source_phase = value

    @property
    def source_amplitude(self) -> float:
        """Source amplitude.

        Returns
        -------
        float : amplitude value.
        """
        return self.core.source_amplitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        self.core.source_amplitude = value

    @property
    def source_phase(self) -> float:
        """Source phase.

        Returns
        -------
        float : phase value.
        """
        return self.core.source_phase

    @source_phase.setter
    def source_phase(self, value):
        self.core.source_phase = value

    @property
    def impedance(self) -> float:
        """Impdeance value.

        Returns
        -------
        float : impedance value.
        """
        return Value(self.core.impedance)

    @impedance.setter
    def impedance(self, value):
        self.core.impedance = value

    @property
    def boundary_type(self) -> str:
        """Boundary type.

        Returns
        -------
        str : Boundary type.
        """
        return self.core.boundary_type.name.lower()

    @boundary_type.setter
    def boundary_type(self, value):
        mapping = {
            "port": GrpcBoundaryType.PORT,
            "dc_terminal": GrpcBoundaryType.DC_TERMINAL,
            "voltage_probe": GrpcBoundaryType.VOLTAGE_PROBE,
            "voltage_source": GrpcBoundaryType.VOLTAGE_SOURCE,
            "current_source": GrpcBoundaryType.CURRENT_SOURCE,
            "rlc": GrpcBoundaryType.RLC,
            "pec": GrpcBoundaryType.PEC,
        }
        if isinstance(value, str):
            key = value.lower()
        else:
            key = value.name.lower()
        new_boundary_type = mapping.get(key)
        if new_boundary_type is None:
            valid_types = ", ".join(mapping.keys())
            raise ValueError(f"Invalid boundary type '{value}'. Valid types are: {valid_types}")
        self.core.boundary_type = new_boundary_type

    @property
    def is_port(self) -> bool:
        if self.boundary_type == "port":
            return True
        return False

    @property
    @deprecated_property
    def ref_terminal(self):
        """Return reference terminal.

        ..deprecated:: 0.43.0
           Use: func:`reference_terminal` property instead.
        """
        self._pedb.logger.warning("ref_terminal property is deprecated, use reference_terminal property instead.")
        return self.reference_terminal

    @ref_terminal.setter
    def ref_terminal(self, value):
        self.reference_terminal = value

    @property
    def terminal_type(self) -> str:
        return "PadstackInstanceTerminal"

    @property
    def reference_terminal(self) -> PadstackInstanceTerminal:
        """Return reference terminal.

        Returns
        -------
        PadstackInstanceTerminal
            Reference terminal object.
        """

        return PadstackInstanceTerminal(self._pedb, self.core.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        try:
            self.core.reference_terminal = value.core
        except AttributeError:
            raise ValueError("Failed to set reference terminal.")

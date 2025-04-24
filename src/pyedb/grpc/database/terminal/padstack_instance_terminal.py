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

from ansys.edb.core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal as GrpcPadstackInstanceTerminal,
)
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

from pyedb.misc.misc import deprecated_property


class PadstackInstanceTerminal(GrpcPadstackInstanceTerminal):
    """Manages bundle terminal properties."""

    def __init__(self, pedb, edb_object=None):
        if edb_object:
            super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def position(self):
        """Terminal position.

        Returns
        -------
        Position [x,y] : [float, float]
        """
        pos_x, pos_y, rotation = self.padstack_instance.get_position_and_rotation()
        return [pos_x.value, pos_y.value]

    @property
    def padstack_instance(self):
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        return PadstackInstance(self._pedb, super().padstack_instance)

    @property
    def component(self):
        from pyedb.grpc.database.hierarchy.component import Component

        return Component(self._pedb, super().component)

    @property
    def location(self):
        """Terminal position.

        Returns
        -------
        Position [x,y] : [float, float]
        """
        p_inst, _ = self.params
        pos_x, pos_y, _ = p_inst.get_position_and_rotation()
        return [pos_x.value, pos_y.value]

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str : name of the net.
        """
        if self.is_null:
            return ""
        elif self.net.is_null:
            return ""
        else:
            return self.net.name

    @net_name.setter
    def net_name(self, val):
        if not self.is_null and self.net.is_null:
            self.net.name = val

    @property
    def magnitude(self):
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
    def phase(self):
        """Source phase.

        Returns
        -------
        float : phase value.
        """
        return self.source_phase

    @phase.setter
    def phase(self, value):
        self.source_phase = value

    @property
    def source_amplitude(self):
        """Source amplitude.

        Returns
        -------
        float : amplitude value.
        """
        return super().source_amplitude

    @source_amplitude.setter
    def source_amplitude(self, value):
        super(PadstackInstanceTerminal, self.__class__).source_amplitude.__set__(self, value)

    @property
    def source_phase(self):
        """Source phase.

        Returns
        -------
        float : phase value.
        """
        return super().source_phase.value

    @source_phase.setter
    def source_phase(self, value):
        super(PadstackInstanceTerminal, self.__class__).source_phase.__set__(self, value)

    @property
    def impedance(self):
        """Impdeance value.

        Returns
        -------
        float : impedance value.
        """
        return super().impedance.value

    @impedance.setter
    def impedance(self, value):
        super(PadstackInstanceTerminal, self.__class__).impedance.__set__(self, value)

    @property
    def boundary_type(self):
        """Boundary type.

        Returns
        -------
        str : Boundary type.
        """
        return super().boundary_type.name.lower()

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
        super(PadstackInstanceTerminal, self.__class__).boundary_type.__set__(self, mapping[value.name.lower()])

    @property
    def is_port(self):
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
        if isinstance(value, PadstackInstanceTerminal):
            self.reference_terminal = value

    @property
    def terminal_type(self):
        return "PadstackInstanceTerminal"

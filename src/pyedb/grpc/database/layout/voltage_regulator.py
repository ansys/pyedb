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

if TYPE_CHECKING:
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from ansys.edb.core.layout.voltage_regulator import (
    VoltageRegulator as GrpcVoltageRegulator,
)

from pyedb.grpc.database.utility.value import Value


class VoltageRegulator(GrpcVoltageRegulator):
    """Class managing voltage regulator."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb

    @property
    def component(self):
        """Voltage regulator component

        Returns
        -------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`
            Component.
        """
        if not self.component.is_null:
            ref_des = self.component.name
            if not ref_des:
                return False
            return self._pedb.components.instances[ref_des]
        return False

    @component.setter
    def component(self, value):
        if not isinstance(value, str):
            self._pedb.logger.error("refdes name must be provided to set vrm component")
            return
        if value not in self._pedb.components.instances:
            self._pedb.logger.error(f"component {value} not found in layout")
            return
        self.group = self._pedb.components.instances[value]

    @property
    def load_regulator_current(self) -> float:
        """Load regulator current value

        Returns
        -------
        float
            Current value.
        """
        return Value(self.load_regulator_current)

    @load_regulator_current.setter
    def load_regulator_current(self, value):
        self.load_regulation_percent = Value(value)

    @property
    def load_regulation_percent(self) -> float:
        """Retrieve load regulation percent value.

        Returns
        -------
        float
            Percent value.
        """
        return Value(self.load_regulation_percent)

    @load_regulation_percent.setter
    def load_regulation_percent(self, value):
        self.load_regulation_percent = Value(value)

    @property
    def negative_remote_sense_pin(self) -> PadstackInstance:
        """Retrieve negative remote sense pin.

        Returns
        -------
        :class:`PadstackInstance pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
            PadstackInstance.
        """
        return self._pedb.padstacks.instances[self.negative_remote_sense_pin.id]

    @negative_remote_sense_pin.setter
    def negative_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                self.neg_remote_sense_pin = self._pedb.padsatcks.instances[value]
        elif isinstance(value, PadstackInstance):
            self.neg_remote_sense_pin = value

    @property
    def positive_remote_sense_pin(self) -> PadstackInstance:
        """Retrieve positive remote sense pin.

        Returns
        -------
        :class:`PadstackInstance pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
            PadstackInstance.
        """
        return self._pedb.padstacks.instances[self.pos_remote_sense_pin.id]

    @positive_remote_sense_pin.setter
    def positive_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                self.positive_remote_sense_pin = self._pedb.padsatcks.instances[value]
                if not self.component:
                    self.component = self._pedb.padsatcks.instances[value].component.name
        elif isinstance(value, PadstackInstance):
            self.positive_remote_sense_pin = value
            if not self.component:
                self.component = value.component.name

    @property
    def voltage(self) -> float:
        """Retrieve voltage value.

        Returns
        -------
        float
            Voltage value.
        """
        return Value(self.voltage)

    @voltage.setter
    def voltage(self, value):
        self.voltage = Value(value)

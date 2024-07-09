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

from pyedb.dotnet.edb_core.cell.connectable import Connectable
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance


class VoltageRegulator(Connectable):
    """Class managing EDB voltage regulator."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @property
    def component(self):
        """Retrieve voltage regulator component"""
        if not self._edb_object.GetComponent().IsNull():
            ref_des = self._edb_object.GetComponent().GetName()
            if not ref_des:
                return False
            return self._pedb.components.instances[ref_des]
        self._pedb.logger.warning("No voltage regulator component.")
        return False

    @component.setter
    def component(self, value):
        if not isinstance(value, str):
            self._pedb.logger.error("refdes name must be provided to set vrm component")
            return
        if value not in self._pedb.components.instances:
            self._pedb.logger.error(f"component {value} not found in layout")
            return
        self._edb_object.SetGroup(self._pedb.components.instances[value]._edb_object)

    @property
    def load_regulator_current(self):
        """Retrieve load regulator current value"""
        return self._edb_object.GetLoadRegulationCurrent().ToDouble()

    @load_regulator_current.setter
    def load_regulator_current(self, value):
        _value = self._pedb.edb_value(value)
        self._edb_object.SetLoadRegulationCurrent(_value)

    @property
    def load_regulation_percent(self):
        """Retrieve load regulation percent value."""
        return self._edb_object.GetLoadRegulationPercent().ToDouble()

    @load_regulation_percent.setter
    def load_regulation_percent(self, value):
        _value = self._edb_object.edb_value(value)
        self._edb_object.SetLoadRegulationPercent(_value)

    @property
    def negative_remote_sense_pin(self):
        """Retrieve negative remote sense pin."""
        edb_pin = self._edb_object.GetNegRemoteSensePin()
        return self._pedb.padstacks.instances[edb_pin.GetId()]

    @negative_remote_sense_pin.setter
    def negative_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                _inst = self._pedb.padsatcks.instances[value]
                if self._edb_object.SetNegRemoteSensePin(_inst._edb_object):
                    self._negative_remote_sense_pin = _inst
        elif isinstance(value, EDBPadstackInstance):
            if self._edb_object.SetNegRemoteSensePin(value._edb_object):
                self._negative_remote_sense_pin = value

    @property
    def positive_remote_sense_pin(self):
        """Retrieve positive remote sense pin."""
        edb_pin = self._edb_object.GetPosRemoteSensePin()
        return self._pedb.padstacks.instances[edb_pin.GetId()]

    @positive_remote_sense_pin.setter
    def positive_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                _inst = self._pedb.padsatcks.instances[value]
                if self._edb_object.SetPosRemoteSensePin(_inst._edb_object):
                    self._positive_remote_sense_pin = _inst
                if not self.component:
                    self.component = _inst._edb_object.GetComponent().GetName()
        elif isinstance(value, EDBPadstackInstance):
            if self._edb_object.SetPosRemoteSensePin(value._edb_object):
                self._positive_remote_sense_pin = value
            if not self.component:
                self.component = value._edb_object.GetComponent().GetName()

    @property
    def voltage(self):
        """Retrieve voltage value."""
        return self._edb_object.GetVoltage().ToDouble()

    @voltage.setter
    def voltage(self, value):
        self._edb_object.SetVoltage(self._pedb.edb_value(value))

    @property
    def is_active(self):
        """Check is voltage regulator is active."""
        return self._edb_object.IsActive()

    @is_active.setter
    def is_active(self, value):
        if isinstance(value, bool):
            self._edb_object.SetIsActive(value)

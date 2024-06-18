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

from pyedb.dotnet.edb_core.edb_data.nets_data import EDBNetsData
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance


class VoltageRegulator:
    def __init__(self, pedb):
        self._pedb = pedb
        self._edb_object = None
        self._edb_component = None

    @property
    def component(self):
        if self._edb_component is None:
            self._edb_component = self._edb_object.GetComponent()
            ref_des = self._edb_component.GetName()
            if not ref_des:
                return False
            return self._pedb.components.instances[ref_des]

    @component.setter
    def component(self, value):
        if not isinstance(value, str):
            self._pedb.logger.error("refdes name must be provided to set vrm component")
            return
        if value not in self._pedb.components.instances:
            self._pedb.logger.error(f"component {value} not found in layout")
            return
        self._edb_object.SetGroup(self._pedb.components.instances[value].edb_component)

    @property
    def id(self):
        return self._edb_object.GetId()

    @property
    def load_regulator_current(self):
        return self._edb_object.GetLoadRegulationCurrent().ToDouble()

    @load_regulator_current.setter
    def load_regulator_current(self, value):
        _value = self._pedb.edb_value(value)
        self._edb_object.SetLoadRegulationCurrent(_value)

    @property
    def load_regulation_percent(self):
        return self._edb_object.GetLoadRegulationPercent().ToDouble()

    @load_regulation_percent.setter
    def load_regulation_percent(self, value):
        _value = self._edb_object.edb_value(value)
        self._edb_object.SetLoadRegulationPercent(_value)

    @property
    def name(self):
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._edb_object.SetName(value)

    @property
    def negative_remote_sense_pin(self):
        edb_padtsack_instance = self._edb_object.GetNegRemoteSensePin()
        return self._pedb.padstacks.instances[edb_padtsack_instance.GetId()]

    @negative_remote_sense_pin.setter
    def negative_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                _inst = self._pedb.padsatcks.instances[value]
                self._edb_object.SetNegRemoteSensePin(_inst.edb_object)
            elif isinstance(value, EDBPadstackInstance):
                self._edb_object.SetNegRemoteSensePin(value.edb_object)

    @property
    def positive_remote_sense_pin(self):
        edb_padtsack_instance = self._edb_object.GetPosRemoteSensePin()
        return self._pedb.padstacks.instances[edb_padtsack_instance.GetId()]

    @positive_remote_sense_pin.setter
    def positive_remote_sense_pin(self, value):
        if isinstance(value, int):
            if value in self._pedb.padsatcks.instances:
                _inst = self._pedb.padsatcks.instances[value]
                self._edb_object.SetPosRemoteSensePin(_inst.edb_object)
            elif isinstance(value, EDBPadstackInstance):
                self._edb_object.SetPosRemoteSensePin(value.edb_object)

    @property
    def voltage(self):
        return self._edb_object.GetVoltage().ToDouble()

    @voltage.setter
    def voltage(self, value):
        self._edb_object.SetVoltage(self._pedb.edb_value(value))

    @property
    def is_active(self):
        return self._edb_object.IsActive()

    @is_active.setter
    def is_active(self, value):
        if isinstance(value, bool):
            self._edb_object.SetIsActive(value)

    @property
    def is_null(self):
        return self._edb_object.IsNull()

    @property
    def net(self):
        edb_net = self._edb_object.GetNet()
        return self._pedb.nets[edb_net.GetName()]

    @net.setter
    def net(self, value):
        if isinstance(value, str):
            if value in self._pedb.nets:
                self._edb_object.SetNet(self._pedb.nets[value]._edb_object)
        elif isinstance(value, EDBNetsData):
            self._edb_object.SetNet(value._edb_object)

    def create(
        self, name=None, is_active=True, voltage="3V", load_regulation_current="1A", load_regulation_percent=0.1
    ):
        voltage = self._pedb.edb_value(voltage)
        load_regulation_current = self._pedb.edb_value(load_regulation_current)
        load_regulation_percent = self._pedb.edb_value(load_regulation_percent)
        self._edb_object = self._pedb.Cell.VoltageRegulator.Create(
            self._pedb.active_layout, name, is_active, voltage, load_regulation_current, load_regulation_percent
        )

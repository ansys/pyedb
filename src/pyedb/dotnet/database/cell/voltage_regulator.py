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

from pyedb.dotnet.database.cell.connectable import Connectable
from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance


class VoltageRegulator(Connectable):
    """Class managing EDB voltage regulator."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @property
    def load_regulator_current(self) -> float:
        """Get load regulator current value.

        Returns
        -------
        float
            Load regulator current.
        """
        return self._edb_object.GetLoadRegulationCurrent().ToDouble()

    @load_regulator_current.setter
    def load_regulator_current(self, value):
        """Set load regulator current value.

        Parameters
        ----------
        value : float
            Load regulator current value.
        """
        _value = self._pedb.edb_value(value)
        self._edb_object.SetLoadRegulationCurrent(_value)

    @property
    def load_regulation_percent(self) -> float:
        """Get load regulation percent value.

        Returns
        -------
        float
            Load regulation percentage.
        """
        return self._edb_object.GetLoadRegulationPercent().ToDouble()

    @load_regulation_percent.setter
    def load_regulation_percent(self, value):
        """Set load regulation percent value.

        Parameters
        ----------
        value : float
            Load regulation percentage value.
        """
        _value = self._edb_object.edb_value(value)
        self._edb_object.SetLoadRegulationPercent(_value)

    @property
    def negative_remote_sense_pin(self) -> EDBPadstackInstance:
        """Get negative remote sense pin.

        Returns
        -------
        EDBPadstackInstance
            Negative remote sense pin instance.
        """
        edb_pin = self._edb_object.GetNegRemoteSensePin()
        return self._pedb.padstacks.instances[edb_pin.GetId()]

    @negative_remote_sense_pin.setter
    def negative_remote_sense_pin(self, value):
        """Set negative remote sense pin.

        Parameters
        ----------
        value : int or EDBPadstackInstance
            ID or instance of the padstack to set as negative remote sense pin.
        """
        if isinstance(value, int):
            if value in self._pedb.padstacks.instances:
                _inst = self._pedb.padstacks.instances[value]
                if self._edb_object.SetNegRemoteSensePin(_inst._edb_object):
                    self._negative_remote_sense_pin = _inst
        elif isinstance(value, EDBPadstackInstance):
            if self._edb_object.SetNegRemoteSensePin(value._edb_object):
                self._negative_remote_sense_pin = value

    @property
    def positive_remote_sense_pin(self) -> EDBPadstackInstance:
        """Get positive remote sense pin.

        Returns
        -------
        EDBPadstackInstance
            Positive remote sense pin instance.
        """
        edb_pin = self._edb_object.GetPosRemoteSensePin()
        return self._pedb.padstacks.instances[edb_pin.GetId()]

    @positive_remote_sense_pin.setter
    def positive_remote_sense_pin(self, value):
        """Set positive remote sense pin.

        Parameters
        ----------
        value : int or EDBPadstackInstance
            ID or instance of the padstack to set as positive remote sense pin.
        """
        if isinstance(value, int):
            if value in self._pedb.padstacks.instances:
                _inst = self._pedb.padstacks.instances[value]
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
    def voltage(self) -> float:
        """Get voltage value.

        Returns
        -------
        float
            Voltage of the regulator.
        """
        return self._edb_object.GetVoltage().ToDouble()

    @voltage.setter
    def voltage(self, value):
        """Set voltage value.

        Parameters
        ----------
        value : float
            Voltage to set.
        """
        self._edb_object.SetVoltage(self._pedb.edb_value(value))

    @property
    def is_active(self) -> bool:
        """Check if voltage regulator is active.

        Returns
        -------
        bool
            True if active, False otherwise.
        """
        return self._edb_object.IsActive()

    @is_active.setter
    def is_active(self, value: bool):
        """Set voltage regulator active state.

        Parameters
        ----------
        value : bool
            True to activate, False to deactivate.
        """
        if isinstance(value, bool):
            self._edb_object.SetIsActive(value)

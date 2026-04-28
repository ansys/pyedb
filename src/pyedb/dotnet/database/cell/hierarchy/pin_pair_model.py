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


class PinPair(object):  # pragma: no cover
    def __init__(self, component, edb_pin_pair):
        self._pedb_comp = component
        self._edb_comp = component.edbcomponent
        # Do NOT call component.component_property.core here — that calls
        # GetComponentProperty() which can crash in EDB 2026.1 during bulk
        # iteration after model write operations.  Lazily resolve on demand.
        self._edb_model = component._edb_model
        self._edb_pin_pair = edb_pin_pair

    @property
    def _edb_comp_prop(self):
        """Lazy accessor — only materialises when a write-back is needed."""
        return self._pedb_comp._get_component_property_clone()

    def _edb_value(self, value):
        return self._pedb_comp._get_edb_value(value)  # pragma: no cover

    @property
    def first_pin(self):
        return self._edb_pin_pair.FirstPin

    @property
    def second_pin(self):
        return self._edb_pin_pair.SecondPin

    @property
    def is_parallel(self):
        return self._pin_pair_rlc.IsParallel  # pragma: no cover

    @is_parallel.setter
    def is_parallel(self, value):
        rlc = self._pin_pair_rlc
        rlc.IsParallel = value
        self._set_comp_prop()  # pragma: no cover

    @property
    def _pin_pair_rlc(self):
        return self._edb_model.GetPinPairRlc(self._edb_pin_pair)

    @property
    def rlc_enable(self):
        rlc = self._pin_pair_rlc
        return [rlc.REnabled, rlc.LEnabled, rlc.CEnabled]

    @rlc_enable.setter
    def rlc_enable(self, value):
        rlc = self._pin_pair_rlc
        rlc.REnabled = value[0]
        rlc.LEnabled = value[1]
        rlc.CEnabled = value[2]
        self._set_comp_prop()  # pragma: no cover

    @property
    def resistance(self):
        return self._pin_pair_rlc.R.ToDouble()  # pragma: no cover

    @resistance.setter
    def resistance(self, value):
        self._pin_pair_rlc.R = value
        self._set_comp_prop()  # pragma: no cover

    @property
    def inductance(self):
        return self._pin_pair_rlc.L.ToDouble()  # pragma: no cover

    @inductance.setter
    def inductance(self, value):
        self._pin_pair_rlc.L = value
        self._set_comp_prop()  # pragma: no cover

    @property
    def capacitance(self):
        return self._pin_pair_rlc.C.ToDouble()  # pragma: no cover

    @capacitance.setter
    def capacitance(self, value):
        self._pin_pair_rlc.C = value
        self._set_comp_prop()  # pragma: no cover

    @property
    def rlc_values(self):  # pragma: no cover
        rlc = self._pin_pair_rlc
        return [rlc.R.ToDouble(), rlc.L.ToDouble(), rlc.C.ToDouble()]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        rlc = self._pin_pair_rlc
        rlc.R = self._edb_value(values[0])
        rlc.L = self._edb_value(values[1])
        rlc.C = self._edb_value(values[2])
        self._set_comp_prop()  # pragma: no cover

    def _set_comp_prop(self):  # pragma: no cover
        comp_prop = self._edb_comp_prop  # safe clone via _get_component_property_clone
        comp_prop.SetModel(self._edb_model)
        self._edb_comp.SetComponentProperty(comp_prop)

    def add_pin_pair(
        self,
        r: float | None = None,
        l: float | None = None,
        c: float | None = None,
        r_enabled: bool | None = None,
        l_enabled: bool | None = None,
        c_enabled: bool | None = None,
        first_pin: str | None = None,
        second_pin: str | None = None,
        is_parallel: bool = False,
    ):
        """Add a pin pair definition.

        Parameters
        ----------
        r: float | None
        l: float | None
        c: float | None
        r_enabled: bool
        l_enabled: bool
        c_enabled: bool
        first_pin: str
        second_pin: str
        is_parallel: bool

        Returns
        -------

        """
        m = self._pedb._edb.Cell.Hierarchy.PinPairModel()
        p = self._pedb._edb.Utility.PinPair(first_pin, second_pin)
        if r is None:
            # If resistance is not defined, set it to 0 and disable it
            r = "0ohm"
            en_res = False
        else:
            # If resistance is defined, use the provided value and enabled status
            en_res = True if r_enabled is True or r_enabled is None else False
        if l is None:
            # If inductance is not defined, set it to 0 and disable it
            l = "0nH"
            en_ind = False
        else:
            # If inductance is defined, use the provided value and enabled status
            en_ind = True if l_enabled is True or l_enabled is None else False
        if c is None:
            # If capacitance is not defined, set it to 0 and disable it
            c = "0pF"
            en_cap = False
        else:
            # If capacitance is defined, use the provided value and enabled status
            en_cap = True if c_enabled is True or c_enabled is None else False

        rlc = self._pedb._edb.Utility.Rlc(
            self._pedb.edb_value(r),
            en_res,
            self._pedb.edb_value(l),
            en_ind,
            self._pedb.edb_value(c),
            en_cap,
            is_parallel,
        )
        m.SetPinPairRlc(p, rlc)
        core = self.component._get_component_property_clone()
        core.SetModel(m)
        self.component.edbcomponent.SetComponentProperty(core)

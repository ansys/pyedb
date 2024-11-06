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


class PinPair(object):  # pragma: no cover
    def __init__(self, pcomp, edb_comp, edb_comp_prop, edb_model, edb_pin_pair):
        self._pedb_comp = pcomp
        self._edb_comp = edb_comp
        self._edb_comp_prop = edb_comp_prop
        self._edb_model = edb_model
        self._edb_pin_pair = edb_pin_pair

    def _edb_value(self, value):
        return self._pedb_comp._get_edb_value(value)  # pragma: no cover

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
        self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

    @property
    def inductance(self):
        return self._pin_pair_rlc.L.ToDouble()  # pragma: no cover

    @inductance.setter
    def inductance(self, value):
        self._pin_pair_rlc.L = value
        self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

    @property
    def capacitance(self):
        return self._pin_pair_rlc.C.ToDouble()  # pragma: no cover

    @capacitance.setter
    def capacitance(self, value):
        self._pin_pair_rlc.C = value
        self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

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
        self._edb_model.SetPinPairRlc(self._edb_pin_pair, self._pin_pair_rlc)
        self._edb_comp_prop.SetModel(self._edb_model)
        self._edb_comp.SetComponentProperty(self._edb_comp_prop)

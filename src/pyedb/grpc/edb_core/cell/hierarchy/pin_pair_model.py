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


from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel
from ansys.edb.core.utility.value import Value as EDBValue


class EDBPinPairModel(PinPairModel):  # pragma: no cover
    def __init__(self, pcomp, edb_comp, edb_comp_prop, edb_model, edb_pin_pair):
        self._pedb_comp = pcomp
        self._edb_comp = edb_comp
        self._edb_comp_prop = edb_comp_prop
        self._edb_model = edb_model
        self._edb_pin_pair = edb_pin_pair
        super().__init__(edb_model)

    @property
    def rlc(self):
        return self.get_rlc()

    @property
    def is_parallel(self):
        return self.rlc.is_parallel

    @is_parallel.setter
    def is_parallel(self, value):
        self.rlc.is_parallel = value
        self._set_comp_prop()  # pragma: no cover

    @property
    def _pin_pair_rlc(self):
        return self.rlc(self._edb_pin_pair)

    @property
    def rlc_enable(self):
        rlc = self._pin_pair_rlc
        return [rlc.r_enabled, rlc.l_enabled, rlc.c_enabled]

    @rlc_enable.setter
    def rlc_enable(self, value):
        rlc = self._pin_pair_rlc
        rlc.r_enabled = value[0]
        rlc.l_enabled = value[1]
        rlc.c_enabled = value[2]
        self._set_comp_prop()  # pragma: no cover

    @property
    def resistance(self):
        return self._pin_pair_rlc.r.value  # pragma: no cover

    @resistance.setter
    def resistance(self, value):
        self._pin_pair_rlc.r = EDBValue(value)
        self._set_comp_prop()  # pragma: no cover

    @property
    def inductance(self):
        return self._pin_pair_rlc.l.value  # pragma: no cover

    @inductance.setter
    def inductance(self, value):
        self._pin_pair_rlc.l = EDBValue(value)
        self._set_comp_prop()  # pragma: no cover

    @property
    def capacitance(self):
        return self._pin_pair_rlc.c.value  # pragma: no cover

    @capacitance.setter
    def capacitance(self, value):
        self._pin_pair_rlc.c = EDBValue(value)
        self._set_comp_prop()  # pragma: no cover

    @property
    def rlc_values(self):  # pragma: no cover
        rlc = self._pin_pair_rlc
        return [rlc.r.value, rlc.l.value, rlc.c.value]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        rlc = self._pin_pair_rlc
        rlc.r = EDBValue(values[0])
        rlc.l = EDBValue(values[1])
        rlc.c = EDBValue(values[2])
        self._set_comp_prop()  # pragma: no cover

    def _set_comp_prop(self):  # pragma: no cover
        self._edb_model.set_rlc(self._edb_pin_pair, self._pin_pair_rlc)
        self._edb_comp_prop.model = self._edb_model
        self._edb_comp.component_property = self._edb_comp_prop

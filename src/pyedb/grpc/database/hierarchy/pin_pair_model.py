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


# from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel
from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel as GrpcPinPairModel
from ansys.edb.core.utility.value import Value as GrpcValue


class PinPairModel(GrpcPinPairModel):  # pragma: no cover
    def __init__(self, pedb, edb_object):
        self._pedb_comp = pedb
        super().__init__(edb_object.msg)

    @property
    def rlc(self):
        return super().rlc(self.pin_pairs()[0])

    @property
    def rlc_enable(self):
        return [self.rlc.r_enabled, self.rlc.l_enabled, self.rlc.c_enabled]

    @rlc_enable.setter
    def rlc_enable(self, value):
        self.rlc.r_enabled = GrpcValue(value[0])
        self.rlc.l_enabled = GrpcValue(value[1])
        self.rlc.c_enabled = GrpcValue(value[2])

    @property
    def resistance(self):
        return self.rlc.r.value  # pragma: no cover

    @resistance.setter
    def resistance(self, value):
        self.rlc.r = GrpcValue(value)

    @property
    def inductance(self):
        return self.rlc.l.value  # pragma: no cover

    @inductance.setter
    def inductance(self, value):
        self.rlc.l = GrpcValue(value)

    @property
    def capacitance(self):
        return self.rlc.c.value  # pragma: no cover

    @capacitance.setter
    def capacitance(self, value):
        self.rlc.c = GrpcValue(value)

    @property
    def rlc_values(self):  # pragma: no cover
        return [self.rlc.r.value, self.rlc.l.value, self.rlc.c.value]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        self.rlc.r = GrpcValue(values[0])
        self.rlc.l = GrpcValue(values[1])
        self.rlc.c = GrpcValue(values[2])

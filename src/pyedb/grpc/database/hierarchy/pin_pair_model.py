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


# from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel
from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel as GrpcPinPairModel

from pyedb.grpc.database.utility.value import Value


class PinPairModel(GrpcPinPairModel):
    """Manage pin-pair model."""

    def __init__(self, pedb, edb_object):
        self._pedb_comp = pedb
        super().__init__(edb_object.msg)

    @property
    def rlc(self) -> tuple[str, str]:
        """Rlc mdodel.

        Returns
        -------
        Tuple

        """
        return super().rlc(self.pin_pairs()[0])

    @property
    def rlc_enable(self) -> list[bool]:
        """Enable model.

        Returns
        -------
        List[Renabled(bool), Lenabled(bool), Cenabled(bool)].

        """
        return [self.rlc.r_enabled, self.rlc.l_enabled, self.rlc.c_enabled]

    @rlc_enable.setter
    def rlc_enable(self, value):
        self.rlc.r_enabled = Value(value[0])
        self.rlc.l_enabled = Value(value[1])
        self.rlc.c_enabled = Value(value[2])

    @property
    def resistance(self) -> float:
        """Resistance.

        Returns
        -------
        float
            Resistance value.

        """
        return Value(self.rlc.r)

    @resistance.setter
    def resistance(self, value):
        self.rlc.r = Value(value)

    @property
    def inductance(self) -> float:
        """Inductance.

        Returns
        -------
        float
            Inductance value.

        """
        return Value(self.rlc.l)

    @inductance.setter
    def inductance(self, value):
        self.rlc.l = Value(value)

    @property
    def capacitance(self) -> float:
        """Capacitance.

        Returns
        -------
        float
            Capacitance value.

        """
        return Value(self.rlc.c)

    @capacitance.setter
    def capacitance(self, value):
        self.rlc.c = Value(value)

    @property
    def rlc_values(self) -> list[float]:
        """Rlc value.

        Returns
        -------
        List[float, float, float]
            [R value, L value, C value].

        """
        return [Value(self.rlc.r), Value(self.rlc.l), Value(self.rlc.c)]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        self.rlc.r = Value(values[0])
        self.rlc.l = Value(values[1])
        self.rlc.c = Value(values[2])

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


from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
from ansys.edb.core.utility.value import Value as GrpcValue


class Rlc(GrpcRlc):
    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def r(self) -> float:
        """R value.

        Returns
        -------
        float
            Resistor value.

        """
        return self.r.value

    @r.setter
    def r(self, value):
        self.r = GrpcValue(value)

    @property
    def l(self) -> float:
        """L value.

        Returns
        -------
        float
            Inductor value.

        """
        return self.l.value

    @l.setter
    def l(self, value):
        self.l = GrpcValue(value)

    @property
    def c(self) -> float:
        """C value.

        Returns
        -------
        float
            Capacitor value.

        """
        return self.c.value

    @c.setter
    def c(self, value):
        self.c = GrpcValue(value)

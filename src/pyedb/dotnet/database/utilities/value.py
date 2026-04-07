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


class Value(float):
    """Class defining Edb Value properties."""

    def __new__(cls, pedb, edb_obj):
        temp = super().__new__(cls, edb_obj.ToDouble())
        temp._pedb = pedb
        temp._edb_obj = edb_obj
        temp.__core = edb_obj
        return temp

    @property
    def core(self):
        return self.__core

    @property
    def value(self) -> float:
        return float(round(self._edb_obj.ToDouble(), 9))

    def __str__(self):
        """Returns the string of the variable.

        Returns
        -------
        str
        """
        return self._edb_obj.ToString()

    def __add__(self, other):
        """Adds two Edb Values."""
        return self._pedb.value(f"({self._edb_obj.ToString()})+({str(other)})")

    def __radd__(self, other):
        return self._pedb.value(f"({str(other)})+({self._edb_obj.ToString()})")

    def __sub__(self, other):
        """Subtracts two Edb Values."""
        return self._pedb.value(f"({self._edb_obj.ToString()})-({str(other)})")

    def __rsub__(self, other):
        return self._pedb.value(f"({str(other)})-({self._edb_obj.ToString()})")

    def __mul__(self, other):
        """Multiplies two Edb Values."""
        return self._pedb.value(f"({self._edb_obj.ToString()})*({str(other)})")

    def __rmul__(self, other):
        return self._pedb.value(f"({str(other)})*({self._edb_obj.ToString()})")

    def __truediv__(self, other):
        """Divides two Edb Values."""
        return self._pedb.value(f"({self._edb_obj.ToString()})/({str(other)})")

    def __rtruediv__(self, other):
        return self._pedb.value(f"({str(other)})/({self._edb_obj.ToString()})")

    def __pow__(self, value):
        """Square of the value.
        Returns
        -------
        Value object
        """
        return self._pedb.value(f"({self._edb_obj.ToString()})**({str(value)})")

    def sqrt(self):
        """Square root of the value.
        Returns
        -------
        Value object
        """
        return self._pedb.value(f"({self._edb_obj.ToString()})**0.5")

    def log10(self):
        """Base-10 logarithm of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"log10({self._edb_obj.ToString()})")

    def sin(self):
        """Sine of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"sin({self._edb_obj.ToString()})")

    def cos(self):
        """Cosine of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"cos({self._edb_obj.ToString()})")

    def asin(self):
        """Arcsine of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"asin({self._edb_obj.ToString()})")

    def acos(self):
        """Arccosine of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"acos({self._edb_obj.ToString()})")

    def tan(self):
        """Tangent of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"tan({self._edb_obj.ToString()})")

    def atan(self):
        """Arctangent of the value.
        Returns
        -------
            Value object
        """
        return self._pedb.value(f"atan({self._edb_obj.ToString()})")

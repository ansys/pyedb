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


class Value(float):
    """Class defining Edb Value properties."""

    def __new__(cls, pedb, edb_obj):
        temp = super().__new__(cls, float(round(edb_obj.ToDouble(), 9)))
        temp._pedb = pedb
        temp._edb_obj = edb_obj
        return temp

    def __str__(self):
        """Returns the string of the variable.

        Returns
        -------
        str
        """
        return self._edb_obj.ToString()

    def __add__(self, other):
        """Adds two Edb Values."""
        edb_object = self._pedb.core.Utility.Value(f"({self._edb_obj.ToString()})+({str(other)})")
        return self.__class__(self._pedb, edb_object)

    def __radd__(self, other):
        edb_object = self._pedb.core.Utility.Value(f"({str(other)})+({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def __sub__(self, other):
        """Subtracts two Edb Values."""
        edb_object = self._pedb.core.Utility.Value(f"({self._edb_obj.ToString()})-({str(other)})")
        return self.__class__(self._pedb, edb_object)

    def __rsub__(self, other):
        edb_object = self._pedb.core.Utility.Value(f"({str(other)})-({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def __mul__(self, other):
        """Multiplies two Edb Values."""
        edb_object = self._pedb.core.Utility.Value(f"({self._edb_obj.ToString()})*({str(other)})")
        return self.__class__(self._pedb, edb_object)

    def __rmul__(self, other):
        edb_object = self._pedb.core.Utility.Value(f"({str(other)})*({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def __truediv__(self, other):
        """Divides two Edb Values."""
        edb_object = self._pedb.core.Utility.Value(f"({self._edb_obj.ToString()})/({str(other)})")
        return self.__class__(self._pedb, edb_object)

    def __rtruediv__(self, other):
        edb_object = self._pedb.core.Utility.Value(f"({str(other)})/({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def sqrt(self):
        """Square root of the value."""
        edb_object = self._pedb.core.Utility.Value(f"({self._edb_obj.ToString()})**0.5")
        return self.__class__(self._pedb, edb_object)

    def log10(self):
        """Base-10 logarithm of the value."""
        edb_object = self._pedb.core.Utility.Value(f"log10({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def sin(self):
        """Sine of the value."""
        edb_object = self._pedb.core.Utility.Value(f"sin({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def cos(self):
        """Cosine of the value."""
        edb_object = self._pedb.core.Utility.Value(f"cos({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def asin(self):
        """Arcsine of the value."""
        edb_object = self._pedb.core.Utility.Value(f"asin({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def acos(self):
        """Arccosine of the value."""
        edb_object = self._pedb.core.Utility.Value(f"acos({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def tan(self):
        """Tangent of the value."""
        edb_object = self._pedb.core.Utility.Value(f"tan({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

    def atan(self):
        """Arctangent of the value."""
        edb_object = self._pedb.core.Utility.Value(f"atan({self._edb_obj.ToString()})")
        return self.__class__(self._pedb, edb_object)

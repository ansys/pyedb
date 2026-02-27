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
import math

from ansys.edb.core.utility.value import Value as CoreValue


class Value(float, CoreValue):
    """Class defining Edb Value properties."""

    def __new__(cls, val, owner=None) -> float:
        core = val if isinstance(val, CoreValue) else CoreValue(val, owner)
        inst = super().__new__(cls, core.value)
        inst.core = core
        inst.owner = owner
        return inst

    def __add__(self, other):
        """Adds two Edb Values."""
        res = self.core.value + other
        return res

    def __radd__(self, other):
        res = self.core.value + other
        return res

    def __sub__(self, other):
        """Subtracts two Edb Values."""
        res = self.core.value - other
        return res

    def __rsub__(self, other):
        res = -self.core.value + other
        return res

    def __mul__(self, other):
        """Multiplies two Edb Values."""
        res = self.core.value * other
        return res

    def __rmul__(self, other):
        res = self.core.value * other
        return res

    def __truediv__(self, other):
        """Divides two Edb Values."""
        res = self.core.value / other
        return res

    def __rtruediv__(self, other):
        res = other / self.core.value
        return res

    @property
    def expression(self):
        return str(self)

    def sqrt(self):
        """Square root of the value."""
        res = self.core.value**0.5
        return res

    def log10(self):
        """Base-10 logarithm of the value."""
        res = math.log10(self.core.value)
        return res

    def sin(self):
        """Sine of the value."""
        res = math.sin(self.core.value)
        return res

    def cos(self):
        """Cosine of the value."""
        res = math.cos(self.core.value)
        return res

    def asin(self):
        """Arcsine of the value."""
        res = math.asin(self.core.value)
        return res

    def acos(self):
        """Arccosine of the value."""
        res = math.acos(self.core.value)
        return res

    def tan(self):
        """Tangent of the value."""
        res = math.tan(self.core.value)
        return res

    def atan(self):
        """Arctangent of the value."""
        res = math.atan(self.core.value)
        return res

    def __abs__(self):
        """Abs of the value."""
        res = math.fabs(self.core.value)
        return res

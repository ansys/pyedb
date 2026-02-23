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

from ansys.edb.core.utility import value


class Value(float, value.Value):
    """Class defining Edb Value properties."""

    def __new__(cls, val, owner=None) -> float:
        core =  val if isinstance(val, value.Value) else value.Value(val, owner.core if owner else None)
        inst = super().__new__(cls, core.value)
        inst.core = core
        return inst

    def __add__(self, other):
        """Adds two Edb Values."""
        core = value.Value(f"({str(self.core)})+({str(other)})")
        return self.__class__(core)

    def __radd__(self, other):
        core = value.Value(f"({str(other)})+({str(self.core)})")
        return self.__class__(core)

    def __sub__(self, other):
        """Subtracts two Edb Values."""
        core = value.Value(f"({str(self.core)})-({str(other)})")
        return self.__class__(core)

    def __rsub__(self, other):
        core = value.Value(f"({str(other)})-({str(self.core)})")
        return self.__class__(core)

    def __mul__(self, other):
        """Multiplies two Edb Values."""
        core = value.Value(f"({str(self.core)})*({str(other)})")
        return self.__class__(core)

    def __rmul__(self, other):
        core = value.Value(f"({str(other)})*({str(self.core)})")
        return self.__class__(core)

    def __truediv__(self, other):
        """Divides two Edb Values."""
        core = value.Value(f"({str(self.core)})/({str(other)})")
        return self.__class__(core)

    def __rtruediv__(self, other):
        core = value.Value(f"({str(other)})/({str(self.core)})")
        return self.__class__(core)

    @property
    def expression(self):
        return str(self)

    def sqrt(self):
        """Square root of the value."""
        core = value.Value(f"({str(self.core)})**0.5")
        return self.__class__(core)

    def log10(self):
        """Base-10 logarithm of the value."""
        core = value.Value(f"log10({str(self.core)})")
        return self.__class__(core)

    def sin(self):
        """Sine of the value."""
        core = value.Value(f"sin({str(self.core)})")
        return self.__class__(core)

    def cos(self):
        """Cosine of the value."""
        core = value.Value(f"cos({str(self.core)})")
        return self.__class__(core)

    def asin(self):
        """Arcsine of the value."""
        core = value.Value(f"asin({str(self.core)})")
        return self.__class__(core)

    def acos(self):
        """Arccosine of the value."""
        core = value.Value(f"acos({str(self.core)})")
        return self.__class__(core)

    def tan(self):
        """Tangent of the value."""
        core = value.Value(f"tan({str(self.core)})")
        return self.__class__(core)

    def atan(self):
        """Arctangent of the value."""
        core = value.Value(f"atan({str(self.core)})")
        return self.__class__(core)

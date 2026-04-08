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
        if isinstance(val, (int, float)):
            inst = super().__new__(cls, val)
            inst.__core = None
            inst.is_core = False
        elif isinstance(val, CoreValue):
            try:
                inst = super().__new__(cls, float(str(val)))
                inst.__core = None
                inst.is_core = False
            except ValueError:
                core = val if isinstance(val, CoreValue) else CoreValue(val, owner)
                inst = super().__new__(cls, core.value)
                inst.__core = core
        else:
            core = val if isinstance(val, CoreValue) else CoreValue(val, owner)
            inst = super().__new__(cls, core.value)
            inst.__core = core
        inst.owner = owner

        return inst

    @property
    def core(self):
        if self.__core is None:
            self.__core = CoreValue(self, self.owner)
        return self.__core

    @core.setter
    def core(self, value):
        self.__core = value

    @property
    def value(self):
        if self.__core is None:
            return self
        return super().value

    def __add__(self, other):
        """Adds two Edb Values."""
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(self) + float(other))
        core = CoreValue(f"({str(self.core)})+({str(other)})", self.owner)
        return self.__class__(core, self.owner)

    def __radd__(self, other):
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(self) + float(other))
        core = CoreValue(f"({str(other)})+({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def __sub__(self, other):
        """Subtracts two Edb Values."""
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(self) - float(other))
        core = CoreValue(f"({str(self.core)})-({str(other)})", self.owner)
        return self.__class__(core, self.owner)

    def __rsub__(self, other):
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(other) - float(self))
        core = CoreValue(f"({str(other)})-({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def __mul__(self, other):
        """Multiplies two Edb Values."""
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(self) * float(other))
        core = CoreValue(f"({str(self.core)})*({str(other)})", self.owner)
        return self.__class__(core, self.owner)

    def __rmul__(self, other):
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(other) * float(self))
        core = CoreValue(f"({str(other)})*({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def __truediv__(self, other):
        """Divides two Edb Values."""
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(self) / float(other))
        core = CoreValue(f"({str(self.core)})/({str(other)})", self.owner)
        return self.__class__(core, self.owner)

    def __rtruediv__(self, other):
        if self.__core is None and (
            (isinstance(other, Value) and other.__core is None) or (not isinstance(other, CoreValue))
        ):
            return self.__class__(float(other) / float(self))
        core = CoreValue(f"({str(other)})/({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    @property
    def expression(self):
        return str(self)

    def sqrt(self):
        """Square root of the value."""
        if self.__core is None:
            return self.__class__(float(self) ** 0.5)
        core = CoreValue(f"({str(self.core)})**0.5", self.owner)
        return self.__class__(core, self.owner)

    def log10(self):
        """Base-10 logarithm of the value."""
        if self.__core is None:
            return self.__class__(math.log10(float(self)))
        core = CoreValue(f"log10({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def sin(self):
        """Sine of the value."""
        if self.__core is None:
            return self.__class__(math.sin(float(self)))
        core = CoreValue(f"sin({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def cos(self):
        """Cosine of the value."""
        if self.__core is None:
            return self.__class__(math.cos(float(self)))
        core = CoreValue(f"cos({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def asin(self):
        """Arcsine of the value."""
        if self.__core is None:
            return self.__class__(math.asin(float(self)))
        core = CoreValue(f"asin({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def acos(self):
        """Arccosine of the value."""
        if self.__core is None:
            return self.__class__(math.acos(float(self)))
        core = CoreValue(f"acos({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def tan(self):
        """Tangent of the value."""
        if self.__core is None:
            return self.__class__(math.tan(float(self)))
        core = CoreValue(f"tan({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def atan(self):
        """Arctangent of the value."""
        if self.__core is None:
            return self.__class__(math.atan(float(self)))
        core = CoreValue(f"atan({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

    def __abs__(self):
        """Abs of the value."""
        if self.__core is None:
            return self.__class__(math.fabs(float(self)))
        core = CoreValue(f"abs({str(self.core)})", self.owner)
        return self.__class__(core, self.owner)

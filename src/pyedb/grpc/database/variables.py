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

import warnings

from pyedb.grpc.database.utility.value import Value


class Variable:
    """Manages EDB methods for variable accessible from `Edb.Utility.VariableServer` property."""

    def __init__(self, pedb, name):
        self._pedb = pedb
        self._name = name

    @property
    def _is_design_variable(self):
        """Determines whether this variable is a design variable."""
        return not self.name.startswith("$")

    @property
    def _var_server(self):
        """Return the server containing this variable."""
        return self._pedb.active_cell if self._is_design_variable else self._pedb.active_db

    @property
    def name(self):
        """Get the name of this variable."""
        return self._name

    @property
    def value_object(self):
        """Get a symbolic value object bound to this variable name."""
        try:
            return Value(self.name, self._var_server)
        except Exception:
            return self._pedb.value(self.name)

    @property
    def value(self):
        """Get the value of this variable.

        Returns
        -------
        float
        """
        return self._pedb.value(self._var_server.get_variable_value(self.name))

    @value.setter
    def value(self, value):
        self._var_server.set_variable_value(self.name, self._pedb.value(value))

    @property
    def description(self):
        """Get the description of this variable."""
        return self._var_server.get_variable_desc(self.name)

    @description.setter
    def description(self, value):
        self._var_server.set_variable_desc(name=self.name, desc=value)

    @property
    def is_parameter(self):
        """Determine whether this variable is a parameter."""
        for method_name in ("is_variable_parameter", "is_parameter"):
            method = getattr(self._var_server, method_name, None)
            if callable(method):
                return method(self.name)
        return False

    def delete(self):
        """Delete this variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.design_variables["new_variable"].delete()
        """
        delete_method = getattr(self._var_server, "delete_variable", None)
        if callable(delete_method):
            return delete_method(self.name)
        return False

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value_object)

    def __repr__(self):
        return f"Variable(name={self.name!r}, value={str(self.value)!r})"

    def __add__(self, other):
        return self.value_object + other

    def __radd__(self, other):
        return other + self.value_object

    def __sub__(self, other):
        return self.value_object - other

    def __rsub__(self, other):
        return other - self.value_object

    def __mul__(self, other):
        return self.value_object * other

    def __rmul__(self, other):
        return other * self.value_object

    def __truediv__(self, other):
        return self.value_object / other

    def __rtruediv__(self, other):
        return other / self.value_object

    @property
    def expression(self):
        return self.name

    def sqrt(self):
        return self.value_object.sqrt()

    def log10(self):
        return self.value_object.log10()

    def sin(self):
        return self.value_object.sin()

    def cos(self):
        return self.value_object.cos()

    def asin(self):
        return self.value_object.asin()

    def acos(self):
        return self.value_object.acos()

    def tan(self):
        return self.value_object.tan()

    def atan(self):
        return self.value_object.atan()

    def __abs__(self):
        return abs(self.value_object)

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


class Variable:
    """Manages EDB methods for variable accessible from `Edb.Utility.VariableServer` property."""

    def __init__(self, pedb, name):
        self._pedb = pedb
        self._name = name

    @property
    def _is_design_varible(self):
        """Determines whether this variable is a design variable."""
        if self.name.startswith("$"):
            return False
        else:
            return True

    @property
    def _var_server(self):
        if self._is_design_varible:
            return self._pedb.active_cell.GetVariableServer()
        else:
            return self._pedb.active_db.GetVariableServer()

    @property
    def name(self):
        """Get the name of this variable."""
        return self._name

    @property
    def value_string(self):
        """Get/Set the value of this variable.

        Returns
        -------
        str

        """
        return self._pedb.get_variable(self.name).tostring

    @property
    def value_object(self):
        """Get/Set the value of this variable.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.edbvalue.EdbValue`
        """
        return self._pedb.get_variable(self.name)

    @property
    def value(self):
        """Get the value of this variable.

        Returns
        -------
        float
        """
        return self._pedb.get_variable(self.name).tofloat

    @value.setter
    def value(self, value):
        self._pedb.change_design_variable_value(self.name, value)

    @property
    def description(self):
        """Get the description of this variable."""
        return self._var_server.GetVariableDescription(self.name)

    @description.setter
    def description(self, value):
        self._var_server.SetVariableDescription(self.name, value)

    @property
    def is_parameter(self):
        """Determine whether this variable is a parameter."""
        return self._var_server.IsVariableParameter(self.name)

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
        return self._var_server.DeleteVariable(self.name)

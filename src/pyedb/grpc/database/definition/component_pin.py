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

from ansys.edb.core.definition.component_pin import ComponentPin as GrpcComponentPin


class ComponentPin:
    """Class managing :class:`ComponentPin <ansys.edb.core.definition.component_pin.ComponentPin>`."""

    def __init__(self, edb_object):
        self.core = edb_object

    @classmethod
    def create(cls, component_def, name):
        """Create a component pin.

        Parameters
        ----------
        component_def : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
            Component definition object.
        name : str
            Name of the component pin.

        Returns
        -------
        :class:`ComponentPin <pyedb.grpc.database.definition.component_pin.ComponentPin>`
            The created component pin object.
        """
        edb_obj = GrpcComponentPin.create(component_def.core, name)
        return cls(edb_obj)

    @property
    def is_null(self):
        return self.core.is_null

    @property
    def name(self):
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

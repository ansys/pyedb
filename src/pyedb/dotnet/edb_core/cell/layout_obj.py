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

from pyedb.dotnet.edb_core.layout_obj_instance import LayoutObjInstance
from pyedb.dotnet.edb_core.utilities.obj_base import ObjBase


class LayoutObj(ObjBase):
    """Manages EDB functionalities for the layout object."""

    def __getattr__(self, key):  # pragma: no cover
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._edb_object, key)
            except AttributeError:
                raise AttributeError(f"Attribute '{key}' not present")

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb.edb_api

    @property
    def _layout_obj_instance(self):
        """Returns :class:`dotnet.edb_core.edb_data.connectable.LayoutObjInstance`."""
        obj = self._pedb.layout_instance.GetLayoutObjInstance(self._edb_object, None)
        return LayoutObjInstance(self._pedb, obj)

    @property
    def _edb_properties(self):
        p = self._edb_object.GetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS")
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self._edb_object.SetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS", value)

    @property
    def _obj_type(self):
        """Returns LayoutObjType."""
        return self._edb_object.GetObjType().ToString()

    @property
    def id(self):
        """Primitive ID.

        Returns
        -------
        int
        """
        return self._edb_object.GetId()

    def delete(self):
        """Delete this primitive."""
        self._edb_object.Delete()
        self._pedb.modeler._primitives = []
        self._pedb.padstacks._instances = {}
        self._pedb.padstacks._definitions = {}
        return True

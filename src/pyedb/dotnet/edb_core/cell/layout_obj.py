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

from pyedb.dotnet.edb_core.utilities.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler


class LayoutObjInstance:
    """Manages EDB functionalities for the layout object instance."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object


class LayoutObj(ObjBase):
    """Manages EDB functionalities for the layout object."""

    def __getattr__(self, key):  # pragma: no cover
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._edb_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

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

    @pyedb_function_handler()
    def delete(self):
        """Delete this primitive."""
        self._edb_object.Delete()
        return True


class Connectable(LayoutObj):
    """Manages EDB functionalities for a connectable object."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def net(self):
        """Net Object.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBNetsData`
        """
        from pyedb.dotnet.edb_core.edb_data.nets_data import EDBNetsData

        return EDBNetsData(self._edb_object.GetNet(), self._pedb)

    @net.setter
    def net(self, value):
        """Set net."""
        net = self._pedb.nets[value]
        self._edb_object.SetNet(net.net_object)

    @property
    def component(self):
        """Component connected to this object.

        Returns
        -------
        :class:`dotnet.edb_core.edb_data.nets_data.EDBComponent`
        """
        from pyedb.dotnet.edb_core.edb_data.components_data import EDBComponent

        edb_comp = self._edb_object.GetComponent()
        if edb_comp.IsNull():
            return None
        else:
            return EDBComponent(self._pedb, edb_comp)

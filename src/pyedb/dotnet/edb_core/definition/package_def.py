import os

from pyedb.dotnet.edb_core.edb_data.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.dotnet.edb_core.definition.component_model import (
    NPortComponentModel
)


class PackageDef(ObjBase):
    """Manages EDB functionalities for package definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Inherited AEDT object.
    edb_object : object
        Edb PackageDef Object
    """

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def maximum_power(self):
        """Maximum power of the package."""
        return self._edb_object.GetMaximumPower().ToDouble()

    @maximum_power.setter
    def maximum_power(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetMaximumPower(value)


    @pyedb_function_handler
    def create(self, name):
        edb_object = self._pedb.edb_api.definition.PackageDef.Create(self._pedb.active_db, name)
        return PackageDef(self._pedb, edb_object)

import os
from pyedb.dotnet.edb_core.definition.component_def import EDBComponentDef
from pyedb.dotnet.edb_core.definition.package_def import PackageDef
from pyedb.generic.general_methods import pyedb_function_handler


class Definitions:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def component(self):
        """Component definitions"""
        return {l.GetName(): EDBComponentDef(self._pedb, l) for l in list(self._pedb.active_db.ComponentDefs)}

    @property
    def package(self):
        """Package definitions."""
        return {l.GetName(): PackageDef(self._pedb, l) for l in list(self._pedb.active_db.PackageDefs)}

    @pyedb_function_handler
    def add_package_def(self, name):
        """Add a package definition.

        Parameters
        ----------
        name: str
            Name of the package definition.

        Returns
        -------

        """
        package_def = PackageDef(self._pedb, name=name)
        return package_def

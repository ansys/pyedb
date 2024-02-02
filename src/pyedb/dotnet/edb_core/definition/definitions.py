import os
from pyedb.dotnet.edb_core.definition.component_def import EDBComponentDef


class Definitions:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def component(self):
        """Component definitions"""
        return {l.GetName(): EDBComponentDef(self._pedb, l) for l in list(self._pedb.active_db.ComponentDefs)}

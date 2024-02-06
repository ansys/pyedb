from pyedb.dotnet.edb_core.edb_data.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler


class DefinitionObj(ObjBase):
    """Base class for definition objects."""
    
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        
    @property
    def definition_obj_type(self):
        return self._edb_object.GetDefinitionObjType()

    @property
    def name(self):
        return self._edb_object.GetName()
    
from pyedb.dotnet.edb_core.edb_data.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler


class ComponentModel(ObjBase):
    """Manages component model class."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._model_type_mapping = {"PinPairModel": self._pedb.edb_api.cell}


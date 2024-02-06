from pyedb.dotnet.edb_core.edb_data.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler


class ComponentModel(ObjBase):
    """Manages component model class."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._model_type_mapping = {"PinPairModel": self._pedb.edb_api.cell}

    @pyedb_function_handler()
    def name(self):
        """Name of the component model."""
        return self._edb_object.GetName()


class NPortComponentModel(ComponentModel):
    """Class for n-port component models."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def reference_file(self):
        return self._edb_object.GetReferenceFile()

    @reference_file.setter
    def reference_file(self, value):
        self._edb_object.SetReferenceFile(value)

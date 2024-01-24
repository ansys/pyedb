from pyedb.generic.general_methods import pyedb_function_handler


class BaseSimulationSettings(object):

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def enabled(self):
        return self._edb_object.Enabled

    @property
    def setup_type(self):
        return self._edb_object.SetupType
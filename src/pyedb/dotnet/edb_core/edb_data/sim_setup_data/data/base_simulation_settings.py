class BaseSimulationSettings(object):  # pragma: no cover

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object

from pyedb.legacy.edb_core.sim_setup_data.data.base_simulation_settings import BaseSimulationSettings


class SIWEMISimulationSettings(BaseSimulationSettings):

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def settings(self):
        return self._edb_object.Settings

    @property
    def tags_xml(self):
        return self._edb_object.TagsXml

from pyedb.dotnet.edb_core.edb_data.sim_setup_data.data.base_simulation_settings import BaseSimulationSettings
from pyedb.dotnet.edb_core.edb_data.sim_setup_data.data.siw_emi_config_file.emc_rule_checker_settings import \
    EMCRuleCheckerSettings


class SIWEMISimulationSettings(BaseSimulationSettings):  # pragma: no cover

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._emc_rule_checker_settings = EMCRuleCheckerSettings()

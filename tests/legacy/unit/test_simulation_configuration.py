import os
from pyedb.legacy.edb_core.edb_data.simulation_configuration import SimulationConfiguration
import pytest

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self,local_scratch,):
        self.local_scratch = local_scratch

    def test_simulation_configuration_export_import(self):
        sim_config = SimulationConfiguration()
        assert sim_config.output_aedb is None
        sim_config.output_aedb = os.path.join(self.local_scratch.path, "test.aedb")
        assert sim_config.output_aedb == os.path.join(self.local_scratch.path, "test.aedb")
        json_file = os.path.join(self.local_scratch.path, "test.json")
        sim_config._filename = json_file
        sim_config.arc_angle = "90deg"
        assert sim_config.export_json(json_file)

        test_0import = SimulationConfiguration()
        assert test_0import.import_json(json_file)
        assert test_0import.arc_angle == "90deg"
        assert test_0import._filename == json_file

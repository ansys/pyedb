"""Tests related to the interaction between Edb and Ipc2581
"""

import pytest
from pathlib import Path

from pyedb.dotnet.edb_core.edb_data.sim_setup_data.data.siw_emi_config_file.emc_rule_checker_settings import \
    EMCRuleCheckerSettings

from tests.conftest import local_path

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.local_temp_dir = Path(self.local_scratch.path)
        self.fdir_model = Path(local_path) / "example_models" / "TEDB"
        print(self.local_temp_dir)

    def test_001_read_write_xml(self):
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.read_xml(self.fdir_model / "emi_scanner.tgs")
        emi_scanner.write_xml(self.local_temp_dir / "test_001_write_xml.tgs")

    def test_002_json(self):
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.read_xml(self.fdir_model / "emi_scanner.tgs")
        emi_scanner.write_json(self.local_temp_dir / "test_002_write_json.json")

    def test_003_system(self):
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.add_net("0", "0", "0", "CHASSIS2", "Ground")
        emi_scanner.add_component(comp_name="U2", comp_value="", device_name="SQFP28X28_208", is_clock_driver="0",
                                  is_high_speed="0", is_ic ="1", is_oscillator="0", x_loc="-21.59", y_loc="-41.91")
        emi_scanner.write_xml(self.local_temp_dir / "test_003.tgs")

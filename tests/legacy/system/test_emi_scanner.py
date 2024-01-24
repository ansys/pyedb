"""Tests related to the interaction between Edb and Ipc2581
"""

import json
import os
import pytest

from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_config_file.emc_rule_checker_settings import EMCRuleCheckerSettings

from pyedb.legacy.edb import EdbLegacy
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_read_write_xml(self):
        fpath_1 = r"D:\to_delete\emi_scanner_tags.xml"
        fpath_2 = "d:to_delete/test_write_xml.xml"
        fpath_3 = "d:to_delete/test_write_json.json"
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.read_xml(fpath_1)
        emi_scanner.write_xml(fpath_2)
        emi_scanner.write_json(fpath_3)

    def test_json(self):
        fpath_1 = r"D:\to_delete\test_write_json.json"
        fpath_2 = "d:to_delete/test_json_to_write.xml"
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.read_json(fpath_1)
        emi_scanner.write_xml(fpath_2)

    def test_system(self):
        fpath_2 = "d:to_delete/test_system.xml"
        emi_scanner = EMCRuleCheckerSettings()
        emi_scanner.add_net("0", "0","0", "CHASSIS2", "Ground")
        emi_scanner.write_xml(fpath_2)
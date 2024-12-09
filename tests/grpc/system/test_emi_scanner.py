# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Tests related to the interaction between Edb and Ipc2581
"""

from pathlib import Path

import pytest

from pyedb.misc.siw_feature_config.emc_rule_checker_settings import (
    EMCRuleCheckerSettings,
)
from tests.conftest import local_path

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
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
        emi_scanner.add_net("CHASSIS2")
        emi_scanner.add_net("LVDS_CH01_P", diff_mate_name="LVDS_CH01_N", net_type="Differential")
        emi_scanner.add_component(
            comp_name="U2",
            comp_value="",
            device_name="SQFP28X28_208",
            is_clock_driver="0",
            is_high_speed="0",
            is_ic="1",
            is_oscillator="0",
            x_loc="-21.59",
            y_loc="-41.91",
            cap_type="Decoupling",
        )
        emi_scanner.write_xml(self.local_temp_dir / "test_003.tgs")

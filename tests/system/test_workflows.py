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

"""Tests related to Edb"""

import os

import pytest

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch

    def test_drc_rules(self):
        from pyedb.workflows.drc import Rules

        RULES_DICT = {
            "minLineWidth": [{"name": "MW", "value": "3.5mil"}],
            "minClearance": [{"name": "CLR", "value": "4mil", "net1": "*", "net2": "*"}],
            "minAnnularRing": [{"name": "AR", "value": "2mil"}],
            "diffPairLengthMatch": [
                {"name": "DPMATCH", "tolerance": "5mil", "pairs": [{"positive": "DP_P", "negative": "DP_N"}]}
            ],
            "impedanceSingleEnd": [{"name": "Z0_50", "value": 50, "layers": ["TOP", "BOTTOM"], "tolerance": 3}],
            "impedanceDiffPair": [
                {"name": "Zdiff_90", "value": 90, "pairs": [{"p": "D_P", "n": "D_N"}], "tolerance": 3}
            ],
            "backDrillStubLength": [{"name": "STUB", "value": "6mil"}],
            "copperBalance": [{"name": "CB", "max_percent": 15, "layers": ["L3", "L4"]}],
        }
        rules = Rules.from_dict(RULES_DICT)
        assert rules.min_clearance[0].name == "CLR"
        assert rules.min_clearance[0].value == "4mil"
        assert rules.min_clearance[0].name == "CLR"
        assert rules.back_drill_stub_length[0].name == "STUB"
        assert rules.back_drill_stub_length[0].value == "6mil"
        assert rules.impedance_single_end[0].name == "Z0_50"
        assert rules.impedance_single_end[0].value == 50
        assert rules.min_clearance[0].net1 == "*"
        assert rules.min_clearance[0].net2 == "*"
        assert rules.diff_pair_length_match[0].name == "DPMATCH"
        assert rules.diff_pair_length_match[0].tolerance == "5mil"
        assert rules.diff_pair_length_match[0].pairs[0].positive == "DP_P"
        assert rules.diff_pair_length_match[0].pairs[0].negative == "DP_N"
        assert rules.impedance_diff_pair[0].name == "Zdiff_90"
        assert rules.impedance_diff_pair[0].value == 90
        assert rules.impedance_diff_pair[0].pairs[0]["p"] == "D_P"
        assert rules.impedance_diff_pair[0].pairs[0]["n"] == "D_N"
        assert rules.copper_balance[0].name == "CB"
        assert rules.copper_balance[0].max_percent == 15

    def test_drc_rules_from_file(self, edb_examples):
        from pyedb.workflows.drc import Drc, Rules

        RULES_DICT = {
            "minLineWidth": [{"name": "MW", "value": "3.5mil"}],
            "minClearance": [{"name": "CLR", "value": "4mil", "net1": "*", "net2": "*"}],
            "minAnnularRing": [{"name": "AR", "value": "2mil"}],
            "diffPairLengthMatch": [
                {"name": "DPMATCH", "tolerance": "5mil", "pairs": [{"positive": "DP_P", "negative": "DP_N"}]}
            ],
            "impedanceSingleEnd": [{"name": "Z0_50", "value": 50, "layers": ["TOP", "BOTTOM"], "tolerance": 3}],
            "impedanceDiffPair": [
                {"name": "Zdiff_90", "value": 90, "pairs": [{"p": "D_P", "n": "D_N"}], "tolerance": 3}
            ],
            "backDrillStubLength": [{"name": "STUB", "value": "6mil"}],
            "copperBalance": [{"name": "CB", "max_percent": 15, "layers": ["L3", "L4"]}],
        }

        edbapp = edb_examples.get_si_verse()
        rules = Rules.from_dict(RULES_DICT)
        drc = Drc(edbapp)
        drc.check(rules)
        #
        # print(f"Found {len(drc.violations)} violations")
        # drc.to_dataframe().to_csv("violations.csv", index=False)
        # drc.to_ipc356a("fab_review.ipc")
        #
        # edb.save()
        # edb.close()

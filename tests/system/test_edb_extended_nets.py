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

"""Tests related to Edb extended nets
"""

import pytest

from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    @pytest.mark.skipif(condition=not config["use_grpc"], reason="Test hanging on windows with grpc")
    def test_nets_queries(self, edb_examples):
        """Evaluate nets queries"""
        edbapp = edb_examples.get_si_verse()
        assert edbapp.extended_nets.auto_identify_signal()
        assert edbapp.extended_nets.auto_identify_power()
        extended_net_name, _ = next(iter(edbapp.extended_nets.items.items()))
        assert edbapp.extended_nets.items[extended_net_name]
        assert edbapp.extended_nets.items[extended_net_name].nets
        assert edbapp.extended_nets.items[extended_net_name].components
        assert edbapp.extended_nets.items[extended_net_name].rlc
        assert edbapp.extended_nets.items[extended_net_name].serial_rlc
        assert edbapp.extended_nets.items["1V0"].serial_rlc
        assert edbapp.extended_nets.create("new_ex_net", "DDR4_A1")
        edbapp.close(terminate_rpc_session=False)

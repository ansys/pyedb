# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path

import pytest

from tests.conftest import config

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch

    def test_hfss_log_parser(self, edb_examples):
        from pyedb.workflows.log_parser.hfss_log_parser import HFSSLogParser

        log_file = edb_examples.get_log_file_example()
        log_parser = HFSSLogParser(log_file).parse()
        assert len(log_parser.adaptive) == 8
        last_adaptive = log_parser.adaptive[-1]
        assert last_adaptive.cobverged
        assert last_adaptive.delta_s == 0.017318
        assert last_adaptive.memory_mb == 263
        assert last_adaptive.tetrahedra == 65671
        assert log_parser.init_mesh.tetrahedra == 28358
        assert log_parser.sweep.frequencies == 201
        assert len(log_parser.sweep.solved) == 10
        # log parser methods
        assert log_parser.is_converged()
        assert not log_parser.is_converged()  # project was stopped before completion
        assert log_parser.adaptive_passes()
        assert log_parser.memory_on_convergence() == 263

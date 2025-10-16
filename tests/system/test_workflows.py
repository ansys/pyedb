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

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Failing on GRPC")
    def test_hfss_auto_setup(self, edb_examples):
        from pyedb.workflows.sipi.hfss_auto_configuration import create_hfss_auto_configuration

        log_file = edb_examples.get_log_file_example()
        log_parser = HFSSLogParser(log_file).parse()
        for nr, line in enumerate(Path(log_file).read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if "converge" in line.lower():
                print(f"{nr:04d}  {line.rstrip()}")
        assert len(log_parser.adaptive) == 8
        last_adaptive = log_parser.adaptive[-1]
        assert last_adaptive.converged
        assert last_adaptive.delta_s == 0.017318
        assert last_adaptive.memory_mb == 263
        assert last_adaptive.tetrahedra == 65671
        assert log_parser.init_mesh.tetrahedra == 28358
        assert log_parser.sweep.frequencies == 201
        assert len(log_parser.sweep.solved) == 10
        # log parser methods
        assert log_parser.is_converged()
        assert log_parser.is_converged()
        assert log_parser.adaptive_passes()
        assert log_parser.memory_on_convergence() == 263
        edbapp = edb_examples.get_si_verse()
        hfss_auto_config = create_hfss_auto_configuration(source_edb_path=edbapp.edbpath, edb=edbapp)
        hfss_auto_config.grpc = edbapp.grpc
        hfss_auto_config.ansys_version = edbapp.version
        hfss_auto_config.auto_populate_batch_groups(["PCIe_Gen4_RX", "PCIe_Gen4_TX"])
        hfss_auto_config.add_simulation_setup(
            meshing_frequency="10GHz", start_frequency="0GHz", stop_frequency="40GHz", frequency_step="0.05GHz"
        )
        hfss_auto_config.create_projects()
        assert sum(1 for item in Path(hfss_auto_config.batch_group_folder).iterdir() if item.is_dir()) == 2

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

import os

import pytest

from tests.conftest import local_path, test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_export_to_ipc2581_0(self, edb_examples):
        """Export of a loaded aedb file to an XML IPC2581 file"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
        edbapp = edb_examples.load_edb(source_path)
        xml_file = edb_examples.get_local_file_folder("test_ipc.xml")
        edbapp.export_to_ipc2581(xml_file)
        assert os.path.exists(xml_file)

        # Export should be made with units set to default -millimeter-.
        edbapp.export_to_ipc2581(xml_file, "mm")
        assert os.path.exists(xml_file)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skip(reason="This test is expected to crash (sometimes) at `ipc_edb.close()`")
    def test_export_to_ipc2581_1(self, edb_examples):
        """Export of a loaded aedb file to an XML IPC2581 file"""
        edbapp = edb_examples.get_si_verse()
        xml_file = edb_examples.get_local_file_folder("test_ipc.xml")
        edbapp.export_to_ipc2581(xml_file)
        edbapp.close(terminate_rpc_session=False)
        assert os.path.isfile(xml_file)
        ipc_edb = edb_examples.load_edb(xml_file, copy_to_temp=False)
        ipc_stats = ipc_edb.get_statistics()
        assert ipc_stats.layout_size == (0.1492, 0.0837)
        assert ipc_stats.num_capacitors == 380
        assert ipc_stats.num_discrete_components == 31
        assert ipc_stats.num_inductors == 10
        assert ipc_stats.num_layers == 15
        assert ipc_stats.num_nets == 348
        assert ipc_stats.num_polygons == 138
        assert ipc_stats.num_resistors == 82
        assert ipc_stats.num_traces == 1565
        assert ipc_stats.num_traces == 1565
        assert ipc_stats.num_vias == 4669
        assert ipc_stats.stackup_thickness == 0.001748
        ipc_edb.close(terminate_rpc_session=False)

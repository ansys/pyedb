"""Tests related to the interaction between Edb and Ipc2581
"""

import os

import pytest

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

    def test_export_to_ipc2581_0(self):
        """Export of a loaded aedb file to an XML IPC2581 file"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_ipc.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = EdbLegacy(target_path, edbversion=desktop_version)
        xml_file = os.path.join(self.local_scratch.path, "test.xml")
        edbapp.export_to_ipc2581(xml_file)
        assert os.path.exists(xml_file)

        # Export should be made with units set to default -millimeter-.
        edbapp.export_to_ipc2581(xml_file, "mm")
        assert os.path.exists(xml_file)
        edbapp.close()

    @pytest.mark.xfail(reason="This test is expected to crash (sometimes) at `ipc_edb.close()`")
    def test_export_to_ipc2581_1(self):
        """Export of a loaded aedb file to an XML IPC2581 file"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_ipc", "ANSYS-HSD_V1_boundaries.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = EdbLegacy(target_path, edbversion=desktop_version)
        xml_file = os.path.join(target_path, "test.xml")
        edbapp.export_to_ipc2581(xml_file)
        edbapp.close()
        assert os.path.isfile(xml_file)
        ipc_edb = EdbLegacy(xml_file, edbversion=desktop_version)
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
        assert ipc_stats.num_vias == 4730
        assert ipc_stats.stackup_thickness == 0.001748
        ipc_edb.close()

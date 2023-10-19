"""Tests related to the interaction between Edb and Ipc2581
"""

import os
import pytest

from pyedb import Edb
from tests.legacy.system.conftest import test_subfolder
from tests.legacy.system.conftest import local_path
from tests.conftest import edb_version

# Mark tests as system tests
pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_export_to_ipc2581(self):
        """Export of a loaded aedb file to an XML IPC2581 file"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_ipc.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=edb_version)
        ipc_path = os.path.join(self.local_scratch.path, "test.xml")
        edbapp.export_to_ipc2581(ipc_path)
        assert os.path.exists(ipc_path)

        # Export should be made with units set to default -millimeter-.
        edbapp.export_to_ipc2581(ipc_path, "mm")
        assert os.path.exists(ipc_path)
        edbapp.close()

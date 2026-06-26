# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Tests related to general Edb functionality: variables, statistics, save, export, settings."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import ansys.edb.core
import pytest

from pyedb import Edb
from pyedb.edb_logger import EdbLogger
from pyedb.generic.general_methods import is_linux
from tests.conftest import GRPC, config, desktop_version
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_add_variables(self):
        """Add design and project variables."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.add_design_variable("my_variable", "1mm")
        assert "my_variable" in edbapp.get_all_variable_names()
        assert edbapp.modeler.parametrize_trace_width("DDR4_DQ25")
        assert edbapp.modeler.parametrize_trace_width("DDR4_A2")
        if edbapp.grpc:
            edbapp.add_design_variable("my_parameter", "2mm", "test description")
        else:
            edbapp.add_design_variable("my_parameter", "2mm", True)
        assert "my_parameter" in edbapp.get_all_variable_names()
        variable_value = edbapp.get_variable("my_parameter")
        assert variable_value.value == 2e-3
        if edbapp.grpc:
            assert not edbapp.add_design_variable("my_parameter", "2mm", "test description")
        else:
            assert not edbapp.add_design_variable("my_parameter", "2mm", True)[0]
        edbapp.add_project_variable("$my_project_variable", "3mm")
        assert edbapp.get_variable("$my_project_variable").value == 3e-3
        if edbapp.grpc:
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")
        else:
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")[0]
        edbapp.close(terminate_rpc_session=False)

    def test_save_edb_as(self):
        """Save edb as some file."""
        edbapp = self.edb_examples.create_empty_edb()
        target_path = Path(self.edb_examples.test_folder) / "si_verse_new.aedb"
        assert edbapp.save_as(target_path)
        assert (target_path / "edb.def").exists()
        edbapp.close(terminate_rpc_session=False)

    def test_export_3d(self):
        """Export EDB to HFSS, Q3D and Maxwell."""
        mock_process = MagicMock()
        edb = self.edb_examples.create_empty_edb()
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.edb_examples.test_folder, options_config)
        assert Path(out).exists()
        with patch("subprocess.run", return_value=mock_process) as mock_run:
            executable = "siwave" if is_linux else "siwave.exe"

            edb.export_hfss(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]
            input_cmd_ = [
                str(Path(edb.ansys_em_path) / executable),
                "-RunScriptAndExit",
                str(Path(edb.edbpath).parent / "export_cad.py"),
            ]
            assert input_cmd == input_cmd_

            edb.export_q3d(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]
            assert input_cmd == input_cmd_

            edb.export_maxwell(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]
            assert input_cmd == input_cmd_

        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6",
        reason="Test skipped for ansys-edb-core version 0.2.6",
    )
    def test_edb_statistics(self):
        """Get EDB statistics."""
        edb = self.edb_examples.get_si_verse_sfp()
        edb_stats = edb.get_statistics(compute_area=False)
        assert edb_stats
        assert edb_stats.num_layers
        assert edb_stats.stackup_thickness
        assert edb_stats.num_vias
        assert edb_stats.layout_size
        assert edb_stats.num_polygons
        assert edb_stats.num_traces
        assert edb_stats.num_nets
        assert edb_stats.num_discrete_components
        assert edb_stats.num_inductors
        assert edb_stats.num_capacitors
        assert edb_stats.num_resistors
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6",
        reason="Test skipped for ansys-edb-core version 0.2.6",
    )
    def test_edb_settings(self):
        """Validate EDB general settings and utility methods."""
        edbapp = self.edb_examples.get_si_verse()
        assert type(edbapp.logger) == EdbLogger
        assert edbapp.version == config["desktopVersion"]
        assert edbapp.base_path == edbapp.ansys_em_path
        assert edbapp.grpc == config["use_grpc"]
        val = edbapp.value(1)
        assert val
        edbapp.add_design_variable("test", 1)
        assert edbapp.design_variables["test"].value == 1
        edbapp.add_project_variable("test2", 2)
        assert edbapp.project_variables["$test2"].value == 2
        assert type(edbapp.layout_validation)
        assert "test", "$test2" in edbapp.variables.items()
        edbapp.change_design_variable_value("test", 3)
        assert edbapp.design_variables["test"].value == 3
        assert edbapp.get_bounding_box()
        assert edbapp.get_statistics()
        assert edbapp.are_port_reference_terminals_connected()
        edbapp.close(terminate_rpc_session=False)

    def test_load_multiple_edb(self):
        """Load two EDB sessions simultaneously and verify isolation."""
        edb1 = self.edb_examples.get_si_board()
        assert len(list(edb1.components.instances.values())) == 4
        assert list(edb1.components.instances.values())[0].name == "U0"
        edb2 = self.edb_examples.get_si_verse()
        assert list(edb1.components.instances.values())[0].name == "U0"
        assert len(list(edb2.components.instances.values())) == 509
        assert list(edb2.components.instances.values())[0].name == "C380"
        edb1.close(terminate_rpc_session=False)
        assert edb1.active_cell is None
        assert len(list(edb2.components.instances.values())) == 509
        assert list(edb2.components.instances.values())[0].name == "C380"
        edb2.close(terminate_rpc_session=False)
        assert edb2.active_cell is None


@pytest.mark.usefixtures("close_rpc_session")
class TestEdbLifecycle:
    """EDB creation, variable management and conflict-file handling tests.

    Uses the ``local_scratch`` fixture directly and constructs ``Edb`` instances
    instead of going through ``BaseTestClass.edb_examples``.
    """

    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_create_edb(self):
        """Create EDB."""
        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        assert edb
        assert edb.active_layout
        edb.close(terminate_rpc_session=False)

    def test_create_edb_without_path(self):
        """Create EDB without path."""
        import time

        edbapp_without_path = Edb(version=desktop_version, isreadonly=False, grpc=GRPC)
        time.sleep(2)
        edbapp_without_path.close(terminate_rpc_session=False)

    def test_variables_value(self):
        """Evaluate variables value."""
        from pyedb.generic.general_methods import check_numeric_equivalence

        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        edb.add_design_variable(variable_name="var1", variable_value=0.01)
        edb.add_design_variable(variable_name="var2", variable_value="10um")
        assert edb.variables["var1"]
        edb.add_design_variable(variable_name="var3", variable_value=0.03, description="test description")
        edb.add_project_variable(variable_name="var4", variable_value="1mm", description="Project variable.")
        edb.add_project_variable(variable_name="$var5", variable_value=0.1)
        assert edb["var1"].value == 0.01
        val2 = edb["var2"].value
        assert check_numeric_equivalence(val2.double if hasattr(val2, "double") else val2, 1.0e-5)
        assert edb["var3"].value == 0.03
        var3 = edb.get_variable("var3")
        if edb.grpc:
            assert edb.active_cell.get_variable_desc("var3") == "test description"
        else:
            assert var3.description == "test description"
        assert edb["$var4"].value == 0.001
        if edb.grpc:
            assert edb.active_db.get_variable_desc("$var4") == "Project variable."
        else:
            assert edb.get_variable("$var4").description == "Project variable."
        assert edb["$var5"].value == 0.1
        if edb.grpc:
            assert "$var5" in edb.active_db.get_all_variable_names()
        else:
            assert edb.get_variable("$var5").delete()

    def test_add_design_variable(self):
        """Add a variable value."""
        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        if edb.grpc:
            edb.add_design_variable(variable_name="ant_length", variable_value="1cm")
            edb.add_design_variable(variable_name="my_parameter_default", variable_value="1mm")
            edb.add_project_variable(variable_name="$my_project_variable", variable_value="1mm")
            assert "ant_length" in edb.active_cell.get_all_variable_names()
            assert "my_parameter_default" in edb.active_cell.get_all_variable_names()
            assert "$my_project_variable" in edb.active_db.get_all_variable_names()
        else:
            is_added, _ = edb.add_design_variable(variable_name="ant_length", variable_value="1cm")
            assert is_added
            is_added, _ = edb.add_design_variable(
                variable_name="my_parameter_default", variable_value="1mm", is_parameter=True
            )
            assert is_added
            is_added, _ = edb.add_design_variable(variable_name="$my_project_variable", variable_value="1mm")
            assert is_added

    def test_add_design_variable_with_setitem(self):
        """Add a variable value via __setitem__."""
        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        edb.add_design_variable("ant_length", "1cm")
        if edb.grpc:
            assert edb.variable_exists("ant_length")
        else:
            assert edb.variable_exists("ant_length")[0]
        assert edb["ant_length"].value == 0.01

    def test_change_design_variable_value(self):
        """Change a variable value."""
        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        edb.add_design_variable(variable_name="ant_length", variable_value="1cm")
        edb.add_design_variable(variable_name="my_parameter_default", variable_value="1mm")
        edb.add_design_variable(variable_name="$my_project_variable", variable_value="1mm")
        if edb.grpc:
            edb.change_design_variable_value(variable_name="ant_length", variable_value="1m")
            edb.change_design_variable_value(variable_name="elephant_length", variable_value="1m")
            edb.change_design_variable_value(variable_name="my_parameter_default", variable_value="1m")
            assert "ant_length" in edb.active_cell.get_all_variable_names()
            assert "elephant_length" not in edb.active_cell.get_all_variable_names()
            assert "my_parameter_default" in edb.active_cell.get_all_variable_names()
        else:
            is_changed, _ = edb.change_design_variable_value("ant_length", "1m")
            assert is_changed
            is_changed, _ = edb.change_design_variable_value("elephant_length", "1m")
            assert not is_changed
            is_changed, _ = edb.change_design_variable_value("my_parameter_default", "1m")
            assert is_changed
            is_changed, _ = edb.change_design_variable_value("$my_project_variable", "1m")
            assert is_changed
            is_changed, _ = edb.change_design_variable_value("$my_parameter", "1m")
            assert not is_changed

    def test_change_design_variable_value_with_setitem(self):
        """Change a variable value via __setitem__."""
        edb = Edb(
            os.path.join(self.local_scratch.path, "temp.aedb"),
            version=desktop_version,
            grpc=GRPC,
        )
        edb.add_design_variable("ant_length", "1cm")
        assert edb["ant_length"].value == 0.01
        edb["ant_length"] = "2cm"
        assert edb["ant_length"].value == 0.02

    @patch("os.path.isfile")
    @patch("os.unlink")
    def test_conflict_files_removal_success(self, mock_unlink, mock_isfile):
        """Conflicting .aedt/.aedt.lock files are deleted when remove_existing_aedt=True."""
        mock_isfile.side_effect = lambda f: f.endswith((".aedt", ".aedt.lock"))

        edbpath = os.path.join(self.local_scratch.path, "conflict_test.aedb")
        aedt_file = os.path.splitext(edbpath)[0] + ".aedt"
        expected_deleted = [aedt_file, aedt_file + ".lock"]

        edb = Edb(edbpath=edbpath, version=desktop_version, grpc=GRPC, remove_existing_aedt=True)
        edb.close(terminate_rpc_session=False)

        for f in expected_deleted:
            mock_unlink.assert_any_call(f)

    @patch("os.path.isfile")
    @patch("os.unlink")
    def test_conflict_files_removal_failure(self, mock_unlink, mock_isfile):
        """Warning is logged when conflicting files exist but removal fails."""
        mock_isfile.side_effect = lambda f: f.endswith((".aedt", ".aedt.lock"))
        mock_unlink.side_effect = Exception("Could not delete file")

        edbpath = os.path.join(self.local_scratch.path, "conflict_fail_test.aedb")
        edb = Edb(edbpath=edbpath, version=desktop_version, grpc=GRPC, remove_existing_aedt=True)
        edb.close(terminate_rpc_session=False)

        aedt_file = os.path.splitext(edbpath)[0] + ".aedt"
        expected_attempted = [aedt_file, aedt_file + ".lock"]
        for f in expected_attempted:
            mock_unlink.assert_any_call(f)

    @patch("os.path.isfile")
    @patch("os.unlink")
    def test_conflict_files_leave_in_place(self, mock_unlink, mock_isfile):
        """Conflicting files are NOT deleted when remove_existing_aedt=False (default)."""
        mock_isfile.side_effect = lambda f: f.endswith((".aedt", ".aedt.lock"))

        edbpath = os.path.join(self.local_scratch.path, "conflict_keep_test.aedb")
        edb = Edb(edbpath=edbpath, version=desktop_version, grpc=GRPC)
        edb.close(terminate_rpc_session=False)

        mock_unlink.assert_not_called()

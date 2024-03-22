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


import os

from mock import MagicMock, PropertyMock, patch
import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_create_edb(self):
        """Create EDB."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        assert edb
        assert edb.active_layout
        edb.close()

    def test_create_edb_without_path(self):
        """Create EDB without path."""
        import time

        edbapp_without_path = Edb(edbversion=desktop_version, isreadonly=False)
        time.sleep(2)
        edbapp_without_path.close()

    def test_variables_value(self):
        """Evaluate variables value."""
        from pyedb.generic.general_methods import check_numeric_equivalence

        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb["var1"] = 0.01
        edb["var2"] = "10um"
        edb["var3"] = [0.03, "test description"]
        edb["$var4"] = ["1mm", "Project variable."]
        edb["$var5"] = 0.1
        assert edb["var1"].value == 0.01
        assert check_numeric_equivalence(edb["var2"].value, 1.0e-5)
        assert edb["var3"].value == 0.03
        assert edb["var3"].description == "test description"
        assert edb["$var4"].value == 0.001
        assert edb["$var4"].description == "Project variable."
        assert edb["$var5"].value == 0.1
        assert edb.project_variables["$var5"].delete()

    def test_add_design_variable(self):
        """Add a variable value."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        is_added, _ = edb.add_design_variable("ant_length", "1cm")
        assert is_added
        is_added, _ = edb.add_design_variable("ant_length", "1cm")
        assert not is_added
        is_added, _ = edb.add_design_variable("my_parameter_default", "1mm", is_parameter=True)
        assert is_added
        is_added, _ = edb.add_design_variable("my_parameter_default", "1mm", is_parameter=True)
        assert not is_added
        is_added, _ = edb.add_design_variable("$my_project_variable", "1mm")
        assert is_added
        is_added, _ = edb.add_design_variable("$my_project_variable", "1mm")
        assert not is_added

    def test_add_design_variable_with_setitem(self):
        """Add a variable value."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb["ant_length"] = "1cm"
        assert edb.variable_exists("ant_length")[0]
        assert edb["ant_length"].value == 0.01

    def test_change_design_variable_value(self):
        """Change a variable value."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb.add_design_variable("ant_length", "1cm")
        edb.add_design_variable("my_parameter_default", "1mm", is_parameter=True)
        edb.add_design_variable("$my_project_variable", "1mm")

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
        """Change a variable value."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb["ant_length"] = "1cm"
        assert edb["ant_length"].value == 0.01
        edb["ant_length"] = "2cm"
        assert edb["ant_length"].value == 0.02

    def test_create_padstack_instance(self):
        """Create padstack instances."""
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)

        pad_name = edb.padstacks.create(
            pad_shape="Rectangle",
            padstackname="pad",
            x_size="350um",
            y_size="500um",
            holediam=0,
        )
        assert pad_name == "pad"

        pad_name = edb.padstacks.create(pad_shape="Circle", padstackname="pad2", paddiam="350um", holediam="15um")
        assert pad_name == "pad2"

        pad_name = edb.padstacks.create(
            pad_shape="Circle",
            padstackname="test2",
            paddiam="400um",
            holediam="200um",
            antipad_shape="Rectangle",
            anti_pad_x_size="700um",
            anti_pad_y_size="800um",
            start_layer="1_Top",
            stop_layer="1_Top",
        )
        pad_name == "test2"
        edb.close()

    @patch("os.path.isfile")
    @patch("shutil.rmtree")
    @patch("pyedb.dotnet.edb_core.dotnet.database.EdbDotNet.logger", new_callable=PropertyMock)
    def test_conflict_files_removal_success(self, mock_logger, mock_rmtree, mock_isfile):
        logger_mock = MagicMock()
        mock_logger.return_value = logger_mock
        mock_isfile.side_effect = lambda file: file.endswith((".aedt", ".aedt.lock"))

        edbpath = "file.edb"
        aedt_file = os.path.splitext(edbpath)[0] + ".aedt"
        files = [aedt_file, aedt_file + ".lock"]
        _ = Edb(edbpath)

        for file in files:
            mock_rmtree.assert_any_call(file)
            logger_mock.info.assert_any_call(f"Removing {file} to allow loading EDB file.")

    @patch("os.path.isfile")
    @patch("shutil.rmtree")
    @patch("pyedb.dotnet.edb_core.dotnet.database.EdbDotNet.logger", new_callable=PropertyMock)
    def test_conflict_files_removal_failure(self, mock_logger, mock_rmtree, mock_isfile):
        logger_mock = MagicMock()
        mock_logger.return_value = logger_mock
        mock_isfile.side_effect = lambda file: file.endswith((".aedt", ".aedt.lock"))
        mock_rmtree.side_effect = Exception("Could not delete file")

        edbpath = "file.edb"
        aedt_file = os.path.splitext(edbpath)[0] + ".aedt"
        files = [aedt_file, aedt_file + ".lock"]
        _ = Edb(edbpath)

        for file in files:
            mock_rmtree.assert_any_call(file)
            logger_mock.info.assert_any_call(
                f"Failed to delete {file} which is located at the same location as the EDB file."
            )

import os
import pytest

from tests.conftest import desktop_version
from pyedb.legacy.edb import EdbLegacy

pytestmark = pytest.mark.unit

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self,local_scratch,):
        self.local_scratch = local_scratch

    def test_create_edb(self):
        """Create EDB."""
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        assert edb
        assert edb.active_layout
        edb.close()

    def test_variables_value(self):
        """Evaluate variables value."""
        from pyedb.generic.general_methods import check_numeric_equivalence

        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
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
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
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
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb["ant_length"] = "1cm"
        assert edb.variable_exists("ant_length")
        assert edb["ant_length"] == "1cm"

    def test_change_design_variable_value(self):
        """Change a variable value."""
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
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
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
        edb["ant_length"] = "1cm"
        assert edb["ant_length"] == "1cm"
        edb["ant_length"] = "2cm"
        assert edb["ant_length"] == "2cm"

    def test_create_padstack_instance(self):
        """Create padstack instances."""
        edb = EdbLegacy(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)

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

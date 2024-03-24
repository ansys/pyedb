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
from pathlib import Path
import sys

import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch
        local_path = Path(__file__).parent.parent.parent
        example_folder = local_path / "example_models" / "TEDB"
        src_edb = example_folder / "ANSYS-HSD_V1.aedb"
        src_input_folder = example_folder / "edb_config_json"

        self.local_edb = Path(self.local_scratch.path) / "ansys.aedb"
        self.local_input_folder = Path(self.local_scratch.path) / "input_files"
        self.local_scratch.copyfolder(str(src_edb), str(self.local_edb))
        self.local_scratch.copyfolder(str(src_input_folder), str(self.local_input_folder))

    def test_01_create_edb(self):
        edbapp = Edb(str(self.local_edb), desktop_version)
        assert edbapp.configuration.load(self.local_input_folder / "stackup.json", apply_file=True)
        edbapp.configuration.load(self.local_input_folder / "components.json")
        assert edbapp.configuration.run()
        assert edbapp.configuration.load(self.local_input_folder / "setups_hfss.json", apply_file=True)
        assert "stackup" in edbapp.configuration.data
        assert edbapp.configuration.load(
            self.local_input_folder / "setups_siwave_syz.json", apply_file=True, append=False
        )
        assert "stackup" not in edbapp.configuration.data
        assert edbapp.configuration.load(self.local_input_folder / "setups_siwave_dc.json", apply_file=True)
        assert edbapp.configuration.load(self.local_input_folder / "s_parameter.json", apply_file=True)
        assert edbapp.configuration.load(
            self.local_input_folder / "ports_coax.json",
            apply_file=True,
            output_file=str(os.path.join(self.local_scratch.path, "exported_1.aedb")),
            open_at_the_end=False,
        )
        assert Path(self.local_scratch.path, "exported_1.aedb").exists()
        assert edbapp.configuration.load(
            self.local_input_folder / "ports_circuit.json",
            apply_file=True,
            output_file=str(os.path.join(self.local_scratch.path, "exported_2.aedb")),
            open_at_the_end=True,
        )
        assert Path(self.local_scratch.path, "exported_2.aedb").exists()
        assert edbapp.configuration.load(self.local_input_folder / "sources.json")
        edbapp.close()

    def test_02_create_port_on_pin_groups(self):
        edbapp = Edb(str(self.local_edb), desktop_version)
        assert edbapp.configuration.load(self.local_input_folder / "pin_groups.json", apply_file=True)
        edbapp.close()

    def test_03_spice_models(self):
        edbapp = Edb(str(self.local_edb), desktop_version)
        assert edbapp.configuration.load(str(self.local_input_folder / "spice.json"), apply_file=True)
        assert edbapp.components["R107"].model.model_name
        assert edbapp.components["R107"].model.spice_file_path
        assert edbapp.components["R106"].model.spice_file_path
        edbapp.close()

    def test_04_nets(self):
        edbapp = Edb(str(self.local_edb), desktop_version)
        assert edbapp.configuration.load(self.local_input_folder / "nets.json", apply_file=True)
        assert edbapp.nets["1.2V_DVDDL"].is_power_ground
        assert not edbapp.nets["SFPA_VCCR"].is_power_ground
        edbapp.close()

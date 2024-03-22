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

from pathlib import Path

import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

local_path = Path(__file__).parent.parent.parent


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_create_edb(self):
        example_folder = local_path / "example_models" / "TEDB"
        example_json_folder = example_folder / "edb_config_json"
        example_edb = example_folder / "ANSYS-HSD_V1.aedb"

        target_path_edb = Path(self.local_scratch.path) / "configuration" / "test.aedb"
        target_path_edb2 = Path(self.local_scratch.path) / "configuration" / "test_new.aedb"

        self.local_scratch.copyfolder(str(example_edb), str(target_path_edb))

        edbapp = Edb(str(target_path_edb), desktop_version)
        assert edbapp.configuration.load(example_json_folder / "stackup.json", apply_file=True)
        edbapp.configuration.load(example_json_folder / "components.json")
        assert edbapp.configuration.run()
        assert edbapp.configuration.load(example_json_folder / "setups_hfss.json", apply_file=True)
        assert "stackup" in edbapp.configuration.data
        assert edbapp.configuration.load(example_json_folder / "setups_siwave_syz.json", apply_file=True, append=False)
        assert "stackup" not in edbapp.configuration.data
        assert edbapp.configuration.load(example_json_folder / "setups_siwave_dc.json", apply_file=True)
        assert edbapp.configuration.load(example_json_folder / "s_parameter.json", apply_file=True)
        assert edbapp.configuration.load(
            example_json_folder / "ports_coax.json",
            apply_file=True,
            output_file=str(target_path_edb2),
            open_at_the_end=False,
        )
        assert edbapp.edbpath == str(target_path_edb)
        assert edbapp.configuration.load(
            example_json_folder / "ports_circuit.json",
            apply_file=True,
            output_file=str(target_path_edb2),
            open_at_the_end=True,
        )
        assert edbapp.edbpath == str(target_path_edb2)
        assert edbapp.configuration.load(example_json_folder / "sources.json")
        edbapp.close()

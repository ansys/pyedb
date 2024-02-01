import os
from pathlib import Path
import sys

import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

# local_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(local_path)
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

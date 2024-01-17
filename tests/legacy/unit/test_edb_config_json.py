import os
import sys

import pytest

from pathlib import Path
from pyedb.legacy.edb import EdbLegacy
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

#local_path = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(local_path)
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

        self.local_scratch.copyfolder(str(example_edb), str(target_path_edb))

        edbapp = EdbLegacy(str(target_path_edb), desktop_version)
        edbapp.configuration.load(example_json_folder / "stackup.json")
        edbapp.configuration.load(example_json_folder / "components.json")
        edbapp.configuration.load(example_json_folder / "setups.json")

        edbapp.close()

import os
import time

import pytest

from pyedb.siwave import Siwave
from tests.conftest import desktop_version
from tests.conftest import local_path
pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_siwave(self):
        """Create Siwave."""
        siw = Siwave(desktop_version)
        time.sleep(10)
        example_project = os.path.join(local_path, "example_models", "siwave", "siw_dc.siw")
        target_path = os.path.join(self.local_scratch.path, "siw_dc.siw")
        self.local_scratch.copyfile(example_project, target_path)
        assert siw
        assert siw.close_project()
        siw.open_project(target_path)
        siw.oproject.ScrRunDcSimulation(1)
        export_report = os.path.join(siw.results_directory, "test.htm")
        assert siw.export_siwave_report("DC IR Sim 3", export_report)
        export_data = os.path.join(siw.results_directory, "test.txt")
        assert siw.export_element_data("DC IR Sim 3", export_data)
        assert siw.quit_application()

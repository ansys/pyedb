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
import time

import pytest

from pyedb.siwave import Siwave
from tests.conftest import desktop_version
from tests.conftest import local_path

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


@pytest.mark.skipif(True, reason="skipping test on CI because they fail in non-graphical")
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

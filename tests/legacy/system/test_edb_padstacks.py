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

"""Tests related to Edb padstacks
"""
import os

import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path3, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path3 = target_path3
        self.target_path4 = target_path4

    def test_padstaks_plot_on_matplotlib(self):
        """Plot a Net to Matplotlib 2D Chart."""
        edb_plot = Edb(self.target_path3, edbversion=desktop_version)

        local_png1 = os.path.join(self.local_scratch.path, "test1.png")
        edb_plot.nets.plot(
            nets=None,
            layers=None,
            save_plot=local_png1,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
            outline=[[-10e-3, -10e-3], [110e-3, -10e-3], [110e-3, 70e-3], [-10e-3, 70e-3]],
        )
        assert os.path.exists(local_png1)

        local_png2 = os.path.join(self.local_scratch.path, "test2.png")
        edb_plot.nets.plot(
            nets="V3P3_S5",
            layers=None,
            save_plot=local_png2,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
        )
        assert os.path.exists(local_png2)

        local_png3 = os.path.join(self.local_scratch.path, "test3.png")
        edb_plot.nets.plot(
            nets=["LVL_I2C_SCL", "V3P3_S5", "GATE_V5_USB"],
            layers="TOP",
            color_by_net=True,
            save_plot=local_png3,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
        )
        assert os.path.exists(local_png3)

        local_png4 = os.path.join(self.local_scratch.path, "test4.png")
        edb_plot.stackup.plot(
            save_plot=local_png4,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)

        local_png5 = os.path.join(self.local_scratch.path, "test5.png")
        edb_plot.stackup.plot(
            scale_elevation=False,
            save_plot=local_png5,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)
        edb_plot.close()

    def test_padstaks_plot_on_matplotlib(self):
        """Plot a Net to Matplotlib 2D Chart."""
        edb_plot = Edb(self.target_path3, edbversion=desktop_version)

        local_png4 = os.path.join(self.local_scratch.path, "test4.png")
        edb_plot.stackup.plot(
            save_plot=local_png4,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)

        local_png5 = os.path.join(self.local_scratch.path, "test5.png")
        edb_plot.stackup.plot(
            scale_elevation=False,
            save_plot=local_png5,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)
        edb_plot.close()

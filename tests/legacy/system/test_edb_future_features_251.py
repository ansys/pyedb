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

"""Tests related to Edb
"""

import pytest

pytestmark = [pytest.mark.system, pytest.mark.legacy]


@pytest.mark.skipif(True, reason="AEDT 2025.1 is not installed")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        pass

    def test_create_hfss_pi_setup(self, edb_examples):
        edbapp = edb_examples.get_si_verse(version=2025.1)
        setup = edbapp.create_hfsspi_setup("test")
        setup.add_frequency_sweep(frequency_sweep=["linear scale", "0.1GHz", "10GHz", "0.1GHz"])
        assert not setup.settings.auto_select_nets_for_simulation
        setup.settings.auto_select_nets_for_simulation = True
        assert setup.settings.auto_select_nets_for_simulation
        assert setup.settings.ignore_dummy_nets_for_selected_nets
        setup.settings.ignore_dummy_nets_for_selected_nets = False
        assert not setup.settings.ignore_dummy_nets_for_selected_nets
        assert setup.settings.ignore_small_holes == 0
        setup.settings.ignore_small_holes_min_diameter = 1e-3
        assert setup.settings.ignore_small_holes_min_diameter == "0.001"
        setup.settings.improved_loss_model = "Level2"
        assert setup.settings.improved_loss_model == "Level2"
        setup.settings.include_enhanced_bond_wire_modeling = True
        assert setup.settings.include_enhanced_bond_wire_modeling
        setup.settings.include_nets = "GND"
        assert setup.settings.include_nets[0] == "GND"
        setup.settings.min_plane_area_to_mesh = "0.30mm2"
        assert setup.settings.min_plane_area_to_mesh == "0.30mm2"
        setup.settings.min_void_area_to_mesh = "0.30mm2"
        assert setup.settings.min_void_area_to_mesh == "0.30mm2"
        setup.settings.model_type = 0
        assert setup.settings.model_type == 0
        setup.settings.perform_erc = True
        assert setup.settings.perform_erc
        setup.settings.pi_slider_pos = 1
        assert setup.settings.pi_slider_pos == 1
        setup.settings.rms_surface_roughness = "2um"
        assert setup.settings.rms_surface_roughness == "2um"
        setup.settings.signal_nets_conductor_modeling = "ImpedanceBoundary"
        assert setup.settings.signal_nets_conductor_modeling == "ImpedanceBoundary"
        setup.settings.signal_nets_error_tolerance = "0.02"
        assert setup.settings.signal_nets_error_tolerance == "0.02"
        setup.settings.signal_nets_include_improved_dielectric_fill_refinement = True
        assert setup.settings.signal_nets_include_improved_dielectric_fill_refinement
        setup.settings.signal_nets_include_improved_loss_handling = True
        assert setup.settings.signal_nets_include_improved_loss_handling
        setup.settings.snap_length_threshold = "5um"
        assert setup.settings.snap_length_threshold == "5um"
        setup.settings.surface_roughness_model = "Hammerstad"
        assert setup.settings.surface_roughness_model == "Hammerstad"

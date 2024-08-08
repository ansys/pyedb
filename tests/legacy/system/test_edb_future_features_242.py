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
VERSION = 2024.2


@pytest.mark.skipif(True, reason="AEDT 2024.2 is not installed")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        pass

    def test_add_raptorx_setup(self, edb_examples):
        edbapp = edb_examples.get_si_verse(version=VERSION)
        setup = edbapp.create_raptorx_setup("test")
        assert "test" in edbapp.setups
        setup.add_frequency_sweep(frequency_sweep=["linear scale", "0.1GHz", "10GHz", "0.1GHz"])
        setup.enabled = False
        assert not setup.enabled
        assert len(setup.frequency_sweeps) == 1
        general_settings = setup.settings.general_settings
        assert general_settings.global_temperature == 22.0
        general_settings.global_temperature = 35.0
        assert edbapp.setups["test"].settings.general_settings.global_temperature == 35.0
        assert general_settings.max_frequency == "10GHz"
        general_settings.max_frequency = 20e9
        assert general_settings.max_frequency == "20GHz"
        advanced_settings = setup.settings.advanced_settings
        assert advanced_settings.auto_removal_sliver_poly == 0.001
        advanced_settings.auto_removal_sliver_poly = 0.002
        assert advanced_settings.auto_removal_sliver_poly == 0.002
        assert advanced_settings.cell_per_wave_length == 80
        advanced_settings.cell_per_wave_length = 60
        assert advanced_settings.cell_per_wave_length == 60
        assert advanced_settings.edge_mesh == "0.8um"
        advanced_settings.edge_mesh = "1um"
        assert advanced_settings.edge_mesh == "1um"
        assert advanced_settings.eliminate_slit_per_hole == 5.0
        advanced_settings.eliminate_slit_per_hole = 4.0
        assert advanced_settings.eliminate_slit_per_hole == 4.0
        assert advanced_settings.mesh_frequency == "1GHz"
        advanced_settings.mesh_frequency = "5GHz"
        assert advanced_settings.mesh_frequency == "5GHz"
        assert advanced_settings.override_shrink_fac == 1.0
        advanced_settings.override_shrink_fac = 1.5
        assert advanced_settings.override_shrink_fac == 1.5
        assert advanced_settings.plane_projection_factor == 1.0
        advanced_settings.plane_projection_factor = 1.4
        assert advanced_settings.plane_projection_factor == 1.4
        assert advanced_settings.use_accelerate_via_extraction
        advanced_settings.use_accelerate_via_extraction = False
        assert not advanced_settings.use_accelerate_via_extraction
        assert not advanced_settings.use_auto_removal_sliver_poly
        advanced_settings.use_auto_removal_sliver_poly = True
        assert advanced_settings.use_auto_removal_sliver_poly
        assert not advanced_settings.use_cells_per_wavelength
        advanced_settings.use_cells_per_wavelength = True
        assert advanced_settings.use_cells_per_wavelength
        assert not advanced_settings.use_edge_mesh
        advanced_settings.use_edge_mesh = True
        assert advanced_settings.use_edge_mesh
        assert not advanced_settings.use_eliminate_slit_per_holes
        advanced_settings.use_eliminate_slit_per_holes = True
        assert advanced_settings.use_eliminate_slit_per_holes
        assert not advanced_settings.use_enable_advanced_cap_effects
        advanced_settings.use_enable_advanced_cap_effects = True
        assert advanced_settings.use_enable_advanced_cap_effects
        assert not advanced_settings.use_enable_etch_transform
        advanced_settings.use_enable_etch_transform = True
        assert advanced_settings.use_enable_etch_transform
        assert advanced_settings.use_enable_substrate_network_extraction
        advanced_settings.use_enable_substrate_network_extraction = False
        assert not advanced_settings.use_enable_substrate_network_extraction
        assert not advanced_settings.use_extract_floating_metals_dummy
        advanced_settings.use_extract_floating_metals_dummy = True
        assert advanced_settings.use_extract_floating_metals_dummy
        assert advanced_settings.use_extract_floating_metals_floating
        advanced_settings.use_extract_floating_metals_floating = False
        assert not advanced_settings.use_extract_floating_metals_floating
        assert not advanced_settings.use_lde
        advanced_settings.use_lde = True
        assert advanced_settings.use_lde
        assert not advanced_settings.use_mesh_frequency
        advanced_settings.use_mesh_frequency = True
        assert advanced_settings.use_mesh_frequency
        assert not advanced_settings.use_override_shrink_fac
        advanced_settings.use_override_shrink_fac = True
        assert advanced_settings.use_override_shrink_fac
        assert advanced_settings.use_plane_projection_factor
        advanced_settings.use_plane_projection_factor = False
        assert not advanced_settings.use_plane_projection_factor
        assert not advanced_settings.use_relaxed_z_axis
        advanced_settings.use_relaxed_z_axis = True
        assert advanced_settings.use_relaxed_z_axis
        edbapp.close()

    def test_create_hfss_pi_setup(self, edb_examples):
        edbapp = edb_examples.get_si_verse(version=VERSION)
        setup = edbapp.create_hfsspi_setup("test")
        assert setup.get_simulation_settings()
        settings = {
            "auto_select_nets_for_simulation": True,
            "ignore_dummy_nets_for_selected_nets": False,
            "ignore_small_holes": 1,
            "ignore_small_holes_min_diameter": 1,
            "improved_loss_model": 2,
            "include_enhanced_bond_wire_modeling": True,
            "include_nets": ["GND"],
            "min_plane_area_to_mesh": "0.2mm2",
            "min_void_area_to_mesh": "0.02mm2",
            "model_type": 2,
            "perform_erc": True,
            "pi_slider_pos": 1,
            "rms_surface_roughness": "1",
            "signal_nets_conductor_modeling": 1,
            "signal_nets_error_tolerance": 0.02,
            "signal_nets_include_improved_dielectric_fill_refinement": True,
            "signal_nets_include_improved_loss_handling": True,
            "snap_length_threshold": "2.6um",
            "surface_roughness_model": 1,
        }
        setup.set_simulation_settings(settings)
        settings_get = edbapp.setups["test"].get_simulation_settings()
        for k, v in settings.items():
            assert settings[k] == settings_get[k]

    def test_create_hfss_pi_setup_add_sweep(self, edb_examples):
        edbapp = edb_examples.get_si_verse(version=VERSION)
        setup = edbapp.create_hfsspi_setup("test")
        setup.add_sweep(name="sweep1", frequency_sweep=["linear scale", "0.1GHz", "10GHz", "0.1GHz"])
        assert setup.sweeps["sweep1"].frequencies
        edbapp.setups["test"].sweeps["sweep1"].adaptive_sampling = True

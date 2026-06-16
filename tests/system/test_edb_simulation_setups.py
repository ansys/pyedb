# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Tests related to Edb simulation setups (HFSS, SIWave, RaptorX, Q3D)."""

import pytest

from pyedb.generic.general_methods import is_linux
from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_siwave_add_syz_analysis(self):
        """Add a SIWave AC analysis."""
        edbapp = self.edb_examples.get_si_verse()
        syz_setup = edbapp.siwave.add_siwave_syz_analysis(start_freq="1GHz", stop_freq="10GHz", step_freq="10MHz")
        syz_setup.use_custom_settings = False
        assert not syz_setup.use_custom_settings
        syz_setup.settings.advanced.min_void_area = "4mm2"
        assert syz_setup.settings.advanced.min_void_area == 4e-06
        syz_setup.mesh_automatic = True
        assert syz_setup.mesh_automatic
        syz_setup.dc_min_plane_area_to_mesh = "0.5mm2"
        assert syz_setup.dc_min_plane_area_to_mesh == "0.5mm2"
        syz_setup.settings.dc.use_dc_custom_settings = False
        assert not syz_setup.settings.dc.use_dc_custom_settings
        syz_sweep = syz_setup.add_sweep()
        syz_sweep.enforce_causality = False
        assert not syz_sweep.enforce_causality
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_add_dc_analysis(self):
        """Add a SIWave DC analysis."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
        edbapp.close(terminate_rpc_session=False)

    def test_hfss_mesh_operations(self):
        """Retrieve the trace width for traces with ports."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.excitation_manager.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type="circuit_port",
        )
        mesh_ops = edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0
        edbapp.close(terminate_rpc_session=False)

    def test_configure_hfss_analysis_setup_enforce_causality(self):
        """Configure HFSS analysis setup enforce causality."""
        edb = self.edb_examples.get_si_verse()
        assert len(edb.setups) == 0
        edb.hfss.add_setup()
        assert edb.hfss_setups
        assert len(edb.setups) == 1
        assert list(edb.setups)[0]
        setup = list(edb.hfss_setups.values())[0]
        # testing DotNet adaptive path compatibility with grpc
        assert setup.settings.general.adaptive_solution_type
        setup.add_sweep()
        assert not setup.sweep_data[0].enforce_causality
        sweeps = setup.sweep_data
        for sweep in sweeps:
            sweep.enforce_causality = True
        setup.sweep_data = sweeps
        assert setup.sweep_data[0].enforce_causality
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"] and is_linux, reason="Crash on DotNet and gRPC on Linux.")
    def test_hfss_simulation_setup(self):
        """Create a setup from a template and evaluate its properties."""
        edbapp = self.edb_examples.get_si_verse()
        setup1 = edbapp.hfss.add_setup("setup1")
        assert setup1.set_solution_single_frequency()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "single"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 1
        assert setup1.set_solution_multi_frequencies(frequencies=("5GHz", "10GHz", "100GHz"))
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "multi_frequencies"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 3
        assert setup1.set_solution_broadband()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "broadband"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 2
        setup1.hfss_solver_settings.enhanced_low_frequency_accuracy = True
        assert setup1.hfss_solver_settings.enhanced_low_frequency_accuracy
        setup1.hfss_solver_settings.relative_residual = 0.0002
        assert setup1.hfss_solver_settings.relative_residual == 0.0002
        setup1.hfss_solver_settings.use_shell_elements = True
        assert setup1.hfss_solver_settings.use_shell_elements

        setup1 = edbapp.setups["setup1"]
        assert not setup1.is_null
        setup1.adaptive_settings.max_refine_per_pass = 20
        assert setup1.adaptive_settings.max_refine_per_pass == 20
        setup1.adaptive_settings.min_passes = 2
        assert setup1.adaptive_settings.min_passes == 2
        setup1.adaptive_settings.save_fields = True
        assert setup1.adaptive_settings.save_fields
        setup1.adaptive_settings.save_rad_field_only = True
        assert setup1.adaptive_settings.save_rad_field_only
        assert edbapp.setups["setup1"].adaptive_settings.adapt_type in ["kBroadband", "broadband"]
        edbapp.setups["setup1"].adaptive_settings.use_max_refinement = True
        assert edbapp.setups["setup1"].adaptive_settings.use_max_refinement
        edbapp.setups["setup1"].defeature_settings.defeature_abs_length = "1um"
        assert edbapp.setups["setup1"].defeature_settings.defeature_abs_length == "1um"
        edbapp.setups["setup1"].defeature_settings.defeature_ratio = 1e-5
        assert edbapp.setups["setup1"].defeature_settings.defeature_ratio == 1e-5
        edbapp.setups["setup1"].defeature_settings.healing_option = 0
        assert edbapp.setups["setup1"].defeature_settings.healing_option == 0
        edbapp.setups["setup1"].defeature_settings.remove_floating_geometry = True
        assert edbapp.setups["setup1"].defeature_settings.remove_floating_geometry
        edbapp.setups["setup1"].defeature_settings.small_void_area = "40000um2"
        assert edbapp.setups["setup1"].defeature_settings.small_void_area == 4e-8
        edbapp.setups["setup1"].defeature_settings.union_polygons = False
        assert not edbapp.setups["setup1"].defeature_settings.union_polygons
        edbapp.setups["setup1"].defeature_settings.use_defeature = False
        assert not edbapp.setups["setup1"].defeature_settings.use_defeature
        edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length = True
        assert edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length
        edbapp.setups["setup1"].via_settings.via_density = 1.0
        assert edbapp.setups["setup1"].via_settings.via_density == 1.0
        edbapp.setups["setup1"].via_settings.via_material = "pec"
        assert edbapp.setups["setup1"].via_settings.via_material == "pec"
        edbapp.setups["setup1"].via_settings.via_num_sides = 8
        assert edbapp.setups["setup1"].via_settings.via_num_sides == 8
        assert edbapp.setups["setup1"].via_settings.via_style in ["k25DViaWirebond", "mesh"]
        edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol = "1e-6"
        assert edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol == "1e-6"
        edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error = "0.1"
        assert edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error == "0.1"
        edbapp.setups["setup1"].curve_approx_settings.max_arc_points = 12
        assert edbapp.setups["setup1"].curve_approx_settings.max_arc_points == 12
        edbapp.setups["setup1"].dcr_settings.conduction_max_passes = 11
        assert edbapp.setups["setup1"].dcr_settings.conduction_max_passes == 11
        edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes = 2
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes == 2
        edbapp.setups["setup1"].dcr_settings.conduction_min_passes = 5
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_passes == 5
        edbapp.setups["setup1"].dcr_settings.conduction_per_error = 2.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_error == 2.0
        edbapp.setups["setup1"].dcr_settings.conduction_per_refine = 20.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_refine == 20.0
        edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 = 0.5
        assert edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 == 0.5
        edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port = 1000
        assert edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port == 1000
        edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port = 500
        assert edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port == 500
        edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port = True
        assert edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"] and is_linux, reason="Crash on DotNet and gRPC on Linux.")
    def test_hfss_simulation_setups_consolidation(self):
        """Create a setup from a template and evaluate settings consolidation."""
        edbapp = self.edb_examples.get_si_verse()
        setup1 = edbapp.hfss.add_setup("setup1")
        assert setup1.set_solution_single_frequency()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "single"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 1
        assert setup1.set_solution_multi_frequencies(frequencies=("5GHz", "10GHz", "100GHz"))
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "multi_frequencies"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 3
        assert setup1.set_solution_broadband()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "broadband"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 2
        setup1.hfss_solver_settings.enhanced_low_frequency_accuracy = True
        assert setup1.hfss_solver_settings.enhanced_low_frequency_accuracy
        setup1.hfss_solver_settings.relative_residual = 0.0002
        assert setup1.hfss_solver_settings.relative_residual == 0.0002
        setup1.hfss_solver_settings.use_shell_elements = True
        assert setup1.hfss_solver_settings.use_shell_elements

        setup1 = edbapp.setups["setup1"]
        setup1.adaptive_settings.max_refine_per_pass = 20
        assert setup1.adaptive_settings.max_refine_per_pass == 20
        setup1.adaptive_settings.min_passes = 2
        assert setup1.adaptive_settings.min_passes == 2
        setup1.adaptive_settings.save_fields = True
        assert setup1.adaptive_settings.save_fields
        setup1.adaptive_settings.save_rad_field_only = True
        assert setup1.adaptive_settings.save_rad_field_only
        assert edbapp.setups["setup1"].adaptive_settings.adapt_type in ["kBroadband", "broadband"]
        edbapp.setups["setup1"].adaptive_settings.use_max_refinement = True
        assert edbapp.setups["setup1"].adaptive_settings.use_max_refinement
        edbapp.setups["setup1"].defeature_settings.defeature_abs_length = "1um"
        assert edbapp.setups["setup1"].defeature_settings.defeature_abs_length == "1um"
        edbapp.setups["setup1"].defeature_settings.defeature_ratio = 1e-5
        assert edbapp.setups["setup1"].defeature_settings.defeature_ratio == 1e-5
        edbapp.setups["setup1"].defeature_settings.healing_option = 0
        assert edbapp.setups["setup1"].defeature_settings.healing_option == 0
        edbapp.setups["setup1"].defeature_settings.remove_floating_geometry = True
        assert edbapp.setups["setup1"].defeature_settings.remove_floating_geometry
        edbapp.setups["setup1"].defeature_settings.small_void_area = 0.1
        assert edbapp.setups["setup1"].defeature_settings.small_void_area == 0.1
        edbapp.setups["setup1"].defeature_settings.union_polygons = False
        assert not edbapp.setups["setup1"].defeature_settings.union_polygons
        edbapp.setups["setup1"].defeature_settings.use_defeature = False
        assert not edbapp.setups["setup1"].defeature_settings.use_defeature
        edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length = True
        assert edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length
        edbapp.setups["setup1"].via_settings.via_density = 1.0
        assert edbapp.setups["setup1"].via_settings.via_density == 1.0
        edbapp.setups["setup1"].via_settings.via_material = "pec"
        assert edbapp.setups["setup1"].via_settings.via_material == "pec"
        edbapp.setups["setup1"].via_settings.via_num_sides = 8
        assert edbapp.setups["setup1"].via_settings.via_num_sides == 8
        assert edbapp.setups["setup1"].via_settings.via_style in ["k25DViaWirebond", "mesh"]
        edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol = "1e-6"
        assert edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol == "1e-6"
        edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error = "0.1"
        assert edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error == "0.1"
        edbapp.setups["setup1"].curve_approx_settings.max_arc_points = 12
        assert edbapp.setups["setup1"].curve_approx_settings.max_arc_points == 12
        edbapp.setups["setup1"].dcr_settings.conduction_max_passes = 11
        assert edbapp.setups["setup1"].dcr_settings.conduction_max_passes == 11
        edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes = 2
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes == 2
        edbapp.setups["setup1"].dcr_settings.conduction_min_passes = 5
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_passes == 5
        edbapp.setups["setup1"].dcr_settings.conduction_per_error = 2.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_error == 2.0
        edbapp.setups["setup1"].dcr_settings.conduction_per_refine = 20.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_refine == 20.0
        edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 = 0.5
        assert edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 == 0.5
        edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port = 1000
        assert edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port == 1000
        edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port = 500
        assert edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port == 500
        edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port = True
        assert edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port
        edbapp.close(terminate_rpc_session=False)

    def test_siwaves_simulation_setups_consolidation(self):
        """Create a SIWave setup and evaluate all settings consolidation."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_setup()
        setup = edbapp.setups[setup.name]
        setup.name = "test_siwave_setup"

        # Advanced settings
        adv_settings = setup.settings.advanced
        adv_settings.cross_talk_threshold = -60
        assert adv_settings.cross_talk_threshold == -60
        adv_settings.ignore_non_functional_pads = False
        assert not adv_settings.ignore_non_functional_pads
        adv_settings.include_co_plane_coupling = False
        assert not adv_settings.include_co_plane_coupling
        adv_settings.include_fringe_plane_coupling = False
        assert not adv_settings.include_fringe_plane_coupling
        adv_settings.include_inf_gnd = True
        assert adv_settings.include_inf_gnd
        adv_settings.include_inter_plane_coupling = True
        assert adv_settings.include_inter_plane_coupling
        adv_settings.include_split_plane_coupling = False
        assert not adv_settings.include_split_plane_coupling
        adv_settings.inf_gnd_location = 1e-3
        assert adv_settings.inf_gnd_location == 1e-3
        adv_settings.mesh_automatic = False
        assert not adv_settings.mesh_automatic
        adv_settings.mesh_frequency = 30e9
        assert adv_settings.mesh_frequency == 30e9
        adv_settings.min_pad_area_to_mesh = 1e-5
        assert adv_settings.min_pad_area_to_mesh == 1e-5
        adv_settings.min_plane_area_to_mesh = 1e-5
        assert adv_settings.min_plane_area_to_mesh == 1e-5
        adv_settings.min_void_area = 3e-06
        assert adv_settings.min_void_area == 3e-06
        adv_settings.perform_erc = True
        assert adv_settings.perform_erc
        adv_settings.return_current_distribution = True
        assert adv_settings.return_current_distribution
        adv_settings.snap_length_threshold = 30e-6
        assert adv_settings.snap_length_threshold == 30e-6

        # DC settings
        dc = setup.settings.dc
        dc.compute_inductance = True
        assert dc.compute_inductance
        dc.contact_radius = "1mm"
        assert dc.contact_radius == "1mm"
        dc.dc_slider_position = 2
        assert dc.dc_slider_position == 2
        dc.plot_jv = False
        assert not dc.plot_jv
        dc.use_dc_custom_settings = True
        assert dc.use_dc_custom_settings

        # DC advanced
        dc_adv = setup.settings.dc_advanced
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        assert dc_adv.dc_min_plane_area_to_mesh == "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        dc_adv.energy_error = 1.5
        assert dc_adv.energy_error == 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        dc_adv.max_num_passes = 10
        assert dc_adv.max_num_passes == 10
        dc_adv.mesh_bws = False
        assert not dc_adv.mesh_bws
        dc_adv.mesh_vias = False
        assert not dc_adv.mesh_vias
        dc_adv.min_num_passes = 5
        assert dc_adv.min_num_passes == 5
        dc_adv.num_bw_sides = 12
        assert dc_adv.num_bw_sides == 12
        dc_adv.num_via_sides = 12
        assert dc_adv.num_via_sides == 12
        dc_adv.percent_local_refinement = 30
        assert dc_adv.percent_local_refinement == 30
        dc_adv.refine_bws = True
        assert dc_adv.refine_bws
        dc_adv.refine_vias = True
        assert dc_adv.refine_vias

        # General
        general = setup.settings.general
        general.pi_slider_position = 0
        assert general.pi_slider_position == 0
        general.si_slider_position = 2
        assert general.si_slider_position == 2
        general.use_custom_settings = True
        assert general.use_custom_settings
        general.use_si_settings = False
        assert not general.use_si_settings

        # S-parameters
        sp = setup.settings.s_parameter
        sp.dc_behavior = "zero"
        assert sp.dc_behavior == "zero"
        sp.extrapolation = "same"
        assert sp.extrapolation == "same"
        sp.interpolation = "point"
        assert sp.interpolation == "point"
        sp.use_state_space = False
        assert not sp.use_state_space

        assert setup.name == "test_siwave_setup"
        edbapp.close(terminate_rpc_session=False)

    def test_siwaves_dcir_simulation_setups_consolidation(self):
        """Create a SIWave DCIR setup and evaluate all settings."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_dcir_setup()
        setup.name = "test_siwave_dcir_setup"
        assert setup.name == "test_siwave_dcir_setup"

        # DC settings
        dc = setup.settings.dc
        dc.compute_inductance = True
        assert dc.compute_inductance
        dc.contact_radius = "1mm"
        assert dc.contact_radius == "1mm"
        dc.dc_report_config_file = "custom_dc_report.cfg"
        assert dc.dc_report_config_file == "custom_dc_report.cfg"
        dc.dc_slider_position = 2
        assert dc.dc_slider_position == 2
        dc.export_dc_thermal_data = True
        assert dc.export_dc_thermal_data
        dc.full_dc_report_path = "full_dc_report.txt"
        assert dc.full_dc_report_path == "full_dc_report.txt"
        dc.icepak_temp_file = "icepak_temp_file.txt"
        assert dc.icepak_temp_file == "icepak_temp_file.txt"
        dc.import_thermal_data = True
        assert dc.import_thermal_data
        dc.per_pin_res_path = "per_pin_res.txt"
        assert dc.per_pin_res_path == "per_pin_res.txt"
        dc.per_pin_use_pin_format = True
        assert dc.per_pin_use_pin_format
        dc.plot_jv = False
        assert not dc.plot_jv
        dc.source_terms_to_ground = {"gnd": 1}
        assert dc.source_terms_to_ground == {"gnd": 1}
        dc.use_dc_custom_settings = True
        assert dc.use_dc_custom_settings
        dc.use_loop_res_for_per_pin = True
        assert dc.use_loop_res_for_per_pin
        dc.via_report_path = "via_report.txt"
        assert dc.via_report_path == "via_report.txt"

        # DC advanced
        dc_adv = setup.settings.dc_advanced
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        assert dc_adv.dc_min_plane_area_to_mesh == "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        dc_adv.energy_error = 1.5
        assert dc_adv.energy_error == 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        dc_adv.max_num_passes = 10
        assert dc_adv.max_num_passes == 10
        dc_adv.mesh_bws = False
        assert not dc_adv.mesh_bws
        dc_adv.mesh_vias = False
        assert not dc_adv.mesh_vias
        dc_adv.min_num_passes = 5
        assert dc_adv.min_num_passes == 5
        dc_adv.num_bw_sides = 12
        assert dc_adv.num_bw_sides == 12
        dc_adv.num_via_sides = 12
        assert dc_adv.num_via_sides == 12
        dc_adv.percent_local_refinement = 30
        assert dc_adv.percent_local_refinement == 30
        dc_adv.refine_bws = True
        assert dc_adv.refine_bws
        dc_adv.refine_vias = True
        assert dc_adv.refine_vias

        # General (for DCIR setups, proxies to DC settings for backward compat)
        general = setup.settings.general
        general.compute_inductance = True
        assert general.compute_inductance
        general.contact_radius = "0.5mm"
        assert general.contact_radius == "0.5mm"
        general.dc_slider_position = 1
        assert general.dc_slider_position == 1
        general.plot_jv = True
        assert general.plot_jv
        general.use_dc_custom_settings = False
        assert not general.use_dc_custom_settings
        edbapp.close(terminate_rpc_session=False)

    def test_raptor_x_simulation_setups_consolidation(self):
        """Create a RaptorX setup and evaluate all settings."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_raptor_x_setup(name="test_raptorx_setup")
        setup.name = "test_raptorx_setup"
        assert setup.name == "test_raptorx_setup"
        assert not setup.sweep_data

        # Advanced general settings
        adv_settings = setup.settings.advanced
        adv_settings.auto_removal_sliver_poly = 1e-2
        assert adv_settings.auto_removal_sliver_poly == 1e-2
        adv_settings.cells_per_wavelength = 60
        assert adv_settings.cells_per_wavelength == 60
        adv_settings.defuse_enable_hybrid_extraction = True
        assert adv_settings.defuse_enable_hybrid_extraction
        adv_settings.edge_mesh = 1e-6
        assert adv_settings.edge_mesh == 1e-6
        adv_settings.eliminate_slit_per_holes = 2.0
        assert adv_settings.eliminate_slit_per_holes == 2.0
        adv_settings.mesh_bws = 25e9
        assert adv_settings.mesh_bws == 25e9
        if config["use_grpc"]:
            adv_settings.net_settings_options = {"VDD": ["mesh_vias", "via_diameter"]}
            assert adv_settings.net_settings_options == {"VDD": ["mesh_vias", "via_diameter"]}
        adv_settings.override_shrink_factor = 2.0
        assert adv_settings.override_shrink_factor == 2.0
        adv_settings.plane_projection_factor = 2.0
        assert adv_settings.plane_projection_factor == 2.0
        adv_settings.use_accelerate_via_extraction = False
        assert not adv_settings.use_accelerate_via_extraction
        adv_settings.use_auto_removal_sliver_poly = True
        assert adv_settings.use_auto_removal_sliver_poly
        adv_settings.use_cells_per_wavelength = True
        assert adv_settings.use_cells_per_wavelength
        adv_settings.use_edge_mesh = True
        assert adv_settings.use_edge_mesh
        adv_settings.use_eliminate_slit_per_holes = True
        assert adv_settings.use_eliminate_slit_per_holes
        adv_settings.use_enable_advanced_cap_effects = True
        assert adv_settings.use_enable_advanced_cap_effects
        adv_settings.use_enable_etch_transform = True
        assert adv_settings.use_enable_etch_transform
        adv_settings.use_enable_substrate_network_extraction = False
        assert not adv_settings.use_enable_substrate_network_extraction
        adv_settings.use_extract_floating_metals_floating = False
        assert not adv_settings.use_extract_floating_metals_floating
        adv_settings.use_extract_floating_metals_dummy = True
        assert adv_settings.use_extract_floating_metals_dummy
        adv_settings.use_lde = True
        assert adv_settings.use_lde
        adv_settings.use_mesh_frequency = True
        assert adv_settings.use_mesh_frequency
        adv_settings.use_overwrite_shrink_factor = True
        assert adv_settings.use_overwrite_shrink_factor
        adv_settings.use_relaxed_z_axis = True
        assert adv_settings.use_relaxed_z_axis

        # General settings
        general = setup.settings.general
        general.global_temperature = 30.0
        assert general.global_temperature == 30.0
        general.max_frequency = 35e9
        assert general.max_frequency == 35e9
        general.netlist_export_spectre = True
        assert general.netlist_export_spectre
        general.save_netlist = True
        assert general.save_netlist
        general.save_rfm = True
        assert general.save_rfm
        general.use_gold_em_solver = True
        assert general.use_gold_em_solver
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="issue #1860. Missing create_q3d_setup in dotnet")
    def test_q3d_simulation_setups_consolidation(self):
        """Create a Q3D setup and evaluate all settings."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_q3d_setup()
        assert not setup.is_null
        setup.name = "test_q3d_setup"
        assert setup.name == "test_q3d_setup"
        assert setup.setup_type == "q3d"

        # ACRL settings
        acrl = setup.settings.acrl
        acrl.max_frequency = 20
        assert acrl.max_frequency == 20
        acrl.max_refine_per_pass = 25
        assert acrl.max_refine_per_pass == 25
        acrl.min_converged_passes = 2
        assert acrl.min_converged_passes == 2
        acrl.min_passes = 2
        assert acrl.min_passes == 2
        acrl.percent_error = 0.5
        assert acrl.percent_error == 0.5

        # Advanced meshing settings
        adv_mesh = setup.settings.advanced_meshing
        adv_mesh.arc_step_size = 0.2
        assert adv_mesh.arc_step_size == 0.2
        adv_mesh.arc_to_chord_error = 1e-6
        assert adv_mesh.arc_to_chord_error == 1e-6
        adv_mesh.circle_start_azimuth = 15
        assert adv_mesh.circle_start_azimuth == 15
        adv_mesh.max_num_arc_points = 6
        assert adv_mesh.max_num_arc_points == 6
        adv_mesh.use_arc_chord_error_approx = True
        assert adv_mesh.use_arc_chord_error_approx

        # CG settings
        cg = setup.settings.cg
        cg.compression_tol = 1e-6
        assert cg.compression_tol == 1e-6
        cg.max_passes = 20
        assert cg.max_passes == 20
        cg.max_refine_per_pass = 20
        assert cg.max_refine_per_pass == 20
        cg.min_converged_passes = 2
        assert cg.min_converged_passes == 2
        cg.min_passes = 2
        assert cg.min_passes == 2
        cg.percent_error = 0.5
        assert cg.percent_error == 0.5
        cg.solution_order = "higher"
        assert cg.solution_order == "higher"

        # DCRL settings
        dcrl = setup.settings.dcrl
        dcrl.max_passes = 20
        assert dcrl.max_passes == 20
        dcrl.max_refine_per_pass = 20
        assert dcrl.max_refine_per_pass == 20
        dcrl.min_converged_passes = 2
        assert dcrl.min_converged_passes == 2
        dcrl.min_passes = 2
        assert dcrl.min_passes == 2
        dcrl.percent_error = 0.5
        assert dcrl.percent_error == 0.5
        dcrl.solution_order = "higher"
        assert dcrl.solution_order == "higher"

        # General settings
        general = setup.settings.general
        general.do_ac = True
        assert general.do_ac
        general.do_cg = True
        assert general.do_cg
        general.do_dc = False
        assert not general.do_dc
        general.do_dc_res_only = True
        assert general.do_dc_res_only
        general.save_netlist = True
        assert general.save_netlist
        general.solution_frequency = 20e9
        assert general.solution_frequency == 20e9
        edbapp.close(terminate_rpc_session=False)

    def test_sweep(self):
        """Create a sweep and evaluate its properties."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_hfss_setup(
            name="test_hfss_setup", distribution="log_scale", start_freq="0GHz", stop_freq="1GHz", freq_step="10"
        )
        sweep = setup.sweep_data[0]
        sweep.compute_dc_point = True
        assert sweep.compute_dc_point
        sweep.enabled = False
        assert not sweep.enabled
        sweep.enabled = True
        sweep.enforce_causality = True
        sweep.enforce_passivity = False
        assert not sweep.enforce_passivity
        assert sweep.frequency_string in [["DEC 0.0GHz 1.0GHz 10"], ["DEC 0GHz 1GHz 10"]]
        sweep.name = "renamed_sweep"
        assert sweep.name == "renamed_sweep"
        sweep.save_fields = True
        assert sweep.save_fields
        sweep.save_rad_fields_only = True
        assert sweep.save_rad_fields_only
        sweep.type = "discrete"
        assert sweep.type == "discrete"
        sweep.use_hfss_solver_regions = True
        assert sweep.use_hfss_solver_regions
        sweep.use_q3d_for_dc = True
        assert sweep.use_q3d_for_dc
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(is_linux and not config["use_grpc"], reason="Randomly fails on linux dotnet")
    def test_siwave_simulation_setup_dotnet_compatibility(self):
        """Validate SIWave DCIR setup settings attribute compatibility."""
        edbapp = self.edb_examples.get_si_verse()
        setup = edbapp.simulation_setups.create_siwave_dcir_setup("setup_1")

        settings = setup.settings
        if not config["use_grpc"]:
            assert hasattr(settings, "dc_report_show_active_devices")
            assert hasattr(settings, "dc_report_config_file")
            assert hasattr(settings, "enabled")
            assert hasattr(settings, "icepak_temp_file")
            assert hasattr(settings, "import_thermal_data")
            assert hasattr(settings, "per_pin_res_path")
            assert hasattr(settings, "per_pin_use_pin_format")
            assert hasattr(settings, "via_report_path")
            assert hasattr(settings, "use_loop_res_for_per_pin")
            assert hasattr(settings, "export_dc_thermal_data")
            assert hasattr(settings, "full_dc_report_path")
            assert hasattr(settings, "use_loop_res_for_per_pin")
            assert hasattr(settings, "add_source_terminal_to_ground")

        settings.dc_report_show_active_devices = True
        settings.dc_report_config_file = "custom_dc_report.cfg"
        settings.enabled = False
        settings.enabled = True
        settings.icepak_temp_file = "icepak_temp_file.txt"
        settings.import_thermal_data = True
        settings.per_pin_res_path = "per_pin_res.txt"
        settings.per_pin_use_pin_format = True
        settings.via_report_path = "via_report.txt"
        settings.use_loop_res_for_per_pin = False
        settings.export_dc_thermal_data = True
        settings.full_dc_report_path = "full_dc_report.txt"
        settings.use_loop_res_for_per_pin = True
        settings.add_source_terminal_to_ground("test", 1)

        if config["use_grpc"]:
            setup_2 = edbapp.simulation_setups.setups["setup_1"]
        else:
            setup_2 = setup
        assert setup_2.settings.use_loop_res_for_per_pin
        assert setup_2.settings.dc_report_show_active_devices
        assert setup_2.settings.dc_report_config_file == "custom_dc_report.cfg"
        assert setup_2.settings.enabled
        assert setup_2.settings.icepak_temp_file == "icepak_temp_file.txt"
        assert setup_2.settings.import_thermal_data
        assert setup_2.settings.per_pin_res_path == "per_pin_res.txt"
        assert setup_2.settings.per_pin_use_pin_format
        assert setup_2.settings.via_report_path == "via_report.txt"
        assert setup_2.settings.export_dc_thermal_data
        assert setup_2.settings.full_dc_report_path == "full_dc_report.txt"
        assert settings.source_terms_to_ground["test"] == 1

        # DC settings
        dc = settings.dc
        if not config["use_grpc"]:
            assert hasattr(dc, "compute_inductance")
            assert hasattr(dc, "contact_radius")
            assert hasattr(dc, "dc_slider_position")
            assert hasattr(dc, "plot_jv")
        dc.compute_inductance = True
        dc.contact_radius = "1mm"
        dc.dc_slider_position = 0
        dc.plot_jv = False

        if config["use_grpc"]:
            setup_2 = edbapp.simulation_setups.setups["setup_1"]
        else:
            setup_2 = setup
        assert setup_2.settings.dc.compute_inductance
        assert setup_2.settings.dc.contact_radius == "1mm"
        assert setup_2.settings.dc.dc_slider_position == 0
        assert not setup_2.settings.dc.plot_jv

        # DC advanced settings
        dc_adv = settings.dc_advanced
        if not config["use_grpc"]:
            assert hasattr(dc_adv, "dc_min_plane_area_to_mesh")
            assert hasattr(dc_adv, "dc_min_void_area_to_mesh")
            assert hasattr(dc_adv, "energy_error")
            assert hasattr(dc_adv, "max_init_mesh_edge_length")
            assert hasattr(dc_adv, "max_num_passes")
            assert hasattr(dc_adv, "mesh_bondwires")
            assert hasattr(dc_adv, "mesh_vias")
            assert hasattr(dc_adv, "min_num_passes")
            assert hasattr(dc_adv, "num_bondwire_sides")
            assert hasattr(dc_adv, "num_via_sides")
            assert hasattr(dc_adv, "percent_local_refinement")
            assert hasattr(dc_adv, "refine_bondwires")
            assert hasattr(dc_adv, "refine_vias")
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        dc_adv.energy_error = 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        dc_adv.max_num_passes = 10
        dc_adv.mesh_bondwires = False
        dc_adv.mesh_vias = False
        dc_adv.min_num_passes = 5
        dc_adv.num_bondwire_sides = 12
        dc_adv.num_via_sides = 12
        dc_adv.percent_local_refinement = 30
        dc_adv.refine_bondwires = True
        dc_adv.refine_vias = True

        if config["use_grpc"]:
            setup_2 = edbapp.simulation_setups.setups["setup_1"]
        else:
            setup_2 = setup
        assert setup_2.settings.dc_advanced.dc_min_plane_area_to_mesh == "0.30mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        assert dc_adv.energy_error == 1.5
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        assert dc_adv.max_num_passes == 10
        assert not dc_adv.mesh_bondwires
        assert not dc_adv.mesh_vias
        assert dc_adv.min_num_passes == 5
        assert dc_adv.num_bondwire_sides == 12
        assert dc_adv.num_via_sides == 12
        assert dc_adv.percent_local_refinement == 30
        assert dc_adv.refine_bondwires
        assert dc_adv.refine_vias

        # General settings (backward compat)
        general = settings.general
        general.pi_slider_position = 0
        general.si_slider_position = 0
        general.use_custom_settings = False
        general.use_si_settings = False

        if config["use_grpc"]:
            setup_2 = edbapp.simulation_setups.setups["setup_1"]
        else:
            setup_2 = setup
        assert setup_2.settings.general.pi_slider_position == 0
        assert setup_2.settings.general.si_slider_position == 0
        assert not setup_2.settings.general.use_custom_settings
        assert not setup_2.settings.general.use_si_settings

        if config["use_grpc"]:
            setup_2 = edbapp.simulation_setups.setups["setup_1"]
        else:
            setup_2 = setup
        assert "pi_slider_position", "si_slider_position" in setup_2.get_configurations().items()
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_siwave_simulation_setup_bug(self):
        """Validate SIWave DCIR setup use_loop_res_for_per_pin persists after reload."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_dcir_setup("setup_1")
        settings = setup.settings
        settings.use_loop_res_for_per_pin = False

        setup = edbapp.setups["setup_1"]
        assert not setup.settings.use_loop_res_for_per_pin
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_hfss_pi_setup_create_and_properties(self):
        """Create an HFSS PI setup and verify basic properties."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_hfss_pi_setup(name="hfss_pi_1")
        assert setup is not None
        assert not setup.is_null
        assert "hfss_pi_1" in edbapp.simulation_setups.hfss_pi
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_hfss_pi_setup_create_with_sweep(self):
        """Create an HFSS PI setup with a frequency sweep."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_hfss_pi_setup(
            name="hfss_pi_sweep",
            start_freq=1e9,
            stop_freq=10e9,
            step_freq=1e8,
        )
        assert setup is not None
        assert len(setup.sweep_data) > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_setup_with_unknown_solver_falls_back_to_hfss(self):
        """Passing an unknown solver name to create() should fall back to HFSS."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create(name="fallback_setup", solver="unknown_solver")
        assert setup is not None
        assert "fallback_setup" in edbapp.simulation_setups.hfss
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_setup_returns_none_for_duplicate_name(self):
        """create() must return None and log an error if setup already exists."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.simulation_setups.create(name="dup_setup", solver="hfss")
        result = edbapp.simulation_setups.create(name="dup_setup", solver="hfss")
        assert result is None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_hfss_pi_property_empty_when_no_setups(self):
        """hfss_pi property returns empty dict when no HFSS PI setups exist."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.simulation_setups.hfss_pi == {}
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_q3d_property_empty_when_no_q3d_setups(self):
        """q3d property returns empty dict when no Q3D setups exist."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.simulation_setups.q3d == {}
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_raptor_x_property_empty_when_no_raptor_x_setups(self):
        """raptor_x property returns empty dict when no RaptorX setups exist."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.simulation_setups.raptor_x == {}
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_siwave_dcir_property_empty_when_no_setups(self):
        """siwave_dcir property returns empty dict when no DCIR setups exist."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.simulation_setups.siwave_dcir == {}
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_siwave_property_empty_when_no_setups(self):
        """siwave property returns empty dict when no SIWave setups exist."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.simulation_setups.siwave == {}
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_siwave_cpa_setup_creates_and_stores(self):
        """create_siwave_cpa_setup creates a CPA setup and stores it internally."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_cpa_setup(name="my_cpa_setup")
        assert setup is not None
        assert "my_cpa_setup" in edbapp.simulation_setups._siwave_cpa_setup
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_siwave_cpa_setup_duplicate_returns_existing(self):
        """create_siwave_cpa_setup returns the existing setup if called with the same name."""
        edbapp = self.edb_examples.create_empty_edb()
        setup1 = edbapp.simulation_setups.create_siwave_cpa_setup(name="cpa_dup")
        setup2 = edbapp.simulation_setups.create_siwave_cpa_setup(name="cpa_dup")
        assert setup2 is setup1
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_hfss_setup_without_sweep(self):
        """create_hfss_setup with no frequency params should not add a sweep."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_hfss_setup(name="hfss_no_sweep")
        assert setup is not None
        assert len(setup.sweep_data) == 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_siwave_setup_without_sweep(self):
        """create_siwave_setup with no frequency params should not add a sweep."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_setup(name="si_no_sweep")
        assert setup is not None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_setups_property_merges_all_solver_types(self):
        """setups property should aggregate all solver setup dicts."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.simulation_setups.create_hfss_setup(name="hfss_merged")
        edbapp.simulation_setups.create_siwave_setup(name="si_merged")
        all_setups = edbapp.simulation_setups.setups
        assert "hfss_merged" in all_setups
        assert "si_merged" in all_setups
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_raptor_x_setup_with_zero_start_freq(self):
        """create_raptor_x_setup with start_freq=0 should still add a sweep (not None)."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_raptor_x_setup(
            name="rx_zero_start",
            start_freq=0,
            stop_freq=10e9,
            step_freq=1e8,
        )
        assert setup is not None
        assert len(setup.sweep_data) > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet skipping")
    def test_create_q3d_setup_without_sweep(self):
        """create_q3d_setup with no frequency params should not add a sweep."""
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_q3d_setup(name="q3d_no_sweep")
        assert setup is not None
        edbapp.close(terminate_rpc_session=False)

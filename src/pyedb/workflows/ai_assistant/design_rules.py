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

from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
# Design rules – grouped by standard
# --------------------------------------------------------------------------- #
@dataclass
class IPC2221C:
    """
    IPC-2221C – Generic Standard on Printed Board Design.
    Covers creepage / clearance / pollution degree for safety.
    """

    min_creepage_30V_mm: float = 0.10
    min_creepage_50V_mm: float = 0.15
    min_creepage_100V_mm: float = 0.20
    min_creepage_150V_mm: float = 0.25
    min_creepage_300V_mm: float = 0.50
    min_creepage_500V_mm: float = 0.80
    min_creepage_1000V_mm: float = 1.50
    min_clearance_30V_mm: float = 0.05
    min_clearance_50V_mm: float = 0.10
    min_clearance_100V_mm: float = 0.10
    min_clearance_150V_mm: float = 0.15
    min_clearance_300V_mm: float = 0.25
    min_clearance_500V_mm: float = 0.50
    min_clearance_1000V_mm: float = 1.00
    min_internal_clearance_coated_mm: float = 0.05
    min_external_clearance_uncoated_mm: float = 0.20
    min_coated_board_pollution_degree_2_mm: float = 0.13
    min_uncoated_board_pollution_degree_3_mm: float = 0.38


@dataclass
class IPC2222C:
    """
    IPC-2222C – Sectional Standard for Rigid Organic Printed Boards.
    Physical / DFM / DFA requirements.
    """

    min_trace_width_outer_mm: float = 0.075
    min_trace_width_inner_mm: float = 0.050
    min_trace_space_outer_mm: float = 0.075
    min_trace_space_inner_mm: float = 0.050
    min_diff_pair_gap_outer_mm: float = 0.075
    min_diff_pair_gap_inner_mm: float = 0.050
    max_trace_width_tolerance_mm: float = 0.012
    max_trace_edge_roughness_um: int = 5
    max_trace_side_etch_um: int = 8
    min_microvia_diameter_mm: float = 0.050
    max_microvia_diameter_mm: float = 0.125
    min_microvia_pad_diameter_mm: float = 0.125
    min_annular_ring_outer_mm: float = 0.050
    min_annular_ring_inner_mm: float = 0.025
    min_annular_ring_microvia_mm: float = 0.025
    max_annular_ring_outgrowth_mm: float = 0.075
    min_via_to_copper_distance_mm: float = 0.125
    min_via_to_via_distance_same_net_mm: float = 0.150
    min_via_to_via_distance_diff_net_mm: float = 0.250
    min_through_via_diameter_mm: float = 0.100
    max_through_via_diameter_mm: float = 6.35
    min_drill_to_drill_distance_mm: float = 0.300
    min_drill_to_board_edge_mm: float = 0.500
    min_plated_hole_to_internal_copper_mm: float = 0.200
    min_non_plated_hole_to_copper_mm: float = 0.250
    min_slot_hole_width_mm: float = 0.450
    max_slot_hole_length_mm: float = 150
    min_press_fit_hole_diameter_tolerance_mm: float = 0.05
    min_press_fit_pad_annular_ring_mm: float = 0.15
    min_layer_to_layer_registration_mm: float = 0.025
    max_layer_to_layer_thickness_tolerance_pct: int = 8
    min_core_thickness_mm: float = 0.025
    min_prepreg_thickness_mm: float = 0.025
    max_total_board_thickness_tolerance_mm: float = 0.05
    min_outerlayer_copper_thickness_um: int = 12
    max_outerlayer_copper_thickness_um: int = 105
    min_innerlayer_copper_thickness_um: int = 12
    max_innerlayer_copper_thickness_um: int = 70
    min_plating_thickness_hole_wall_um: int = 20
    min_final_finish_thickness_Ni_um: int = 3
    min_final_finish_thickness_Au_um: float = 0.03
    max_final_finish_thickness_Au_um: float = 0.10
    min_solder_mask_clearance_mm: float = 0.025
    min_solder_mask_bridge_mm: float = 0.075
    min_solder_mask_thickness_um: int = 8
    max_solder_mask_thickness_um: int = 30
    min_silkscreen_width_mm: float = 0.100
    min_silkscreen_height_mm: float = 0.500
    min_silkscreen_to_pad_clearance_mm: float = 0.125
    min_silkscreen_to_copper_clearance_mm: float = 0.075


@dataclass
class IPC6012F:
    """
    IPC-6012F – Qualification and Performance Specification for Rigid Printed Boards.
    Reliability / environmental / HDI / edge plating.
    """

    min_peel_strength_N_mm: float = 0.8
    min_pull_off_force_N: int = 50
    min_solder_float_temp_C: int = 288
    min_solder_float_time_s: int = 10
    max_thermal_shock_cycles_neg55_to_125C: int = 500
    max_thermal_shock_cycles_neg40_to_150C: int = 1000
    min_surface_insulation_resistance_after_bias_Mohm: int = 1000
    min_volume_resistivity_Ohm_cm: float = 1e8
    min_surface_resistivity_Ohm: float = 1e7
    min_arc_tracking_cti_V: int = 175
    max_arc_tracking_time_s: int = 420
    min_flammability_rating: str = "V-0"
    max_smoke_density_Ds_1p5: int = 100
    max_toxic_gas_index: int = 50
    min_rohs_exemption_lead_pct: float = 0.1
    max_halogen_content_ppm: int = 900
    max_bromine_ppm: int = 900
    max_chlorine_ppm: int = 900
    max_antimony_ppm: int = 900
    min_fiber_weave_angle_deg: int = 0
    max_fiber_weave_angle_deg: int = 7
    min_spread_glass_fiber_pct: int = 98
    min_dielectric_breakdown_kV_mm: int = 40
    min_dielectric_strength_kV_mm: int = 30
    min_tracking_index_cti_V: int = 175
    max_comparative_tracking_index_V: int = 600
    min_arc_resistance_s: int = 120
    min_dielectric_loss_tangent_1MHz: float = 0.02
    max_dielectric_loss_tangent_1GHz: float = 0.005
    min_relative_permittivity_tolerance_pct: int = 2
    max_thickness_tolerance_pct: int = 8
    min_tg_delta_Tg_C: int = 5
    max_moisture_absorption_pct: float = 0.5
    min_cte_xy_below_Tg_ppm_C: int = 11
    max_cte_xy_below_Tg_ppm_C: int = 16
    min_cte_xy_above_Tg_ppm_C: int = 50
    max_cte_xy_above_Tg_ppm_C: int = 70
    min_laminate_void_area_pct: int = 2
    max_laminate_void_diameter_mm: float = 0.05
    min_delamination_after_thermal_mm: float = 0.025


@dataclass
class IPC2226:
    """
    IPC-2226 – Sectional Design Standard for High-Density Interconnect (HDI) Boards.
    Laser-drilled micro-via, blind/buried via, back-drill rules.
    """

    min_laser_drill_registration_mm: float = 0.012
    max_laser_drill_taper_angle_deg: int = 15
    min_laser_drill_bottom_diameter_um: int = 50
    max_laser_drill_aspect_ratio_hdi: float = 1.0
    max_laser_drill_aspect_ratio_uv: float = 0.8
    min_mech_drill_to_laser_drill_distance_mm: float = 0.20
    min_blind_buried_via_fill_void_diameter_mm: float = 0.05
    max_blind_buried_via_fill_void_count_per_via: int = 1
    min_conductive_via_fill_resistance_mOhm: float = 0.5
    min_non_conductive_via_fill_thermal_cond_W_mK: float = 3.0
    min_backdrill_depth_control_mm: float = 0.05
    max_backdrill_stub_length_mm: float = 0.10
    min_backdrill_bit_size_overshoot_mm: float = 0.10
    max_backdrill_bit_size_overshoot_mm: float = 0.25
    min_filled_via_flatness_um: int = 15
    max_filled_via_dimple_um: int = 25
    min_filled_via_void_diameter_mm: float = 0.025
    max_filled_via_voids_per_unit_area_per_cm2: int = 5


@dataclass
class IPC2615:
    """
    IPC-2615 – Generic Requirements for Board Assembly / Panel / Mechanical.
    Fiducials, tooling holes, panel rails, chamfers, castellated holes, etc.
    """

    min_castellated_half_hole_diameter_mm: float = 0.30
    max_castellated_half_hole_depth_tolerance_mm: float = 0.05
    min_castellated_pad_pull_back_mm: float = 0.15
    min_edge_plating_thickness_um: int = 20
    min_edge_plating_wrap_around_mm: float = 0.30
    max_edge_plating_wrap_around_mm: float = 0.50
    min_plated_slot_radius_mm: float = 0.15
    max_plated_slot_aspect_ratio: float = 3.0
    min_edge_strap_copper_width_mm: float = 0.30
    min_edge_strap_copper_thickness_um: int = 35
    min_edge_strap_overlap_mm: float = 1.00
    max_edge_strap_resistance_mOhm: float = 5
    min_fiducial_diameter_mm: float = 1.00
    max_fiducial_diameter_mm: float = 3.00
    min_fiducial_copper_clearance_mm: float = 2.00
    min_fiducial_soldermask_clearance_mm: float = 0.500
    min_tooling_hole_diameter_mm: float = 2.50
    max_tooling_hole_diameter_mm: float = 6.35
    min_tooling_hole_to_copper_mm: float = 1.00
    min_tooling_hole_to_board_edge_mm: float = 1.00
    min_score_line_web_thickness_mm: float = 0.30
    min_routed_tab_width_mm: float = 2.00
    min_breakaway_tab_width_mm: float = 5.00
    min_panel_rail_width_mm: float = 8.00
    max_board_warp_twist_pct: float = 0.75
    max_panel_warp_twist_pct: float = 0.50
    max_bow_mm_per_100mm: float = 0.50
    min_chamfer_45_deg_mm: float = 0.10
    min_chamfer_round_radius_mm: float = 0.20


@dataclass
class IPC7351C:
    """
    IPC-7351C – Generic Requirements for Surface-Mount Design and Land Pattern Standards.
    BGA, QFN, thermal vias, component keep-outs, solder mask, heatsink keep-outs, etc.
    """

    min_component_keepout_to_board_edge_mm: float = 0.50
    min_component_keepout_to_panel_edge_mm: float = 2.00
    min_component_keepout_to_mounting_hole_mm: float = 1.00
    min_component_keepout_to_rail_v_score_mm: float = 1.50
    min_smd_pad_to_via_edge_mm: float = 0.075
    min_smd_pad_to_smd_pad_gap_mm: float = 0.075
    min_bga_pad_diameter_mm: float = 0.200
    max_bga_pad_diameter_mm: float = 0.850
    min_bga_mask_opening_mm: float = 0.050
    min_bga_ball_to_ball_pitch_mm: float = 0.350
    min_bga_keepout_ring_mm: float = 0.100
    min_bga_laser_via_pad_diameter_mm: float = 0.075
    max_bga_laser_via_pad_diameter_mm: float = 0.125
    min_bga_microvia_fill_target_void_pct: int = 10
    max_bga_microvia_fill_target_void_pct: int = 25
    min_qfn_thermal_pad_coverage_pct: int = 50
    min_qfn_thermal_via_diameter_mm: float = 0.150
    min_qfn_thermal_via_fill_void_pct: int = 25
    min_heatsink_mounting_hole_diameter_mm: float = 2.20
    max_heatsink_mounting_hole_diameter_mm: float = 2.30
    min_heatsink_keepout_to_copper_mm: float = 0.30
    min_heatsink_keepout_to_component_mm: float = 0.50
    min_press_fit_pin_keepout_to_internal_plane_mm: float = 0.40
    min_press_fit_pin_keepout_to_PTH_via_mm: float = 0.50
    max_press_fit_pin_hole_position_tolerance_mm: float = 0.025
    min_thermal_relief_spoke_width_mm: float = 0.10
    max_thermal_relief_spoke_count: int = 4
    min_thermal_relief_air_gap_mm: float = 0.075
    max_thermal_relief_connection_pct: int = 50
    min_teardrop_length_mm: float = 0.30
    min_teardrop_width_pct: int = 110
    max_teardrop_width_pct: int = 150


@dataclass
class JEDECJESD22A104D:
    """
    JEDEC JESD22-A104D – Underfill and Adhesive Reliability Requirements.
    Underfill volume, voiding, CTE, modulus, die shear, etc.
    """

    min_underfill_volume_pct: int = 95
    max_underfill_void_diameter_mm: float = 0.05
    max_underfill_void_count_per_device: int = 3
    min_underfill_edge_fill_mm: float = 0.10
    max_underfill_edge_fill_mm: float = 0.30
    min_flip_chip_underfill_cTE_ppm_C: int = 25
    max_flip_chip_underfill_cTE_ppm_C: int = 45
    min_flip_chip_underfill_Tg_C: int = 120
    max_flip_chip_underfill_Tg_C: int = 160
    min_flip_chip_underfill_modulus_GPa: int = 5
    max_flip_chip_underfill_modulus_GPa: int = 10
    min_flip_chip_underfill_shrinkage_pct: float = 0.5
    max_flip_chip_underfill_shrinkage_pct: float = 2.0
    min_adhesive_die_shear_strength_MPa: int = 15
    max_adhesive_cure_temp_C: int = 180
    min_adhesive_cure_time_min: int = 30


@dataclass
class IEC61249221:
    """
    IEC 61249-2-21 + IPC-4101D – Halogen-Free / RoHS Environmental Requirements.
    """

    min_rohs_exemption_lead_pct: float = 0.1
    max_halogen_content_ppm: int = 900
    max_bromine_ppm: int = 900
    max_chlorine_ppm: int = 900
    max_antimony_ppm: int = 900


@dataclass
class DesignRules:
    # Design rules by standard
    ipc2221c: IPC2221C = field(default_factory=IPC2221C)
    ipc2222c: IPC2222C = field(default_factory=IPC2222C)
    ipc6012f: IPC6012F = field(default_factory=IPC6012F)
    ipc2226: IPC2226 = field(default_factory=IPC2226)
    ipc2615: IPC2615 = field(default_factory=IPC2615)
    ipc7351c: IPC7351C = field(default_factory=IPC7351C)
    jedec_jesd22_a104d: JEDECJESD22A104D = field(default_factory=JEDECJESD22A104D)
    iec_61249_2_21: IEC61249221 = field(default_factory=IEC61249221)

# knowledge.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# --------------------------------------------------------------------------- #
# 1.  Net-name regular expressions
# --------------------------------------------------------------------------- #
@dataclass
class NetRegex:
    pattern: str
    examples: List[str]
    conf: float = 0.90


@dataclass
class NetRegexes:
    diff_pair: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(\w+)[-_]?(P|N|[+-])$|^(\w+)[-_]?(DP|DN)$|^(\w+)[-_]?(TX|RX)[-_]?(P|N|[+-])$",
            examples=["USB_DP", "CLK_P", "LAN_TX_N", "DATA+"],
            conf=0.95,
        )
    )
    ddr_bus: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(DDR[45]?|LPDDR[45]?).*?(DQ|DQS|DM|ADDR|BA|BG|CLK|CKE|ODT|CS|RAS|CAS|WE)",
            examples=["DDR4_DQ0", "LPDDR5_CLK_P"],
            conf=0.93,
        )
    )
    pciexpress: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(PCIe|PCI_E).*?(TX|RX|CLK|REFCLK|PERST|CLKREQ|WAKE)",
            examples=["PCIe_TX_P", "PCI_E_REFCLK_N"],
            conf=0.96,
        )
    )
    usb3: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(USB|SS).*?(TX|RX|DP|DN)",
            examples=["USB3_SSTX_P", "SS_RX_N"],
            conf=0.94,
        )
    )
    usb4: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(USB4|SB)(TX|RX|CLK|RST|IRQ)",
            examples=["USB4_SBTX_P", "SB_RX_N"],
            conf=0.94,
        )
    )
    ethernet: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(ETH|LAN|RGMII|SGMII|XGMII|XAUI|MDI).*?(TX|RX|CLK)",
            examples=["ETH_TX_P", "RGMII_RX_CLK"],
            conf=0.92,
        )
    )
    power_rail: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(VDD|VCC|VSS|GND|PVDD|PVCC|VIN|VOUT|VTT|VREF|VPP|VBAT|VSB|VSTBY|V[A-Z]\d+V)\d*$",
            examples=["VDDIO", "3V3", "P12V", "VDD_CORE"],
            conf=0.97,
        )
    )
    rf_antenna: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(RF|ANT|LTE|5G|GPS|GNSS|WIFI|BT|BLE|NFC|PIFA|MATCH|BALUN|SAW|LNA|PA)",
            examples=["ANT_2G4", "RFOUT", "LTE_MIPI"],
            conf=0.91,
        )
    )
    clock_pll: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(CLK|OSC|XTAL|PLL|TCXO|VCXO|REFCLK|SYSCLK|CPUCLK|MEMCLK)",
            examples=["CLK_25M", "PLL_REFCLK"],
            conf=0.93,
        )
    )
    analog: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(ADC|DAC|AIN|AOUT|VREF|VCM|AGND|VTT|ISENSE|VSENSE)",
            examples=["ADC_IN0", "VREF_1V2"],
            conf=0.90,
        )
    )
    shield_gnd: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(SHIELD|CHASSIS|PE|GND_SHIELD|EGND|SGND|LGND)",
            examples=["SHIELD_USB", "CHASSIS_GND"],
            conf=0.88,
        )
    )
    esd_guard: NetRegex = field(
        default_factory=lambda: NetRegex(
            pattern=r"^(ESD|TVS|SP72|PESD|TPD).*?(DP|DN|TX|RX|CLK)",
            examples=["ESD_USB_DP", "TVS_HDMI_CLK"],
            conf=0.89,
        )
    )


# --------------------------------------------------------------------------- #
# 2.  Component fuzzy selector defaults
# --------------------------------------------------------------------------- #
@dataclass
class Capacitor:
    @dataclass
    class HighFreqDecoupling:
        value_regex: str = r"^(1|2\.2|4\.7|10|22|47|100|220|470|1000)pF$"
        package_max_mm: float = 1.6
        voltage_min_V: int = 16
        tolerance_max_pct: int = 10
        dielectric: List[str] = field(default_factory=lambda: ["C0G", "NP0", "X7R"])
        reason: str = "<=1 nF, C0G/X7R, ≤0402"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class RfDcBlock:
        value_regex: str = r"^(1|2\.2|4\.7|10|22|47)nF$"
        package_max_mm: float = 2.0
        dielectric: List[str] = field(default_factory=lambda: ["C0G", "NP0"])
        reason: str = "1-47 nF, RF grade"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class BulkDecoupling:
        value_regex: str = r"^(4\.7|10|22|47|100|220|470|1000)uF$"
        package_min_mm: float = 1.6
        voltage_min_V: float = 6.3
        reason: str = ">=4.7 µF, ≥6.3 V"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class PackageDecoupling:
        value_regex: str = r"^(0\.1|0\.22|0\.47|1)uF$"
        package_max_mm: float = 1.0
        reason: str = "0402/0201 100 nF-1 µF"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class EsdShunt:
        value_regex: str = r"^(15|22|33|47|100)nF$"
        package_max_mm: float = 1.6
        dielectric: List[str] = field(default_factory=lambda: ["X7R", "X5R"])
        reason: str = "15-100 nF close to connector"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class CrystalLoad:
        value_regex: str = r"^(10|12|15|18|22|27|33|39|47)pF$"
        tolerance_max_pct: int = 5
        dielectric: List[str] = field(default_factory=lambda: ["C0G", "NP0"])
        reason: str = "5 % C0G crystal load"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    high_freq_decoupling: HighFreqDecoupling = field(default_factory=HighFreqDecoupling)
    rf_dc_block: RfDcBlock = field(default_factory=RfDcBlock)
    bulk_decoupling: BulkDecoupling = field(default_factory=BulkDecoupling)
    package_decoupling: PackageDecoupling = field(default_factory=PackageDecoupling)
    esd_shunt: EsdShunt = field(default_factory=EsdShunt)
    crystal_load: CrystalLoad = field(default_factory=CrystalLoad)


@dataclass
class Resistor:
    @dataclass
    class PrecisionTermination:
        value_regex: str = r"^(49\.9|50|60|75|100)(\.0)?(R|Ω|Ohm)$"
        tolerance_max_pct: int = 1
        package_max_mm: float = 2.0
        reason: str = "1 % 49.9-100 Ω"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class SeriesTermination:
        value_regex: str = r"^(22|33|47|68)(\.0)?(R|Ω|Ohm)$"
        tolerance_max_pct: int = 5
        package_max_mm: float = 1.6
        reason: str = "22-68 Ω 5 %"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class PullUpDown:
        value_regex: str = r"^(1|4\.7|10|47|100)k(Ω|R|Ohm)?$"
        tolerance_max_pct: int = 10
        reason: str = "1 k-100 k pull"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class CurrentSense:
        value_regex: str = r"^(0\.01|0\.02|0\.05|0\.1|0\.2|0\.5)(R|Ω|Ohm)$"
        power_min_W: float = 0.25
        tolerance_max_pct: int = 1
        reason: str = "<1 Ω 1 % sense"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class ZeroOhm:
        value_regex: str = r"^(0|0R|0Ω|0Ohm|0\.0R)$"
        reason: str = "Zero-ohm link"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class RfMatch:
        value_regex: str = r"^(0|1|2\.2|4\.7|10|22|33|47|68|100)(\.0)?(R|Ω|Ohm)$"
        tolerance_max_pct: int = 1
        package_max_mm: float = 1.0
        reason: str = "≤100 Ω 1 % RF"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    precision_termination: PrecisionTermination = field(default_factory=PrecisionTermination)
    series_termination: SeriesTermination = field(default_factory=SeriesTermination)
    pull_up_down: PullUpDown = field(default_factory=PullUpDown)
    current_sense: CurrentSense = field(default_factory=CurrentSense)
    zero_ohm: ZeroOhm = field(default_factory=ZeroOhm)
    rf_match: RfMatch = field(default_factory=RfMatch)


@dataclass
class Inductor:
    @dataclass
    class EmiChock:
        value_regex: str = r"^(100nH|1uH|2\.2uH|4\.7uH|10uH)$"
        current_min_A: float = 0.1
        reason: str = "100 nH-10 µH EMI"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class RfChock:
        value_regex: str = r"^(10|22|47|68|100)nH$"
        tolerance_max_pct: int = 10
        reason: str = "10-100 nH RF"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class PowerFilter:
        value_regex: str = r"^(10|22|47|100)uH$"
        current_min_A: float = 0.5
        reason: str = "≥10 µH power"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class VrmOutput:
        value_regex: str = r"^(0\.47|1|2\.2|4\.7)uH$"
        current_min_A: float = 1
        reason: str = "0.47-4.7 µH VRM"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    emi_chock: EmiChock = field(default_factory=EmiChock)
    rf_chock: RfChock = field(default_factory=RfChock)
    power_filter: PowerFilter = field(default_factory=PowerFilter)
    vrm_output: VrmOutput = field(default_factory=VrmOutput)


@dataclass
class FerriteBead:
    @dataclass
    class EmiSuppression:
        impedance_regex: str = r"^(120|220|470|600|1000)@100MHz$"
        current_min_A: float = 0.1
        reason: str = "120-1 kΩ @100 MHz"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class HighFreqBlock:
        impedance_regex: str = r"^(2200|5000)@100MHz$"
        current_min_A: float = 0.05
        reason: str = "≥2 kΩ @100 MHz"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    emi_suppression: EmiSuppression = field(default_factory=EmiSuppression)
    high_freq_block: HighFreqBlock = field(default_factory=HighFreqBlock)


@dataclass
class CommonModeChoke:
    @dataclass
    class UsbFilter:
        impedance_regex: str = r"^90@100MHz$"
        reason: str = "USB 90 Ω CM choke"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class LanFilter:
        impedance_regex: str = r"^2200@100MHz$"
        reason: str = "LAN 2.2 kΩ CM choke"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class HdmiFilter:
        impedance_regex: str = r"^1000@100MHz$"
        reason: str = "HDMI 1 kΩ CM choke"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    usb_filter: UsbFilter = field(default_factory=UsbFilter)
    lan_filter: LanFilter = field(default_factory=LanFilter)
    hdmi_filter: HdmiFilter = field(default_factory=HdmiFilter)


@dataclass
class EsdDiode:
    @dataclass
    class SignalEsd:
        voltage_max_V: int = 5
        capacitance_max_pF: float = 0.5
        package_max_mm: float = 1.6
        reason: str = "≤5 V, ≤0.5 pF, ≤0402"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    @dataclass
    class PowerEsd:
        voltage_min_V: int = 12
        power_min_W: float = 0.2
        reason: str = "≥12 V stand-off"
        part_name: str = ""
        ref_des: str = ""
        value: float = 0.0
        confidence: float = 0.0

    signal_esd: SignalEsd = field(default_factory=SignalEsd)
    power_esd: PowerEsd = field(default_factory=PowerEsd)


@dataclass
class ComponentFuzzy:
    capacitor: Capacitor = field(default_factory=Capacitor)
    resistor: Resistor = field(default_factory=Resistor)
    inductor: Inductor = field(default_factory=Inductor)
    ferrite_bead: FerriteBead = field(default_factory=FerriteBead)
    common_mode_choke: CommonModeChoke = field(default_factory=CommonModeChoke)
    esd_diode: EsdDiode = field(default_factory=EsdDiode)


# --------------------------------------------------------------------------- #
# 3.  Design rules – grouped by standard
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


# --------------------------------------------------------------------------- #
# 4.  Top-level aggregator (mirrors the original JSON)
# --------------------------------------------------------------------------- #
@dataclass
class KnowledgeBase:
    net_regexes: NetRegexes = field(default_factory=NetRegexes)
    component_fuzzy: ComponentFuzzy = field(default_factory=ComponentFuzzy)
    # Design rules by standard
    ipc2221c: IPC2221C = field(default_factory=IPC2221C)
    ipc2222c: IPC2222C = field(default_factory=IPC2222C)
    ipc6012f: IPC6012F = field(default_factory=IPC6012F)
    ipc2226: IPC2226 = field(default_factory=IPC2226)
    ipc2615: IPC2615 = field(default_factory=IPC2615)
    ipc7351c: IPC7351C = field(default_factory=IPC7351C)
    jedec_jesd22_a104d: JEDECJESD22A104D = field(default_factory=JEDECJESD22A104D)
    iec_61249_2_21: IEC61249221 = field(default_factory=IEC61249221)

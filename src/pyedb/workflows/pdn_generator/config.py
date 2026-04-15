from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ModeName = Literal["draft", "realistic"]
PlacementPattern = Literal["auto", "north_south", "horseshoe", "ring"]
StackupPresetName = Literal["4L", "6L"]
DecapRole = Literal["hf", "mid", "bulk"]
LoadVariantName = Literal["small_ic", "fpga_cluster", "connector_load", "multi_pin_module"]
SourceVariantName = Literal["edge_pad", "connector", "vrm_patch", "remote_source", "dual_entry"]
SourceTopologyName = Literal["dedicated", "shared_pairs", "shared_all"]


@dataclass(frozen=True)
class PackageSpec:
    """Physical footprint intent for a two-pin device."""

    name: str
    body_length_m: float
    body_width_m: float
    pad_length_m: float
    pad_width_m: float
    pin_pitch_m: float
    courtyard_clearance_m: float

    @property
    def envelope_radius_m(self) -> float:
        return ((self.body_length_m / 2.0) ** 2 + (self.body_width_m / 2.0) ** 2) ** 0.5 + self.courtyard_clearance_m


@dataclass(frozen=True)
class DecapFamily:
    """Curated decoupling component definition used by the planner."""

    name: str
    part_name: str
    package: PackageSpec
    role: DecapRole
    capacitance_f: float
    esr_ohm: float
    esl_h: float
    preferred_distance_min_m: float
    preferred_distance_max_m: float
    selection_weight: float = 1.0


@dataclass(frozen=True)
class ViaPreset:
    """Fabrication-friendly via geometry preset."""

    name: str
    hole_diameter_m: float
    pad_diameter_m: float
    antipad_diameter_m: float
    pad_to_via_distance_m: float
    trace_width_m: float


@dataclass(frozen=True)
class StackupLayerSpec:
    """Stackup layer definition."""

    name: str
    layer_type: Literal["signal", "dielectric"]
    thickness_m: float
    material: str
    fill_material: str | None = None


@dataclass(frozen=True)
class LoadVariantSpec:
    """Mechanical/electrical style used for the sink landing pattern."""

    name: LoadVariantName
    package: PackageSpec
    decap_distance_scale: float = 1.0
    capacitor_multiplier: float = 1.0
    placement_pattern: PlacementPattern = "auto"
    preferred_rotation_deg: float = 0.0


@dataclass(frozen=True)
class SourceVariantSpec:
    """Power-entry style used for the source copper pads."""

    name: SourceVariantName
    pad_length_m: float
    pad_width_m: float
    pad_pitch_m: float
    pad_count: int
    trace_width_scale: float
    side: Literal["left", "right", "top", "bottom"]
    offset_m: float = 0.0


@dataclass(frozen=True)
class RailSpec:
    """Power rail definition for multi-island / multi-load PDN generation."""

    name: str
    current_a: float
    max_ripple_v: float
    target_impedance_ohm: float | None = None
    capacitor_count: int | None = None
    load_variant: LoadVariantName = "small_ic"
    source_variant: SourceVariantName = "edge_pad"
    island_width_m: float | None = None
    island_height_m: float | None = None
    center_hint: tuple[float, float] | None = None
    placement_pattern: PlacementPattern = "auto"
    decap_library: list[DecapFamily] | None = None
    source_group: str | None = None


@dataclass
class PDNGeneratorConfig:
    """Input configuration for the PDN-only layout generator."""

    board_width_m: float = 0.060
    board_height_m: float = 0.045
    stackup_preset: StackupPresetName = "4L"
    mode: ModeName = "realistic"
    placement_pattern: PlacementPattern = "auto"
    copper_thickness_m: float = 35e-6
    dielectric_thicknesses_m: list[float] = field(default_factory=lambda: [90e-6, 180e-6, 90e-6])
    power_net_name: str = "VDD"
    ground_net_name: str = "GND"
    vin_net_name: str = "VIN"
    include_vin: bool = False
    load_current_a: float = 8.0
    max_ripple_v: float = 0.030
    target_impedance_ohm: float | None = None
    capacitor_count: int | None = None
    edge_clearance_m: float = 0.0025
    plane_edge_inset_m: float = 0.0010
    power_island_edge_inset_m: float = 0.0040
    placement_keepout_m: float = 0.00035
    source_trace_width_m: float = 0.0010
    source_pad_length_m: float = 0.0035
    source_pad_width_m: float = 0.0015
    load_package: PackageSpec | None = None
    via_preset: ViaPreset | None = None
    decap_library: list[DecapFamily] | None = None
    case_name_prefix: str = "pdn_case"
    dataset_name: str = "pdn_dataset"
    label_schema_version: str = "pdn_labels.v1"
    source_topology: SourceTopologyName = "dedicated"
    rails: list[RailSpec] | None = None
    load_variants: dict[str, LoadVariantSpec] | None = None
    source_variants: dict[str, SourceVariantSpec] | None = None

    @property
    def resolved_target_impedance_ohm(self) -> float:
        if self.target_impedance_ohm is not None:
            return self.target_impedance_ohm
        current = max(self.load_current_a, 1e-6)
        return self.max_ripple_v / current

    @property
    def resolved_capacitor_count(self) -> int:
        if self.capacitor_count is not None:
            return max(2, self.capacitor_count)
        if self.mode == "draft":
            base = 5
            scale = self.load_current_a / 6.0
        else:
            base = 8
            scale = self.load_current_a / 4.0
        if self.resolved_target_impedance_ohm <= 0.010:
            base += 4
        elif self.resolved_target_impedance_ohm <= 0.020:
            base += 2
        return max(4, min(20, round(base + scale)))

    @property
    def resolved_rail_count(self) -> int:
        return len(self.rails) if self.rails else 1

    def stackup_layers(self) -> list[StackupLayerSpec]:
        if self.stackup_preset == "4L":
            dielectric = list(self.dielectric_thicknesses_m[:3])
            if len(dielectric) < 3:
                dielectric.extend([180e-6] * (3 - len(dielectric)))
            return [
                StackupLayerSpec("L1_TOP", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
                StackupLayerSpec("D1_PREPREG", "dielectric", dielectric[0], "FR4_epoxy"),
                StackupLayerSpec("L2_GND", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
                StackupLayerSpec("D2_CORE", "dielectric", dielectric[1], "FR4_epoxy"),
                StackupLayerSpec("L3_VDD", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
                StackupLayerSpec("D3_PREPREG", "dielectric", dielectric[2], "FR4_epoxy"),
                StackupLayerSpec("L4_BOT", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            ]
        dielectric = list(self.dielectric_thicknesses_m[:5])
        if len(dielectric) < 5:
            dielectric.extend([140e-6] * (5 - len(dielectric)))
        return [
            StackupLayerSpec("L1_TOP", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            StackupLayerSpec("D1_PREPREG", "dielectric", dielectric[0], "FR4_epoxy"),
            StackupLayerSpec("L2_GND", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            StackupLayerSpec("D2_CORE", "dielectric", dielectric[1], "FR4_epoxy"),
            StackupLayerSpec("L3_VDD", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            StackupLayerSpec("D3_PREPREG", "dielectric", dielectric[2], "FR4_epoxy"),
            StackupLayerSpec("L4_SIG", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            StackupLayerSpec("D4_CORE", "dielectric", dielectric[3], "FR4_epoxy"),
            StackupLayerSpec("L5_GND", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
            StackupLayerSpec("D5_PREPREG", "dielectric", dielectric[4], "FR4_epoxy"),
            StackupLayerSpec("L6_BOT", "signal", self.copper_thickness_m, "copper", "FR4_epoxy"),
        ]


from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random

from .config import PDNGeneratorConfig, PackageSpec, PlacementPattern, RailSpec, StackupLayerSpec, ViaPreset
from .library import refine_decap_mix, resolve_config_defaults
from .variants import resolve_rail_specs


Point = tuple[float, float]


@dataclass(frozen=True)
class TracePlan:
    layer_name: str
    net_name: str
    points: list[Point]
    width_m: float


@dataclass(frozen=True)
class RectanglePlan:
    layer_name: str
    net_name: str
    center: Point
    width_m: float
    height_m: float


@dataclass(frozen=True)
class PolygonPlan:
    layer_name: str
    net_name: str
    points: list[Point]


@dataclass(frozen=True)
class TwoPinDevicePlan:
    refdes: str
    part_name: str
    package_name: str
    role: str
    center: Point
    rotation_deg: float
    power_pin: Point
    ground_pin: Point
    power_via: Point
    ground_via: Point
    power_net: str
    ground_net: str
    capacitance_f: float | None = None
    resistance_ohm: float | None = None
    inductance_h: float | None = None
    distance_to_load_m: float = 0.0


@dataclass(frozen=True)
class SourcePlan:
    name: str
    source_group: str
    rail_name: str
    served_rails: list[str]
    variant_name: str
    center: Point
    pads: list[RectanglePlan]
    power_launches: dict[str, Point]
    ground_launches: dict[str, Point]


@dataclass(frozen=True)
class PowerIslandPlan:
    name: str
    rail_name: str
    polygon: PolygonPlan
    load_refdes: str
    source_name: str


@dataclass(frozen=True)
class RailPlan:
    name: str
    source_group: str
    target_impedance_ohm: float
    load_current_a: float
    capacitor_count: int
    load_variant: str
    source_variant: str
    load_refdes: str
    source_name: str
    island_name: str
    decap_refdes: list[str]
    total_capacitance_f: float
    average_esr_ohm: float
    average_esl_h: float


@dataclass(frozen=True)
class LayerMap:
    signal_layers: list[str]
    dielectric_layers: list[str]
    top_layer: str
    bottom_layer: str
    power_plane_layers: list[str]
    ground_plane_layers: list[str]
    outline_layer: str = "Outline"


@dataclass(frozen=True)
class PDNGenerationPlan:
    seed: int
    config: PDNGeneratorConfig
    layers: LayerMap
    stackup: list[StackupLayerSpec]
    outline: PolygonPlan
    ground_planes: list[PolygonPlan]
    power_planes: list[PolygonPlan]
    source_pads: list[RectanglePlan]
    feed_traces: list[TracePlan]
    load: TwoPinDevicePlan
    decaps: list[TwoPinDevicePlan]
    rails: list[RailPlan]
    loads: list[TwoPinDevicePlan]
    sources: list[SourcePlan]
    islands: list[PowerIslandPlan]

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "dataset_name": self.config.dataset_name,
            "label_schema_version": self.config.label_schema_version,
            "source_topology": self.config.source_topology,
            "board": {"width_m": self.config.board_width_m, "height_m": self.config.board_height_m},
            "stackup": [asdict(layer) for layer in self.stackup],
            "outline": asdict(self.outline),
            "ground_planes": [asdict(plane) for plane in self.ground_planes],
            "power_planes": [asdict(plane) for plane in self.power_planes],
            "source_pads": [asdict(pad) for pad in self.source_pads],
            "feed_traces": [asdict(trace) for trace in self.feed_traces],
            "load": asdict(self.load),
            "loads": [asdict(device) for device in self.loads],
            "decaps": [asdict(device) for device in self.decaps],
            "sources": [asdict(source) for source in self.sources],
            "islands": [asdict(island) for island in self.islands],
            "rails": [asdict(rail) for rail in self.rails],
            "counts": {
                "rails": len(self.rails),
                "loads": len(self.loads),
                "sources": len(self.sources),
                "islands": len(self.islands),
                "decaps": len(self.decaps),
                "hf": sum(1 for device in self.decaps if device.role == "hf"),
                "mid": sum(1 for device in self.decaps if device.role == "mid"),
                "bulk": sum(1 for device in self.decaps if device.role == "bulk"),
            },
        }


_DEF_SEED = 7


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _offset(point: Point, vector: Point) -> Point:
    return point[0] + vector[0], point[1] + vector[1]


def _polar(radius: float, angle_deg: float) -> Point:
    angle = math.radians(angle_deg)
    return radius * math.cos(angle), radius * math.sin(angle)


def _rotate(vector: Point, angle_deg: float) -> Point:
    angle = math.radians(angle_deg)
    return (
        vector[0] * math.cos(angle) - vector[1] * math.sin(angle),
        vector[0] * math.sin(angle) + vector[1] * math.cos(angle),
    )


def _closed_rectangle(width_m: float, height_m: float, center: Point = (0.0, 0.0)) -> list[Point]:
    half_w = width_m / 2.0
    half_h = height_m / 2.0
    cx, cy = center
    return [
        (cx - half_w, cy - half_h),
        (cx + half_w, cy - half_h),
        (cx + half_w, cy + half_h),
        (cx - half_w, cy + half_h),
        (cx - half_w, cy - half_h),
    ]


def _device_from_center(
    refdes: str,
    part_name: str,
    package: PackageSpec,
    role: str,
    center: Point,
    rotation_deg: float,
    load_center: Point,
    power_net: str,
    ground_net: str,
    via_preset: ViaPreset,
    capacitance_f: float | None = None,
    resistance_ohm: float | None = None,
    inductance_h: float | None = None,
) -> TwoPinDevicePlan:
    axis = _rotate((1.0, 0.0), rotation_deg)
    half_pitch = package.pin_pitch_m / 2.0
    pin_a = _offset(center, (-axis[0] * half_pitch, -axis[1] * half_pitch))
    pin_b = _offset(center, (axis[0] * half_pitch, axis[1] * half_pitch))
    if _dist(pin_a, load_center) <= _dist(pin_b, load_center):
        power_pin, ground_pin = pin_a, pin_b
        power_sign, ground_sign = -1.0, 1.0
    else:
        power_pin, ground_pin = pin_b, pin_a
        power_sign, ground_sign = 1.0, -1.0

    power_via = _offset(
        power_pin,
        (axis[0] * power_sign * via_preset.pad_to_via_distance_m, axis[1] * power_sign * via_preset.pad_to_via_distance_m),
    )
    ground_via = _offset(
        ground_pin,
        (axis[0] * ground_sign * via_preset.pad_to_via_distance_m, axis[1] * ground_sign * via_preset.pad_to_via_distance_m),
    )
    return TwoPinDevicePlan(
        refdes=refdes,
        part_name=part_name,
        package_name=package.name,
        role=role,
        center=center,
        rotation_deg=rotation_deg,
        power_pin=power_pin,
        ground_pin=ground_pin,
        power_via=power_via,
        ground_via=ground_via,
        power_net=power_net,
        ground_net=ground_net,
        capacitance_f=capacitance_f,
        resistance_ohm=resistance_ohm,
        inductance_h=inductance_h,
        distance_to_load_m=_dist(center, load_center),
    )


def _layer_map(stackup: list[StackupLayerSpec]) -> LayerMap:
    signal_layers = [layer.name for layer in stackup if layer.layer_type == "signal"]
    dielectric_layers = [layer.name for layer in stackup if layer.layer_type == "dielectric"]
    power_plane_layers = [name for name in signal_layers if "VDD" in name or name.endswith("_VDD")]
    ground_plane_layers = [name for name in signal_layers if "GND" in name]
    return LayerMap(
        signal_layers=signal_layers,
        dielectric_layers=dielectric_layers,
        top_layer=signal_layers[0],
        bottom_layer=signal_layers[-1],
        power_plane_layers=power_plane_layers,
        ground_plane_layers=ground_plane_layers,
    )


def _pattern_sectors(pattern: PlacementPattern, count: int) -> list[tuple[float, float]]:
    if pattern == "north_south":
        return [(60.0, 120.0), (240.0, 300.0)]
    if pattern == "ring":
        return [(35.0, 145.0), (215.0, 325.0), (145.0, 215.0)]
    if pattern == "horseshoe":
        return [(40.0, 135.0), (225.0, 320.0), (320.0, 350.0)]
    if count <= 6:
        return _pattern_sectors("horseshoe", count)
    if count <= 8:
        return _pattern_sectors("north_south", count)
    return _pattern_sectors("ring", count)


def _is_inside_board(center: Point, radius_m: float, config: PDNGeneratorConfig) -> bool:
    usable_w = config.board_width_m / 2.0 - config.edge_clearance_m - radius_m
    usable_h = config.board_height_m / 2.0 - config.edge_clearance_m - radius_m
    return abs(center[0]) <= usable_w and abs(center[1]) <= usable_h


def _is_clear(center: Point, radius_m: float, existing: list[tuple[Point, float]], minimum_gap_m: float) -> bool:
    for other_center, other_radius in existing:
        if _dist(center, other_center) < radius_m + other_radius + minimum_gap_m:
            return False
    return True


def _device_keepout_radius(package: PackageSpec, via_preset: ViaPreset) -> float:
    via_reach = package.pin_pitch_m / 2.0 + via_preset.pad_to_via_distance_m + via_preset.pad_diameter_m / 2.0
    return max(package.envelope_radius_m, via_reach + package.courtyard_clearance_m)


def _load_keepout_radius(package: PackageSpec) -> float:
    return max(package.body_width_m / 2.0, package.pad_width_m) + package.courtyard_clearance_m * 0.5


def _device_is_valid(
    device: TwoPinDevicePlan,
    keepout_radius_m: float,
    occupied: list[tuple[Point, float]],
    config: PDNGeneratorConfig,
) -> bool:
    return _is_inside_board(device.center, keepout_radius_m, config) and _is_clear(
        device.center,
        keepout_radius_m,
        occupied,
        config.placement_keepout_m,
    )


def _role_radius_window(config: PDNGeneratorConfig, role: str, preferred_min_m: float, preferred_max_m: float) -> tuple[float, float]:
    mid_lower = 4.6e-3 if config.mode == "realistic" else 4.0e-3
    bulk_lower = 10.5e-3 if config.mode == "realistic" else 9.2e-3
    if role == "hf":
        lower_bound = preferred_min_m
        upper_bound = min(max(preferred_max_m, mid_lower - 0.5e-3), mid_lower - 0.3e-3)
    elif role == "mid":
        lower_bound = max(preferred_min_m, mid_lower)
        upper_bound = min(preferred_max_m, bulk_lower - 0.6e-3)
    else:
        lower_bound = max(preferred_min_m, bulk_lower)
        upper_bound = preferred_max_m
    upper_bound = max(lower_bound + 0.3e-3, upper_bound)
    return lower_bound, upper_bound


def _fallback_search(
    rng: random.Random,
    index: int,
    family,
    load: TwoPinDevicePlan,
    keepout_radius: float,
    occupied: list[tuple[Point, float]],
    config: PDNGeneratorConfig,
    radius_low: float,
    radius_high: float,
) -> TwoPinDevicePlan | None:
    radius_span = radius_high - radius_low
    base_offset = rng.uniform(0.0, 360.0)
    radii = [radius_low + radius_span * frac for frac in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)]
    radii.extend([radius_high + 0.2e-3, radius_high + 0.4e-3])
    angles = [base_offset + step * 7.5 for step in range(48)]
    for radius in radii:
        for angle in angles:
            candidate = _device_from_center(
                refdes=f"C{index}",
                part_name=family.part_name,
                package=family.package,
                role=family.role,
                center=_offset(load.center, _polar(radius, angle)),
                rotation_deg=angle + 90.0,
                load_center=load.center,
                power_net=load.power_net,
                ground_net=load.ground_net,
                via_preset=config.via_preset,
                capacitance_f=family.capacitance_f,
                resistance_ohm=family.esr_ohm,
                inductance_h=family.esl_h,
            )
            if _device_is_valid(candidate, keepout_radius, occupied, config):
                return candidate
    return None


def _orthogonal_trace(start: Point, end: Point) -> list[Point]:
    midpoint_x = (start[0] + end[0]) / 2.0
    points = [start, (midpoint_x, start[1]), (midpoint_x, end[1]), end]
    deduped: list[Point] = []
    for point in points:
        if not deduped or point != deduped[-1]:
            deduped.append(point)
    return deduped


def _rail_anchor_points(config: PDNGeneratorConfig, rails: list[RailSpec]) -> list[Point]:
    anchors: list[Point] = []
    x_positions = [min(0.010, config.board_width_m * 0.17), min(0.022, config.board_width_m * 0.30)]
    rail_count = len(rails)
    if rail_count <= 3:
        usable_span = max(config.board_height_m * 0.66, 0.014)
        y_positions = [0.0] if rail_count == 1 else [(-usable_span / 2.0) + usable_span * index / (rail_count - 1) for index in range(rail_count)]
        anchors = [(x_positions[0], y) for y in y_positions]
    else:
        rows = math.ceil(rail_count / 2)
        usable_span = max(config.board_height_m * 0.72, 0.020)
        y_positions = [(-usable_span / 2.0) + usable_span * index / max(rows - 1, 1) for index in range(rows)]
        for index in range(rail_count):
            anchors.append((x_positions[index % 2], y_positions[index // 2]))
    return [rail.center_hint if rail.center_hint else anchors[index] for index, rail in enumerate(rails)]


def _source_pad_centers(center: Point, variant) -> tuple[list[Point], list[Point]]:
    offsets = [variant.pad_pitch_m * (index - (variant.pad_count - 1) / 2.0) for index in range(variant.pad_count)]
    power_centers: list[Point] = []
    ground_centers: list[Point] = []
    if variant.side in {"left", "right"}:
        for offset in offsets:
            power_centers.append((center[0], center[1] + variant.pad_pitch_m * 0.65 + offset))
            ground_centers.append((center[0], center[1] - variant.pad_pitch_m * 0.65 + offset))
    else:
        for offset in offsets:
            power_centers.append((center[0] - variant.pad_pitch_m * 0.65 + offset, center[1]))
            ground_centers.append((center[0] + variant.pad_pitch_m * 0.65 + offset, center[1]))
    return power_centers, ground_centers


def _source_launch_point(center: Point, variant) -> Point:
    if variant.side == "left":
        return center[0] + variant.pad_length_m / 2.0, center[1]
    if variant.side == "right":
        return center[0] - variant.pad_length_m / 2.0, center[1]
    if variant.side == "top":
        return center[0], center[1] - variant.pad_length_m / 2.0
    return center[0], center[1] + variant.pad_length_m / 2.0


def _rail_target_impedance(rail: RailSpec) -> float:
    return rail.target_impedance_ohm if rail.target_impedance_ohm is not None else rail.max_ripple_v / max(rail.current_a, 1e-6)


def _build_load_plan(config: PDNGeneratorConfig, rail: RailSpec, rail_center: Point, load_index: int) -> TwoPinDevicePlan:
    load_variant = (config.load_variants or {})[rail.load_variant]
    return _device_from_center(
        refdes=f"LOAD{load_index}",
        part_name=f"PDN_{rail.load_variant.upper()}_{rail.name}",
        package=load_variant.package,
        role="load",
        center=rail_center,
        rotation_deg=load_variant.preferred_rotation_deg,
        load_center=rail_center,
        power_net=rail.name,
        ground_net=config.ground_net_name,
        via_preset=config.via_preset,
        resistance_ohm=max(_rail_target_impedance(rail), 1e-3),
    )


def _build_source_plan(
    config: PDNGeneratorConfig,
    source_group: str,
    grouped_rails: list[RailSpec],
    loads_by_rail: dict[str, TwoPinDevicePlan],
    top_layer: str,
) -> tuple[SourcePlan, list[tuple[Point, float]]]:
    source_variant = (config.source_variants or {})[grouped_rails[0].source_variant]
    group_loads = [loads_by_rail[rail.name] for rail in grouped_rails]
    if source_variant.side in {"left", "right"}:
        average_axis = sum(load.center[1] for load in group_loads) / len(group_loads)
        base_center = (
            -config.board_width_m / 2.0 + config.edge_clearance_m + source_variant.pad_length_m
            if source_variant.side == "left"
            else config.board_width_m / 2.0 - config.edge_clearance_m - source_variant.pad_length_m,
            average_axis + source_variant.offset_m,
        )
    else:
        average_axis = sum(load.center[0] for load in group_loads) / len(group_loads)
        base_center = (
            average_axis,
            config.board_height_m / 2.0 - config.edge_clearance_m - source_variant.pad_length_m
            if source_variant.side == "top"
            else -config.board_height_m / 2.0 + config.edge_clearance_m + source_variant.pad_length_m,
        )

    slot_spacing = max(max((config.source_variants or {})[rail.source_variant].pad_pitch_m for rail in grouped_rails) * 2.2, 3.2e-3)
    slot_offsets = [slot_spacing * (index - (len(grouped_rails) - 1) / 2.0) for index in range(len(grouped_rails))]
    if source_variant.side == "left":
        source_center = base_center
    elif source_variant.side == "right":
        source_center = base_center
    elif source_variant.side == "top":
        source_center = base_center
    else:
        source_center = base_center

    pads: list[RectanglePlan] = []
    occupied: list[tuple[Point, float]] = []
    power_launches: dict[str, Point] = {}
    ground_launches: dict[str, Point] = {}
    served_rails: list[str] = []

    for rail, slot_offset in zip(grouped_rails, slot_offsets):
        served_rails.append(rail.name)
        rail_variant = (config.source_variants or {})[rail.source_variant]
        if rail_variant.side in {"left", "right"}:
            slot_center = (source_center[0], source_center[1] + slot_offset)
        else:
            slot_center = (source_center[0] + slot_offset, source_center[1])
        power_centers, ground_centers = _source_pad_centers(slot_center, rail_variant)
        pad_radius = math.hypot(rail_variant.pad_length_m / 2.0, rail_variant.pad_width_m / 2.0)
        for center in power_centers:
            pads.append(RectanglePlan(top_layer, rail.name, center, rail_variant.pad_length_m, rail_variant.pad_width_m))
            occupied.append((center, pad_radius))
        for center in ground_centers:
            pads.append(RectanglePlan(top_layer, config.ground_net_name, center, rail_variant.pad_length_m, rail_variant.pad_width_m))
            occupied.append((center, pad_radius))
        primary_index = len(power_centers) // 2
        power_launches[rail.name] = _source_launch_point(power_centers[primary_index], rail_variant)
        ground_launches[rail.name] = _source_launch_point(ground_centers[primary_index], rail_variant)

    source = SourcePlan(
        name=source_group,
        source_group=source_group,
        rail_name=grouped_rails[0].name,
        served_rails=served_rails,
        variant_name=source_variant.name,
        center=source_center,
        pads=pads,
        power_launches=power_launches,
        ground_launches=ground_launches,
    )
    return source, occupied


def _power_island_polygon(
    config: PDNGeneratorConfig,
    rail: RailSpec,
    load: TwoPinDevicePlan,
    source: SourcePlan,
    decaps: list[TwoPinDevicePlan],
) -> list[Point]:
    if rail.island_width_m and rail.island_height_m:
        center_x = (load.center[0] + source.center[0]) / 2.0
        center_y = (load.center[1] + source.center[1]) / 2.0
        return _closed_rectangle(rail.island_width_m, rail.island_height_m, (center_x, center_y))

    xs = [load.center[0], load.power_via[0], load.ground_via[0], source.center[0]]
    ys = [load.center[1], load.power_via[1], load.ground_via[1], source.center[1]]
    for decap in decaps:
        xs.extend([decap.center[0], decap.power_via[0], decap.ground_via[0]])
        ys.extend([decap.center[1], decap.power_via[1], decap.ground_via[1]])
    margin = 4.0e-3 if config.mode == "realistic" else 2.5e-3
    xmin = max(-config.board_width_m / 2.0 + config.power_island_edge_inset_m, min(xs) - margin)
    xmax = min(config.board_width_m / 2.0 - config.power_island_edge_inset_m, max(xs) + margin)
    ymin = max(-config.board_height_m / 2.0 + config.power_island_edge_inset_m, min(ys) - margin)
    ymax = min(config.board_height_m / 2.0 - config.power_island_edge_inset_m, max(ys) + margin)
    return [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]


def _plan_single_rail(
    config: PDNGeneratorConfig,
    rail: RailSpec,
    layers: LayerMap,
    load: TwoPinDevicePlan,
    source: SourcePlan,
    global_occupied: list[tuple[Point, float]],
    decap_start_index: int,
    plan_seed: int,
    rng: random.Random,
) -> tuple[
    RailPlan,
    PowerIslandPlan,
    list[TwoPinDevicePlan],
    list[TracePlan],
    list[tuple[Point, float]],
    int,
]:
    load_variant = (config.load_variants or {})[rail.load_variant]
    source_variant = (config.source_variants or {})[rail.source_variant]
    sequence, mix_metrics = refine_decap_mix(config, rail, rng)
    occupied = list(global_occupied)
    added_occupied: list[tuple[Point, float]] = []
    traces = [
        TracePlan(
            layers.top_layer,
            rail.name,
            _orthogonal_trace(source.power_launches[rail.name], load.power_via),
            config.source_trace_width_m * source_variant.trace_width_scale,
        ),
        TracePlan(
            layers.top_layer,
            config.ground_net_name,
            _orthogonal_trace(source.ground_launches[rail.name], load.ground_via),
            max(config.source_trace_width_m * 0.75, config.via_preset.trace_width_m) * source_variant.trace_width_scale,
        ),
        TracePlan(layers.top_layer, rail.name, [load.power_pin, load.power_via], config.via_preset.trace_width_m),
        TracePlan(layers.top_layer, config.ground_net_name, [load.ground_pin, load.ground_via], config.via_preset.trace_width_m),
    ]

    placement_pattern = rail.placement_pattern
    if placement_pattern == "auto":
        placement_pattern = load_variant.placement_pattern if load_variant.placement_pattern != "auto" else config.placement_pattern
    sectors = _pattern_sectors(placement_pattern, len(sequence))

    decaps: list[TwoPinDevicePlan] = []
    decap_index = decap_start_index
    for family in sequence:
        scaled_min = family.preferred_distance_min_m * load_variant.decap_distance_scale
        scaled_max = family.preferred_distance_max_m * load_variant.decap_distance_scale
        radius_low, radius_high = _role_radius_window(config, family.role, scaled_min, scaled_max)
        accepted = None
        keepout_radius = _device_keepout_radius(family.package, config.via_preset)
        for attempt in range(80):
            sector = sectors[(decap_index + attempt) % len(sectors)]
            angle = rng.uniform(sector[0], sector[1])
            radius = rng.uniform(radius_low, radius_high)
            tangent_rotation = angle + 90.0 + rng.uniform(-8.0, 8.0)
            center = _offset(load.center, _polar(radius, angle))
            if not _is_inside_board(center, keepout_radius, config):
                continue
            candidate = _device_from_center(
                refdes=f"C{decap_index}",
                part_name=family.part_name,
                package=family.package,
                role=family.role,
                center=center,
                rotation_deg=tangent_rotation,
                load_center=load.center,
                power_net=rail.name,
                ground_net=config.ground_net_name,
                via_preset=config.via_preset,
                capacitance_f=family.capacitance_f,
                resistance_ohm=family.esr_ohm,
                inductance_h=family.esl_h,
            )
            if _device_is_valid(candidate, keepout_radius, occupied, config):
                accepted = candidate
                break
        if accepted is None:
            accepted = _fallback_search(rng, decap_index, family, load, keepout_radius, occupied, config, radius_low, radius_high)
        if accepted is None:
            raise ValueError(
                f"Unable to place {family.part_name} for seed {plan_seed} on rail {rail.name}. "
                "Reduce capacitor count, enlarge the board, or loosen placement constraints."
            )
        decaps.append(accepted)
        occupied.append((accepted.center, keepout_radius))
        added_occupied.append((accepted.center, keepout_radius))
        traces.append(TracePlan(layers.top_layer, rail.name, [accepted.power_pin, accepted.power_via], config.via_preset.trace_width_m))
        traces.append(
            TracePlan(layers.top_layer, config.ground_net_name, [accepted.ground_pin, accepted.ground_via], config.via_preset.trace_width_m)
        )
        decap_index += 1

    power_layer = layers.power_plane_layers[0] if layers.power_plane_layers else layers.top_layer
    island_polygon = PolygonPlan(power_layer, rail.name, _power_island_polygon(config, rail, load, source, decaps))
    island = PowerIslandPlan(
        name=f"ISLAND_{rail.name}",
        rail_name=rail.name,
        polygon=island_polygon,
        load_refdes=load.refdes,
        source_name=source.name,
    )
    rail_plan = RailPlan(
        name=rail.name,
        source_group=rail.source_group or source.source_group,
        target_impedance_ohm=mix_metrics["target_impedance_ohm"],
        load_current_a=rail.current_a,
        capacitor_count=len(decaps),
        load_variant=rail.load_variant,
        source_variant=rail.source_variant,
        load_refdes=load.refdes,
        source_name=source.name,
        island_name=island.name,
        decap_refdes=[device.refdes for device in decaps],
        total_capacitance_f=mix_metrics["total_capacitance_f"],
        average_esr_ohm=mix_metrics["average_esr_ohm"],
        average_esl_h=mix_metrics["average_esl_h"],
    )
    return rail_plan, island, decaps, traces, added_occupied, decap_index


def plan_pdn_case(config: PDNGeneratorConfig | None = None, seed: int | None = None) -> PDNGenerationPlan:
    config = resolve_config_defaults(config or PDNGeneratorConfig())
    plan_seed = _DEF_SEED if seed is None else seed
    rng = random.Random(plan_seed)

    stackup = config.stackup_layers()
    layers = _layer_map(stackup)
    outline = PolygonPlan(layers.outline_layer, "", _closed_rectangle(config.board_width_m, config.board_height_m))
    ground_polygon = _closed_rectangle(
        config.board_width_m - 2.0 * config.plane_edge_inset_m,
        config.board_height_m - 2.0 * config.plane_edge_inset_m,
    )
    ground_planes = [PolygonPlan(layer_name, config.ground_net_name, ground_polygon) for layer_name in layers.ground_plane_layers]

    rails = resolve_rail_specs(config)
    anchors = _rail_anchor_points(config, rails)
    global_occupied: list[tuple[Point, float]] = []
    rail_plans: list[RailPlan] = []
    loads: list[TwoPinDevicePlan] = [_build_load_plan(config, rail, anchor, load_index) for load_index, (rail, anchor) in enumerate(zip(rails, anchors), start=1)]
    loads_by_rail = {load.power_net: load for load in loads}
    for rail, load in zip(rails, loads):
        global_occupied.append((load.center, _load_keepout_radius((config.load_variants or {})[rail.load_variant].package)))
    grouped_rails: dict[str, list[RailSpec]] = {}
    for rail in rails:
        grouped_rails.setdefault(rail.source_group or f"SRC_{rail.name}", []).append(rail)
    sources: list[SourcePlan] = []
    sources_by_group: dict[str, SourcePlan] = {}
    islands: list[PowerIslandPlan] = []
    power_planes: list[PolygonPlan] = []
    source_pads: list[RectanglePlan] = []
    feed_traces: list[TracePlan] = []
    decaps: list[TwoPinDevicePlan] = []
    decap_index = 1

    for source_group, group in grouped_rails.items():
        source, source_occupied = _build_source_plan(config, source_group, group, loads_by_rail, layers.top_layer)
        sources.append(source)
        sources_by_group[source_group] = source
        source_pads.extend(source.pads)
        global_occupied.extend(source_occupied)

    for rail in rails:
        rail_plan, island, rail_decaps, rail_traces, occupied_additions, decap_index = _plan_single_rail(
            config=config,
            rail=rail,
            layers=layers,
            load=loads_by_rail[rail.name],
            source=sources_by_group[rail.source_group or f"SRC_{rail.name}"],
            global_occupied=global_occupied,
            decap_start_index=decap_index,
            plan_seed=plan_seed,
            rng=rng,
        )
        rail_plans.append(rail_plan)
        islands.append(island)
        power_planes.append(island.polygon)
        feed_traces.extend(rail_traces)
        decaps.extend(rail_decaps)
        global_occupied.extend(occupied_additions)

    role_order = {"hf": 0, "mid": 1, "bulk": 2}
    decaps.sort(key=lambda device: (device.power_net, role_order[device.role], device.distance_to_load_m, device.refdes))
    loads.sort(key=lambda device: device.refdes)
    return PDNGenerationPlan(
        seed=plan_seed,
        config=config,
        layers=layers,
        stackup=stackup,
        outline=outline,
        ground_planes=ground_planes,
        power_planes=power_planes,
        source_pads=source_pads,
        feed_traces=feed_traces,
        load=loads[0],
        decaps=decaps,
        rails=rail_plans,
        loads=loads,
        sources=sources,
        islands=islands,
    )


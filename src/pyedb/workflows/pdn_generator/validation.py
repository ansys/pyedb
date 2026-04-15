from __future__ import annotations

import math
from typing import Any

from .config import PDNGeneratorConfig
from .placement import PDNGenerationPlan
from .variants import resolve_rail_specs


class PDNGenerationError(RuntimeError):
    """Raised when the generated PDN plan violates expected PDN generation rules."""


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def validate_generator_config(config: PDNGeneratorConfig) -> None:
    """Validate user-facing configuration before building a generation plan."""

    if config.board_width_m <= 0.0 or config.board_height_m <= 0.0:
        raise PDNGenerationError("Board dimensions must be positive.")
    if config.stackup_preset not in {"4L", "6L"}:
        raise PDNGenerationError("Only 4-layer and 6-layer presets are supported.")
    if config.edge_clearance_m < 0.0 or config.plane_edge_inset_m < 0.0 or config.power_island_edge_inset_m < 0.0:
        raise PDNGenerationError("All board and plane clearance parameters must be non-negative.")
    if config.edge_clearance_m * 2.0 >= min(config.board_width_m, config.board_height_m):
        raise PDNGenerationError("Edge clearance consumes the entire board area.")
    if config.load_current_a <= 0.0:
        raise PDNGenerationError("Load current must be positive.")
    if config.max_ripple_v <= 0.0:
        raise PDNGenerationError("Maximum ripple must be positive.")
    if config.target_impedance_ohm is not None and config.target_impedance_ohm <= 0.0:
        raise PDNGenerationError("Target impedance must be positive when provided.")
    if config.capacitor_count is not None and config.capacitor_count < 2:
        raise PDNGenerationError("At least two capacitors are required for ML dataset generation.")
    if config.power_net_name == config.ground_net_name:
        raise PDNGenerationError("Power and ground net names must be distinct.")
    if not config.decap_library:
        raise PDNGenerationError("Decap library must not be empty after defaults are resolved.")
    if config.via_preset is None or config.load_package is None:
        raise PDNGenerationError("Load package and via preset must be resolved before planning.")
    if not config.load_variants or not config.source_variants:
        raise PDNGenerationError("Load/source variants must be resolved before planning.")

    rails = resolve_rail_specs(config)
    rail_names = [rail.name for rail in rails]
    if len(rail_names) != len(set(rail_names)):
        raise PDNGenerationError("Rail names must be unique.")
    if config.ground_net_name in rail_names:
        raise PDNGenerationError("Ground net name cannot also be used as a power rail.")
    for rail in rails:
        if rail.current_a <= 0.0:
            raise PDNGenerationError(f"Rail {rail.name} current must be positive.")
        if rail.max_ripple_v <= 0.0:
            raise PDNGenerationError(f"Rail {rail.name} ripple target must be positive.")
        if rail.load_variant not in config.load_variants:
            raise PDNGenerationError(f"Unknown load variant: {rail.load_variant}")
        if rail.source_variant not in config.source_variants:
            raise PDNGenerationError(f"Unknown source variant: {rail.source_variant}")


def validate_generation_plan(plan: PDNGenerationPlan) -> None:
    """Validate the geometric and electrical intent of a generated PDN plan."""

    config = plan.config
    validate_generator_config(config)

    signal_layers = [layer.name for layer in plan.stackup if layer.layer_type == "signal"]
    if len(signal_layers) not in {4, 6}:
        raise PDNGenerationError(f"Expected 4 or 6 signal/component layers, got {len(signal_layers)}.")
    if len(signal_layers) % 2 != 0:
        raise PDNGenerationError("Signal/component layers must be even in count.")
    if not plan.layers.ground_plane_layers:
        raise PDNGenerationError("A continuous ground plane layer is required.")
    if not plan.layers.power_plane_layers:
        raise PDNGenerationError("At least one VDD-style plane layer is required.")
    if len(plan.loads) != len(plan.rails):
        raise PDNGenerationError("Each rail must have exactly one load plan.")
    if len(plan.sources) > len(plan.rails):
        raise PDNGenerationError("Source plans cannot outnumber rails.")
    if len(plan.islands) != len(plan.rails):
        raise PDNGenerationError("Each rail must have exactly one power island.")
    if len(plan.power_planes) != len(plan.rails):
        raise PDNGenerationError("Each rail must contribute one power-plane/island polygon.")

    total_expected_caps = sum(rail.capacitor_count for rail in plan.rails)
    if len(plan.decaps) != total_expected_caps:
        raise PDNGenerationError(f"Generated {len(plan.decaps)} decaps but rail plans expect {total_expected_caps}.")

    source_names = {source.name for source in plan.sources}
    if len(source_names) != len(plan.sources):
        raise PDNGenerationError("Source plan names must be unique.")
    served_rails = set()
    for source in plan.sources:
        if not source.served_rails:
            raise PDNGenerationError(f"Source {source.name} must serve at least one rail.")
        for rail_name in source.served_rails:
            served_rails.add(rail_name)
            if rail_name not in source.power_launches or rail_name not in source.ground_launches:
                raise PDNGenerationError(f"Source {source.name} is missing launch points for rail {rail_name}.")
    if served_rails != {rail.name for rail in plan.rails}:
        raise PDNGenerationError("Shared-source coverage does not match the planned rail set.")

    seen_refdes: set[str] = set()
    board_half_w = config.board_width_m / 2.0
    board_half_h = config.board_height_m / 2.0
    for device in [*plan.loads, *plan.decaps]:
        if device.refdes in seen_refdes:
            raise PDNGenerationError(f"Duplicate refdes detected: {device.refdes}")
        seen_refdes.add(device.refdes)
        if device.ground_net != config.ground_net_name:
            raise PDNGenerationError(f"{device.refdes} is not tied to the configured ground net.")
        if abs(device.center[0]) >= board_half_w or abs(device.center[1]) >= board_half_h:
            raise PDNGenerationError(f"{device.refdes} center lies outside the board outline.")
        if _distance(device.power_pin, device.power_via) > config.via_preset.pad_to_via_distance_m * 1.35:
            raise PDNGenerationError(f"{device.refdes} power via is too far from its pad.")
        if _distance(device.ground_pin, device.ground_via) > config.via_preset.pad_to_via_distance_m * 1.35:
            raise PDNGenerationError(f"{device.refdes} ground via is too far from its pad.")

    role_rank = {"hf": 0, "mid": 1, "bulk": 2}
    for rail in plan.rails:
        if rail.source_name not in source_names:
            raise PDNGenerationError(f"Rail {rail.name} references missing source {rail.source_name}.")
        rail_decaps = [device for device in plan.decaps if device.power_net == rail.name]
        if len(rail_decaps) != rail.capacitor_count:
            raise PDNGenerationError(f"Rail {rail.name} expected {rail.capacitor_count} decaps but found {len(rail_decaps)}.")
        previous_rank = -1
        previous_distance = -1.0
        role_distances: dict[str, list[float]] = {"hf": [], "mid": [], "bulk": []}
        for device in rail_decaps:
            current_rank = role_rank[device.role]
            current_distance = device.distance_to_load_m
            if current_rank < previous_rank or (current_rank == previous_rank and current_distance < previous_distance):
                raise PDNGenerationError(f"Rail {rail.name} decaps are not ordered deterministically by role and distance.")
            previous_rank = current_rank
            previous_distance = current_distance
            role_distances[device.role].append(current_distance)
        if role_distances["hf"] and role_distances["mid"] and max(role_distances["hf"]) > min(role_distances["mid"]) + 1e-9:
            raise PDNGenerationError(f"Rail {rail.name} high-frequency caps must remain closer than mid-band caps.")
        if role_distances["mid"] and role_distances["bulk"] and max(role_distances["mid"]) > min(role_distances["bulk"]) + 1e-9:
            raise PDNGenerationError(f"Rail {rail.name} mid-band caps must remain closer than bulk caps.")

    for idx, left in enumerate(plan.decaps):
        for right in plan.decaps[idx + 1 :]:
            separation = _distance(left.center, right.center)
            if separation <= config.placement_keepout_m + 0.5e-3:
                raise PDNGenerationError(
                    f"Decaps {left.refdes} and {right.refdes} are unrealistically close ({separation:.6f} m)."
                )

    for trace in plan.feed_traces:
        if len(trace.points) < 2:
            raise PDNGenerationError(f"Trace on {trace.layer_name}/{trace.net_name} has fewer than two points.")
        if trace.width_m <= 0.0:
            raise PDNGenerationError(f"Trace on {trace.layer_name}/{trace.net_name} must use a positive width.")

    expected_ground_planes = 1 if config.stackup_preset == "4L" else 2
    if len(plan.ground_planes) != expected_ground_planes:
        raise PDNGenerationError(
            f"Expected {expected_ground_planes} ground planes for preset {config.stackup_preset}, got {len(plan.ground_planes)}."
        )


def validate_realized_edb(edb: Any, plan: PDNGenerationPlan) -> None:
    """Validate the main artifacts in the realized EDB after generation."""

    if plan.config.ground_net_name not in edb.nets.nets:
        raise PDNGenerationError(f"Missing realized net {plan.config.ground_net_name}.")
    for rail in plan.rails:
        if rail.name not in edb.nets.nets:
            raise PDNGenerationError(f"Missing realized power net {rail.name}.")
    for device in [*plan.loads, *plan.decaps]:
        if device.refdes not in edb.components.instances:
            raise PDNGenerationError(f"Missing realized component {device.refdes}.")
    via_count = len(edb.padstacks.get_via_instance_from_net(plan.config.ground_net_name))
    for rail in plan.rails:
        via_count += len(edb.padstacks.get_via_instance_from_net(rail.name))
    expected_min_vias = 2 * (len(plan.loads) + len(plan.decaps))
    if via_count < expected_min_vias:
        raise PDNGenerationError(f"Realized EDB contains too few vias ({via_count}); expected at least {expected_min_vias}.")


def summarize_generation_plan(plan: PDNGenerationPlan) -> dict[str, Any]:
    """Return a compact, serializable summary for logs and dataset metadata."""

    return {
        "seed": plan.seed,
        "dataset_name": plan.config.dataset_name,
        "label_schema_version": plan.config.label_schema_version,
        "source_topology": plan.config.source_topology,
        "stackup_preset": plan.config.stackup_preset,
        "mode": plan.config.mode,
        "rails": len(plan.rails),
        "sources": len(plan.sources),
        "islands": len(plan.islands),
        "loads": len(plan.loads),
        "decaps": len(plan.decaps),
        "load_variants": sorted({rail.load_variant for rail in plan.rails}),
        "source_variants": sorted({rail.source_variant for rail in plan.rails}),
        "source_groups": {rail.name: rail.source_group for rail in plan.rails},
        "total_capacitance_f": sum(rail.total_capacitance_f for rail in plan.rails),
        "rail_targets_ohm": {rail.name: rail.target_impedance_ohm for rail in plan.rails},
        "role_counts": {
            "hf": sum(1 for device in plan.decaps if device.role == "hf"),
            "mid": sum(1 for device in plan.decaps if device.role == "mid"),
            "bulk": sum(1 for device in plan.decaps if device.role == "bulk"),
        },
        "nets": {
            "ground": plan.config.ground_net_name,
            "power": [rail.name for rail in plan.rails],
        },
    }


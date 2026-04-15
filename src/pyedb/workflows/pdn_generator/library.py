from __future__ import annotations

import random

from .config import DecapFamily, PDNGeneratorConfig, PackageSpec, RailSpec, ViaPreset
from .variants import default_load_variants, default_source_variants


def default_packages() -> dict[str, PackageSpec]:
    return {
        "0201": PackageSpec("0201", 0.60e-3, 0.30e-3, 0.28e-3, 0.26e-3, 0.48e-3, 0.18e-3),
        "0402": PackageSpec("0402", 1.00e-3, 0.50e-3, 0.45e-3, 0.40e-3, 0.82e-3, 0.22e-3),
        "0603": PackageSpec("0603", 1.60e-3, 0.80e-3, 0.70e-3, 0.55e-3, 1.35e-3, 0.30e-3),
        "0805": PackageSpec("0805", 2.00e-3, 1.25e-3, 0.95e-3, 0.85e-3, 1.80e-3, 0.35e-3),
        "LOAD": PackageSpec("LOAD", 3.20e-3, 1.60e-3, 1.15e-3, 0.95e-3, 2.40e-3, 0.40e-3),
    }


def default_via_presets() -> dict[str, ViaPreset]:
    return {
        "compact": ViaPreset("compact", 0.18e-3, 0.38e-3, 0.65e-3, 0.32e-3, 0.20e-3),
        "robust": ViaPreset("robust", 0.20e-3, 0.45e-3, 0.75e-3, 0.36e-3, 0.25e-3),
    }


def default_decap_library() -> list[DecapFamily]:
    packages = default_packages()
    return [
        DecapFamily("C_22N_0201", "CAP_22N_0201_X5R", packages["0201"], "hf", 22e-9, 0.030, 55e-12, 1.1e-3, 3.0e-3, 1.0),
        DecapFamily("C_47N_0201", "CAP_47N_0201_X5R", packages["0201"], "hf", 47e-9, 0.028, 60e-12, 1.1e-3, 3.4e-3, 1.2),
        DecapFamily("C_100N_0402", "CAP_100N_0402_X7R", packages["0402"], "hf", 100e-9, 0.020, 95e-12, 1.5e-3, 4.5e-3, 1.4),
        DecapFamily("C_220N_0402", "CAP_220N_0402_X7R", packages["0402"], "mid", 220e-9, 0.016, 120e-12, 3.0e-3, 6.5e-3, 1.0),
        DecapFamily("C_470N_0402", "CAP_470N_0402_X7R", packages["0402"], "mid", 470e-9, 0.014, 140e-12, 3.5e-3, 7.0e-3, 1.2),
        DecapFamily("C_1U_0603", "CAP_1U_0603_X5R", packages["0603"], "mid", 1.0e-6, 0.012, 220e-12, 5.5e-3, 10.0e-3, 1.3),
        DecapFamily("C_2U2_0603", "CAP_2U2_0603_X5R", packages["0603"], "bulk", 2.2e-6, 0.011, 260e-12, 7.0e-3, 13.0e-3, 1.0),
        DecapFamily("C_4U7_0805", "CAP_4U7_0805_X5R", packages["0805"], "bulk", 4.7e-6, 0.010, 380e-12, 8.5e-3, 16.0e-3, 1.1),
        DecapFamily("C_10U_0805", "CAP_10U_0805_X5R", packages["0805"], "bulk", 10.0e-6, 0.013, 520e-12, 10.0e-3, 18.0e-3, 0.8),
    ]


def default_load_package() -> PackageSpec:
    return default_packages()["LOAD"]


def resolve_config_defaults(config: PDNGeneratorConfig) -> PDNGeneratorConfig:
    if config.decap_library is None:
        config.decap_library = default_decap_library()
    if config.via_preset is None:
        config.via_preset = default_via_presets()["compact" if config.mode == "draft" else "robust"]
    if config.load_package is None:
        config.load_package = default_load_package()
    if config.load_variants is None:
        config.load_variants = default_load_variants()
    if config.source_variants is None:
        config.source_variants = default_source_variants()
    return config


def _distribute(total: int, weights: list[float]) -> list[int]:
    weight_sum = sum(weights)
    raw = [total * weight / weight_sum for weight in weights]
    counts = [int(value) for value in raw]
    remainder = total - sum(counts)
    ranked = sorted(range(len(raw)), key=lambda idx: raw[idx] - counts[idx], reverse=True)
    for idx in ranked[:remainder]:
        counts[idx] += 1
    return counts


def _resolved_target_impedance(rail: RailSpec) -> float:
    if rail.target_impedance_ohm is not None:
        return rail.target_impedance_ohm
    return rail.max_ripple_v / max(rail.current_a, 1e-6)


def _resolved_capacitor_count(config: PDNGeneratorConfig, rail: RailSpec) -> int:
    if rail.capacitor_count is not None:
        return max(2, rail.capacitor_count)
    load_variant = (config.load_variants or default_load_variants())[rail.load_variant]
    base = config.resolved_capacitor_count
    current_factor = max(0.55, rail.current_a / max(config.load_current_a, 1e-6))
    shared_board_factor = 1.0 / (1.0 + 0.25 * max(config.resolved_rail_count - 1, 0))
    scaled = round(base * load_variant.capacitor_multiplier * current_factor * shared_board_factor)
    return max(4, min(24, scaled))


def _role_weights_for_target(config: PDNGeneratorConfig, rail: RailSpec) -> list[float]:
    target_z = _resolved_target_impedance(rail)
    load_variant = (config.load_variants or default_load_variants())[rail.load_variant]
    source_variant = (config.source_variants or default_source_variants())[rail.source_variant]

    if target_z <= 0.005:
        role_weights = [0.56, 0.28, 0.16]
    elif target_z <= 0.010:
        role_weights = [0.50, 0.31, 0.19]
    elif target_z <= 0.020:
        role_weights = [0.42, 0.35, 0.23]
    else:
        role_weights = [0.30, 0.38, 0.32]

    if config.mode == "draft":
        role_weights = [role_weights[0] - 0.04, role_weights[1] + 0.01, role_weights[2] + 0.03]

    if load_variant.name == "fpga_cluster":
        role_weights[0] += 0.05
        role_weights[1] += 0.03
        role_weights[2] -= 0.08
    elif load_variant.name == "connector_load":
        role_weights[0] -= 0.03
        role_weights[2] += 0.03

    if source_variant.name in {"remote_source", "vrm_patch"}:
        role_weights[2] += 0.04
        role_weights[0] -= 0.02
        role_weights[1] -= 0.02

    total = sum(role_weights)
    return [max(weight / total, 0.05) for weight in role_weights]


def refine_decap_mix(config: PDNGeneratorConfig, rail: RailSpec, rng: random.Random) -> tuple[list[DecapFamily], dict[str, float]]:
    """Select a decap mix driven by the rail target impedance and endpoint variants."""

    library = list(rail.decap_library or config.decap_library or default_decap_library())
    total = _resolved_capacitor_count(config, rail)
    role_weights = _role_weights_for_target(config, rail)
    role_counts = dict(zip(("hf", "mid", "bulk"), _distribute(total, role_weights)))

    sequence: list[DecapFamily] = []
    for role in ("hf", "mid", "bulk"):
        choices = [family for family in library if family.role == role]
        if not choices or role_counts[role] <= 0:
            continue
        unique_count = 1 if role_counts[role] <= 3 else min(2, len(choices))
        selected_unique: list[DecapFamily] = []
        if len(choices) <= unique_count:
            selected_unique = list(choices)
        else:
            while len(selected_unique) < unique_count:
                candidate = rng.choices(choices, weights=[family.selection_weight for family in choices], k=1)[0]
                if candidate.name not in {family.name for family in selected_unique}:
                    selected_unique.append(candidate)
        counts = _distribute(role_counts[role], [family.selection_weight for family in selected_unique])
        for family, count in zip(selected_unique, counts):
            sequence.extend([family] * count)

    role_order = {"hf": 0, "mid": 1, "bulk": 2}
    sequence.sort(key=lambda item: (role_order[item.role], item.preferred_distance_min_m, item.capacitance_f, item.name))
    metrics = {
        "target_impedance_ohm": _resolved_target_impedance(rail),
        "capacitor_count": float(len(sequence)),
        "total_capacitance_f": sum(family.capacitance_f for family in sequence),
        "average_esr_ohm": sum(family.esr_ohm for family in sequence) / max(len(sequence), 1),
        "average_esl_h": sum(family.esl_h for family in sequence) / max(len(sequence), 1),
    }
    return sequence, metrics


def select_decap_sequence(config: PDNGeneratorConfig, rng: random.Random, rail: RailSpec | None = None) -> list[DecapFamily]:
    resolved_rail = rail or RailSpec(
        name=config.power_net_name,
        current_a=config.load_current_a,
        max_ripple_v=config.max_ripple_v,
        target_impedance_ohm=config.target_impedance_ohm,
        capacitor_count=config.capacitor_count,
        load_variant="small_ic",
        source_variant="edge_pad",
        placement_pattern=config.placement_pattern,
        decap_library=config.decap_library,
    )
    sequence, _ = refine_decap_mix(config, resolved_rail, rng)
    return sequence


from __future__ import annotations

from .config import LoadVariantSpec, PDNGeneratorConfig, PackageSpec, RailSpec, SourceVariantSpec


def default_load_variants() -> dict[str, LoadVariantSpec]:
    return {
        "small_ic": LoadVariantSpec(
            name="small_ic",
            package=PackageSpec("LOAD_SMALL", 2.60e-3, 1.20e-3, 0.95e-3, 0.75e-3, 1.90e-3, 0.30e-3),
            decap_distance_scale=0.90,
            capacitor_multiplier=0.90,
            placement_pattern="horseshoe",
            preferred_rotation_deg=0.0,
        ),
        "fpga_cluster": LoadVariantSpec(
            name="fpga_cluster",
            package=PackageSpec("LOAD_FPGA", 4.80e-3, 4.80e-3, 1.30e-3, 1.10e-3, 3.40e-3, 0.45e-3),
            decap_distance_scale=1.10,
            capacitor_multiplier=1.35,
            placement_pattern="ring",
            preferred_rotation_deg=0.0,
        ),
        "connector_load": LoadVariantSpec(
            name="connector_load",
            package=PackageSpec("LOAD_CONN", 5.40e-3, 1.40e-3, 1.20e-3, 0.80e-3, 4.10e-3, 0.35e-3),
            decap_distance_scale=1.20,
            capacitor_multiplier=1.00,
            placement_pattern="north_south",
            preferred_rotation_deg=90.0,
        ),
        "multi_pin_module": LoadVariantSpec(
            name="multi_pin_module",
            package=PackageSpec("LOAD_MULTI", 4.10e-3, 2.40e-3, 1.10e-3, 0.90e-3, 3.00e-3, 0.40e-3),
            decap_distance_scale=1.05,
            capacitor_multiplier=1.20,
            placement_pattern="horseshoe",
            preferred_rotation_deg=0.0,
        ),
    }


def default_source_variants() -> dict[str, SourceVariantSpec]:
    return {
        "edge_pad": SourceVariantSpec("edge_pad", 3.5e-3, 1.5e-3, 2.4e-3, 1, 1.00, "left", 0.0),
        "connector": SourceVariantSpec("connector", 2.8e-3, 1.2e-3, 2.0e-3, 2, 1.05, "left", 0.0),
        "vrm_patch": SourceVariantSpec("vrm_patch", 4.5e-3, 2.0e-3, 2.8e-3, 1, 1.40, "left", 0.0),
        "remote_source": SourceVariantSpec("remote_source", 3.2e-3, 1.4e-3, 2.2e-3, 1, 0.90, "top", 0.0),
        "dual_entry": SourceVariantSpec("dual_entry", 3.0e-3, 1.4e-3, 1.8e-3, 2, 1.10, "left", 0.0),
    }


def resolve_rail_specs(config: PDNGeneratorConfig) -> list[RailSpec]:
    """Return the normalized rail list while preserving the existing single-rail API."""

    rails = list(config.rails) if config.rails else []
    if not rails:
        rails = [
            RailSpec(
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
        ]

    normalized: list[RailSpec] = []
    for rail in rails:
        current_a = rail.current_a if rail.current_a > 0.0 else config.load_current_a
        max_ripple_v = rail.max_ripple_v if rail.max_ripple_v > 0.0 else config.max_ripple_v
        if rail.source_group:
            source_group = rail.source_group
        elif config.source_topology == "shared_all":
            source_group = "SRC_MAIN"
        elif config.source_topology == "shared_pairs":
            source_group = f"SRC_PAIR_{len(normalized) // 2 + 1}"
        else:
            source_group = f"SRC_{rail.name}"
        normalized.append(
            RailSpec(
                name=rail.name,
                current_a=current_a,
                max_ripple_v=max_ripple_v,
                target_impedance_ohm=rail.target_impedance_ohm,
                capacitor_count=rail.capacitor_count,
                load_variant=rail.load_variant,
                source_variant=rail.source_variant,
                island_width_m=rail.island_width_m,
                island_height_m=rail.island_height_m,
                center_hint=rail.center_hint,
                placement_pattern=rail.placement_pattern,
                decap_library=rail.decap_library or config.decap_library,
                source_group=source_group,
            )
        )
    return normalized


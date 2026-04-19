from __future__ import annotations

from pathlib import Path
from typing import Any

from pyedb import Edb

from .config import PDNGeneratorConfig, StackupLayerSpec
from .placement import PDNGenerationPlan, RectanglePlan, TwoPinDevicePlan, plan_pdn_case
from .validation import validate_generation_plan, validate_realized_edb


def _ensure_clean_stackup(edb: Any, stackup: list[StackupLayerSpec]) -> None:
    existing = set(edb.stackup.layers.keys())
    conflicts = sorted(existing.intersection({layer.name for layer in stackup}))
    if conflicts:
        raise ValueError(
            "The target EDB already contains stackup layers that conflict with the PDN generator: "
            + ", ".join(conflicts)
        )


def _build_stackup(edb: Any, stackup: list[StackupLayerSpec]) -> None:
    previous_layer = None
    for index, layer in enumerate(stackup):
        kwargs = {
            "layer_type": layer.layer_type,
            "material": layer.material,
            "thickness": layer.thickness_m,
        }
        if layer.fill_material and layer.layer_type != "dielectric":
            kwargs["filling_material"] = layer.fill_material
        if index == 0:
            created = edb.stackup.add_layer(layer.name, **kwargs)
        else:
            created = edb.stackup.add_layer(layer.name, base_layer=previous_layer, method="insert_below", **kwargs)
        if not created:
            raise RuntimeError(f"Failed to create stackup layer {layer.name}.")
        previous_layer = layer.name


def _ensure_outline_layer(edb: Any, outline_layer_name: str) -> None:
    if outline_layer_name in edb.stackup.non_stackup_layers:
        return
    if outline_layer_name == "Outline":
        if not edb.stackup.add_outline_layer():
            raise RuntimeError("Failed to create the default outline layer.")
        return
    document_layer = edb.stackup.add_document_layer(outline_layer_name, layer_type="outline")
    if not document_layer:
        raise RuntimeError(f"Failed to create outline layer {outline_layer_name}.")


def _ensure_nets(edb: Any, plan: PDNGenerationPlan) -> None:
    edb.nets.find_or_create_net(plan.config.ground_net_name)
    for rail in plan.rails:
        edb.nets.find_or_create_net(rail.name)
    if plan.config.include_vin:
        edb.nets.find_or_create_net(plan.config.vin_net_name)


def _create_outline_and_copper(edb: Any, plan: PDNGenerationPlan) -> None:
    edb.modeler.create_polygon(plan.outline.points, plan.outline.layer_name)
    for polygon in [*plan.ground_planes, *plan.power_planes]:
        edb.modeler.create_polygon(points=polygon.points, layer_name=polygon.layer_name, net_name=polygon.net_name)
    for pad in plan.source_pads:
        _create_rectangle(edb, pad)
    for trace in plan.feed_traces:
        edb.modeler.create_trace(path_list=trace.points, layer_name=trace.layer_name, width=trace.width_m, net_name=trace.net_name)


def _create_rectangle(edb: Any, rectangle: RectanglePlan) -> None:
    edb.modeler.create_rectangle(
        layer_name=rectangle.layer_name,
        net_name=rectangle.net_name,
        center_point=list(rectangle.center),
        width=rectangle.width_m,
        height=rectangle.height_m,
        representation_type="center_width_height",
    )


def _ensure_via_definition(edb: Any, name: str, plan: PDNGenerationPlan, stop_layer: str) -> str:
    if name in edb.padstacks.definitions:
        return name
    created = edb.padstacks.create(
        padstackname=name,
        holediam=plan.config.via_preset.hole_diameter_m,
        paddiam=plan.config.via_preset.pad_diameter_m,
        antipaddiam=plan.config.via_preset.antipad_diameter_m,
        start_layer=plan.layers.top_layer,
        stop_layer=stop_layer,
    )
    if not created:
        raise RuntimeError(f"Failed to create via padstack {name}.")
    return name


def _ensure_smd_pad_definition(edb: Any, package_name: str, pad_length_m: float, pad_width_m: float, top_layer: str) -> str:
    definition_name = f"PDN_SMD_{package_name}"
    if definition_name in edb.padstacks.definitions:
        return definition_name
    created = edb.padstacks.create(
        padstackname=definition_name,
        has_hole=False,
        pad_shape="Rectangle",
        antipad_shape="Rectangle",
        x_size=pad_length_m,
        y_size=pad_width_m,
        anti_pad_x_size=pad_length_m * 1.25,
        anti_pad_y_size=pad_width_m * 1.25,
        start_layer=top_layer,
        stop_layer=top_layer,
        add_default_layer=True,
    )
    if not created:
        raise RuntimeError(f"Failed to create SMD padstack {definition_name}.")
    return definition_name


def _resolve_device_package(plan: PDNGenerationPlan, device: TwoPinDevicePlan):
    for variant in (plan.config.load_variants or {}).values():
        if variant.package.name == device.package_name:
            return variant.package
    for family in plan.config.decap_library or []:
        if family.part_name == device.part_name:
            return family.package
    if plan.config.load_package and plan.config.load_package.name == device.package_name:
        return plan.config.load_package
    raise RuntimeError(f"Unable to resolve package for {device.refdes} ({device.package_name}).")


def _place_component(edb: Any, device: TwoPinDevicePlan, plan: PDNGenerationPlan) -> None:
    package = _resolve_device_package(plan, device)
    pin_definition = _ensure_smd_pad_definition(
        edb,
        package_name=package.name,
        pad_length_m=package.pad_length_m,
        pad_width_m=package.pad_width_m,
        top_layer=plan.layers.top_layer,
    )
    # Span the instance through the full stackup (top → bottom).  The EDB gRPC server
    # rejects CorePadstackInstance.create() when top_layer == bottom_layer, which would
    # happen if we let place() auto-resolve layers from the single-layer SMD definition.
    # Real SMD components in EDB always span the full board thickness even though the
    # physical pad only exists on the component layer.
    power_pin = edb.padstacks.place(
        position=list(device.power_pin),
        definition_name=pin_definition,
        net_name=device.power_net,
        via_name=f"{device.refdes}_P",
        rotation=device.rotation_deg,
        from_layer=plan.layers.top_layer,
        to_layer=plan.layers.bottom_layer,
    )
    ground_pin = edb.padstacks.place(
        position=list(device.ground_pin),
        definition_name=pin_definition,
        net_name=device.ground_net,
        via_name=f"{device.refdes}_N",
        rotation=device.rotation_deg,
        from_layer=plan.layers.top_layer,
        to_layer=plan.layers.bottom_layer,
    )

    if power_pin.core.is_null or ground_pin.core.is_null:
        raise RuntimeError(
            f"Failed to place SMD pads for {device.refdes}: EDB server returned a null padstack instance. "
            f"Check that '{pin_definition}' is a valid padstack definition and that layers "
            f"'{plan.layers.top_layer}' and '{plan.layers.bottom_layer}' exist in the stackup."
        )

    power_kwargs = {
        "pins": [power_pin, ground_pin],
        "component_name": device.refdes,
        "placement_layer": plan.layers.top_layer,
        "component_part_name": device.part_name,
        "r_value": device.resistance_ohm,
        "c_value": device.capacitance_f,
        "l_value": device.inductance_h,
    }
    component = edb.components.create(**power_kwargs)
    if not component:
        raise RuntimeError(f"Failed to create component {device.refdes}.")


def _place_vias(edb: Any, device: TwoPinDevicePlan, plan: PDNGenerationPlan, pwr_def: str, gnd_def: str) -> None:
    power_via = edb.padstacks.place(
        position=list(device.power_via),
        definition_name=pwr_def,
        net_name=device.power_net,
        via_name=f"{device.refdes}_P_VIA",
        from_layer=plan.layers.top_layer,
        to_layer=plan.layers.bottom_layer,
    )
    ground_via = edb.padstacks.place(
        position=list(device.ground_via),
        definition_name=gnd_def,
        net_name=device.ground_net,
        via_name=f"{device.refdes}_N_VIA",
        from_layer=plan.layers.top_layer,
        to_layer=plan.layers.bottom_layer,
    )
    if power_via.core.is_null or ground_via.core.is_null:
        raise RuntimeError(f"Failed to place vias for {device.refdes}: EDB server returned a null padstack instance.")


def realize_pdn_plan(edb: Any, plan: PDNGenerationPlan) -> Any:
    """Apply a validated PDN plan to an open EDB instance."""

    validate_generation_plan(plan)
    _ensure_clean_stackup(edb, plan.stackup)
    _build_stackup(edb, plan.stackup)
    _ensure_outline_layer(edb, plan.layers.outline_layer)
    _ensure_nets(edb, plan)
    _create_outline_and_copper(edb, plan)

    power_stop_layer = plan.layers.power_plane_layers[0]
    ground_stop_layer = plan.layers.ground_plane_layers[0]
    pwr_via_def = _ensure_via_definition(edb, f"PDN_PWR_VIA_{power_stop_layer}", plan, power_stop_layer)
    gnd_via_def = _ensure_via_definition(edb, f"PDN_GND_VIA_{ground_stop_layer}", plan, ground_stop_layer)

    for device in [*plan.loads, *plan.decaps]:
        _place_vias(edb, device, plan, pwr_via_def, gnd_via_def)
        _place_component(edb, device, plan)

    validate_realized_edb(edb, plan)
    return edb


def generate_pdn_dataset_case(
    output_aedb_path: str | Path,
    config: PDNGeneratorConfig | None = None,
    seed: int | None = None,
    *,
    version: str | None = None,
    grpc: bool | None = True,
    save: bool = True,
    close_edb: bool = True,
) -> PDNGenerationPlan:
    """Create a randomized PDN-only AEDB suitable for ML dataset generation."""

    plan = plan_pdn_case(config=config, seed=seed)
    output_aedb_path = Path(output_aedb_path)
    output_aedb_path.parent.mkdir(parents=True, exist_ok=True)
    edb = Edb(edbpath=str(output_aedb_path), version=version, grpc=grpc)
    try:
        realize_pdn_plan(edb, plan)
        if save:
            edb.save()
    finally:
        if close_edb:
            edb.close()
    return plan


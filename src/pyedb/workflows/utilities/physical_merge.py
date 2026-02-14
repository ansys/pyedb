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

from time import time
from typing import Union

from ansys.edb.core.primitive.padstack_instance import PadstackInstance as CorePadstackInstance
from ansys.edb.core.utility.layer_map import (
    LayerMap as CoreLayerMap,
    LayerMapUniqueDirection as CoreLayerMapUniqueDirection,
)

from pyedb import Edb
from pyedb.workflows.utilities.helpers import finish_progress, print_progress

layer_mapping = {
    "two_way": CoreLayerMapUniqueDirection.TWOWAY_UNIQUE,
    "forward": CoreLayerMapUniqueDirection.FORWARD_UNIQUE,
    "backward": CoreLayerMapUniqueDirection.BACKWARD_UNIQUE,
}
cache_padstack_def = {}
cache_layers = {}


def _layer_mapping(direction):
    core_layer_map = CoreLayerMap.create(layer_mapping[direction])
    return core_layer_map


def __add_layers_to_hosting_edb(hosting_edb, merged_edb, base_layer, prefix, on_top, grpc):
    if on_top:
        layers = dict(reversed(merged_edb.stackup.layers.items()))
        add_method = "add_on_top"
    else:
        layers = merged_edb.stackup.layers
        add_method = "add_below"
    for layer_name, layer in layers.items():
        hosting_edb.stackup.add_layer(
            layer_name=f"{prefix}{layer_name}",
            base_layer=base_layer,
            method=add_method,
            material=layer.material,
            thickness=layer.thickness,
            layer_type=layer.type,
        )
        base_layer = hosting_edb.stackup.layers[f"{prefix}{layer_name}"]
        if grpc:
            cache_layers[f"{prefix}{layer_name}"] = base_layer.core
        else:
            cache_layers[f"{prefix}{layer_name}"] = base_layer
        if base_layer.type == "signal":
            base_layer.fill_material = layer.fill_material
        hosting_edb.logger.info(f"Layer {layer_name} added as {prefix}{layer_name} to main board.")


def _get_contact_layer(hosting_edb, on_top) -> str:
    """Retrieve the name of the contact layer in the hosting EDB, which will be used as reference for adding
    the merged layers.

    Parameters
    ----------
    hosting_edb : Edb
        The EDB that will host the merged primitives.
    on_top : bool
        If True, the primitives from the merged_edb will be placed on top of the hosting_edb primitives.
        If False, they will be placed below. This affects the search order for the

    Returns
    -------
    str
        The name of the contact layer in the hosting EDB.
    """
    if on_top:
        layers = hosting_edb.stackup.layers
    else:
        layers = dict(reversed(hosting_edb.stackup.layers.items()))
    for layer_name, layer in layers.items():
        if layer.type == "signal":
            hosting_edb.logger.info(f"Layer {layer_name} found as is a signal for contact {layer.thickness}.")
            contact_layer = layer
            return contact_layer.name
    raise ValueError("No contact layer found in the hosting EDB. At least one metal layer is required for merging.")


def _add_definitions_to_hosting_edb(hosting_edb, merged_edb, prefix):
    hosting_edb.logger.info(f"Loading merged EDB definitions.")
    for padstack_def_name, padstack_def in merged_edb.padstacks.definitions.items():
        new_def_name = hosting_edb.padstacks.create(f"{prefix}{padstack_def_name}")
        new_def = hosting_edb.padstacks.definitions[new_def_name]
        new_def.core.data = padstack_def.core.data
        cache_padstack_def[new_def_name] = new_def.core


def physical_merge(
    hosting_edb,
    merged_edb: Union[str, Edb],
    on_top=True,
    vector=(0.0, 0.0),
    prefix="merged_",
    show_progress: bool = True,
) -> bool:
    """Merge two EDBs together by copying the primitives from the merged_edb into the hosting_edb.

    Parameters
    ----------
    hosting_edb : Edb
        The EDB that will host the merged primitives.
    merged_edb : str, Edb
        Aedb folder path or The EDB that will be merged into the hosting_edb.
    on_top : bool, optional
        If True, the primitives from the merged_edb will be placed on top of the hosting_edb primitives.
        If False, they will be placed below. Default is True.
    vector : tuple, optional
        A tuple (x, y) representing the offset to apply to the primitives from the merged. Default is (0.0, 0.0).
    prefix : str, optional
        A prefix to add to the layer names of the merged primitives to avoid name clashes. Default is "merged_."
    show_progress : bool, optional
        If True, print progress to stdout during long operations (primitives/padstacks merging). Default is True.

    Returns
    -------
    bool
        True if the merge was successful, False otherwise.

    """
    version = hosting_edb.version
    grpc = hosting_edb.grpc
    layout = hosting_edb.layout.core
    if not grpc:
        raise NotImplementedError(
            "Feature only available with gRPC EDB. Please initialize hosting_edb with grpc=True to use this function."
        )
    # Loading merged EDB if path provided, otherwise using the provided EDB object
    if isinstance(merged_edb, str):
        hosting_edb.logger.info(f"Loading merged EDB from path: {merged_edb}")
        merged_edb = Edb(edbpath=merged_edb, version=version, grpc=grpc)

    # caching hosting_edb layers to improve performances
    for layer_name, layer in hosting_edb.stackup.layers.items():
        cache_layers[layer_name] = layer.core

    # contact layer from where design is merged.
    contact_layer = _get_contact_layer(hosting_edb=hosting_edb, on_top=on_top)

    # adding layers from merged EDB to hosting EDB
    __add_layers_to_hosting_edb(
        hosting_edb=hosting_edb,
        merged_edb=merged_edb,
        base_layer=contact_layer,
        prefix=prefix,
        on_top=on_top,
        grpc=grpc,
    )

    # adding definitions
    _add_definitions_to_hosting_edb(hosting_edb=hosting_edb, merged_edb=merged_edb, prefix=prefix)

    # adding primitives
    primitives = merged_edb.modeler.primitives
    hosting_edb.logger.info(f"Merging primitives from merged EDB. Total primitives to merge: {len(primitives)}.")
    start = time()
    total_primitives = len(primitives)
    primitive_count = 0
    # print initial progress (0/total)
    if show_progress:
        print_progress(0, total_primitives, start, prefix_desc="Merging primitives")
    for primitive in primitives:
        primitive_count += 1
        # update terminal progress every 100 items or on last item
        if primitive_count % 100 == 0 or primitive_count == total_primitives:
            if show_progress:
                print_progress(primitive_count, total_primitives, start, prefix_desc="Merging primitives")
        primitive_type = primitive.type
        layer_name = f"{prefix}{primitive.layer.name}"
        if layer_name not in cache_layers:
            if primitive.layer.name in hosting_edb.stackup.non_stackup_layers:
                layer_name = primitive.layer.name
            else:
                layer_name = None
        if primitive_type in ["polygon", "rectangle"]:
            polygon_data = primitive.polygon_data
            polygon_data = polygon_data.core.move(vector)
            voids = []
            for void in primitive.voids:
                void_polygon_data = void.polygon_data
                void_polygon_data = void_polygon_data.core.move(vector)
                voids.append(void_polygon_data)
            if layer_name:
                hosting_edb.modeler.create_polygon(
                    points=polygon_data,
                    layer_name=layer_name,
                    net_name=primitive.net.name,
                    voids=voids,
                )
        elif primitive_type == "circle":
            if hasattr(primitive, "get_parameters") and hasattr(primitive, "set_parameters"):
                center_x, center_y, radius = primitive.get_parameters()
                center_x += vector[0]
                center_y += vector[1]
                if layer_name:
                    hosting_edb.modeler.create_circle(layer_name=layer_name, x=center_x, y=center_y, radius=radius)
        elif primitive_type == "path":
            if hasattr(primitive, "width"):
                width = primitive.width
                center_line = primitive.core.center_line
                center_line = center_line.move(vector)
                hosting_edb.modeler.create_trace(
                    path_list=center_line,
                    layer_name=layer_name,
                    width=width,
                    net_name=primitive.net.name,
                )
        else:
            print(f"Primitive type {primitive_type} not supported for merging and will be skipped.")
    stop = time()
    # ensure progress line ends with newline so following logs don't continue the same line
    finish_progress()
    elapsed = stop - start
    hosting_edb.logger.info(f"Merging primitives from merged EDB completed in {elapsed} seconds.")

    padstack_instances = list(merged_edb.padstacks.instances.values())
    hosting_edb.logger.info(
        f"Merging padstack instances from merged EDB. Total padstack instances to merge: {len(padstack_instances)}."
    )
    start = time()
    total_padstacks = len(padstack_instances)
    components_dict = {}
    padstack_count = 0
    if show_progress:
        # print initial progress (0/total)
        print_progress(0, total_padstacks, start, prefix_desc="Merging padstacks")
    for padstack_inst in padstack_instances:
        padstack_count += 1
        # update terminal progress every 50 items or on last item
        if padstack_count % 50 == 0 or padstack_count == total_padstacks:
            if show_progress:
                print_progress(padstack_count, total_padstacks, start, prefix_desc="Merging padstacks")

        position = padstack_inst.position
        x = hosting_edb.value(position[0] + vector[0])
        y = hosting_edb.value(position[1] + vector[1])
        rotation = hosting_edb.value(padstack_inst.rotation)
        from_layer = cache_layers[f"{prefix}{padstack_inst.start_layer}"]
        to_layer = cache_layers[f"{prefix}{padstack_inst.stop_layer}"]
        net = padstack_inst.net.core
        name = f"{prefix}{padstack_inst.name}"
        padstack_definition = cache_padstack_def[f"{prefix}{padstack_inst.definition.name}"]
        inst = CorePadstackInstance.create(
            layout=layout,
            net=net,
            padstack_def=padstack_definition,
            position_x=x,
            position_y=y,
            rotation=rotation,
            top_layer=from_layer,
            bottom_layer=to_layer,
            name=name,
            solder_ball_layer=None,
            layer_map=_layer_mapping("two_way"),
        )
        inst.is_pin = padstack_inst.is_pin
        if hasattr(padstack_inst, "component"):
            if padstack_inst.component:
                components_dict.setdefault(padstack_inst.component.name, []).append(inst)
    # finish progress line
    finish_progress()

    if components_dict:
        for ref_des, pins in components_dict.items():
            hosting_edb.logger.info(f"Merging component {ref_des}.")
            origin_comp = merged_edb.components[ref_des]
            is_rlc = False
            if origin_comp.type.lower() in ["resistor", "capacitor", "inductor"]:
                is_rlc = True
            try:
                hosting_edb.components.create(
                    pins=pins,
                    component_name=f"{prefix}{ref_des}",
                    component_part_name=f"{prefix}{origin_comp.part_name}",
                    placement_layer=f"{prefix}{origin_comp.placement_layer}",
                    is_rlc=is_rlc,
                    r_value=origin_comp.rlc_values[0],
                    l_value=origin_comp.rlc_values[1],
                    c_value=origin_comp.rlc_values[2],
                )
            except Exception as e:
                hosting_edb.logger.warning(f"Failed to create component {ref_des} during merge: {e}")
    stop = time()
    elapsed = stop - start
    hosting_edb.logger.info(f"Merging padstack instances from merged EDB completed in {elapsed} seconds.")
    merged_edb.close(terminate_rpc_session=False)  # do not terminate rpc session main edb is still open.
    hosting_edb.modeler.clear_cache()
    return True

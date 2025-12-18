# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""
This module contains the array building feature from unit cell.
"""

import itertools
from typing import Optional, Union
import warnings

from pyedb import Edb
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.misc.decorators import execution_timer


# ----------------------
# Public api
# ----------------------
def create_array_from_unit_cell(
    edb: Edb,
    x_number: int = 2,
    y_number: int = 2,
    offset_x: Optional[Union[int, float, str]] = None,
    offset_y: Optional[Union[int, float, str]] = None,
) -> bool:
    """
    Create a 2-D rectangular array from the current EDB unit cell.

    The function duplicates every primitive (polygon, rectangle, circle), path,
    padstack via, and component found in the active layout and places copies on
    a regular grid defined by *offset_x* and *offset_y*. If the offsets are
    omitted they are automatically derived from the bounding box of the first
    primitive found on the layer called **outline** (case-insensitive).

    Parameters
    ----------
    edb : pyedb.Edb
        An open Edb instance whose active layout is used as the unit cell.
    x_number : int, optional
        Number of columns (X-direction). Must be > 0.  Defaults to 2.
    y_number : int, optional
        Number of rows (Y-direction). Must be > 0.  Defaults to 2.
    offset_x : int | float | str, None, optional
        Horizontal pitch (distance between cell origins).  When *None* the
        value is derived from the outline geometry.
    offset_y : int | float | str, None, optional
        Vertical pitch (distance between cell origins).  When *None* the
        value is derived from the outline geometry.

    Returns
    -------
    bool
        ``True`` if the operation completed successfully.

    Raises
    ------
    ValueError
        If *x_number* or *y_number* are non-positive.
    RuntimeError
        If no outline is found and the offsets were not supplied, or if the
        outline is not a supported type (polygon/rectangle).

    Notes
    -----
    The routine is technology-agnostic; it delegates all EDB-specific calls to
    small adapter classes that handle either the **gRPC** or **.NET** back-end
    transparently.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb("unit_cell.aedb")
    >>> create_array_from_unit_cell(edb, x_number=4, y_number=3)
    True
    """
    if edb.grpc:
        adapter = _GrpcAdapter(edb)
    else:
        adapter = _DotNetAdapter(edb)
        warnings.warn(".NET back-end is deprecated and will be removed in future releases.", UserWarning)
        warnings.warn("Consider moving to PyEDB gRPC (ANSYS 2025R2) for better performances", UserWarning)
    return __create_array_from_unit_cell_impl(edb, adapter, x_number, y_number, offset_x, offset_y)


# ------------------------------------------------------------------
# Implementation (technology-agnostic)
# ------------------------------------------------------------------
@execution_timer("create_array_from_unit_cell")
def __create_array_from_unit_cell_impl(
    edb: Edb,
    adapter: "_BaseAdapter",
    x_number: int,
    y_number: int,
    offset_x: Optional[Union[int, float]],
    offset_y: Optional[Union[int, float]],
) -> bool:
    """
    Inner worker that performs the actual replication.

    Parameters
    ----------
    edb : pyedb.Edb
        Edb instance (already validated by the façade).
    adapter : _BaseAdapter
        Technology-specific adapter (gRPC or .NET).
    x_number : int
        Number of columns.
    y_number : int
        Number of rows.
    offset_x : float
        Absolute pitch in X (always resolved by the caller).
    offset_y : float
        Absolute pitch in Y (always resolved by the caller).

    Returns
    -------
    bool
        ``True`` when finished.
    """
    # ---------- Sanity & auto-pitch detection ----------
    if x_number <= 0 or y_number <= 0:
        raise ValueError("x_number and y_number must be positive integers")
    if offset_x and not offset_y:
        raise ValueError("If offset_x is provided, offset_y must be provided as well")
    if offset_y and not offset_x:
        raise ValueError("If offset_y is provided, offset_x must be provided as well")

    if not offset_x and not offset_y:
        edb.logger.info("Auto-detecting outline extents")
        outline_prims = [p for p in edb.modeler.primitives if p.layer_name.lower() == "outline"]
        if not outline_prims:
            raise RuntimeError("No outline found. Provide offset_x / offset_y or add an 'Outline' layer primitive.")
        outline = outline_prims[0]
        if not adapter.is_supported_outline(outline):
            raise RuntimeError("Outline primitive is not a polygon/rectangle. Provide offset_x / offset_y.")
        offset_x, offset_y = adapter.pitch_from_outline(outline)
    offset_x = edb.value(offset_x)
    offset_y = edb.value(offset_y)

    # ---------- Collect everything we have to replicate ----------
    primitives = [p for p in edb.modeler.primitives if adapter.is_primitive_to_copy(p)]
    paths = list(edb.modeler.paths)
    vias = list(edb.padstacks.vias.values())
    components = list(edb.components.instances.values())
    pingroups = edb.layout.pin_groups
    if edb.grpc:
        pg_dict = {
            pad.edb_uid: pg.name  # edb_uid → PinGroup.name
            for pg in pingroups  # for every PinGroup
            for pad in pg.pins.values()  # for every PadstackInstance in its pin-dict
        }
    else:
        pg_dict = {
            pad.id: pg.name  # edb_uid → PinGroup.name
            for pg in pingroups  # for every PinGroup
            for pad in pg.pins.values()  # for every PadstackInstance in its pin-dict
        }

    # ---------- Replication loops ----------
    edb.logger.info(f"Starting array replication {x_number}×{y_number}")
    total_number = x_number * y_number - 1  # minus original
    cell_count = 0
    for i, j in itertools.product(range(x_number), range(y_number)):
        if i == 0 and j == 0:
            continue  # original already exists
        dx = edb.value(offset_x * i)
        dy = edb.value(offset_y * j)
        # Components
        for comp in components:
            adapter.duplicate_component(comp, dx, dy, i, j, pin_groups=pg_dict)
        # Primitives & voids
        for prim in primitives:
            if not prim.is_void:
                adapter.duplicate_primitive(prim, dx, dy, i, j)
        # Paths
        for path in paths:
            adapter.duplicate_path(path, dx, dy, i, j)
        # Stand-alone vias
        for via in (v for v in vias if not v.component):
            adapter.duplicate_standalone_via(via, dx, dy, i, j)
        cell_count += 1
        edb.logger.info(f"Replicated cell {cell_count} of {total_number} ({(cell_count / total_number) * 100:.1f}%)")
    edb.logger.info("Array replication finished successfully")
    return True


# ------------------------------------------------------------------
# Technology-specific adapters
# ------------------------------------------------------------------
class _BaseAdapter:
    """Abstract adapter defining the required interface."""

    def __init__(self, edb: Edb):
        self.edb = edb
        self.layers = edb.stackup.layers
        self.active_layout = edb.active_layout

    # ---- Outline helpers ----
    def is_supported_outline(self, outline) -> bool:
        """Return True when *outline* is a primitive type from which pitch can be inferred."""
        raise NotImplementedError

    def pitch_from_outline(self, outline) -> tuple[float, float]:
        """
        Compute the (offset_x, offset_y) pitch from the bounding box of *outline*.

        Returns
        -------
        tuple[float, float]
            (width, height) of the outline primitive in database units.
        """
        raise NotImplementedError

    # ---- Duplication helpers ----
    def is_primitive_to_copy(self, prim) -> bool:
        """Return True when *prim* is a primitive that must be duplicated."""
        raise NotImplementedError

    def duplicate_primitive(self, prim, dx, dy, i, j):
        """Return a new primitive translated by (dx, dy)."""
        raise NotImplementedError

    def duplicate_path(self, path, dx, dy, i, j):
        """Create a translated copy of *path*."""
        raise NotImplementedError

    def duplicate_standalone_via(self, via, dx, dy, i, j):
        """Create a translated copy of a stand-alone via."""
        raise NotImplementedError

    def duplicate_component(self, comp, dx, dy, i, j, pin_groups=None):
        """Create a translated copy of *comp* (including its pins)."""
        raise NotImplementedError


class _GrpcAdapter(_BaseAdapter):
    """Adapter for the gRPC-based EDB back-end."""

    def is_supported_outline(self, outline) -> bool:
        return outline.type in {"polygon", "rectangle"}

    def pitch_from_outline(self, outline):
        bbox = outline.polygon_data.bounding_box
        return self.edb.value(bbox[1][0] - bbox[0][0]), self.edb.value(bbox[1][1] - bbox[0][1])

    def is_primitive_to_copy(self, prim):
        return prim.type in {"polygon", "rectangle", "circle"}

    def duplicate_primitive(self, prim, dx, dy, i, j):
        moved_pd = prim.polygon_data.core.move((dx, dy))
        voids = [voids.polygon_data.core.move((dx, dy)) for voids in prim.voids]
        return self.edb.modeler.create_polygon(
            moved_pd, layer_name=prim.layer.name, net_name=prim.net.name, voids=voids
        )

    def duplicate_path(self, path, dx, dy, i, j):
        moved_line = path.core.polygon_data.move((dx, dy))
        self.edb.modeler.create_trace(
            moved_line,
            width=path.width,
            layer_name=path.layer.name,
            net_name=path.net.name,
            corner_style=path.corner_style,
            start_cap_style=path.end_cap1,
            end_cap_style=path.end_cap2,
        )

    def duplicate_standalone_via(self, via, dx, dy, i, j):
        pos = via.position
        PadstackInstance.create(
            self.active_layout,
            net=via.net,
            name=f"{via.name}_X{i}_Y{j}",
            padstack_definition=via.definition,
            position_x=pos[0] + dx,
            position_y=pos[1] + dy,
            rotation=0.0,
            top_layer=self.layers[via.start_layer],
            bottom_layer=self.layers[via.stop_layer],
        )

    def duplicate_component(self, comp, dx, dy, i, j, pin_groups=None):
        new_pins = []
        _pg = {}
        for pin in comp.pins.values():
            pg_name = pin_groups.get(pin.edb_uid, None) if pin_groups else None
            pos = pin.position
            new_pin = PadstackInstance.create(
                self.edb.active_layout,
                net=pin.net,
                name=f"{pin.name}_i{i}_j{j}",
                padstack_def=self.edb.padstacks.definitions[pin.padstack_definition],
                position_x=pos[0] + dx,
                position_y=pos[1] + dy,
                rotation=0.0,
                top_layer=self.edb.stackup.layers[pin.start_layer],
                bottom_layer=self.edb.stackup.layers[pin.stop_layer],
            )
            new_pins.append(new_pin)
            if pg_name:
                _pg.setdefault(pg_name, []).append(new_pin)

        if new_pins:
            res = self.edb.value(comp.res_value) if hasattr(comp, "res_value") and comp.res_value else None
            cap = self.edb.value(comp.cap_value) if hasattr(comp, "cap_value") and comp.cap_value else None
            ind = self.edb.value(comp.ind_value) if hasattr(comp, "ind_value") and comp.ind_value else None
            new_comp = self.edb.components.create(
                pins=new_pins,
                component_name=f"{comp.name}_array_{i}_{j}",
                placement_layer=comp.placement_layer,
                component_part_name=comp.part_name,
                r_value=res,
                l_value=ind,
                c_value=cap,
            )
            new_comp.type = comp.type
            if hasattr(comp, "component_property") and comp.component_property:
                new_comp.component_property = comp.component_property
            for pg_name, pins in _pg.items():
                self.edb.components.create_pingroup_from_pins(pins=pins, group_name=f"{pg_name}_{i}_{j}")


class _DotNetAdapter(_BaseAdapter):
    """Adapter for the legacy .NET-based EDB back-end."""

    def is_supported_outline(self, outline) -> bool:
        return outline.type.lower() in {"polygon", "rectangle"}

    def pitch_from_outline(self, outline):
        bbox = outline.polygon_data.bounding_box
        return self.edb.value(bbox[1][0] - bbox[0][0]), self.edb.value(bbox[1][1] - bbox[0][1])

    def is_primitive_to_copy(self, prim):
        return prim.type.lower() in {"polygon", "rectangle", "circle"}

    def duplicate_primitive(self, prim, dx, dy, i, j):
        from pyedb.dotnet.database.geometry.point_data import PointData

        vector = PointData.create_from_xy(self.edb, x=dx, y=dy)
        moved_pd = prim.polygon_data
        moved_pd._edb_object.Move(vector._edb_object)
        return self.edb.modeler.create_polygon(
            moved_pd,
            layer_name=prim.layer.name,
            net_name=prim.net.name,
        )

    def duplicate_path(self, path, dx, dy, i, j):
        from pyedb.dotnet.database.geometry.point_data import PointData

        vector = PointData.create_from_xy(self.edb, x=dx, y=dy)
        moved_path = path._edb_object.GetCenterLine()
        moved_path.Move(vector._edb_object)
        moved_path = [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(moved_path.Points)]
        end_caps = path._edb_object.GetEndCapStyle()

        self.edb.modeler.create_trace(
            path_list=list(moved_path),
            width=path.width,
            layer_name=path.layer.name,
            net_name=path.net.name,
            start_cap_style=str(end_caps[1]),
            end_cap_style=str(end_caps[2]),
        )

    def duplicate_standalone_via(self, via, dx, dy, i, j):
        pos = via.position
        self.edb.padstacks.place(
            [pos[0] + dx, pos[1] + dy],
            via.padstack_definition,
            via_name=f"{via.aedt_name}_i{i}_j{j}",
        )

    def duplicate_component(self, comp, dx, dy, i, j, pin_groups=None):
        new_pins = []
        for pin in comp.pins.values():
            pos = pin.position
            new_pin = self.edb.padstacks.place(
                [pos[0] + dx, pos[1] + dy],
                pin.padstack_definition,
                via_name=f"{pin.aedt_name}_i{i}_j{j}",
            )
            new_pins.append(new_pin)
        if new_pins:
            new_comp = self.edb.components.create(
                pins=new_pins,
                component_name=f"{comp.name}_array_{i}_{j}",
                placement_layer=comp.placement_layer,
                component_part_name=comp.part_name,
            )
            if hasattr(comp, "component_property"):
                new_comp._edb_object.SetComponentProperty(comp.component_property)

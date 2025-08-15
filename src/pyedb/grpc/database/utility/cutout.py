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

"""
NumPy-free, performance-neutral version of the original cut-out helper.
Only the parts that interacted with NumPy were adjusted.
"""

from __future__ import annotations

import concurrent.futures as _cf
from functools import lru_cache
from typing import Any, Sequence, Tuple

from ansys.edb.core.geometry.polygon_data import ExtentType as GrpcExtentType
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

from pyedb.misc.decorators import execution_timer


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------
def _safe_net_name(obj) -> str | None:
    """Return obj.net.name if both exist, else None."""
    try:
        net = getattr(obj, "net", None)
        return net.name if net else None
    except Exception:
        return None


# ------------------------------------------------------------------
# Geometry helpers
# ------------------------------------------------------------------
def extent_from_nets(edb, sig, exp, ext_type, **kw):
    """Compute clipping polygon from net lists."""
    nets = [n for n in edb.layout.nets if n.name in sig]
    ext_type = ext_type.lower()

    if ext_type in {"conforming", "conformal", "convex_hull", "convexhull"}:
        poly = edb.layout.expanded_extent(
            nets=nets,
            extent=GrpcExtentType.CONFORMING,
            expansion_factor=exp,
            expansion_unitless=False,
            use_round_corner=kw.get("use_round_corner", False),
            num_increments=1,
        )
        if ext_type in {"convex_hull", "convexhull"}:
            poly = GrpcPolygonData.convex_hull(poly)
    elif ext_type in {"bounding", "bounding_box", "bbox", "boundingbox"}:
        poly = edb.layout.expanded_extent(
            nets=nets,
            extent=GrpcExtentType.BOUNDING_BOX,
            expansion_factor=exp,
            expansion_unitless=False,
            use_round_corner=kw.get("use_round_corner", False),
            num_increments=1,
        )
    else:
        raise ValueError(f"Unknown extent type: {ext_type}. " "Supported: 'Conforming', 'ConvexHull', 'BoundingBox'.")

    return [(pt.x.value, pt.y.value) for pt in poly.points]


def classify_intersection(
    poly1_pts: list[tuple[float, float]],
    poly2_pts: list[tuple[float, float]],
) -> Tuple[bool, str]:
    """
    Returns
    -------
    intersects : bool
    relation   : str
        One of {"disjoint", "within", "covered_by", "touches", "overlaps"}
    """
    poly1 = ShapelyPolygon(poly1_pts)
    poly2 = ShapelyPolygon(poly2_pts)

    # Cheapest tests first
    if poly1.disjoint(poly2):
        return False, "disjoint"
    if poly2.contains(poly1):
        return True, "within"
    if poly2.covers(poly1):
        return True, "covered_by"
    if poly1.touches(poly2):
        return True, "touches"
    return True, "overlaps"


def point_inside(poly_pts: list[tuple[float, float]], pt: tuple[float, float]) -> bool:
    """True if pt lies inside or on the boundary of poly_pts."""
    return ShapelyPolygon(poly_pts).contains(ShapelyPoint(pt))


# ------------------------------------------------------------------
# Pin/primitive filtering (NumPy-free)
# ------------------------------------------------------------------
def pick_pins(
    pin_handles: list[Any],
    net_list: list[str | None],
    xy_list: list[tuple[float, float]],
    keep_nets: set[str],
    extent_pts: list[tuple[float, float]],
) -> list[Any]:
    """
    Return pins whose net is in keep_nets **and** whose location is
    **outside** the clipping polygon (i.e. to be deleted).
    """
    poly = ShapelyPolygon(extent_pts)

    to_delete = []
    for h, net, (x, y) in zip(pin_handles, net_list, xy_list):
        if net in keep_nets and not poly.contains(ShapelyPoint(x, y)):
            to_delete.append(h)
    return to_delete


@lru_cache(maxsize=1)
def _cached_pin_array(edb):
    pins = list(edb.padstacks.instances.values())
    handles = pins
    nets = [_safe_net_name(p) for p in pins]
    xy = [(p.position[0], p.position[1]) for p in pins]
    return handles, nets, xy


@lru_cache(maxsize=1)
def _cached_primitive_array(edb):
    handles, nets, pts_per_prim = [], [], []
    for p in edb.modeler.primitives:
        net_name = _safe_net_name(p)
        poly_data = getattr(p, "polygon_data", None)
        pts = [(pt.x.value, pt.y.value) for pt in poly_data.points] if poly_data else None
        handles.append(p)
        nets.append(net_name)
        pts_per_prim.append(pts)
    return handles, nets, pts_per_prim


def classify_primitives_batch(
    handles: list[Any],
    net_list: list[str | None],
    pts_per_prim: list[list[tuple[float, float]] | None],
    keep_nets: set[str],
    extent_pts: list[tuple[float, float]],
    reference_nets: set[str],
) -> tuple[list[Any], list[tuple[Any, list[Any]]]]:
    """
    Classify primitives into:
        * to_delete  – primitives that should be removed entirely
        * to_clip    – primitives that should be clipped to the extent
    """
    prims_del, prims_clip = [], []
    ext_poly = ShapelyPolygon(extent_pts)

    for handle, net_name, pts in zip(handles, net_list, pts_per_prim):
        # Net filter
        if net_name is None or net_name not in keep_nets:
            prims_del.append(handle)
            if getattr(handle, "has_void", None) is not None:
                prims_del.extend(handle.voids)
            continue

        # Geometry filter
        if pts is None or len(pts) < 3:
            prims_del.append(handle)
            continue

        poly = ShapelyPolygon(pts)
        if poly.disjoint(ext_poly):
            prims_del.append(handle)
            continue

        # Reference nets that need clipping
        if reference_nets and net_name in reference_nets:
            voids_to_keep = []
            if getattr(handle, "has_voids", False):
                for v in handle.voids:
                    void_pts = [(pt.x.value, pt.y.value) for pt in v.polygon_data.without_arcs().points]
                    if classify_intersection(void_pts, extent_pts)[0]:
                        voids_to_keep.append(v)
            prims_clip.append((handle, voids_to_keep))

    return prims_del, prims_clip


# ------------------------------------------------------------------
# Main worker
# ------------------------------------------------------------------
@execution_timer("_cutout_worker")
def cutout_worker(
    edb,
    extent_points: list[tuple[float, float]],
    output_path: str | None,
    open_when_done: bool,
    signal_nets: Sequence[str] | None,
    reference_nets: Sequence[str] | None,
    **kw,
) -> bool:
    keep_nets = set((signal_nets or [])) | set((reference_nets or []))
    reference_nets = set(reference_nets or [])
    if not keep_nets:
        raise ValueError("No nets specified to keep.")

    legacy_path = edb.edbpath
    edb.save_as(output_path) if output_path else edb.save()

    # ------------------------------------------------------------------
    # Parallel READ phase
    # ------------------------------------------------------------------
    with _cf.ThreadPoolExecutor() as pool:
        # pins
        pin_handles, pin_nets, pin_xy = _cached_pin_array(edb)
        fut_pins = pool.submit(
            pick_pins,
            pin_handles,
            pin_nets,
            pin_xy,
            keep_nets,
            extent_points,
        )

        # primitives
        prim_handles, prim_nets, pts_per_prim = _cached_primitive_array(edb)
        fut_prims = pool.submit(
            classify_primitives_batch,
            prim_handles,
            prim_nets,
            pts_per_prim,
            keep_nets,
            extent_points,
            reference_nets,
        )

        pins_del = fut_pins.result()
        prims_del, prims_clip = fut_prims.result()

    # ------------------------------------------------------------------
    # Single-threaded WRITE phase
    # ------------------------------------------------------------------
    nets_del = [n for n in edb.layout.nets if n.name not in keep_nets]

    for n in nets_del:
        n.delete()
    for p in pins_del:
        p.delete()
    for p in prims_del:
        p.delete()

    extent = GrpcPolygonData(points=extent_points)
    for prim, voids in prims_clip:
        clipped_polys = GrpcPolygonData.intersect(extent, prim.polygon_data)
        for c in clipped_polys:
            new_poly = edb.modeler.create_polygon(
                c,
                net_name=_safe_net_name(prim),
                layer_name=prim.layer.name,
            )
            for v in voids:
                new_poly.add_void(v)
        prim.delete()

    # Post-processing
    if kw.get("remove_single_pin_components", True):
        edb.components.delete_single_pin_rlc()
        edb.components.refresh_components()

    if not open_when_done and output_path:
        edb.close()
        edb.edbpath = legacy_path
        edb.open()

    return True

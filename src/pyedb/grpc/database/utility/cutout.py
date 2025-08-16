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


from collections.abc import Iterable
import concurrent.futures as _cf
from functools import lru_cache
from typing import Any, Sequence, Tuple
import warnings

from ansys.edb.core.geometry.polygon_data import ExtentType as GrpcExtentType
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
import numpy as np
from shapely import contains_xy as _contains_xy
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

from pyedb.misc.decorators import execution_timer


def flatten(seq):
    for elem in seq:
        if isinstance(elem, Iterable) and not isinstance(elem, (str, bytes)):
            yield from flatten(elem)
        else:
            yield elem


def _safe_net_name(obj) -> str | None:
    """Return obj.net.name if both exist, else None."""
    try:
        net = getattr(obj, "net", None)
        return net.name if net else None
    except Exception:
        return None


@execution_timer("extent_generation")
def extent_from_nets(edb, signal_nets, expansion, extent_type, **kw):
    """Compute clipping polygon from net lists."""
    nets = [n for n in edb.layout.nets if n.name in signal_nets]
    prims = []
    for net in nets:
        prims.extend(net.primitives)
    point_clouds = list(flatten([p.polygon_data.without_arcs().points for p in prims]))
    poly = GrpcPolygonData(point_clouds)

    if extent_type.lower() in ["conforming", "conformal"]:
        warnings.warn(
            "'Conforming' extent type is not recommended and CPU expensive. "
            "Use 'convex_hull' or 'bounding_box instead."
        )
        poly = edb.layout.expanded_extent(
            nets=nets,
            extent=GrpcExtentType.CONFORMING,
            expansion_factor=expansion,
            expansion_unitless=False,
            use_round_corner=kw.get("use_round_corner", False),
            num_increments=1,
        )
        return [(pt.x.value, pt.y.value) for pt in poly.points]
    elif extent_type in ["convex_hull", "convexhull"]:
        return [
            (pt.x.value, pt.y.value)
            for pt in GrpcPolygonData.convex_hull(poly)
            .expand(edb.value(expansion), False, edb.value(expansion))[0]
            .points
        ]
    elif extent_type in {"bounding", "bounding_box", "bbox", "boundingbox"}:
        bbox = GrpcPolygonData.bbox(poly)
        return [
            (bbox[0].x.value - edb.value(expansion), bbox[0].y.value - edb.value(expansion)),
            (bbox[1].x.value + edb.value(expansion), bbox[0].y.value - -edb.value(expansion)),
            (bbox[1].x.value + edb.value(expansion), bbox[1].y.value + edb.value(expansion)),
            (bbox[0].x.value - edb.value(expansion), bbox[1].y.value) + edb.value(expansion),
        ]
    else:
        raise ValueError(
            f"Unknown extent type: {extent_type}. " "Supported: 'Conforming', 'ConvexHull', 'BoundingBox'."
        )


def classify_intersection(poly1_pts, poly2_pts) -> Tuple[bool, str]:
    """
    poly1_pts, poly2_pts: list of (x, y) tuples
    returns: (intersects?, type_string)
    """
    poly1 = ShapelyPolygon(poly1_pts)
    poly2 = ShapelyPolygon(poly2_pts)

    # Fast path: disjoint() is a single DE-9IM query (cheapest)
    if poly1.disjoint(poly2):
        return False, "disjoint"

    # Ordered from cheapest to slightly more expensive.
    # Pick the FIRST predicate that is true; this avoids extra work.
    if poly2.contains(poly1):
        return True, "within"
    if poly2.covers(poly1):
        return True, "covered_by"
    if poly2.touches(poly1):
        return True, "touches"
    # At this point we have proper intersection (overlap of interiors)
    return False, "overlaps"


def point_inside(poly_pts, pt) -> bool:
    """
    Parameters
    ----------
    poly_pts : list[(x, y), …]
    pt: (x, y)
        query point
    returns True if pt lies inside/on the boundary of poly_pts
    """
    return ShapelyPolygon(poly_pts).contains(ShapelyPoint(pt))


# ------------------------------------------------------------------
# Vectorised pin filtering
# ------------------------------------------------------------------
@execution_timer("vectorised_pin_filtering")
def pick_pins(
    pin_handles: np.ndarray,
    net_arr: np.ndarray,
    xy_arr: np.ndarray,
    keep_nets: set[str],
    extent_pts: list[tuple[float, float]],
) -> list[Any]:
    mask = np.isin(net_arr, list(keep_nets))
    if not mask.any():
        return pin_handles.tolist()

    poly = ShapelyPolygon(extent_pts)
    inside = _contains_xy(poly, xy_arr[:, 0], xy_arr[:, 1])  # vectorised
    mask &= inside
    return pin_handles[~mask].tolist()


@execution_timer("pin_array_cache")
@lru_cache(maxsize=1)
def _cached_pin_array(edb):
    pins = list(edb.padstacks.instances.values())
    handles = np.array(pins, dtype=object)
    nets = np.array([_safe_net_name(p) for p in pins], dtype=object)
    xy = np.array([(p.position[0], p.position[1]) for p in pins], dtype=np.float64)
    return handles, nets, xy


@execution_timer("primitive_cache")
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
    return np.array(handles, dtype=object), np.array(nets, dtype=object), pts_per_prim


@execution_timer("primitive_classification")
def classify_primitives_batch(
    handles: np.ndarray,
    net_arr: np.ndarray,
    pts_per_prim: list,
    keep_nets: set[str],
    extent_pts: list[tuple[float, float]],
    reference_nets: set[str],
) -> tuple[list[Any], list[tuple[Any, list]]]:
    prims_del, prims_clip = [], []
    ext_poly = ShapelyPolygon(extent_pts)

    for handle, net_name, pts in zip(handles, net_arr, pts_per_prim):
        if net_name is None or net_name not in keep_nets:
            prims_del.append(handle)
            if getattr(handle, "has_void", None) is not None:
                prims_del.append(handle.voids)
            continue
        if pts is None or len(pts) < 3:
            prims_del.append(handle)
            continue

        poly = ShapelyPolygon(pts)
        if poly.disjoint(ext_poly):
            prims_del.append(handle)
        elif reference_nets and net_name in reference_nets:
            voids = []
            if getattr(handle, "has_voids", False):
                for v in handle.voids:
                    void_pts = [(pt.x.value, pt.y.value) for pt in v.polygon_data.without_arcs().points]
                    if classify_intersection(void_pts, extent_pts)[0]:
                        voids.append(v)
            prims_clip.append((handle, voids))

    return prims_del, prims_clip


@execution_timer("cutout_worker")
def cutout_worker(
    edb,
    extent_points: list[tuple[float, float]],
    signal_nets: Sequence[str] | None,
    reference_nets: Sequence[str] | None,
    number_of_threads: int = None,
    **kw,
) -> bool:
    keep_nets = set((signal_nets or []) + (reference_nets or []))
    reference_nets = set(reference_nets or [])
    if not keep_nets:
        raise ValueError("No nets specified to keep.")

    # ------------------------------------------------------------------
    # Parallel READ phase
    # ------------------------------------------------------------------
    with _cf.ThreadPoolExecutor(max_workers=number_of_threads) as pool:
        # pins
        pin_handles, pin_nets, pin_xy = _cached_pin_array(edb)
        fut_pins = pool.submit(pick_pins, pin_handles, pin_nets, pin_xy, keep_nets, extent_points)

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

        # wait for both
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

    extent = GrpcPolygonData(points=[[edb.value(pt[0]), edb.value(pt[1])] for pt in extent_points])
    for prim in prims_clip:
        clipped_polys = GrpcPolygonData.intersect(extent, prim[0].polygon_data)
        for c in clipped_polys:
            new_poly = edb.modeler.create_polygon(
                c,
                net_name=_safe_net_name(prim),
                layer_name=prim[0].layer.name,
            )
            for v in prim[1]:
                new_poly.add_void(v)
        prim[0].delete()

    # post-processing
    if kw.get("remove_single_pin_components", True):
        edb.components.delete_single_pin_rlc()
        edb.components.refresh_components()
    return True

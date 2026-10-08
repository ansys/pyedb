# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
Interactive 2D / 3D layout viewer for an open gRPC :class:`pyedb.Edb` session.

The viewer is a live companion of an EDB session. Geometry is extracted from EDB in a
single pass (``refresh``) into a flat, EDB-independent snapshot. Rendering is done with
Three.js (WebGL) in a browser tab served by a tiny local HTTP server, so no Qt / PySide
dependency is needed (Three.js is vendored in `viewer_static`). The page polls the server and
updates itself, keeping the camera / zoom, every time :meth:`LayoutViewer.refresh` is called.

EDB is never accessed from the HTTP threads: only :meth:`LayoutViewer.refresh` talks to
EDB (from the caller thread).

Examples
--------
>>> from pyedb import Edb
>>> from pyedb.extensions.layout_viewer import view_layout
>>> edb = Edb("my_design.aedb", version="2026.1")
>>> viewer = view_layout(edb, nets=["GND", "DDR4_DQ0"], mode="3d")
>>> edb.modeler.create_trace([[0, 0], [1e-3, 0]], "TOP", net_name="GND")
>>> viewer.refresh()  # the browser view is updated in place
>>> viewer.refresh(nets=[])  # all nets
>>> viewer.close()
"""

from __future__ import annotations

import atexit
from dataclasses import dataclass, field
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Iterable, Optional, Sequence
import webbrowser

import numpy as np

MM = 1e3  # EDB is in meters, the viewer works in millimeters.
COMPONENT_HEIGHT_MM = 0.3
_UNSET: Any = object()

LAYER_COLORS = [
    "#e6a23c",
    "#4fa3e0",
    "#3fb98a",
    "#e0597a",
    "#9b72e0",
    "#d8d84a",
    "#41c9c9",
    "#e07b3f",
    "#8bd04a",
    "#6f86e8",
    "#c96fd0",
    "#b0b7c3",
]
BACKGROUND = "#1b1e23"
GRID = "#2c313c"
TEXT = "#dce1ec"


def _in_notebook() -> bool:
    """`True` in a Jupyter kernel able to render HTML (Spyder consoles can not, they use the browser)."""
    return "ipykernel" in sys.modules and "spyder_kernels" not in sys.modules and "SPY_PYTHONPATH" not in os.environ


def _require(module: str, extra: str = "viewer"):
    try:
        return __import__(module)
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError(
            f"'{module}' is required by the layout viewer. Install it with 'pip install pyedb[{extra}]'."
        ) from exc


# ----------------------------------------------------------------------------------
# Snapshot (EDB independent)
# ----------------------------------------------------------------------------------
@dataclass
class LayerInfo:
    """Stackup layer description (millimeters)."""

    name: str
    kind: str  # "metal" | "dielectric"
    z0: float
    z1: float
    color: str = "#b0b7c3"


@dataclass
class LayoutSnapshot:
    """Flat copy of the layout geometry, safe to render from any thread.

    Attributes
    ----------
    layers : list[LayerInfo]
        Stackup layers, top to bottom.
    nets : list[str]
        Net names, the index being the net id used in the arrays below.
    geoms : dict
        ``layer name -> (shapely polygons ndarray, net id ndarray)``. Net id ``-1`` is "no net".
    outline : list
        Shapely polygons found on outline layers.
    vias : dict
        Via barrels: ``xy`` (N, 2), ``d`` (N,), ``z0``, ``z1``, ``net`` arrays.
    components : list[dict]
        ``name``, ``bbox`` (x0, y0, x1, y1), ``top`` (bool).
    """

    layers: list = field(default_factory=list)
    nets: list = field(default_factory=list)
    geoms: dict = field(default_factory=dict)
    outline: list = field(default_factory=list)
    vias: dict = field(default_factory=dict)
    components: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def metal_layers(self) -> list:
        return [layer for layer in self.layers if layer.kind == "metal"]

    def bounds(self) -> tuple:
        """Return ``(xmin, ymin, xmax, ymax)`` in mm."""
        import shapely

        boxes = []
        for polys, _ in self.geoms.values():
            if len(polys):
                boxes.append(shapely.total_bounds(polys))
        if self.outline:
            boxes.append(shapely.total_bounds(np.asarray(self.outline, dtype=object)))
        if self.components:
            b = np.array([c["bbox"] for c in self.components], dtype=float)
            boxes.append([b[:, 0].min(), b[:, 1].min(), b[:, 2].max(), b[:, 3].max()])
        if not boxes:
            return 0.0, 0.0, 1.0, 1.0
        boxes = np.asarray(boxes, dtype=float)
        return (
            float(boxes[:, 0].min()),
            float(boxes[:, 1].min()),
            float(boxes[:, 2].max()),
            float(boxes[:, 3].max()),
        )


# ----------------------------------------------------------------------------------
# EDB extraction (single pass, must be called from the thread owning EDB)
# ----------------------------------------------------------------------------------
def _f(value, default: float = 0.0) -> float:
    """Convert EDB values (float, ``Value``) to float."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    for attr in ("double", "value"):
        v = getattr(value, attr, None)
        if v is not None:
            try:
                return float(v() if callable(v) else v)
            except Exception:  # pragma: no cover - defensive
                pass
    try:
        return float(value)
    except Exception:
        return default


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _coord(value, owner) -> float:
    """Coordinate to float. Constant coordinates are read without any RPC call."""
    if isinstance(value, (int, float)):
        return float(value)
    if value.is_parametric and value.msg.variable_owner.id == 0:
        # Parametric coordinates returned by the server miss their owner (pyedb-core issue #726).
        from ansys.edb.core.utility.value import Value as CoreValue

        value = CoreValue(value.msg.text, owner)
    return _f(value)


def _ring(polygon_data, owner) -> np.ndarray:
    """Return the vertices (mm) of a core PolygonData with arcs tessellated."""
    pts = polygon_data.points
    if any(p.is_arc for p in pts):
        polygon_data = polygon_data.without_arcs(max_arc_angle=math.pi / 18)
        pts = polygon_data.points
    # ``_x`` / ``_y`` hold plain floats for constant coordinates, avoiding a Value wrapper per point.
    return np.array([(_coord(p._x, owner), _coord(p._y, owner)) for p in pts], dtype=float) * MM


def _primitive_polygon(prim, owner):
    """Return a shapely polygon (mm, voids included) for a core primitive or ``None``."""
    import shapely

    pd = prim.polygon_data
    outer = _ring(pd, owner)
    if len(outer) < 3:
        return None
    holes = [r for r in (_ring(h, owner) for h in (pd.holes or [])) if len(r) >= 3]
    for void in prim.voids or []:
        void = void.cast() if hasattr(void, "cast") else void
        ring = _safe(lambda: _ring(void.polygon_data, owner))
        if ring is not None and len(ring) >= 3:
            holes.append(ring)
    return shapely.Polygon(outer, holes)


class _PadSpec:
    """Pad outline of a padstack definition on one layer (local coordinates, mm)."""

    __slots__ = ("outline", "rotation", "size")

    def __init__(self, outline: np.ndarray, rotation: float, size: float):
        self.outline = outline
        self.rotation = rotation
        self.size = size


def _pad_outline(shape: str, sizes, polygon=None, owner=None) -> Optional[np.ndarray]:
    if polygon is not None:
        ring = _safe(lambda: _ring(polygon, owner))
        return ring if ring is not None and len(ring) >= 3 else None
    vals = [abs(_f(s)) * MM for s in (sizes or [])]
    vals = [v for v in vals if v > 0]
    if not vals:
        return None
    sx = vals[0]
    sy = vals[1] if len(vals) > 1 and shape not in ("circle", "square") else sx
    if shape in ("circle", "oval", "bullet", "round", "round45", "round90"):
        t = np.linspace(0.0, 2 * math.pi, 25)[:-1]
        return np.column_stack((sx / 2 * np.cos(t), sy / 2 * np.sin(t)))
    return np.array(
        [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)],
        dtype=float,
    )


def _padstack_definition(pdef, owner) -> dict:
    """Read pad outlines per layer and the barrel (hole) diameter of a core padstack definition."""
    from ansys.edb.core.definition.padstack_def_data import PadType
    from ansys.edb.core.geometry.polygon_data import PolygonData

    data = pdef.data
    pads: dict[str, _PadSpec] = {}
    for lname in _safe(lambda: list(data.layer_names), []) or []:
        p = _safe(lambda: data.get_pad_parameters(lname, PadType.REGULAR_PAD))
        if not p:
            continue
        if isinstance(p[0], PolygonData):
            outline = _pad_outline("polygon", None, polygon=p[0], owner=owner)
            ox, oy, rot = _f(p[1]) * MM, _f(p[2]) * MM, _f(p[3])
        else:
            shape = p[0].name.split("_")[-1].lower()
            outline = _pad_outline(shape, p[1])
            ox, oy, rot = _f(p[2]) * MM, _f(p[3]) * MM, _f(p[4])
        if outline is None:
            continue
        pads[lname] = _PadSpec(outline + np.array([ox, oy]), rot, float(np.ptp(outline, axis=0).min()))
    hole = 0.0
    hp = _safe(lambda: data.get_hole_parameters())
    if hp and hasattr(hp[0], "name") and hp[0].name.lower() == "padgeomtype_circle":
        hole = abs(_f(hp[1][0])) * MM
    if hole <= 0 and pads:
        hole = 0.5 * min(p.size for p in pads.values())
    return {"pads": pads, "barrel": hole}


def _clean(polys: np.ndarray, nets: np.ndarray) -> tuple:
    """Make polygons valid, drop empty ones and orient them (CCW exterior, CW holes)."""
    import shapely

    if not len(polys):
        return polys, nets
    invalid = ~shapely.is_valid(polys)
    if invalid.any():
        fixed, src = shapely.get_parts(shapely.make_valid(polys[invalid]), return_index=True)
        keep = shapely.get_type_id(fixed) == 3
        polys = np.concatenate([polys[~invalid], fixed[keep]])
        nets = np.concatenate([nets[~invalid], nets[invalid][src[keep]]])
    keep = ~shapely.is_empty(polys) & (shapely.area(polys) > 0)
    polys, nets = polys[keep], nets[keep]
    return shapely.orient_polygons(polys, exterior_cw=False), nets


def extract_snapshot(
    edb,
    nets: Optional[Sequence[str]] = None,
    layers: Optional[Sequence[str]] = None,
    include_components: bool = True,
    include_vias: bool = True,
) -> LayoutSnapshot:
    """Extract a renderable snapshot from an open gRPC EDB session.

    Parameters
    ----------
    edb : pyedb.Edb
        Open EDB session (gRPC backend).
    nets : list[str], optional
        Nets to extract. ``None`` or an empty list extracts all nets.
    layers : list[str], optional
        Metal layers to extract. ``None`` or an empty list extracts all layers.
    include_components : bool, optional
        Extract component outlines. Default is ``True``.
    include_vias : bool, optional
        Extract padstack instances (pads and via barrels). Default is ``True``.

    Returns
    -------
    LayoutSnapshot
    """
    import shapely

    t0 = time.time()
    snap = LayoutSnapshot()

    # --- stackup -------------------------------------------------------------------
    stack = []
    for name, layer in edb.stackup.layers.items():
        ltype = str(_safe(lambda: layer.type, "")).lower()
        if "signal" in ltype or "plane" in ltype:
            kind = "metal"
        elif "dielectric" in ltype:
            kind = "dielectric"
        else:
            continue
        z0 = _f(_safe(lambda: layer.lower_elevation, 0.0)) * MM
        z1 = _f(_safe(lambda: layer.upper_elevation, 0.0)) * MM
        stack.append(LayerInfo(name, kind, min(z0, z1), max(z0, z1)))
    stack.sort(key=lambda x: -x.z1)
    metal_i = 0
    for layer in stack:
        if layer.kind == "metal":
            layer.color = LAYER_COLORS[metal_i % len(LAYER_COLORS)]
            metal_i += 1
        else:
            layer.color = "#6b7a6a"
    snap.layers = stack
    metal_names = [x.name for x in stack if x.kind == "metal"]
    layer_index = {n: i for i, n in enumerate(metal_names)}
    wanted_layers = set(layers) if layers else set(metal_names)

    # --- nets ----------------------------------------------------------------------
    net_filter = [n for n in (nets or [])]
    all_nets = edb.nets.nets
    missing = [n for n in net_filter if n not in all_nets]
    if missing:
        edb.logger.warning(f"Layout viewer: net(s) not found and ignored: {missing}")
    net_filter = [n for n in net_filter if n in all_nets]
    if nets and not net_filter:
        edb.logger.warning("Layout viewer: none of the requested nets exist, nothing to display.")
    net_ids: dict[str, int] = {}

    def net_id(name) -> int:
        if not name:
            return -1
        idx = net_ids.get(name)
        if idx is None:
            idx = net_ids[name] = len(net_ids)
        return idx

    # --- primitives ----------------------------------------------------------------
    chunks: dict[str, tuple[list, list]] = {n: ([], []) for n in metal_names}
    outline: list = []
    n_prims = 0
    if nets:
        sources = [(n, all_nets[n].core.primitives) for n in net_filter]
    else:
        sources = [(None, edb.layout.core.primitives)]
    kinds = {"polygon", "path", "rectangle", "circle"}
    owner = edb.active_cell
    for known_net, prims in sources:
        for prim in prims:
            try:
                prim = prim.cast() if hasattr(prim, "cast") else prim
                ptype = prim.primitive_type.name.lower()
                if ptype not in kinds or prim.is_void:
                    continue
                lname = prim.layer.name
                if lname not in layer_index:
                    if "outline" in lname.lower():
                        poly = _primitive_polygon(prim, owner)
                        if poly is not None:
                            outline.append(poly)
                    continue
                if lname not in wanted_layers:
                    continue
                poly = _primitive_polygon(prim, owner)
                if poly is None:
                    continue
                if known_net is None:
                    net = prim.net
                    nname = None if net.is_null else net.name
                else:
                    nname = known_net
                chunks[lname][0].append(poly)
                chunks[lname][1].append(net_id(nname))
                n_prims += 1
            except Exception as exc:  # one bad primitive must not break the view
                edb.logger.debug(f"Layout viewer: skipping primitive: {exc}")

    # --- padstack instances ----------------------------------------------------------
    comp_names: set = set()
    via_xy: list = []
    via_d: list = []
    via_z: list = []
    via_net: list = []
    n_inst = 0
    if include_vias:
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        if nets:
            inst_sources = [(n, all_nets[n].core.padstack_instances) for n in net_filter]
        else:
            inst_sources = [(None, edb.layout.core.padstack_instances)]
        pdefs: dict[str, dict] = {}
        groups: dict[str, dict] = {}
        for known_net, instances in inst_sources:
            for inst in instances:
                try:
                    pdef = inst.padstack_def
                    dname = pdef.name
                    if dname not in pdefs:
                        pdefs[dname] = _padstack_definition(pdef, owner)
                    start, stop = inst.get_layer_range()
                    i0, i1 = layer_index.get(start.name), layer_index.get(stop.name)
                    idx = [i for i in (i0, i1) if i is not None]
                    if not idx:
                        continue
                    if inst.is_layout_pin:
                        wrapped = PadstackInstance(edb, inst)
                        x, y = wrapped.position_and_rotation[:2]
                        rot = _f(inst.get_position_and_rotation()[2])
                        comp = _safe(lambda: wrapped.component)
                        if comp is not None:
                            comp_names.add(comp.name)
                    else:
                        pos = inst.get_position_and_rotation()
                        x, y, rot = _f(pos[0]), _f(pos[1]), _f(pos[2])
                    if known_net is None:
                        net = inst.net
                        nname = None if net.is_null else net.name
                    else:
                        nname = known_net
                    g = groups.setdefault(dname, {"xy": [], "rot": [], "net": [], "l0": [], "l1": []})
                    g["xy"].append((x * MM, y * MM))
                    g["rot"].append(rot)
                    g["net"].append(net_id(nname))
                    g["l0"].append(min(idx))
                    g["l1"].append(max(idx))
                    n_inst += 1
                except Exception as exc:
                    edb.logger.debug(f"Layout viewer: skipping padstack instance: {exc}")

        z_top = {x.name: x.z1 for x in stack}
        z_bot = {x.name: x.z0 for x in stack}
        for dname, g in groups.items():
            spec = pdefs[dname]
            xy = np.asarray(g["xy"], dtype=float)
            rot = np.asarray(g["rot"], dtype=float)
            nid = np.asarray(g["net"], dtype=int)
            l0, l1 = np.asarray(g["l0"]), np.asarray(g["l1"])
            for lname, pad in spec["pads"].items():
                li = layer_index.get(lname)
                if li is None or lname not in wanted_layers:
                    continue
                sel = (l0 <= li) & (li <= l1)
                if not sel.any():
                    continue
                ang = rot[sel] + pad.rotation
                c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
                ox, oy = pad.outline[None, :, 0], pad.outline[None, :, 1]
                px = xy[sel, 0:1] + c * ox - s * oy
                py = xy[sel, 1:2] + s * ox + c * oy
                polys = shapely.polygons(np.stack((px, py), axis=-1))
                chunks[lname][0].extend(polys)
                chunks[lname][1].extend(nid[sel].tolist())
            barrel = spec["barrel"]
            if barrel > 0:
                for i in range(len(xy)):
                    top = metal_names[l0[i]]
                    bot = metal_names[l1[i]]
                    if l0[i] == l1[i]:
                        continue
                    via_xy.append(xy[i])
                    via_d.append(barrel)
                    via_z.append((z_bot[bot], z_top[top]))
                    via_net.append(nid[i])

    for lname, (polys, nids) in chunks.items():
        if polys:
            p, n = _clean(np.asarray(polys, dtype=object), np.asarray(nids, dtype=int))
            snap.geoms[lname] = (p, n)
    snap.outline = [p for p in outline if p is not None]
    if via_xy:
        z = np.asarray(via_z, dtype=float)
        snap.vias = {
            "xy": np.asarray(via_xy, dtype=float),
            "d": np.asarray(via_d, dtype=float),
            "z0": z[:, 0],
            "z1": z[:, 1],
            "net": np.asarray(via_net, dtype=int),
        }
    snap.nets = list(net_ids.keys())

    # --- components ------------------------------------------------------------------
    if include_components:
        top_layer = metal_names[0] if metal_names else None
        for cname, comp in edb.components.instances.items():
            try:
                if nets and comp_names and cname not in comp_names:
                    continue
                bbox = [float(v) * MM for v in comp.bounding_box]
                if len(bbox) != 4 or bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                    continue
                snap.components.append({"name": cname, "bbox": bbox, "top": comp.placement_layer == top_layer})
            except Exception as exc:
                edb.logger.debug(f"Layout viewer: skipping component {cname}: {exc}")

    snap.stats = {
        "primitives": n_prims,
        "padstack_instances": n_inst,
        "components": len(snap.components),
        "nets": len(snap.nets),
        "seconds": round(time.time() - t0, 3),
    }
    edb.logger.info(f"Layout viewer snapshot extracted: {snap.stats}")
    return snap


# ----------------------------------------------------------------------------------
# Scene encoding (pure numpy / shapely, no EDB access)
# ----------------------------------------------------------------------------------
_STATIC = Path(__file__).with_name("viewer_static")


def net_color_table(n: int) -> list:
    """Return ``n`` visually distinct ``#rrggbb`` colors (golden ratio hue stepping)."""
    import colorsys

    colors = []
    for i in range(max(n, 1)):
        r, g, b = colorsys.hsv_to_rgb((i * 0.61803398875) % 1.0, 0.55 + 0.25 * (i % 2), 0.95 - 0.1 * (i % 3))
        colors.append(f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}")
    return colors


def _ring_segments(polys) -> np.ndarray:
    """Boundary segments ``(S, 4)`` float32 (x0, y0, x1, y1) of polygons, holes included."""
    import shapely

    rings, _ = shapely.get_rings(np.asarray(polys, dtype=object), return_index=True)
    coords, idx = shapely.get_coordinates(rings, return_index=True)
    if len(coords) < 2:
        return np.empty((0, 4), np.float32)
    same = np.flatnonzero(idx[:-1] == idx[1:])
    return np.column_stack((coords[same], coords[same + 1])).astype(np.float32)


def _layer_mesh(polys: np.ndarray, bottom_cap: bool = False) -> tuple:
    """Triangulate and extrude polygons with shared vertices.

    Returns
    -------
    tuple
        ``xy (V, 2)`` float32, ``is_top (V,)`` bool (vertex lies on the top face), ``faces (T, 3)`` int32 and
        ``face_poly (T,)`` int32 (index of the source polygon). Z is applied by the browser, so the result
        is independent of the elevation / Z scale and can be cached.
    """
    import shapely

    tri_geo = shapely.constrained_delaunay_triangles(polys)
    parts, pidx = shapely.get_parts(tri_geo, return_index=True)
    ok = shapely.get_num_coordinates(parts) == 4
    parts, pidx = parts[ok], pidx[ok]
    tri = shapely.get_coordinates(parts).reshape(-1, 4, 2)[:, :3, :].reshape(-1, 2)
    # Share the vertices of the triangulation.
    uniq, inv = np.unique(tri[:, 0] + 1j * tri[:, 1], return_inverse=True)
    n_u = len(uniq)
    xy = [np.column_stack((uniq.real, uniq.imag))]
    top = [np.ones(n_u, bool)]
    faces = [inv.reshape(-1, 3)]
    fpoly = [pidx]
    base = n_u
    if bottom_cap:
        xy.append(xy[0])
        top.append(np.zeros(n_u, bool))
        faces.append(faces[0] + base)
        fpoly.append(pidx)
        base += n_u
    # side walls, vertices of every ring at the bottom then at the top
    rings, ridx = shapely.get_rings(polys, return_index=True)
    coords, cidx = shapely.get_coordinates(rings, return_index=True)
    m = len(coords)
    if m > 1:
        same = np.flatnonzero(cidx[:-1] == cidx[1:])
        if len(same):
            xy += [coords, coords]
            top += [np.zeros(m, bool), np.ones(m, bool)]
            la, lb, ua, ub = same + base, same + 1 + base, same + base + m, same + 1 + base + m
            faces += [np.column_stack((la, lb, ub)), np.column_stack((la, ub, ua))]
            owner = ridx[cidx[same]]
            fpoly += [owner, owner]
    return (
        np.concatenate(xy).astype(np.float32),
        np.concatenate(top),
        np.concatenate(faces).astype(np.int32),
        np.concatenate(fpoly).astype(np.int32),
    )


def _geometry_key(polys: np.ndarray) -> bytes:
    """Cheap, exact fingerprint of a polygon array (used to skip re-meshing unchanged layers)."""
    import hashlib

    import shapely

    h = hashlib.blake2b(digest_size=16)
    for wkb in shapely.to_wkb(polys):
        h.update(wkb)
    return h.digest()


def auto_z_scale(snap: LayoutSnapshot) -> float:
    """Z exaggeration so that the stackup stays visible on large boards."""
    metal = snap.metal_layers
    if not metal:
        return 1.0
    total = max(max(m.z1 for m in metal) - min(m.z0 for m in metal), 1e-6)
    x0, y0, x1, y1 = snap.bounds()
    extent = max(x1 - x0, y1 - y0, 1e-6)
    return float(min(max(0.06 * extent / total, 1.0), 50.0))


class _Blob:
    """Binary buffer writer, every array is 4 bytes aligned (typed array views in the browser)."""

    def __init__(self):
        self.parts: list = []
        self.size = 0

    def add(self, array, dtype) -> int:
        raw = np.ascontiguousarray(array, dtype=dtype).tobytes()
        offset = self.size
        pad = (-len(raw)) % 4
        self.parts.append(raw)
        if pad:
            self.parts.append(b"\0" * pad)
        self.size += len(raw) + pad
        return offset


def build_scene(
    snap: LayoutSnapshot,
    version: int = 0,
    z_scale: Optional[float] = None,
    mesh_cache: Optional[dict] = None,
) -> bytes:
    """Encode a snapshot into the binary scene read by the Three.js page.

    Format: ``uint32`` header length (multiple of 4), UTF-8 JSON header, binary arrays referenced by byte
    offsets from the header. Colors, Z scale, layer visibility and 2D / 3D mode are applied in the browser.

    Parameters
    ----------
    snap : LayoutSnapshot
    version : int, optional
        Version stored in the header.
    z_scale : float, optional
        Initial Z exaggeration. Default is computed automatically (:func:`auto_z_scale`).
    mesh_cache : dict, optional
        Dictionary reused between calls: layers whose geometry did not change are not re-meshed.

    Returns
    -------
    bytes
    """
    import struct

    blob = _Blob()
    cache = mesh_cache if mesh_cache is not None else {}
    layers = [m for m in snap.metal_layers if m.name in snap.geoms and len(snap.geoms[m.name][0])]
    lowest = layers[-1].name if layers else None
    keys = {m.name: (m.name, _geometry_key(snap.geoms[m.name][0]), m.name == lowest) for m in layers}
    todo = [m for m in layers if keys[m.name] not in cache]
    if todo:
        # GEOS releases the GIL: layers are triangulated in parallel.
        # Plain threads (not ThreadPoolExecutor): the executor refuses to run once the interpreter is shutting
        # down, which is when a finished script keeps the viewer alive (see LayoutViewer._at_exit).
        import os

        queue = list(todo)
        errors: list = []

        def work():
            while queue:
                try:
                    m = queue.pop()
                except IndexError:
                    return
                try:
                    cache[keys[m.name]] = _layer_mesh(snap.geoms[m.name][0], bottom_cap=m.name == lowest)
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        threads = [threading.Thread(target=work) for _ in range(max(1, min(len(todo), os.cpu_count() or 1, 8)))]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        if errors:
            raise errors[0]
    live = {keys[m.name] for m in layers}
    for stale in [k for k in cache if k not in live]:
        del cache[stale]

    meshes_h = []
    for info in layers:
        xy, is_top, faces, fpoly = cache[keys[info.name]]
        nets = snap.geoms[info.name][1]
        meshes_h.append(
            {
                "layer": info.name,
                "nv": len(xy),
                "nf": len(faces),
                "xy": blob.add(xy, np.float32),
                "top": blob.add(is_top, np.uint8),
                "faces": blob.add(faces, np.uint32),
                "fnet": blob.add(nets[fpoly], np.int32),
            }
        )

    metal = snap.metal_layers
    z_top = max((m.z1 for m in metal), default=0.0)
    z_bot = min((m.z0 for m in metal), default=0.0)
    header: dict = {
        "version": version,
        "bounds": list(snap.bounds()),
        "zmin": z_bot - (COMPONENT_HEIGHT_MM if snap.components else 0.0),
        "zmax": z_top + (COMPONENT_HEIGHT_MM if snap.components else 0.0),
        "zScale": auto_z_scale(snap) if z_scale is None else float(z_scale),
        "nets": list(snap.nets),
        "netColors": net_color_table(len(snap.nets)),
        "layers": [{"name": x.name, "kind": x.kind, "z0": x.z0, "z1": x.z1, "color": x.color} for x in snap.layers],
        "meshes": meshes_h,
        "stats": {
            "nets": snap.stats.get("nets", len(snap.nets)),
            "primitives": snap.stats.get("primitives", 0),
            "padstack_instances": snap.stats.get("padstack_instances", 0),
        },
        "vias": None,
        "comps": None,
        "outline": None,
    }
    v = snap.vias
    if len(v.get("d", [])):
        header["vias"] = {
            "n": int(len(v["d"])),
            "xy": blob.add(v["xy"], np.float32),
            "d": blob.add(v["d"], np.float32),
            "z": blob.add(np.column_stack((v["z0"], v["z1"])), np.float32),
            "net": blob.add(v["net"], np.int32),
        }
    if snap.components:
        boxes = np.array([c["bbox"] for c in snap.components], dtype=float)
        top = np.array([c["top"] for c in snap.components])
        z0 = np.where(top, z_top, z_bot - COMPONENT_HEIGHT_MM)
        z1 = np.where(top, z_top + COMPONENT_HEIGHT_MM, z_bot)
        header["comps"] = {
            "n": len(boxes),
            "names": [c["name"] for c in snap.components],
            "bbox": blob.add(boxes, np.float32),
            "z": blob.add(np.column_stack((z0, z1)), np.float32),
        }
    if snap.outline:
        seg = _ring_segments(snap.outline)
        if len(seg):
            header["outline"] = {"n": len(seg), "seg": blob.add(seg, np.float32)}
    raw = json.dumps(header, separators=(",", ":")).encode("utf-8")
    raw += b" " * ((-len(raw)) % 4)
    return b"".join([struct.pack("<I", len(raw)), raw, *blob.parts])


# ----------------------------------------------------------------------------------
# Live browser session
# ----------------------------------------------------------------------------------
_THREE_FILES = {"three.module.min.js": "three", "OrbitControls.js": "orbit"}


def _page(boot: dict, import_map: dict) -> str:
    """HTML page (Three.js viewer). ``boot`` is injected as ``window.PYEDB_VIEWER``."""
    html = (_STATIC / "viewer.html").read_text(encoding="utf-8")
    js = (_STATIC / "viewer.js").read_text(encoding="utf-8")
    # str.replace is applied to the template only, the injected values may contain any text
    parts = html.split("__JS__")
    head = parts[0].replace("__IMPORTMAP__", json.dumps({"imports": import_map})).replace("__BOOT__", json.dumps(boot))
    return head + js + parts[1]


class LayoutViewer:
    """Live 2D / 3D viewer bound to an open gRPC EDB session.

    The view is rendered in a browser with Three.js (WebGL). Layers, vias, components, colors (layer / net),
    net highlighting, Z scale and 2D / 3D mode are controlled in the page without any new EDB access.

    Parameters
    ----------
    edb : pyedb.Edb
        Open EDB session (gRPC backend).
    nets : list[str], optional
        Nets to display. ``None`` or an empty list displays all nets.
    layers : list[str], optional
        Metal layers to display. ``None`` or an empty list displays all layers.
    mode : str, optional
        Initial view, ``"2d"`` (default) or ``"3d"``. Both views can be switched in the browser.
    color_by : str, optional
        Initial coloring, ``"layer"`` (default) or ``"net"``.
    show_components : bool, optional
        Extract component outlines / boxes. Default is ``True``.
    show_vias : bool, optional
        Extract pads and via barrels. Default is ``True``.
    z_scale : float, optional
        Initial 3D Z exaggeration. Default is automatic.
    show_dielectrics : bool, optional
        Initially display dielectric slabs in 3D. Default is ``False``.

    Examples
    --------
    >>> viewer = LayoutViewer(edb, nets=["GND"])
    >>> viewer.show()
    >>> edb.modeler.create_trace([[0, 0], [1e-3, 0]], "TOP", net_name="GND")
    >>> viewer.refresh()
    """

    def __init__(
        self,
        edb,
        nets: Optional[Sequence[str]] = None,
        layers: Optional[Sequence[str]] = None,
        mode: str = "2d",
        color_by: str = "layer",
        show_components: bool = True,
        show_vias: bool = True,
        z_scale: Optional[float] = None,
        show_dielectrics: bool = False,
    ):
        _require("shapely")
        if not type(edb).__module__.startswith("pyedb.grpc"):
            raise TypeError("The layout viewer requires an Edb session opened with the gRPC backend (grpc=True).")
        if mode not in ("2d", "3d"):
            raise ValueError("mode must be '2d' or '3d'.")
        if color_by not in ("layer", "net"):
            raise ValueError("color_by must be 'layer' or 'net'.")
        self._edb = edb
        self.nets = list(nets) if nets else []
        self.layers = list(layers) if layers else []
        self.mode = mode
        self.color_by = color_by
        self.show_components = show_components
        self.show_vias = show_vias
        self.z_scale = z_scale
        self.show_dielectrics = show_dielectrics
        self._snapshot: Optional[LayoutSnapshot] = None
        self._version = 0
        self._payload: Optional[bytes] = None
        self._mesh_cache: dict = {}
        self._lock = threading.Lock()
        self._build_lock = threading.Lock()
        self._server = None
        self._thread = None

    # ------------------------------------------------------------------ public API
    @property
    def url(self) -> Optional[str]:
        """URL of the live view, ``None`` if the session is not started."""
        if self._server is None:
            return None
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}/"

    @property
    def snapshot(self) -> Optional[LayoutSnapshot]:
        """Last extracted :class:`LayoutSnapshot`."""
        return self._snapshot

    def refresh(self, nets: Any = _UNSET, layers: Any = _UNSET) -> LayoutSnapshot:
        """Re-read the layout from EDB and update the view.

        Call it each time the design is modified programmatically.

        Parameters
        ----------
        nets : list[str], optional
            New list of nets to display. An empty list displays all nets. By default the
            current selection is kept.
        layers : list[str], optional
            New list of layers to display. By default the current selection is kept.

        Returns
        -------
        LayoutSnapshot
        """
        if nets is not _UNSET:
            self.nets = list(nets) if nets else []
        if layers is not _UNSET:
            self.layers = list(layers) if layers else []
        snap = extract_snapshot(
            self._edb,
            nets=self.nets,
            layers=self.layers,
            include_components=self.show_components,
            include_vias=self.show_vias,
        )
        with self._lock:
            self._snapshot = snap
            self._version += 1
            self._payload = None
        return snap

    def show(self, port: int = 0, open_browser: bool = True, inline: Optional[bool] = None) -> str:
        """Start the live view server and display it.

        In a Jupyter notebook the view is shown in the cell output (an iframe on the local server, so the
        kernel must run on the same machine as the browser). Elsewhere (scripts, Spyder, terminals) it opens a
        browser tab. Spyder keeps the kernel alive, so ``viewer.refresh()`` updates the open tab live.

        Parameters
        ----------
        inline : bool, optional
            Force (``True``) or forbid (``False``) the display in the notebook cell output. Default is automatic.

        Parameters
        ----------
        port : int, optional
            Local TCP port. Default ``0`` picks a free port.
        open_browser : bool, optional
            Open the default browser. Default is ``True``.

        Returns
        -------
        str
            URL of the live view.
        """
        from http.server import ThreadingHTTPServer

        if self._server is None:
            if self._snapshot is None:
                self.refresh()
            self._server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(self))
            self._thread = threading.Thread(target=self._server.serve_forever, name="pyedb-layout-viewer", daemon=True)
            self._thread.start()
            atexit.register(self._at_exit)
        if open_browser:
            if _in_notebook() if inline is None else inline:
                from IPython.display import display

                display(self.iframe())
            else:
                webbrowser.open(self.url)
        return self.url

    def iframe(self, height: int = 700):
        """Return an `IPython.display.IFrame` of the live view (starts the server if needed)."""
        from IPython.display import IFrame

        if self._server is None:
            self.show(open_browser=False)
        return IFrame(src=self.url, width="100%", height=height)

    def _ipython_display_(self) -> None:
        from IPython.display import display

        display(self.iframe())

    def save_html(self, path: str) -> str:
        """Save the current view as a standalone HTML file (Three.js is embedded, works offline)."""
        import base64

        if self._snapshot is None:
            self.refresh()
        import_map = {}
        for name, key in _THREE_FILES.items():
            data = base64.b64encode((_STATIC / name).read_bytes()).decode("ascii")
            import_map[key] = "data:text/javascript;base64," + data
        boot = self._boot()
        boot["scene"] = base64.b64encode(self._scene_payload()[1]).decode("ascii")
        Path(path).write_text(_page(boot, import_map), encoding="utf-8")
        return path

    def wait(self) -> None:
        """Block until Ctrl+C, keeping the live view alive.

        The server runs in a daemon thread: in a plain script the process exits (and the view dies) as soon as
        the script ends, so call this at the end of a script. Ctrl+C, Ctrl+Break (PyCharm "Stop" on Windows)
        and SIGTERM end the wait, so the IDE stop button closes the process cleanly.
        """
        import signal

        print(f"Layout viewer running at {self.url} (Ctrl+C or the IDE stop button to stop)")
        stop = threading.Event()
        previous = {}
        if threading.current_thread() is threading.main_thread():
            for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
                sig = getattr(signal, name, None)
                if sig is not None:
                    try:
                        previous[sig] = signal.signal(sig, lambda *_: stop.set())
                    except (ValueError, OSError):  # pragma: no cover
                        pass
        try:
            while self._server is not None and not stop.wait(0.2):
                pass
        except KeyboardInterrupt:
            pass
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        self.close()

    def close(self) -> None:
        """Stop the server. The EDB session is not touched."""
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None
        atexit.unregister(self._at_exit)

    # ------------------------------------------------------------------ internals
    def _at_exit(self) -> None:
        """Keep a plain script alive while the view is open.

        The server thread dies with the process, so without this a script ends (and EDB is closed by its own exit
        hook, which runs after this one) right after `show()`. Interactive sessions are not blocked.
        """
        interactive = hasattr(sys, "ps1") or sys.flags.interactive or "ipykernel" in sys.modules
        if self._server is not None and not interactive:
            print("Script finished: the layout viewer stays open, press Ctrl+C to close it and exit.")
            self.wait()

    def _boot(self) -> dict:
        return {
            "mode": self.mode,
            "color": self.color_by,
            "zScale": self.z_scale,
            "dielectrics": self.show_dielectrics,
            "scene": None,
        }

    def _scene_payload(self) -> tuple:
        """``(version, scene bytes)``. Only uses the snapshot, never EDB."""
        with self._build_lock:
            with self._lock:
                if self._payload is not None:
                    return self._version, self._payload
                snap, version = self._snapshot, self._version
            payload = build_scene(snap, version=version, z_scale=self.z_scale, mesh_cache=self._mesh_cache)
            with self._lock:
                if version == self._version:
                    self._payload = payload
            return version, payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _make_handler(viewer: LayoutViewer):
    from http.server import BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence
            pass

        def _send(self, body: bytes, ctype: str, headers: Optional[dict] = None):
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            path = self.path.split("?", 1)[0]
            try:
                if path == "/":
                    import_map = {key: f"/static/{name}" for name, key in _THREE_FILES.items()}
                    self._send(_page(viewer._boot(), import_map).encode("utf-8"), "text/html; charset=utf-8")
                elif path.startswith("/static/") and path[8:] in _THREE_FILES:
                    self._send((_STATIC / path[8:]).read_bytes(), "text/javascript; charset=utf-8")
                elif path == "/version":
                    self._send(json.dumps({"version": viewer._version}).encode(), "application/json")
                elif path == "/scene":
                    version, payload = viewer._scene_payload()
                    self._send(payload, "application/octet-stream", {"X-Scene-Version": str(version)})
                else:
                    self.send_error(404)
            except (BrokenPipeError, ConnectionResetError):  # browser closed the tab
                pass

    return Handler


def view_layout(
    edb,
    nets: Optional[Iterable[str]] = None,
    mode: str = "2d",
    open_browser: bool = True,
    block: bool = False,
    inline: Optional[bool] = None,
    **kwargs,
) -> LayoutViewer:
    """Open a live 2D / 3D viewer (Three.js, in the web browser) on an EDB session.

    Parameters
    ----------
    edb : pyedb.Edb
        Open EDB session (gRPC backend).
    nets : list[str], optional
        Nets to display. ``None`` or an empty list displays all nets.
    mode : str, optional
        ``"2d"`` (default) or ``"3d"``.
    open_browser : bool, optional
        Open the default browser. Default is ``True``.
    inline : bool, optional
        Display in the notebook cell output. Default is automatic (Jupyter only, see :meth:`LayoutViewer.show`).
    block : bool, optional
        Block until Ctrl+C (needed at the end of a script, otherwise the process exits and the view stops).
        Default is `False`.
    **kwargs
        Additional :class:`LayoutViewer` arguments (``layers``, ``color_by``, ``show_components``,
        ``show_vias``, ``z_scale``, ``show_dielectrics``).

    Returns
    -------
    LayoutViewer
        Call :meth:`LayoutViewer.refresh` after each modification of the design to update the view.

    Examples
    --------
    >>> viewer = view_layout(edb, nets=["GND"], mode="3d")
    >>> # ... modify edb ...
    >>> viewer.refresh()
    """
    viewer = LayoutViewer(edb, nets=list(nets) if nets else None, mode=mode, **kwargs)
    viewer.show(open_browser=open_browser, inline=inline)
    if block:
        viewer.wait()
    return viewer

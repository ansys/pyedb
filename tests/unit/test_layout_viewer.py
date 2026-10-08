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

"""Unit tests of the layout viewer rendering (no EDB / license needed)."""

import json
import urllib.request

import numpy as np
import pytest

shapely = pytest.importorskip("shapely")

from pyedb.extensions.layout_viewer import (  # noqa: E402
    LayerInfo,
    LayoutSnapshot,
    LayoutViewer,
    _clean,
    _layer_mesh,
    build_scene,
)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


def _snapshot() -> LayoutSnapshot:
    plane = shapely.Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(4, 4), (6, 4), (6, 6), (4, 6)]])
    trace = shapely.box(1, 1, 9, 1.2)
    polys, nets = _clean(np.array([plane, trace], dtype=object), np.array([0, 1]))
    snap = LayoutSnapshot()
    snap.layers = [
        LayerInfo("TOP", "metal", 0.035, 0.07, "#e6a23c"),
        LayerInfo("D1", "dielectric", 0.0, 0.035),
        LayerInfo("BOT", "metal", -0.035, 0.0, "#4fa3e0"),
    ]
    snap.nets = ["GND", "SIG"]
    snap.geoms = {"TOP": (polys, nets), "BOT": (polys.copy(), nets.copy())}
    snap.vias = {
        "xy": np.array([[2.0, 2.0]]),
        "d": np.array([0.2]),
        "z0": np.array([-0.035]),
        "z1": np.array([0.07]),
        "net": np.array([0]),
    }
    snap.components = [{"name": "U1", "bbox": [1.0, 2.0, 3.0, 4.0], "top": True}]
    snap.stats = {"nets": 2, "primitives": 2, "padstack_instances": 1}
    return snap


def test_clean_orients_and_fixes_polygons():
    bowtie = shapely.Polygon([(0, 0), (2, 2), (2, 0), (0, 2)])
    polys, nets = _clean(np.array([bowtie, shapely.Polygon()], dtype=object), np.array([3, 4]))
    assert len(polys) == len(nets) >= 1
    assert all(shapely.is_valid(polys))
    assert set(nets) == {3}


def _decode(scene: bytes):
    import struct

    n = struct.unpack_from("<I", scene)[0]
    assert n % 4 == 0
    return json.loads(scene[4 : 4 + n]), memoryview(scene)[4 + n :]


def test_build_scene_layout():
    scene = build_scene(_snapshot(), version=7)
    head, blob = _decode(scene)
    assert head["version"] == 7 and head["nets"] == ["GND", "SIG"]
    assert [m["layer"] for m in head["meshes"]] == ["TOP", "BOT"]
    for m in head["meshes"]:
        faces = np.frombuffer(blob, np.uint32, m["nf"] * 3, m["faces"])
        fnet = np.frombuffer(blob, np.int32, m["nf"], m["fnet"])
        assert faces.max() < m["nv"]
        assert set(fnet) <= {0, 1}
    assert head["vias"]["n"] == 1 and head["comps"]["names"] == ["U1"]
    assert head["zScale"] >= 1.0


def test_layer_mesh_is_indexed_and_cacheable():
    polys = _snapshot().geoms["TOP"][0]
    xy, is_top, faces, face_poly = _layer_mesh(polys, bottom_cap=True)
    assert len(xy) == len(is_top)
    assert faces.max() < len(xy)
    assert len(faces) == len(face_poly)
    cache: dict = {}
    snap = _snapshot()
    build_scene(snap, mesh_cache=cache)
    n = len(cache)
    build_scene(snap, mesh_cache=cache)
    assert len(cache) == n == 2


def test_live_server_refresh(monkeypatch):
    class FakeEdb:  # only the type module is checked at construction
        pass

    FakeEdb.__module__ = "pyedb.grpc.edb"
    viewer = LayoutViewer(FakeEdb(), nets=["GND"])
    snap = _snapshot()
    monkeypatch.setattr(viewer, "_snapshot", snap)
    viewer._version = 1
    url = viewer.show(open_browser=False)
    try:
        v1 = json.loads(urllib.request.urlopen(url + "version").read())["version"]
        resp = urllib.request.urlopen(url + "scene")
        assert int(resp.headers["X-Scene-Version"]) == v1
        head, _ = _decode(resp.read())
        assert head["meshes"]
        # a refresh bumps the version, the page polls it to reload
        with viewer._lock:
            viewer._version += 1
            viewer._payload = None
        v2 = json.loads(urllib.request.urlopen(url + "version").read())["version"]
        assert v2 == v1 + 1
        page = urllib.request.urlopen(url).read().decode()
        assert "importmap" in page and "PYEDB_VIEWER" in page
        assert b"WebGLRenderer" in urllib.request.urlopen(url + "static/three.module.min.js").read()
        assert b"OrbitControls" in urllib.request.urlopen(url + "static/OrbitControls.js").read()
    finally:
        viewer.close()
    assert viewer.url is None


def test_save_html_standalone(tmp_path, monkeypatch):
    class FakeEdb:
        pass

    FakeEdb.__module__ = "pyedb.grpc.edb"
    viewer = LayoutViewer(FakeEdb(), mode="3d", color_by="net")
    monkeypatch.setattr(viewer, "_snapshot", _snapshot())
    out = tmp_path / "view.html"
    viewer.save_html(str(out))
    text = out.read_text(encoding="utf-8")
    assert "data:text/javascript;base64," in text and '"mode": "3d"' in text


def test_requires_grpc_backend():
    with pytest.raises(TypeError):
        LayoutViewer(object())

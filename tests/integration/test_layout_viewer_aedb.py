# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Licensed regression tests of the working tree against ANSYS-HSD_V1.aedb.

Enable with PYEDB_VIEWER_AEDB_TESTS=1; optionally select the installed server
with PYEDB_VIEWER_EDB_VERSION. The native rendering test additionally requires
PYEDB_VIEWER_RHI_TESTS=1 and a desktop. Only a temporary copy is opened writable.
No EDB objects, geometry extraction or graphics backends are mocked. Spies count
full and incremental captures without replacing their implementation.
"""

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import shutil
import time
from unittest.mock import Mock

import numpy as np
import pytest

from pyedb.grpc.database.layout_changes import layout_changes
from pyedb.viewer import scene_from_edb
from pyedb.viewer.adapters.grpc import scene_patch_from_edb
from pyedb.viewer.capture import SourceCapture
from pyedb.viewer.incremental import prepare_incremental
from pyedb.viewer.mesh import prepare_scene
from tests.conftest import config

pytestmark = [
    pytest.mark.integration,
    pytest.mark.grpc,
    pytest.mark.slow,
    pytest.mark.skipif(os.getenv("PYEDB_VIEWER_AEDB_TESTS") != "1", reason="Requires an installed, licensed gRPC EDB"),
]

MODEL = Path(__file__).resolve().parents[1] / "example_models" / "TEDB" / "ANSYS-HSD_V1.aedb"


def _manifest(directory):
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*")
        if path.is_file()
    }


def _id(obj):
    return obj.core.edb_uid if type(obj).__name__ == "PadstackInstance" else obj.id


def _wait(window, predicate):
    from PySide6.QtTest import QTest

    deadline = time.monotonic() + float(os.getenv("PYEDB_VIEWER_TEST_TIMEOUT", "180"))
    while not predicate() and time.monotonic() < deadline:
        assert window.canvas.error is None, window.canvas.error
        QTest.qWait(20)
    assert predicate(), f"Viewer timed out: busy={window._busy}, capture_error={window._capture_error}"


@dataclass
class _Board:
    edb: object
    scene: object
    prepared: object
    layer: str
    net: str
    origin: tuple
    via_definition: str | None


@pytest.fixture(scope="module")
def hsd_board(tmp_path_factory):
    from pyedb import Edb
    from pyedb.generic.settings import settings

    assert (MODEL / "edb.def").is_file(), f"Missing regression model: {MODEL}"
    version = os.getenv("PYEDB_VIEWER_EDB_VERSION", config.version)
    assert tuple(int(part) for part in str(version).split(".")[:2]) >= (2026, 1), (
        f"These viewer tests require gRPC EDB 2026.1 or later; PYEDB_VIEWER_EDB_VERSION={version} is unsupported."
    )
    assert version in settings.INSTALLED_VERSIONS, (
        f"EDB {version} is not installed. Available versions: {', '.join(settings.INSTALLED_VERSIONS)}"
    )
    original = _manifest(MODEL)
    target = tmp_path_factory.mktemp("viewer_hsd") / MODEL.name
    shutil.copytree(MODEL, target)
    edb = Edb(str(target), grpc=True, version=version)
    try:
        assert edb.active_db and edb.active_cell, "EDB did not open the copied model"
        layout_changes(edb)
        snapshot = scene_from_edb(edb, analytic_traces=False)
        assert snapshot.layers and snapshot.bounds is not None
        assert sum(1 for _ in snapshot.geometry) > 100, "The fixture must contain the actual board geometry"
        assert snapshot.components, "Component geometry must be exercised by this board fixture"
        prepared = prepare_scene(snapshot)
        nets = edb.nets.nets
        net = "GND" if "GND" in nets else next(name for name in nets if name)
        # Test geometry sits outside the imported board, making pixel checks
        # independent of its routing and component locations.
        x0, y0, x1, y1 = snapshot.bounds
        origin = (x1 + max(10, (x1 - x0) * 0.1), y1 + max(10, (y1 - y0) * 0.1))
        via_ids = {info.object_id for info in snapshot.object_info if info.kind == "via"}
        via_definition = next(
            (
                instance.padstack_def.name
                for instance in edb.layout.core.padstack_instances
                if instance.edb_uid in via_ids
            ),
            None,
        )
        yield _Board(edb, snapshot, prepared, snapshot.layers[0].name, net, origin, via_definition)
    finally:
        edb.close()
        assert _manifest(MODEL) == original, "The source AEDB fixture was changed"


@dataclass
class _Case:
    board: _Board
    source: object
    full: object
    delta: object
    scene: object
    prepared: object
    created: list = field(default_factory=list)

    def track(self, obj):
        assert obj and not obj.is_null, "A native EDB geometry operation failed"
        self.created.append(obj)
        return obj

    def rectangle(self, offset=0):
        x, y = self.board.origin
        return self.track(
            self.board.edb.modeler.create_rectangle(
                layer_name=self.board.layer,
                net_name=self.board.net,
                lower_left_point=[f"{x + offset}mm", f"{y}mm"],
                upper_right_point=[f"{x + offset + 2}mm", f"{y + 2}mm"],
            )
        )

    def circle(self, offset=4):
        x, y = self.board.origin
        return self.track(
            self.board.edb.modeler.create_circle(
                layer_name=self.board.layer,
                net_name=self.board.net,
                x=f"{x + offset}mm",
                y=f"{y + 1}mm",
                radius=".5mm",
            )
        )

    def delete(self, obj):
        obj.delete()
        self.created.remove(obj)

    def advance(self, changed=None, *, full=False):
        result = self.source.capture(previous=self.scene, full=full)
        if changed is not None:
            assert result.patch is not None, "A local edit unexpectedly triggered a full board capture"
            assert result.changed == set(changed)
        prepared = (
            prepare_incremental(result.scene, self.scene, self.prepared, result.patch, result.changed)
            if result.patch is not None
            else prepare_scene(result.scene)
        )
        self.source.revision = result.revision
        self.scene, self.prepared = result.scene, prepared
        return result


@pytest.fixture
def hsd_case(hsd_board):
    edb = hsd_board.edb
    full = Mock(wraps=lambda progress, preview=None: scene_from_edb(edb, analytic_traces=False, preview=preview))
    delta = Mock(wraps=lambda changes, previous, progress: scene_patch_from_edb(edb, changes, previous))
    source = SourceCapture(full, changes=layout_changes(edb), delta_loader=delta)
    # Previous tests remove every newly created object. The original detached
    # board and its mesh can therefore be shared without repeated full reads.
    source.revision = source.changes.revision
    case = _Case(hsd_board, source, full, delta, hsd_board.scene, hsd_board.prepared)
    try:
        yield case
    finally:
        for obj in reversed(case.created):
            obj.delete()
        source.close()


def test_hsd_initial_scene_is_detached_and_pickable(hsd_board, record_property):
    board = hsd_board
    ids = {item.object_id for item in board.scene.geometry}
    assert board.prepared.picking.objects
    assert {obj.info.object_id for obj in board.prepared.picking.objects} == ids
    assert board.prepared.vertices.nbytes + board.prepared.instances.nbytes > 0
    record_property("aedb_geometry_parts", sum(1 for _ in board.scene.geometry))
    record_property("aedb_components", len(board.scene.components))
    record_property("edb_version", board.edb.version)


def test_hsd_native_creation_batch_is_one_delta_and_reuses_the_board(hsd_case):
    case = hsd_case
    edb = case.board.edb
    x, y = case.board.origin
    revision = case.source.revision
    with case.source.changes.batch():
        rectangle = case.rectangle()
        circle = case.circle()
        polygon = case.track(
            edb.modeler.create_polygon(
                [[f"{x + 6}mm", f"{y}mm"], [f"{x + 8}mm", f"{y}mm"], [f"{x + 7}mm", f"{y + 2}mm"]],
                case.board.layer,
                net_name=case.board.net,
            )
        )
        trace = case.track(
            edb.modeler.create_trace(
                [[f"{x}mm", f"{y + 4}mm"], [f"{x + 4}mm", f"{y + 4}mm"]],
                case.board.layer,
                width=".2mm",
                net_name=case.board.net,
            )
        )
    assert case.source.changes.revision == revision + 1
    original = case.prepared
    result = case.advance({_id(obj) for obj in (rectangle, circle, polygon, trace)})
    assert {item.object_id for item in result.patch.geometry} == result.changed
    assert case.prepared.vertices.chunks[0] is original.vertices
    assert case.prepared.instances.chunks[0] is original.instances
    assert case.prepared.picking.base is original.picking
    assert case.prepared.component_batches is original.component_batches
    assert all(item is previous for item, previous in zip(case.scene.polygons, case.board.scene.polygons))
    case.full.assert_not_called()
    assert case.delta.call_count == 1


def test_hsd_native_modify_and_delete_rebind_picking_without_full_capture(hsd_case):
    case = hsd_case
    circle = case.circle()
    case.advance({_id(circle)})
    previous = case.prepared
    x, y = case.board.origin
    circle.center = ((x + 8) / 1000, (y + 1) / 1000)
    case.advance({_id(circle)})
    assert case.prepared.instances.chunks[0] is previous.instances.chunks[0]
    hit = case.prepared.picking.pick((x + 8, y + 1), 100, {case.board.layer})
    assert hit is not None and hit.picked.object_id == _id(circle)
    assert case.prepared.picking.pick((x + 4, y + 1), 100, {case.board.layer}) is None
    object_id = _id(circle)
    case.delete(circle)
    case.advance({object_id})
    assert all(key[1] != object_id for key in case.prepared.picking.by_key)
    assert case.prepared.picking.pick((x + 8, y + 1), 100, {case.board.layer}) is None
    case.full.assert_not_called()


def test_hsd_native_standalone_via_updates_all_its_layers(hsd_case):
    case = hsd_case
    assert case.board.via_definition, "The reference board must contain a drilled via"
    x, y = case.board.origin
    via = case.track(
        case.board.edb.padstacks.place(
            [(x + 2) / 1000, (y + 5) / 1000],
            case.board.via_definition,
            net_name=case.board.net,
            via_name="pyedb_viewer_regression_via",
        )
    )
    result = case.advance({_id(via)})
    assert len({item.layer for item in result.patch.geometry}) > 1
    assert any(info.kind == "via" for info in result.patch.object_info)
    via.position = [(x + 5) / 1000, (y + 5) / 1000]
    result = case.advance({_id(via)})
    assert all(item.object_id == _id(via) for item in result.patch.geometry)
    object_id = _id(via)
    case.delete(via)
    case.advance({object_id})
    assert not any(key[1] == object_id for key in case.prepared.picking.by_key)
    case.full.assert_not_called()


def test_hsd_void_dependency_and_manual_refresh_use_full_capture(hsd_case):
    case = hsd_case
    x, y = case.board.origin
    parent = case.track(
        case.board.edb.modeler.create_polygon(
            [[f"{x}mm", f"{y}mm"], [f"{x + 3}mm", f"{y}mm"], [f"{x + 3}mm", f"{y + 3}mm"], [f"{x}mm", f"{y + 3}mm"]],
            case.board.layer,
            net_name=case.board.net,
        )
    )
    case.advance({_id(parent)})
    void = case.track(
        case.board.edb.modeler.create_rectangle(
            layer_name=case.board.layer,
            net_name=case.board.net,
            lower_left_point=[f"{x + 1}mm", f"{y + 1}mm"],
            upper_right_point=[f"{x + 2}mm", f"{y + 2}mm"],
        )
    )
    parent.add_void(void)
    assert case.advance().patch is None
    polygon = next(item for item in case.scene.polygons if item.object_id == _id(parent))
    assert len(polygon.holes) == 1
    assert all(item.object_id != _id(void) for item in case.scene.geometry)
    assert case.full.call_count == 1 and case.prepared.update_count == 0
    # Raw core edits are deliberately untracked and require explicit full refresh.
    parent.core.is_negative = True
    assert case.advance(full=True).patch is None
    assert all(item.object_id != _id(parent) for item in case.scene.geometry)
    assert case.full.call_count == 2


@pytest.mark.skipif(os.getenv("PYEDB_VIEWER_RHI_TESTS") != "1", reason="Requires a native RHI desktop")
def test_hsd_live_window_pixels_uploads_selection_and_full_refresh(hsd_case, record_property):
    pytest.importorskip("PySide6")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    case = hsd_case
    app = QApplication.instance() or QApplication([])
    window = case.board.edb.view_layout(live=True, block=False, color_by_net=False, refresh_interval=1)
    errors = []
    window.refresh_failed.connect(errors.append)

    def ready():
        revision = window._source.changes.revision
        _wait(window, lambda: not window._busy and window._source.revision == revision)
        assert not errors, errors
        frame = window.canvas.grabFramebuffer().convertToFormat(QImage.Format.Format_RGBA8888)
        assert not frame.isNull(), window.canvas.error
        return np.frombuffer(frame.constBits(), dtype=np.uint8).reshape(frame.height(), frame.width(), 4).copy()

    try:
        ready()
        canvas = window.canvas
        canvas.show_grid = False
        canvas.opacity = 1
        window.pick_action.setChecked(False)
        window.set_visible_layers(case.board.layer)
        x, y = case.board.origin
        canvas.zoom_to_bounds((x - 1, y - 1, x + 10, y + 4))
        blank = ready()
        source_loader = Mock(wraps=window._source.loader)
        window._source.loader = source_loader
        device = canvas.renderer.device
        initial_bytes = device.geometry_upload_bytes
        camera = (canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale)
        results, script_errors = [], []
        window.script_finished.connect(results.append)
        window.script_failed.connect(script_errors.append)

        def draw():
            with window.batch_update():
                return case.rectangle()

        window.run_script(draw)
        _wait(window, lambda: window._script is None)
        assert not script_errors, script_errors
        assert len(results) == 1
        rectangle = results[0]
        added = ready()
        rectangle_bytes = device.geometry_upload_bytes - initial_bytes
        assert 0 < rectangle_bytes < min(initial_bytes // 10, 4096)
        assert not np.array_equal(blank, added)
        window.select_object(_id(rectangle))
        assert window.selected_object.object_id == _id(rectangle)
        assert (canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale) == camera
        before_delete = device.geometry_upload_bytes
        case.delete(rectangle)
        deleted = ready()
        assert window.selected_object is None
        assert device.geometry_upload_bytes == before_delete
        np.testing.assert_array_equal(blank, deleted)
        circle = case.circle()
        ready()
        before_move = device.geometry_upload_bytes
        circle.center = ((x + 7) / 1000, (y + 1) / 1000)
        moved = ready()
        circle_bytes = device.geometry_upload_bytes - before_move
        assert 0 < circle_bytes < 1024
        source_loader.assert_not_called()
        window.refresh()
        rebuilt = ready()
        assert source_loader.call_count == 1
        np.testing.assert_array_equal(moved, rebuilt)
        record_property("initial_geometry_upload_bytes", initial_bytes)
        record_property("rectangle_delta_upload_bytes", rectangle_bytes)
        record_property("circle_move_upload_bytes", circle_bytes)
    finally:
        window.close()
        _wait(window, lambda: not window._busy and window._script is None)
        app.processEvents()

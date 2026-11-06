# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Object extraction, resident geometry reuse and picking on large scenes."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from pyedb.grpc.database.layout_changes import layout_changes
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.viewer import LayoutScene, ScenePad, SceneTrace
from pyedb.viewer.adapters.grpc import scene_from_edb, scene_patch_from_edb
from pyedb.viewer.capture import SourceCapture, merge_scene
from pyedb.viewer.incremental import BufferChain, append_buffer, prepare_incremental
from pyedb.viewer.mesh import prepare_scene, scene_network_names
from pyedb.viewer.picking import OverlayPickIndex, PickIndex
from tests.unit.test_layout_viewer import _edb, _primitive, _via, picking_scene
from tests.unit.test_layout_viewer_live import scene, wait_until

pytestmark = [pytest.mark.unit, pytest.mark.grpc, pytest.mark.no_licence]


def capture_source(edb):
    full = Mock(side_effect=lambda progress, preview=None: scene_from_edb(edb, preview=preview))
    capture = SourceCapture(
        full,
        changes=layout_changes(edb),
        delta_loader=lambda delta, previous, progress: scene_patch_from_edb(edb, delta, previous),
    )
    return capture, full


def test_journal_coalesces_and_keeps_independent_viewer_revisions():
    edb = _edb([])
    changes = layout_changes(edb)
    core = _primitive(7)
    primitive = Primitive(edb, core)
    with changes.batch():
        primitive.is_negative = True
        primitive.is_negative = False
    assert changes.since(0).upserts == ((7, core),) and not changes.since(0).full
    assert changes.since(1).upserts == ()
    core.delete = Mock()
    primitive.delete()
    assert changes.since(0).removed == {7} and changes.since(0).upserts == ()
    assert changes.since(1).removed == {7} and changes.since(2).removed == set()
    with changes.batch():
        changes.invalidate()
    assert changes.since(1).full


def test_journal_falls_back_after_eviction_and_for_void_edits():
    edb = _edb([])
    changes = layout_changes(edb)
    for index in range(140):
        with changes.batch():
            changes.record(index, object())
    assert changes.since(0).full and not changes.since(139).full
    Primitive(edb, _primitive(1, is_void=True)).is_negative = True
    assert changes.since(140).full
    with changes.batch():
        for index in range(8193):
            changes.record(index, object())
    assert changes.since(141).full
    assert sum(len(delta.upserts) for delta in changes._history) <= 8192


def test_rectangle_factory_records_its_new_source_handle(monkeypatch):
    from pyedb.grpc.database.primitive.rectangle import Rectangle

    edb = _edb([])
    edb._value_setter = lambda value: value
    changes = layout_changes(edb)
    core = _primitive(90, type="rectangle")
    monkeypatch.setattr("pyedb.grpc.database.primitive.rectangle.CoreRectangle.create", Mock(return_value=core))
    rectangle = Rectangle.create(layout=SimpleNamespace(_pedb=edb, core=object()), layer="TOP")
    assert rectangle.core is core
    assert changes.since(0).upserts == ((90, core),) and not changes.since(0).full


def test_one_edit_on_2000_objects_reads_only_the_changed_contour():
    cores = [_primitive(index) for index in range(2000)]
    edb = _edb(cores)
    capture, full = capture_source(edb)
    previous = capture(None)
    reads = [core.polygon_data.reads for core in cores]
    edb.layout = edb.nets = edb.stackup = None  # No whole-layout API is available to delta extraction.
    Primitive(edb, cores[1000]).is_negative = False
    result = capture.capture(previous=previous)
    assert result.changed == {1000} and full.call_count == 1
    assert len(result.patch.polygons) == 1 and result.patch.polygons[0].object_id == 1000
    assert [core.polygon_data.reads for core in cores] == [count + (i == 1000) for i, count in enumerate(reads)]
    untouched = {item.object_id: item for item in previous.polygons}
    assert all(item is untouched[item.object_id] for item in result.scene.polygons if item.object_id != 1000)


def test_deleted_handle_is_never_queried_and_manual_refresh_is_full():
    core = _primitive(1)
    edb = _edb([core])
    capture, full = capture_source(edb)
    previous = capture(None)
    core.delete = Mock()
    Primitive(edb, core).delete()
    del core.polygon_data
    result = capture.capture(previous=previous)
    assert result.scene.polygons == () and result.changed == {1} and full.call_count == 1
    edb.layout.primitives.clear()
    assert capture.capture(previous=previous, full=True).patch is None and full.call_count == 2


def test_incremental_extraction_failure_does_not_advance_revision():
    core = _primitive(1)
    edb = _edb([core])
    capture, _ = capture_source(edb)
    previous = capture(None)
    Primitive(edb, core).is_negative = False
    core.polygon_data.error = RuntimeError("Lost source")
    with pytest.raises(RuntimeError, match="Lost source"):
        capture.capture(previous=previous)
    assert capture.revision == 0
    core.polygon_data.error = None
    assert capture.capture(previous=previous).changed == {1}


def test_standalone_via_delta_captures_all_its_layers_without_enumerating_instances():
    from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

    via = _via()
    edb = _edb([])
    edb.layout.padstack_instances = [via]
    capture, full = capture_source(edb)
    previous = capture(None)
    edb.layout = None  # A via delta must not enumerate all layout instances.
    via.position = (0.030, 0.040)
    via.set_product_property = Mock()
    PadstackInstance(edb, via).name = "Moved via"
    result = capture.capture(previous=previous)
    assert not edb._layout_changes.since(0).full
    assert result.changed == {via.id} and full.call_count == 1
    assert {pad.layer for pad in result.patch.pads} == {"TOP", "BOTTOM"}
    assert result.patch.object_info[0].name == "Moved via"
    assert result.patch.object_info[0].drill_diameter == 1
    parent = prepare_scene(previous)
    changed = prepare_incremental(result.scene, previous, parent, result.patch, result.changed)
    assert changed.picking.by_key[("via", via.id)].info.name == "Moved via"
    assert changed.instances.chunks[0] is parent.instances


def test_paged_buffer_preserves_prefix_without_copying_it():
    original = np.arange(80, dtype=np.float32).reshape(-1, 4)
    tail = np.ones((2, 4), dtype=np.float32)
    joined = append_buffer(original, tail)
    assert isinstance(joined, BufferChain) and joined.chunks[0] is original
    assert np.shares_memory(joined[len(original) :], tail)
    np.testing.assert_array_equal(np.asarray(joined), np.concatenate((original, tail)))
    np.testing.assert_array_equal(joined[18:21], np.concatenate((original, tail))[18:21])
    assert append_buffer(joined, tail[:0]) is joined


def test_small_update_only_triangulates_its_local_mesh(monkeypatch):
    import mapbox_earcut

    previous = scene(*range(2000))
    parent = prepare_scene(previous)
    triangulate = Mock(wraps=mapbox_earcut.triangulate_float64)
    monkeypatch.setattr(mapbox_earcut, "triangulate_float64", triangulate)
    patch = scene(9999)
    merged = merge_scene(previous, patch, {9999})
    result = prepare_incremental(merged, previous, parent, patch, {9999})
    assert triangulate.call_count == 1 and result.vertices.chunks[0] is parent.vertices
    assert len(result.vertices) - len(parent.vertices) == 4
    assert len(result.indices) - len(parent.indices) == 6
    assert result.picking.base is parent.picking and result.nets == scene_network_names(merged)


def test_modified_and_deleted_objects_are_not_in_draw_ranges_or_picking():
    previous = scene(1, 2)
    parent = prepare_scene(previous)
    patch = replace(scene(1), polygons=(replace(scene(1).polygons[0], exterior=((10, 0), (11, 0), (11, 1), (10, 1))),))
    merged = merge_scene(previous, patch, {1, 2})
    result = prepare_incremental(merged, previous, parent, patch, {1, 2})
    assert [batch.object_id for batch in result.batches] == [1]
    assert result.batches[0].vertex_start == len(parent.vertices)
    assert result.picking.pick((1.5, 0.5), 100, {"TOP"}) is None
    assert result.picking.pick((2.5, 0.5), 100, {"TOP"}) is None
    assert result.picking.pick((10.5, 0.5), 100, {"TOP"}).picked.object_id == 1
    assert ("zone", 2) not in result.picking.by_key


def test_analytic_packets_keep_other_objects_and_drop_removed_ranges():
    previous = replace(
        scene(), pads=(ScenePad(1, "TOP", "GND", (0, 0), (1, 1)), ScenePad(2, "TOP", "GND", (2, 0), (1, 1)))
    )
    parent = prepare_scene(previous)
    patch = replace(scene(), traces=(SceneTrace(1, "TOP", "GND", (10, 0), (11, 0), 0.2),))
    merged = merge_scene(previous, patch, {1})
    result = prepare_incremental(merged, previous, parent, patch, {1})
    surviving = {
        index
        for batch in result.sdf_batches
        for index in range(batch.instance_start, batch.instance_start + batch.instance_count)
    }
    assert surviving == {1, 2} and result.instances.chunks[0] is parent.instances
    assert result.picking.pick((0, 0), 100, {"TOP"}) is None
    assert result.picking.pick((2, 0), 100, {"TOP"}).picked.object_id == 2
    assert result.picking.pick((10.5, 0), 100, {"TOP"}).picked.kind == "trace"


def test_new_networks_do_not_renumber_existing_gpu_packets():
    previous = replace(scene(1), net_names=("GND", "Z_OLD"))
    parent = prepare_scene(previous)
    patch = replace(
        scene(2, 3), polygons=(replace(scene(2).polygons[0], net="Z_NEW"), replace(scene(3).polygons[0], net="A_NEW"))
    )
    merged = merge_scene(previous, patch, {2, 3})
    result = prepare_incremental(merged, previous, parent, patch, {2, 3})
    assert result.nets[: len(parent.nets)] == parent.nets and result.nets == scene_network_names(merged)


def test_overlay_picker_matches_full_picker_after_repeated_changes():
    current = scene(*range(30))
    prepared = prepare_scene(current)
    for index in range(8):
        patch = replace(scene(index), polygons=(replace(scene(index).polygons[0], net="DATA"),))
        merged = merge_scene(current, patch, {index})
        prepared = prepare_incremental(merged, current, prepared, patch, {index})
        current = merged
    full = PickIndex(current)
    assert isinstance(prepared.picking, OverlayPickIndex)
    for mirror in (False, True):
        for net in (None, "GND", "DATA"):
            for x in np.arange(-1, 32, 0.25):
                actual = prepared.picking.pick((x, 0.5), 100, {"TOP"}, net=net, mirror=mirror)
                expected = full.pick((x, 0.5), 100, {"TOP"}, net=net, mirror=mirror)
                assert (actual.picked if actual else None) == (expected.picked if expected else None)


def test_overlay_picker_matches_full_for_holes_layers_nets_and_pad_drills():
    previous = picking_scene()
    parent = prepare_scene(previous)
    patch = replace(
        previous,
        polygons=(),
        joins=(),
        components=(),
        traces=(),
        object_info=(),
        pads=(replace(previous.pads[0], center=(0, 0)), replace(previous.pads[1], center=(0, 0))),
    )
    merged = merge_scene(previous, patch, {4})
    changed = prepare_incremental(merged, previous, parent, patch, {4})
    full = PickIndex(merged)
    for layers in ({"TOP"}, {"BOTTOM"}, {"TOP", "BOTTOM"}):
        for mirror in (False, True):
            for net in (None, "GND", "VIA_NET", "DATA_SIGNAL"):
                for x in np.arange(-5, 6, 0.5):
                    for y in (0, 0.5, 2):
                        actual = changed.picking.pick((x, y), 100, layers, net=net, mirror=mirror)
                        expected = full.pick((x, y), 100, layers, net=net, mirror=mirror)
                        assert (actual.picked if actual else None) == (expected.picked if expected else None)


def test_repeated_edits_compact_without_retaining_an_unbounded_chain():
    current = scene(1)
    prepared = prepare_scene(current)
    for index in range(270):
        patch = replace(scene(1), polygons=(replace(scene(1).polygons[0], net=f"N{index % 3}"),))
        merged = merge_scene(current, patch, {1})
        prepared = prepare_incremental(merged, current, prepared, patch, {1})
        current = merged
    assert prepared.update_count == 13
    assert len(prepared.vertices.chunks) == 14
    assert len(prepared.picking.objects) == 1
    assert prepared.picking.pick((1.5, 0.5), 100, {"TOP"}).picked.net == "N2"


def test_compaction_reclaims_tombstones_and_rebuilds_picking():
    previous = scene(1, 2)
    parent = replace(prepare_scene(previous), update_count=256)
    patch = scene(3)
    merged = merge_scene(previous, patch, {1, 3})
    compact = prepare_incremental(merged, previous, parent, patch, {1, 3})
    assert compact.mesh_parent_id == 0 and compact.update_count == 0
    assert isinstance(compact.vertices, np.ndarray) and isinstance(compact.picking, PickIndex)
    assert {batch.object_id for batch in compact.batches} == {2, 3}


def test_live_window_uses_object_delta_but_refresh_forces_full_capture():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    core = _primitive(1)
    edb = _edb([core])
    capture, full = capture_source(edb)
    window = LayoutWindow(LayoutScene((), ()), loader=capture, live=True, refresh_interval=1)
    try:
        wait_until(lambda: not window._busy)
        window.select_object(1)
        Primitive(edb, core).is_negative = False
        wait_until(lambda: not window._busy and capture.revision == 1)
        assert window.canvas._prepared.update_count == 1 and window.selected_object.object_id == 1
        assert full.call_count == 1
        window.refresh()
        wait_until(lambda: not window._busy)
        assert full.call_count == 2 and window.canvas._prepared.update_count == 0
    finally:
        window.close()
        wait_until(lambda: not window._busy)
        app.processEvents()


@pytest.mark.parametrize("failure_stage", ["capture", "mesh"])
def test_failed_incremental_job_retries_from_the_last_accepted_revision(monkeypatch, failure_stage):
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    import pyedb.viewer.incremental as module
    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    core = _primitive(1)
    edb = _edb([core])
    capture, full = capture_source(edb)
    window = LayoutWindow(LayoutScene((), ()), loader=capture, live=True, refresh_interval=1)
    failures = []
    window.refresh_failed.connect(failures.append)
    try:
        wait_until(lambda: not window._busy)
        accepted = window.canvas.scene
        original_prepare = module.prepare_incremental
        if failure_stage == "capture":
            core.polygon_data.error = RuntimeError("Temporary failure")
        else:
            monkeypatch.setattr(module, "prepare_incremental", Mock(side_effect=RuntimeError("Temporary failure")))
        Primitive(edb, core).is_negative = False
        wait_until(lambda: len(failures) == 1 and not window._busy)
        assert capture.revision == 0 and window.canvas.scene is accepted
        core.polygon_data.error = None
        monkeypatch.setattr(module, "prepare_incremental", original_prepare)
        Primitive(edb, core).is_negative = False
        wait_until(lambda: capture.revision == 2 and not window._busy)
        assert full.call_count == 1 and window.canvas._prepared.update_count == 1
    finally:
        window.close()
        wait_until(lambda: not window._busy)
        app.processEvents()

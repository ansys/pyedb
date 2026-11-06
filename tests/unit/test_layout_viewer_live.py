# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Live session updates, without an EDB server or graphics device."""

from dataclasses import replace
from threading import Event, Thread
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pyedb.grpc.database.layout_changes import layout_changes, layout_mutation, layout_session_close
from pyedb.grpc.database.modeler import Modeler
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon, launch_viewer
from pyedb.viewer.capture import SourceCapture

pytestmark = [pytest.mark.unit, pytest.mark.grpc, pytest.mark.no_licence]


def scene(*ids):
    return LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1))),
        tuple(ScenePolygon(i, "TOP", "GND", ((i, 0), (i + 1, 0), (i + 1, 1), (i, 1))) for i in ids),
    )


def wait_until(predicate):
    from PySide6.QtTest import QTest

    for _ in range(500):
        if predicate():
            return
        QTest.qWait(10)
    assert predicate(), "Timed out waiting for the viewer worker"


@pytest.fixture
def live_window():
    pytest.importorskip("PySide6")
    pytest.importorskip("mapbox_earcut")
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    source = SimpleNamespace(current=scene(1), calls=0)
    changes = layout_changes(source)

    def load(progress, preview=None):
        source.calls += 1
        return source.current

    capture = SourceCapture(load, changes=changes)
    window = LayoutWindow(LayoutScene((), ()), loader=capture, live=True, refresh_interval=5)
    wait_until(lambda: not window._busy)
    yield window, source, changes
    window.close()
    wait_until(lambda: not window._busy and window._script is None)
    app.processEvents()


class TestChangeNotifications:
    def test_modeler_creation_and_primitive_edit_delete_notify(self, monkeypatch):
        edb = SimpleNamespace(
            nets=SimpleNamespace(find_or_create_net=Mock()),
            active_layout=object(),
            stackup=SimpleNamespace(layers={"BOTTOM": SimpleNamespace(core="bottom")}),
        )
        state = layout_changes(edb)
        events = []
        state.subscribe(events.append)
        polygon = SimpleNamespace(is_null=False)
        monkeypatch.setattr("pyedb.grpc.database.modeler.Polygon.create", Mock(return_value=polygon))
        assert Modeler(edb).create_polygon(SimpleNamespace(points=[1], holes=[]), "TOP") is polygon
        assert events == [1]
        core = SimpleNamespace(delete=Mock())
        primitive = Primitive(edb, core)
        primitive.layer_name = "BOTTOM"
        primitive.delete()
        assert core.layer == "bottom"
        core.delete.assert_called_once()
        assert events == [1, 2, 3]

    def test_nested_edits_batch_and_failure(self):
        edb = SimpleNamespace()
        wrapper = SimpleNamespace(_pedb=edb)
        state = layout_changes(edb)
        events = []
        unsubscribe = state.subscribe(events.append)

        @layout_mutation
        def edit(owner, result=True):
            return result

        @layout_mutation
        def outer(owner):
            edit(owner)
            edit(owner)

        outer(wrapper)
        assert events == [1]
        edit(wrapper, False)
        assert events == [1]
        with pytest.raises(ValueError), state.batch():
            edit(wrapper)
            edit(wrapper)
            raise ValueError("Later edit failed")
        assert events == [1, 2]
        unsubscribe()
        unsubscribe()
        edit(wrapper)
        assert events == [1, 2]

    def test_failed_edit_does_not_notify_and_observer_cannot_fail_an_edit(self):
        edb = SimpleNamespace()
        state = layout_changes(edb)
        callback = Mock(side_effect=ValueError("Bad subscriber"))
        state.subscribe(callback)

        @layout_mutation
        def edit(owner, fail=False):
            if fail:
                raise RuntimeError("Failed edit")
            return True

        wrapper = SimpleNamespace(_pedb=edb)
        with pytest.raises(RuntimeError):
            edit(wrapper, fail=True)
        callback.assert_not_called()
        assert edit(wrapper)
        callback.assert_called_once_with(1)

    def test_class_factory_and_no_viewer_fast_path(self):
        class Factory:
            @classmethod
            @layout_mutation
            def create(cls, layout):
                return 123

        edb = SimpleNamespace()
        layout = SimpleNamespace(_pedb=edb)
        assert Factory.create(layout=layout) == 123
        assert not hasattr(edb, "_layout_changes")
        state = layout_changes(edb)
        Factory.create(layout)
        Factory.create(layout=layout)
        assert state.revision == 2

    def test_static_add_void_keeps_keyword_arguments(self):
        edb = SimpleNamespace()
        state = layout_changes(edb)
        shape = Primitive(edb, SimpleNamespace(add_void=Mock()))
        void = Primitive(edb, object())
        assert Modeler.add_void(shape=shape, void_shape=void)
        shape.core.add_void.assert_called_once_with(void.core)
        assert state.revision == 1

    def test_capture_excludes_concurrent_edit_and_session_close(self):
        edb = SimpleNamespace()
        state = layout_changes(edb)
        entered, release, edited, closed = Event(), Event(), Event(), Event()

        def load(progress, preview=None):
            entered.set()
            assert release.wait(5)
            return scene(1)

        capture = SourceCapture(load, changes=state)
        reader = Thread(target=capture, args=(None,))

        @layout_mutation
        def edit(owner):
            edited.set()

        @layout_session_close
        def close(owner):
            closed.set()
            return True

        reader.start()
        assert entered.wait(5)
        writer = Thread(target=edit, args=(SimpleNamespace(_pedb=edb),))
        closer = Thread(target=close, args=(edb,))
        writer.start()
        closer.start()
        try:
            assert not edited.wait(0.05)
            assert not closed.is_set()
        finally:
            release.set()
            for thread in (reader, writer, closer):
                thread.join(5)
                assert not thread.is_alive()
        assert edited.is_set() and closed.is_set()
        with pytest.raises(RuntimeError, match="session is closed"):
            capture(None)


class TestLiveWindow:
    def test_moved_selection_rebinds_inspector_anchor(self, live_window):
        window, source, _ = live_window
        window.select_object(1)
        source.current = replace(
            source.current,
            polygons=(replace(source.current.polygons[0], exterior=((10, 0), (12, 0), (12, 2), (10, 2))),),
        )
        window.refresh()
        wait_until(lambda: not window._busy)
        assert window.selected_object.object_id == 1
        assert window.canvas._selection_anchor == (11, 1)

    def test_manual_refresh_preserves_view_filters_and_selection(self, live_window):
        window, source, _ = live_window
        window.stop_live()
        window.set_visible_layers(["TOP", "BOTTOM"])
        window.select_net("GND")
        window.network_panel.search.setText("GN")
        window.select_object(1)
        window.canvas.camera.center_x = 42
        window.canvas.camera.scale = 123
        window.canvas.opacity = 0.33
        source.current = scene(1, 2)
        finished, nets = [], []
        window.refresh_finished.connect(finished.append)
        window.net_changed.connect(nets.append)
        window.refresh()
        wait_until(lambda: len(finished) == 1)
        assert window.canvas.scene is source.current
        assert window.selected_object.object_id == 1
        assert window.selected_net == "GND" and nets == []
        assert window.network_panel.search.text() == "GN"
        assert window.visible_layers == ("TOP", "BOTTOM")
        assert window.canvas.camera.center_x == 42 and window.canvas.camera.scale == 123
        assert window.canvas.opacity == 0.33
        assert window.select_object(2).object_id == 2

    def test_automatic_batch_update_and_deleted_selection(self, live_window):
        window, source, changes = live_window
        window.select_object(1)
        finished = []
        window.refresh_finished.connect(finished.append)
        with window.batch_update():
            for i in range(50):
                source.current = scene(i + 2)
                with changes.batch():
                    changes._dirty = True
        wait_until(lambda: len(finished) == 1)
        assert source.calls == 2
        assert window.selected_object is None
        assert window.select_object(51).object_id == 51

    def test_background_script_leaves_event_loop_active(self, live_window):
        window, source, _ = live_window
        results = []
        started, release = Event(), Event()
        window.script_finished.connect(results.append)

        @layout_mutation
        def edit(owner):
            source.current = scene(9)

        def draw():
            edit(SimpleNamespace(_pedb=source))
            started.set()
            assert release.wait(5)
            return "done"

        window.run_script(draw)
        try:
            assert started.wait(5)
            with pytest.raises(RuntimeError, match="already running"):
                window.run_script(draw)
            wait_until(lambda: window.canvas.scene is source.current)
            assert results == []  # Rendering completed while the script was still running.
        finally:
            release.set()
        wait_until(lambda: results == ["done"])

    def test_edits_during_preparation_are_not_lost(self, live_window, monkeypatch):
        window, source, changes = live_window
        import pyedb.viewer.qt.window as module

        original = module.prepare_scene
        entered, release = Event(), Event()

        def prepare(*args, **kwargs):
            entered.set()
            assert release.wait(5)
            return original(*args, **kwargs)

        monkeypatch.setattr(module, "prepare_scene", prepare)
        source.current = scene(2)
        window.refresh()
        try:
            assert entered.wait(5)
            source.current = scene(3)
            with changes.batch():
                changes._dirty = True
            # Deliver the notification while the first mesh is being prepared.
            from PySide6.QtWidgets import QApplication

            QApplication.processEvents()
        finally:
            release.set()
        wait_until(lambda: window.canvas.scene is source.current and not window._busy)
        assert window.select_object(3).object_id == 3
        assert source.calls == 3

    def test_close_during_capture_waits_before_releasing_source(self, live_window):
        window, source, changes = live_window
        entered, release = Event(), Event()
        capture = window._source
        loader = capture.loader

        def read(*args, **kwargs):
            entered.set()
            assert release.wait(5)
            return loader(*args, **kwargs)

        capture.loader = read
        window.refresh()
        try:
            assert entered.wait(5)
            window.close()
            assert window._closed and window._close_after_capture
            assert window._source is capture and capture.loader is read
            assert not changes._listeners
        finally:
            release.set()
        wait_until(lambda: window._source is None)
        assert capture.loader is None
        assert not changes.closed  # The window never closes its caller's EDB.

    def test_many_refresh_requests_during_capture_merge_into_one_followup(self, live_window):
        window, source, _ = live_window
        entered, release = Event(), Event()
        original = window._source.loader

        def read(*args, **kwargs):
            entered.set()
            assert release.wait(5)
            return original(*args, **kwargs)

        window._source.loader = read
        window.refresh()
        try:
            assert entered.wait(5)
            for _ in range(20):
                window.refresh()
        finally:
            release.set()
        wait_until(lambda: source.calls == 3 and not window._busy)

    def test_script_errors_are_reported_and_another_script_can_run(self, live_window):
        window, _, _ = live_window
        errors, results = [], []
        window.script_failed.connect(errors.append)
        window.script_finished.connect(results.append)

        def broken():
            raise ValueError("Bad geometry")

        window.run_script(broken)
        wait_until(lambda: bool(errors))
        assert isinstance(errors[0], ValueError)
        assert window.canvas.error is None
        window.run_script(lambda: 42)
        wait_until(lambda: results == [42])

    def test_refresh_failure_retains_old_scene_and_can_retry(self, live_window):
        window, source, _ = live_window
        previous = window.canvas.scene
        loader = window._source.loader
        window._source.loader = Mock(side_effect=RuntimeError("temporary read failure"))
        failures = []
        window.refresh_failed.connect(failures.append)
        window.refresh()
        wait_until(lambda: bool(failures))
        assert window.canvas.scene is previous
        assert window.canvas.error is None
        assert not window._closed
        window._source.loader = loader
        source.current = scene(4)
        window.refresh()
        wait_until(lambda: window.canvas.scene is source.current and not window._busy)
        assert window.select_object(4).object_id == 4

    def test_close_detaches_source_and_session_close_keeps_snapshot(self, live_window):
        window, source, changes = live_window

        @layout_session_close
        def close(edb):
            return True

        close(source)
        wait_until(lambda: window._unsubscribe is None)
        assert window.select_object(1).object_id == 1
        with pytest.raises(RuntimeError, match="session is closed"):
            window.refresh()
        window.close()
        assert window._source is None and not changes._listeners

    def test_closed_and_detached_windows_reject_refresh(self, live_window):
        window, _, _ = live_window
        window._source = None
        with pytest.raises(RuntimeError, match="EDB session"):
            window.refresh()
        window.close()
        with pytest.raises(RuntimeError, match="viewer is closed"):
            window.refresh()


def test_launch_forwards_live_options_and_manual_refresh_source(monkeypatch):
    pytest.importorskip("PySide6")
    show = Mock()
    monkeypatch.setattr("pyedb.viewer.qt.app.show_scene", show)
    edb = SimpleNamespace(edbpath="board.aedb")
    launch_viewer(edb, live=True, refresh_interval=80, layers="TOP", nets="GND")
    assert show.call_args.kwargs["live"] is True
    assert show.call_args.kwargs["refresh_interval"] == 80
    capture = show.call_args.kwargs["loader"]
    extract = Mock(return_value=scene(1))
    monkeypatch.setattr("pyedb.viewer.scene_from_edb", extract)
    capture(None)
    capture.release_source()
    capture(None)
    assert extract.call_count == 2
    assert extract.call_args.kwargs["layers"] == "TOP"
    assert extract.call_args.kwargs["nets"] == "GND"


@pytest.mark.parametrize("interval", [-1, 0.5, True])
def test_invalid_live_options(interval):
    with pytest.raises(ValueError, match="refresh_interval"):
        launch_viewer(scene=scene(1), refresh_interval=interval)
    with pytest.raises(ValueError, match="requires an EDB"):
        launch_viewer(scene=scene(1), live=True)

# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Optional, Qt-independent notifications for changes to a gRPC layout."""

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from inspect import signature
import logging
from threading import Lock, RLock

_creation_lock = Lock()
_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PadstackSource:
    """Tag an isolated via handle without importing the EDB client in this module."""

    core: object


@dataclass(frozen=True)
class LayoutChangeSet:
    """Coalesced source records since one viewer's last capture.

    Source handles are used only under the session lock, never by Qt or GPU
    workers. A bounded journal lets multiple windows consume independently.
    """

    revision: int
    upserts: tuple = ()
    removed: frozenset = frozenset()
    full: bool = False


class LayoutChanges:
    """Serialize viewer reads with geometry edits and coalesce nested edits."""

    def __init__(self):
        self.lock = RLock()
        self.revision = 0
        self.closed = False
        self._depth = 0
        self._dirty = False
        self._listeners = set()
        self._listener_lock = Lock()
        self._records = {}
        self._full = False
        self._history = deque(maxlen=128)

    def record(self, object_id, core=None):
        """Record an upsert or deletion inside a locked mutation batch."""
        self._dirty = True
        if self._full:
            return
        if len(self._records) >= 8192:
            self.invalidate()
            return
        self._records[object_id] = core

    def invalidate(self):
        """Require a fresh snapshot for operations with unknown dependencies."""
        self._dirty = self._full = True
        self._records.clear()

    def since(self, revision):
        """Return last-write-wins changes; caller must hold ``lock``."""
        if revision == self.revision:
            return LayoutChangeSet(self.revision)
        if not self._history or revision < self._history[0].revision - 1:
            return LayoutChangeSet(self.revision, full=True)
        records = {}
        for delta in self._history:
            if delta.revision <= revision:
                continue
            if delta.full:
                return LayoutChangeSet(self.revision, full=True)
            records.update(delta.upserts)
            records.update((key, None) for key in delta.removed)
        return LayoutChangeSet(
            self.revision,
            tuple((key, core) for key, core in records.items() if core is not None),
            frozenset(key for key, core in records.items() if core is None),
        )

    def subscribe(self, callback):
        """Subscribe to revisions; return an idempotent unsubscribe function."""
        with self._listener_lock:
            self._listeners.add(callback)

        def unsubscribe():
            with self._listener_lock:
                self._listeners.discard(callback)

        return unsubscribe

    @contextmanager
    def batch(self):
        """Hold off source reads and publish one revision when edits finish.

        This is notification batching, not a database transaction. Successful
        edits still publish if a later operation in the batch raises.
        """
        with self.lock:
            self._depth += 1
            try:
                yield
            finally:
                self._depth -= 1
                if self._depth == 0 and self._dirty:
                    self._dirty = False
                    self.revision += 1
                    # Bound both revisions and retained source handles. Falling
                    # behind this journal is safe: consumers recapture fully.
                    full = self._full or not self._records or len(self._records) > 8192
                    if sum(len(item.upserts) for item in self._history) + len(self._records) > 8192:
                        self._history.clear()
                    self._history.append(
                        LayoutChangeSet(
                            self.revision,
                            ()
                            if full
                            else tuple((key, core) for key, core in self._records.items() if core is not None),
                            frozenset()
                            if full
                            else frozenset(key for key, core in self._records.items() if core is None),
                            full,
                        )
                    )
                    self._records.clear()
                    self._full = False
                    with self._listener_lock:
                        listeners = tuple(self._listeners)
                    for callback in listeners:
                        try:
                            callback(self.revision)
                        except Exception:
                            # A display must never turn a completed edit into a failure.
                            _logger.exception("Layout change listener failed")


def layout_changes(edb):
    """Get or create notification state only when a viewer requests it."""
    with _creation_lock:
        state = vars(edb).get("_layout_changes")
        if state is None or state.closed:
            state = edb._layout_changes = LayoutChanges()
        return state


def layout_mutation(method):
    """Notify after a geometry method or setter completes successfully.

    Class factories take a layout as their first argument. Instance methods
    take a wrapper with ``_pedb``. Without an attached viewer this is a fast
    pass-through and introduces no Qt dependency.
    """

    owner_parameter = next(iter(signature(method).parameters))

    @wraps(method)
    def wrapped(*args, **kwargs):
        owner = args[0] if args else kwargs.get(owner_parameter)
        if isinstance(owner, type):
            layout = kwargs.get("layout", args[1] if len(args) > 1 else None)
            edb = getattr(layout, "_pedb", None)
        else:
            edb = getattr(owner, "_pedb", None)
        state = vars(edb).get("_layout_changes") if edb is not None else None
        if not isinstance(state, LayoutChanges):
            return method(*args, **kwargs)
        with state.batch():
            before = _primitive_record(owner) if method.__name__ == "delete" else None
            result = method(*args, **kwargs)
            if result is not False:
                if before is not None:
                    state.record(before[0])
                elif method.__name__ in {
                    "create",
                    "create_rectangle",
                    "create_polygon",
                    "create_circle",
                    "create_trace",
                    "_create_path",
                    "place",
                }:
                    record = _primitive_record(result)
                    state.record(*record) if record is not None else state.invalidate()
                elif method.__name__ in {
                    "subtract",
                    "intersect",
                    "unite",
                    "add_void",
                    "convert_to_polygon",
                    "clone",
                    "duplicate_across_layers",
                    "fix_self_intersections",
                    "delete",
                }:
                    state.invalidate()
                else:
                    record = _primitive_record(owner)
                    state.record(*record) if record is not None else state.invalidate()
            return result

    return wrapped


def _primitive_record(wrapper):
    """Recognize single copper edits without importing backend wrapper classes."""
    try:
        module = type(wrapper).__module__
        if module == "pyedb.grpc.database.primitive.padstack_instance":
            core = wrapper.core
            component = core.component
            if component is not None and not component.is_null:
                return None  # Pin edits can also change a component's envelope.
            return core.edb_uid, PadstackSource(core)
        if module not in {
            "pyedb.grpc.database.primitive." + name for name in ("primitive", "polygon", "rectangle", "circle", "path")
        }:
            return None
        core = wrapper.core
        # Editing a void also changes its owner, whose id is not exposed here.
        if core.is_void:
            return None
        object_id = core.id
        return (object_id, core) if isinstance(object_id, int) and not isinstance(object_id, bool) else None
    except Exception:
        return None


def layout_session_close(method):
    """Wait for an active viewer read before closing its source session."""

    @wraps(method)
    def wrapped(edb, *args, **kwargs):
        state = vars(edb).get("_layout_changes")
        if state is None:
            return method(edb, *args, **kwargs)
        with state.batch():
            result = method(edb, *args, **kwargs)
            if result is not False:
                state.closed = True
                state._history.clear()
                state._dirty = True
            return result

    return wrapped

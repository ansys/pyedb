# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Source capture for detached snapshots and refreshable session views."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable


@dataclass(frozen=True)
class CaptureResult:
    """A captured snapshot and the revision it actually contains."""

    scene: Any
    revision: int
    patch: Any = None
    changed: frozenset = frozenset()


def merge_scene(previous, patch, changed):
    """Replace only changed source records, preserving untouched value identities."""
    from pyedb.viewer.mesh import scene_network_names

    updates = {}
    for name in ("polygons", "traces", "joins", "pads", "object_info"):
        updates[name] = tuple(item for item in getattr(previous, name) if item.object_id not in changed) + getattr(
            patch, name
        )
    updates["net_names"] = tuple(dict.fromkeys((*scene_network_names(previous)[1:], *scene_network_names(patch)[1:])))
    updates["diagnostics"] = tuple(dict.fromkeys((*previous.diagnostics, *patch.diagnostics)))
    return replace(previous, **updates)


class SourceCapture:
    def __init__(
        self, loader: Callable[..., Any], progressive: bool = True, *, changes=None, delta_loader=None
    ) -> None:
        self.loader = loader
        self.progressive = progressive
        self.preview = None
        self.changes = changes
        self.revision = -1
        self.delta_loader = delta_loader

    def set_preview(self, callback: Callable[..., Any] | None) -> None:
        if self.progressive:
            self.preview = callback

    def __call__(self, progress: Callable[[str, int, int], None] | None) -> Any:
        if self.changes is None:
            return self.loader(progress, preview=self.preview)
        result = self.capture(progress, full=True)
        self.revision = result.revision
        return result.scene

    def capture(self, progress=None, *, previous=None, full=False):
        """Capture a full snapshot or a journal delta under the source lock.

        The consumer commits ``revision`` only after mesh preparation succeeds,
        so failed preparation never drops notifications on the next refresh.
        """
        with self.changes.lock:
            if self.changes.closed:
                raise RuntimeError("The source EDB session is closed.")
            delta = self.changes.since(self.revision)
            if not full and previous is not None and self.delta_loader is not None and not delta.full:
                changed = frozenset(key for key, _ in delta.upserts) | delta.removed
                if not changed:
                    return CaptureResult(previous, delta.revision, previous, changed)
                patch = self.delta_loader(delta, previous, progress)
                return CaptureResult(merge_scene(previous, patch, changed), delta.revision, patch, changed)
            scene = self.loader(progress, preview=self.preview)
            return CaptureResult(scene, self.changes.revision)

    def release_source(self) -> None:
        self.preview = None
        if self.changes is None:
            self.loader = None

    def close(self) -> None:
        """Release the caller-owned session after the last capture finishes."""
        self.preview = self.loader = None
        self.delta_loader = None

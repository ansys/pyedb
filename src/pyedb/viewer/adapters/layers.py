# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Live, per-open layer source. All EDB access belongs to one worker queue."""

import math

from pyedb.viewer.adapters.grpc import (
    _components,
    _conductor_names,
    _padstack_layers,
    _padstacks,
    _primitives,
    _scene_filters,
)
from pyedb.viewer.progress import progress_items
from pyedb.viewer.scene import LayoutScene, SceneLayer


class LayerSceneSource:
    """Index source handles once; extract geometry only for requested layers.

    The caller owns the EDB session and must keep it open until the window
    closes. No EDB access occurs in the constructor or after ``release_source``.
    StreamItems still enumerates the full collection on current EDB servers.
    """

    def __init__(
        self,
        edb,
        *,
        layers=None,
        nets=None,
        arc_segments=None,
        chord_error=0.01,
        analytic_traces=False,
        exact_component_bounds=False,
        progressive=True,
    ):
        self.edb = edb
        self.layer_filter, self.net_filter = layers, nets
        self.arc_segments, self.chord_error = arc_segments, chord_error
        self.analytic_traces = analytic_traces
        self.exact_component_bounds = exact_component_bounds
        self.progressive = progressive
        self.layers = None
        self.primitives = {}
        self.pads = None
        self.components = None
        self.pad_state = {}
        self.diagnostics = []

    def _index(self, progress):
        if self.layers is not None:
            return
        if self.edb is None:
            raise RuntimeError("The layer source has been closed.")
        if not self.edb.grpc:
            raise ValueError("The interactive layout viewer currently supports only the gRPC backend.")
        arc_segments, chord_error = self.arc_segments, self.chord_error
        if arc_segments is None:
            if (
                isinstance(self.chord_error, bool)
                or not isinstance(self.chord_error, (float, int))
                or not math.isfinite(self.chord_error)
                or self.chord_error <= 0
            ):
                raise ValueError("chord_error must be a positive finite number in millimeters.")
            arc_segments = 8
        elif isinstance(self.arc_segments, bool) or not isinstance(self.arc_segments, int) or self.arc_segments < 3:
            raise ValueError("arc_segments must be an integer of at least three.")
        else:
            chord_error = None
        selected, self.selected_nets = _scene_filters(self.edb, self.layer_filter, self.net_filter)
        layers = tuple(
            SceneLayer(name, (*tuple(float(v) / 255 for v in layer.color[:3]), 1.0))
            for name, layer in self.edb.stackup.layers.items()
            if name in selected
        )
        self.net_names = tuple(self.edb.nets.nets)
        self.title = self.edb.active_cell.name
        primitives = {layer.name: [] for layer in layers}
        for primitive in progress_items(lambda: self.edb.layout.primitives, progress, "Reading polygons"):
            if not primitive.is_void and primitive.layer_name in primitives:
                primitives[primitive.layer_name].append(primitive)
        self.primitives = primitives
        self.layers = layers
        self.arc_segments, self.chord_error = arc_segments, chord_error

    def _index_pads(self, progress):
        if self.pads is not None:
            return
        conductors = _conductor_names(self.edb)
        selected = set(self.primitives)
        extended = bool(set(conductors).difference(self.edb.stackup.signal_layers))
        manager = getattr(self.edb, "padstacks", None)
        pads = {name: [] for name in selected}
        spans = {}
        for instance in progress_items(
            lambda: manager.instances.values() if manager is not None else (), progress, "Reading pads and vias"
        ):
            try:
                if self.selected_nets is not None and instance.net_name not in self.selected_nets:
                    continue
                span = _padstack_layers(instance, selected, conductors, extended)
                spans[instance.id] = tuple(span)
                for name in span:
                    pads[name].append(instance)
            except Exception as exc:
                self.diagnostics.append(f"Padstack {instance.id}: {exc}")
        self.pad_state["spans"] = spans
        self.pads = pads

    def _index_components(self, progress):
        if self.components is not None:
            return
        manager = getattr(self.edb, "components", None)
        components = {name: [] for name in self.primitives}
        for reference, component in progress_items(
            lambda: manager.instances.items() if manager is not None else (), progress, "Reading components"
        ):
            try:
                layer = component.placement_layer
                if layer in components:
                    components[layer].append((reference, component))
            except Exception as exc:
                self.diagnostics.append(f"Component {reference}: {exc}")
        self.components = components

    def load_layer(self, name=None, *, progress=None, preview=None):
        """Return one layer with stable global layer order and network IDs."""
        if self.edb is None:
            raise RuntimeError("The layer source has been closed.")
        self._index(progress)
        if name is None:
            name = self.layers[0].name if self.layers else None
        if name is not None and name not in self.primitives:
            raise ValueError(f"Unknown layer: {name}")
        if name is None:
            return None, LayoutScene(self.layers, (), self.title, net_names=self.net_names)
        diagnostics = list(self.diagnostics)
        polygons, traces, joins, pads = _primitives(
            self.edb,
            {name},
            self.selected_nets,
            self.arc_segments,
            diagnostics,
            progress,
            self.analytic_traces,
            self.chord_error,
            source=self.primitives[name],
        )

        def scene(components=()):
            return LayoutScene(
                self.layers,
                tuple(polygons),
                self.title,
                tuple(diagnostics),
                tuple(traces),
                tuple(pads),
                tuple(joins),
                self.net_names,
                components,
            )

        if self.progressive and preview is not None and (polygons or traces or pads):
            preview(name, scene())
        self._index_pads(progress)
        diagnostics.extend(note for note in self.diagnostics if note not in diagnostics)
        component_geometry = None if self.exact_component_bounds else {}
        via_pads, via_polygons = _padstacks(
            self.edb,
            {name},
            self.selected_nets,
            self.arc_segments,
            diagnostics,
            progress,
            component_geometry,
            self.chord_error,
            instances=self.pads[name],
            state=self.pad_state,
        )
        pads.extend(via_pads)
        polygons.extend(via_polygons)
        self._index_components(progress)
        diagnostics.extend(note for note in self.diagnostics if note not in diagnostics)
        components = _components(
            self.edb,
            {name},
            self.selected_nets,
            diagnostics,
            progress,
            component_geometry,
            instances=self.components[name],
        )
        return name, scene(components)

    def release_source(self):
        """Drop this window's references without closing the caller's EDB."""
        self.edb = None
        self.primitives.clear()
        self.pads = None
        self.components = None
        self.pad_state.clear()

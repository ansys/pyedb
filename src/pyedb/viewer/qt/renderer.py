# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Resident layout geometry rendered through Qt RHI.

Separate stencil bits preserve exterior/hole ownership. Analytic primitives
are marked into a reusable texture and composited once per category.
"""

import math

import numpy as np
from PySide6.QtGui import QRhiBuffer, QRhiColorAttachment, QRhiTextureRenderTargetDescription

from pyedb.viewer.colors import (
    COMPONENT_COLORS,
    DRILL_COLOR,
    HIGHLIGHT_KEYLINE_COLOR,
    HOVER_COLOR,
    SELECTION_COLOR,
    net_color,
)
from pyedb.viewer.qt.component_labels import ComponentLabels
from pyedb.viewer.qt.coverage import SdfCoverage
from pyedb.viewer.qt.grid import GridRenderer
from pyedb.viewer.qt.rhi import Device, Target, camera_uniforms
from pyedb.viewer.scene import ScenePolygon


class Renderer:
    def __init__(self):
        self.device = self.main = self.mask = None
        self.vbo = self.ebo = self.net_vbo = None
        self.outline_vbo = None
        self._outline_ranges = {}
        self.prepared = None
        self.upload_count = self.draw_calls = 0
        self.layer_batches = {}
        self.sdf = SdfCoverage()
        self.labels = ComponentLabels()
        self.grid = GridRenderer()
        self._overlay_ranges = {}
        self._polygon_objects = {}
        self._target_key = None

    def initialize(self, widget):
        """Create resources for the widget's current device and attachments."""
        if self.device is None:
            self.device = Device(widget.rhi())
        target = widget.renderTarget()
        size = target.pixelSize()
        key = (
            size.width(),
            size.height(),
            target.sampleCount(),
            target,
            widget.colorTexture(),
            widget.resolveTexture(),
            widget.msaaColorBuffer(),
            widget.depthStencilBuffer(),
        )
        if key == self._target_key:
            return
        self.device.release_targets()
        if self.main is not None:
            self.main.release()
            self.mask.release()
        attachment = QRhiColorAttachment(
            widget.msaaColorBuffer() if target.sampleCount() > 1 else widget.colorTexture()
        )
        if target.sampleCount() > 1:
            attachment.setResolveTexture(widget.resolveTexture())
        description = QRhiTextureRenderTargetDescription(attachment, widget.depthStencilBuffer())
        self.main = Target(self.device, size, target.sampleCount(), description=description, preserve=True)
        self.mask = Target(self.device, size, target.sampleCount())
        self._target_key = key

    def upload(self, prepared, updates):
        """Upload once; progressive appends retain resident geometry prefixes."""
        old = self.prepared
        parent = old if old is not None and prepared.mesh_parent_id == id(old) else None
        if old is None or old.vertices is not prepared.vertices or old.batches is not prepared.batches:
            self._upload_outlines(prepared, updates, parent)
        for name, attribute, usage in (
            ("vertices", "vbo", QRhiBuffer.UsageFlag.VertexBuffer),
            ("indices", "ebo", QRhiBuffer.UsageFlag.IndexBuffer),
            ("vertex_nets", "net_vbo", QRhiBuffer.UsageFlag.VertexBuffer),
        ):
            values = getattr(prepared, name)
            if values is None:
                values = np.zeros(len(prepared.vertices), dtype=np.uint32)
            previous = getattr(self, attribute)
            if (
                old is not None
                and getattr(old, name) is getattr(prepared, name)
                and previous is not None
                and (name != "vertex_nets" or prepared.vertex_nets is not None)
            ):
                continue
            buffer = self.device.buffer(values, usage, previous)
            before = getattr(parent, name) if parent is not None else None
            append = before is not None and buffer is previous
            self.device.upload_buffer(
                updates, buffer, values[len(before) :] if append else values, before.nbytes if append else 0
            )
            setattr(self, attribute, buffer)
        self.prepared = prepared
        self.layer_batches = {}
        self._overlay_ranges.clear()
        self._polygon_objects = {}
        for batch in prepared.batches:
            self.layer_batches.setdefault(batch.layer, []).append(batch)
            self._polygon_objects.setdefault((batch.object_id, batch.layer, batch.category), []).append(batch)
        self.sdf.upload(self.device, updates, prepared, parent=parent)
        if old is None or old.component_batches is not prepared.component_batches:
            self.labels.upload(self.device, updates, prepared.component_batches)
        self.upload_count += 1

    def _upload_outlines(self, prepared, updates, parent):
        """Retain split-coordinate edge endpoints for instanced, antialiased strokes."""
        if prepared.outlines is not None:
            edges = prepared.outlines
            self._outline_ranges = {
                id(batch): (batch.vertex_start, sum(batch.ring_sizes)) for batch in prepared.batches
            }
            previous = self.outline_vbo
            self.outline_vbo = self.device.buffer(edges, QRhiBuffer.UsageFlag.VertexBuffer, previous)
            start = len(parent.vertices) if parent is not None and self.outline_vbo is previous else 0
            self.device.upload_buffer(updates, self.outline_vbo, edges[start:], start * 32)
            return
        edges = np.empty((len(prepared.vertices), 8), dtype=np.float32)
        self._outline_ranges = {}
        cursor = 0
        for batch in prepared.batches:
            start = cursor
            first = batch.vertex_start
            for size in batch.ring_sizes:
                ring = prepared.vertices[first : first + size]
                edges[cursor : cursor + size, :4] = ring
                edges[cursor : cursor + size, 4:] = np.roll(ring, -1, axis=0)
                cursor += size
                first += size
            self._outline_ranges[id(batch)] = start, cursor - start
        edges = np.ascontiguousarray(edges[:cursor])
        previous = self.outline_vbo
        self.outline_vbo = self.device.buffer(edges, QRhiBuffer.UsageFlag.VertexBuffer, previous)
        start = sum(sum(batch.ring_sizes) for batch in parent.batches) if parent is not None else 0
        if self.outline_vbo is not previous:
            start = 0
        self.device.upload_buffer(updates, self.outline_vbo, edges[start:], start * 32)

    def draw(
        self,
        command_buffer,
        updates,
        scene,
        camera,
        visible_layers,
        opacity,
        net,
        pixel_ratio,
        color_by_net=False,
        show_components=True,
        components_on_both_sides=True,
        annotate_component_names=True,
        show_grid=True,
        selection=None,
        hover=None,
        show_outlines=True,
    ):
        """Record bottom-to-top layers, then submit the frame and overlays."""
        self.device.begin_frame()
        self.uniforms = camera_uniforms(self.device.rhi, camera, pixel_ratio)
        self.uniforms[56] = self.main.samples > 1
        self.camera, self.pixel_ratio = camera, pixel_ratio
        self.draw_calls = self.labels.drawn_count = self.sdf.drawn_pin_count = 0
        self.device.begin_pass(self.main)
        self.grid.draw(self.device, self.uniforms, camera, pixel_ratio, show_grid)
        layers = scene.layers if camera.mirror else reversed(scene.layers)
        drill_layers = []
        if self.prepared is not None:
            for layer in layers:
                alpha = layer.color[3] * opacity
                if layer.name not in visible_layers or (alpha <= 0 and not show_outlines):
                    continue
                drill_layers.append(layer.name)
                for category in ("zone", "trace", "pad"):
                    self._polygons(layer, category, alpha, net, color_by_net, show_outlines)
                    if category != "zone":
                        self._analytic(
                            self.sdf.ranges(camera, [layer.name], category=category),
                            (*layer.color[:3], alpha),
                            net,
                            color_by_net=color_by_net,
                            outline=show_outlines,
                        )
            self._analytic(
                self.sdf.ranges(camera, drill_layers, drills=True), DRILL_COLOR, net, drills=True, outline=show_outlines
            )
            if show_components and opacity > 0:
                groups = {"top": [], "bottom": []}
                for batch in self.sdf.component_batches:
                    component = batch.component
                    if component.visible_on(drill_layers, camera.mirror, net, components_on_both_sides) and (
                        camera.visible(component.bounds)
                    ):
                        groups[component.side].append((batch.instance_start, 1))
                for side in ("top", "bottom") if camera.mirror else ("bottom", "top"):
                    self._analytic(groups[side], (*COMPONENT_COLORS[side], 1), None, components=True)
                if annotate_component_names:
                    self.draw_calls += self.labels.draw(
                        self.device, self.uniforms, camera, drill_layers, 1, net, components_on_both_sides
                    )
            if opacity > 0:
                for hit, hovering in ((selection, False), (hover, True)):
                    if hit is not None and not (hovering and selection is not None and hit.key == selection.key):
                        self._selection(hit, visible_layers, net, hovering)
        self.device.submit(command_buffer, updates)

    def _mesh(self, uniforms, start, count, *, blend="alpha", stencil=None, scissor=None, reference=0):
        self.device.draw(
            "copper",
            uniforms,
            layout="mesh",
            buffers=((self.vbo, 0), (self.net_vbo, 0)),
            index=self.ebo,
            start=start,
            count=count,
            texture=self.sdf.palette,
            blend=blend,
            stencil=stencil,
            scissor=scissor,
            reference=reference,
        )

    def _rectangle(self, uniforms, *, blend="alpha", stencil=None, scissor=None, reference=0):
        values = uniforms.copy()
        values[36] = 1
        self.device.draw(
            "copper",
            values,
            texture=self.sdf.palette,
            blend=blend,
            stencil=stencil,
            scissor=scissor,
            reference=reference,
        )

    def _polygons(self, layer, category, alpha, net, color_by_net, show_outlines):
        uniforms = self.uniforms.copy()
        uniforms[28:32] = *layer.color[:3], alpha
        uniforms[37] = float(color_by_net and self.prepared.vertex_nets is not None)
        solid_start = solid_count = 0
        outlines = []
        for batch in self.layer_batches.get(layer.name, ()):
            if (
                batch.category != category
                or (net is not None and batch.net != net)
                or not self.camera.visible(batch.bounds)
            ):
                continue
            if show_outlines:
                outlines.append(batch)
            if not batch.hole_count:
                if solid_count and solid_start + solid_count != batch.index_start:
                    self._mesh(uniforms, solid_start, solid_count)
                    self.draw_calls += 1
                    solid_count = 0
                if not solid_count:
                    solid_start = batch.index_start
                solid_count += batch.outer_count
                continue
            if solid_count:
                self._mesh(uniforms, solid_start, solid_count)
                self.draw_calls += 1
                solid_count = 0
            masked = uniforms.copy()
            if color_by_net:
                masked[28:31] = net_color(self.sdf.net_ids.get(batch.net, 0)) or layer.color[:3]
            self._batch(batch, masked)
        if solid_count:
            self._mesh(uniforms, solid_start, solid_count)
            self.draw_calls += 1
        if outlines:
            values = self.uniforms.copy()
            values[28:32] = *layer.color[:3], 1
            ranges = []
            for batch in outlines:
                start, count = self._outline_ranges[id(batch)]
                if ranges and sum(ranges[-1]) == start:
                    ranges[-1][1] += count
                else:
                    ranges.append([start, count])
            for start, count in ranges:
                self.device.draw(
                    "outline",
                    values,
                    layout="outline",
                    buffers=((self.outline_vbo, start * 32), (self.net_vbo, start * 4)),
                    instances=count,
                    texture=self.sdf.palette,
                )
            self.draw_calls += len(ranges)

    def _batch(self, batch, uniforms):
        a = self.camera.world_to_screen(*batch.bounds[:2])
        b = self.camera.world_to_screen(*batch.bounds[2:])
        left, right = max(0.0, min(a[0], b[0])), min(self.camera.width, max(a[0], b[0]))
        top, bottom = max(0.0, min(a[1], b[1])), min(self.camera.height, max(a[1], b[1]))
        if left >= right or top >= bottom:
            return
        values = uniforms.copy()
        values[32:36] = left, top, right, bottom
        # QRhi scissor coordinates, like QRhiViewport, have a bottom-left origin.
        x0, x1 = math.floor(left * self.pixel_ratio), math.ceil(right * self.pixel_ratio)
        y0 = math.floor((self.camera.height - bottom) * self.pixel_ratio)
        y1 = math.ceil((self.camera.height - top) * self.pixel_ratio)
        scissor = x0, y0, x1 - x0, y1 - y0
        self._rectangle(values, blend="none", stencil=("clear", 3), scissor=scissor)
        self._mesh(
            values,
            batch.index_start,
            batch.outer_count,
            blend="none",
            stencil=("mark", 1),
            scissor=scissor,
            reference=1,
        )
        if batch.hole_count:
            self._mesh(
                values,
                batch.index_start + batch.outer_count,
                batch.hole_count,
                blend="none",
                stencil=("mark", 2),
                scissor=scissor,
                reference=2,
            )
        self._rectangle(values, stencil=("cover", 0), scissor=scissor, reference=1)
        self.draw_calls += 3 + bool(batch.hole_count)

    def _mark(self, ranges, uniforms):
        for start, count in ranges:
            self.device.draw(
                "sdf",
                uniforms,
                layout="sdf",
                buffers=((self.sdf.vbo, start * 160),),
                instances=count,
                texture=self.sdf.palette,
                blend="union",
            )
        self.draw_calls += len(ranges)

    def _analytic(self, ranges, color, net, *, drills=False, color_by_net=False, components=False, outline=False):
        if not ranges:
            return
        values = self.uniforms.copy()
        values[25:28] = -1 if net is None else self.sdf.net_ids.get(net, -2), drills, components
        values[28:32] = color
        values[37] = (color_by_net and not drills) or outline
        values[39] = outline
        values[58] = color_by_net and not drills
        self.device.begin_pass(self.mask)
        self._mark(ranges, values)
        self.device.begin_pass(self.main)
        self.device.draw("coverage", values, layout="fullscreen", count=3, texture=self.mask.texture)
        self.draw_calls += 1

    def _object_ranges(self, hit, visible_layers, net):
        key = hit.key, frozenset(visible_layers), net
        if key not in self._overlay_ranges:
            polygons, identities = [], []
            for item in hit.object.items:
                if item.layer not in visible_layers or (net is not None and item.net != net):
                    continue
                if isinstance(item, ScenePolygon):
                    polygons.extend(self._polygon_objects.get((item.object_id, item.layer, item.category), ()))
                else:
                    identities.append(id(item))
            sources = self.prepared.sdf_sources
            if self.prepared.sdf_ranges is not None:
                indices = sorted(
                    index
                    for source in identities
                    for start, count in self.prepared.sdf_ranges.get(source, ())
                    for index in range(start, start + count)
                )
            else:
                indices = np.flatnonzero(np.isin(sources, identities)) if identities and sources is not None else ()
            ranges = []
            for index in indices:
                if ranges and sum(ranges[-1]) == index:
                    ranges[-1][1] += 1
                else:
                    ranges.append([int(index), 1])
            if len(self._overlay_ranges) >= 4:
                self._overlay_ranges.clear()
            self._overlay_ranges[key] = polygons, ranges
        return self._overlay_ranges[key]

    def _selection(self, hit, visible_layers, net, hovering):
        polygons, ranges = self._object_ranges(hit, visible_layers, net)
        if not polygons and not ranges:
            return
        self.device.begin_pass(self.mask)
        values = self.uniforms.copy()
        values[28:32] = 1
        for polygon in polygons:
            if self.camera.visible(polygon.bounds):
                self._batch(polygon, values)
        self._mark(ranges, values)
        self.device.begin_pass(self.main)
        values[20:22] = self.main.size.width(), self.main.size.height()
        values[44:46] = hovering, hit.object.info.kind in {"trace", "zone"}
        values[48:51] = HOVER_COLOR if hovering else SELECTION_COLOR
        values[52:55] = HIGHLIGHT_KEYLINE_COLOR
        self.device.draw("selection", values, layout="fullscreen", count=3, texture=self.mask.texture)
        self.draw_calls += 1

    def release(self):
        """Release resources before Qt destroys their owning RHI device."""
        if self.device is not None:
            self.device.release()
        if self.main is not None:
            self.main.release()
        if self.mask is not None:
            self.mask.release()
        self.device = self.main = self.mask = None
        self.vbo = self.ebo = self.net_vbo = None
        self.outline_vbo = None
        self._outline_ranges.clear()
        self.sdf = SdfCoverage()
        self.labels = ComponentLabels()
        self.prepared = None
        self._target_key = None
        self._overlay_ranges.clear()
        self._polygon_objects.clear()

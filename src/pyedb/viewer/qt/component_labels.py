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

"""Resident reference-label atlas and instances, built once on the GUI thread."""

from __future__ import annotations

from collections.abc import Collection, Sequence
import math
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen, QRhi, QRhiBuffer, QRhiTexture

from pyedb.viewer.colors import COMPONENT_OUTLINE_COLOR
from pyedb.viewer.mesh import split_coordinates

if TYPE_CHECKING:
    from pyedb.viewer.camera import Camera
    from pyedb.viewer.mesh import ComponentBatch
    from pyedb.viewer.scene import SceneComponent


class ComponentLabels:
    """Reference labels use immutable GPU sprites, with CPU visibility/decluttering."""

    def __init__(self):
        self.vbo = self.texture = None
        self.records = ()
        self.drawn_count = 0

    @staticmethod
    def _glyph(component: SceneComponent) -> tuple[QPainterPath, QRectF, int, int]:
        # Match nets.plot's small/large-component typography threshold: 6 mm².
        x0, y0, x1, y1 = component.bounds
        font = QFont()
        font.setPixelSize(16 if (x1 - x0) * (y1 - y0) < 6 else 24)
        path = QPainterPath()
        path.addText(0, 0, font, component.reference)
        bounds = path.boundingRect()
        return path, bounds, math.ceil(bounds.width()) + 8, math.ceil(bounds.height()) + 8

    def upload(self, device, updates, batches):
        """Bake labels at 2x density, then upload atlas and instance coordinates once."""
        self.records = ()
        if not batches:
            return
        limit = device.rhi.resourceLimit(QRhi.ResourceLimit.TextureSizeMax)
        glyphs = [self._glyph(batch.component) for batch in batches]
        width = min(2048, limit)
        if any(glyph[2] > width for glyph in glyphs):
            width = min(limit, max(glyph[2] for glyph in glyphs))
        placements = []
        x = y = row_height = 0
        for _, _, w, h in glyphs:
            if w > width:
                raise ValueError("A component reference exceeds the GPU label atlas width.")
            if x + w > width:
                x, y, row_height = 0, y + row_height, 0
            placements.append((x, y))
            x += w
            row_height = max(row_height, h)
        height = y + row_height
        if height > limit:
            raise ValueError("Component reference labels exceed the GPU label atlas capacity.")
        image = QImage(width, height, QImage.Format.Format_RGBA8888)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            QPen(QColor("white"), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        )
        painter.setBrush(QColor("black"))
        packets, records = [], []
        try:
            for batch, glyph, (x, y) in zip(batches, glyphs, placements):
                path, bounds, w, h = glyph
                painter.save()
                painter.translate(x + 4 - bounds.left(), y + 4 - bounds.top())
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(path)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor("black"))
                painter.drawPath(path)
                painter.restore()
                component = batch.component
                x0, y0, x1, y1 = component.bounds
                center = x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2
                packets.append(
                    (
                        *split_coordinates([center])[0],
                        w / 2,
                        h / 2,
                        float(component.side == "bottom"),
                        0,
                        x / width,
                        y / height,
                        (x + w) / width,
                        (y + h) / height,
                    )
                )
                records.append((component, center, w / 2, h / 2))
        finally:
            painter.end()
        if self.texture is not None:
            device.release_targets()
            self.texture.deleteLater()
            device.resources.remove(self.texture)
        self.texture = device.create(device.rhi.newTexture(QRhiTexture.Format.RGBA8, image.size()))
        updates.uploadTexture(self.texture, image)
        data = np.asarray(packets, dtype=np.float32)
        self.vbo = device.buffer(data, QRhiBuffer.UsageFlag.VertexBuffer, self.vbo)
        device.upload_buffer(updates, self.vbo, data)
        self.records = tuple(records)

    def _visible(self, camera: Camera, visible_layers: Collection[str], net: str | None, both_sides: bool) -> list[int]:
        candidates = []
        for index, (component, center, width, height) in enumerate(self.records):
            if not component.visible_on(visible_layers, camera.mirror, net, both_sides):
                continue
            if not camera.visible(component.bounds):
                continue
            x0, y0, x1, y1 = component.bounds
            # Reveal labels as footprints become large enough to read them.
            if (x1 - x0) * camera.scale < width or (y1 - y0) * camera.scale < height:
                continue
            x, y = camera.world_to_screen(*center)
            rectangle = x - width / 2 - 2, y - height / 2 - 2, x + width / 2 + 2, y + height / 2 + 2
            if rectangle[2] < 0 or rectangle[0] > camera.width or rectangle[3] < 0 or rectangle[1] > camera.height:
                continue
            near_side = component.side == ("bottom" if camera.mirror else "top")
            candidates.append((near_side, (x1 - x0) * (y1 - y0), index, rectangle))
        occupied, accepted = {}, []
        for _, _, index, rectangle in sorted(candidates, reverse=True):
            x0, y0, x1, y1 = rectangle
            cells = [
                (x, y)
                for x in range(math.floor(x0 / 64), math.floor(x1 / 64) + 1)
                for y in range(math.floor(y0 / 64), math.floor(y1 / 64) + 1)
            ]
            if any(
                not (x1 < r[0] or x0 > r[2] or y1 < r[1] or y0 > r[3]) for cell in cells for r in occupied.get(cell, ())
            ):
                continue
            accepted.append(index)
            for cell in cells:
                occupied.setdefault(cell, []).append(rectangle)
        return sorted(accepted)

    def draw(self, device, uniforms, camera, visible_layers, opacity, net, both_sides=False):
        self.drawn_count = 0
        if opacity <= 0:
            return 0
        accepted = self._visible(camera, visible_layers, net, both_sides)
        if not accepted:
            return 0
        ranges = []
        for index in accepted:
            if ranges and ranges[-1][0] + ranges[-1][1] == index:
                ranges[-1][1] += 1
            else:
                ranges.append([index, 1])
        values = uniforms.copy()
        values[28:32] = *COMPONENT_OUTLINE_COLOR, opacity
        for start, count in ranges:
            device.draw(
                "label",
                values,
                layout="label",
                buffers=((self.vbo, start * 48),),
                instances=count,
                texture=self.texture,
            )
        self.drawn_count = len(accepted)
        return len(ranges)

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

from ctypes import c_void_p
import math
from pathlib import Path

import numpy as np
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen

from pyedb.viewer.colors import COMPONENT_OUTLINE_COLOR
from pyedb.viewer.mesh import split_coordinates
from pyedb.viewer.qt.coverage import _shader_source


class ComponentLabels:
    """Reference labels use immutable GPU sprites, with CPU visibility/decluttering."""

    def __init__(self):
        self.program = self.vao = self.vbo = self.texture = 0
        self.records = ()
        self.drawn_count = 0

    def initialize(self):
        shaders = Path(__file__).with_name("shaders")
        self.program = compileProgram(
            compileShader(_shader_source(shaders / "label.vert"), GL.GL_VERTEX_SHADER),
            compileShader(_shader_source(shaders / "label.frag"), GL.GL_FRAGMENT_SHADER),
            validate=False,
        )
        self.uniforms = {
            name: GL.glGetUniformLocation(self.program, name)
            for name in ("camera_split", "viewport", "scale", "mirror_x", "atlas", "opacity", "label_color")
        }
        self.vao = int(GL.glGenVertexArrays(1))
        self.vbo = int(GL.glGenBuffers(1))
        self.texture = int(GL.glGenTextures(1))

    @staticmethod
    def _glyph(component):
        # Match nets.plot's small/large-component typography threshold: 6 mm².
        x0, y0, x1, y1 = component.bounds
        font = QFont()
        font.setPixelSize(16 if (x1 - x0) * (y1 - y0) < 6 else 24)
        path = QPainterPath()
        path.addText(0, 0, font, component.reference)
        bounds = path.boundingRect()
        return path, bounds, math.ceil(bounds.width()) + 8, math.ceil(bounds.height()) + 8

    def upload(self, batches):
        """Bake labels at 2x density, then upload atlas and instance coordinates once."""
        self.records = ()
        if not batches:
            return
        limit = int(GL.glGetIntegerv(GL.GL_MAX_TEXTURE_SIZE))
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
        pixels = np.frombuffer(image.bits(), dtype=np.uint8, count=image.sizeInBytes())
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixels)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        data = np.asarray(packets, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_STATIC_DRAW)
        self.records = tuple(records)

    def _visible(self, camera, visible_layers, net, both_sides):
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

    def draw(self, camera, visible_layers, opacity, net, both_sides=False):
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
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFuncSeparate(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glUseProgram(self.program)
        u = self.uniforms
        GL.glUniform4fv(u["camera_split"], 1, split_coordinates([[camera.center_x, camera.center_y]])[0])
        GL.glUniform2f(u["viewport"], camera.width, camera.height)
        GL.glUniform1f(u["scale"], camera.scale)
        GL.glUniform1f(u["mirror_x"], -1 if camera.mirror else 1)
        GL.glUniform1f(u["opacity"], opacity)
        GL.glUniform3f(u["label_color"], *COMPONENT_OUTLINE_COLOR)
        GL.glUniform1i(u["atlas"], 0)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        for start, count in ranges:
            for location in range(3):
                GL.glEnableVertexAttribArray(location)
                GL.glVertexAttribPointer(location, 4, GL.GL_FLOAT, False, 48, c_void_p(start * 48 + location * 16))
                GL.glVertexAttribDivisor(location, 1)
            GL.glDrawArraysInstanced(GL.GL_TRIANGLE_STRIP, 0, 4, count)
        self.drawn_count = len(accepted)
        return len(ranges)

    def release(self):
        if self.vbo:
            GL.glDeleteBuffers(1, [self.vbo])
        if self.vao:
            GL.glDeleteVertexArrays(1, [self.vao])
        if self.texture:
            GL.glDeleteTextures([self.texture])
        if self.program:
            GL.glDeleteProgram(self.program)
        self.program = self.vao = self.vbo = self.texture = 0
        self.records = ()
        self.drawn_count = 0

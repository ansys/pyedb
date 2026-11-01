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

"""Resident geometry and object-local two-bit stencil coverage in a Qt-owned context.

Scene preparation, resident geometry and coverage passes are separate. Qt owns
the native window, buffer swaps and default framebuffer.
"""

from ctypes import c_void_p
import math
from pathlib import Path

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from pyedb.viewer.colors import BACKGROUND_COLOR, DRILL_COLOR, net_color
from pyedb.viewer.mesh import split_coordinates
from pyedb.viewer.qt.component_labels import ComponentLabels
from pyedb.viewer.qt.coverage import SdfCoverage, _shader_source
from pyedb.viewer.qt.grid import GridRenderer


class Renderer:
    def __init__(self):
        self.program = self.vao = self.quad_vao = self.vbo = self.ebo = 0
        self.prepared = None
        self.upload_count = 0
        self.draw_calls = 0
        self.layer_batches = {}
        self._stencil_checked = False
        self.sdf = SdfCoverage()
        self.labels = ComponentLabels()
        self.grid = GridRenderer()

    def initialize(self):
        """Create resources only with this widget's context current."""
        shader_dir = Path(__file__).with_name("shaders")
        self.program = compileProgram(
            compileShader(_shader_source(shader_dir / "copper.vert"), GL.GL_VERTEX_SHADER),
            compileShader(_shader_source(shader_dir / "copper.frag"), GL.GL_FRAGMENT_SHADER),
            validate=False,
        )
        self.uniforms = {
            name: GL.glGetUniformLocation(self.program, name)
            for name in ("camera_split", "viewport", "scale", "mirror_x", "rectangle_pass", "rectangle", "color")
        }
        self.vao, self.quad_vao = (int(v) for v in GL.glGenVertexArrays(2))
        self.vbo, self.ebo = (int(v) for v in GL.glGenBuffers(2))
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, False, 16, c_void_p(0))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBindVertexArray(0)
        self.sdf.initialize()
        self.labels.initialize()
        self.grid.initialize()

    def upload(self, prepared):
        """Upload once per snapshot, never on camera or visibility changes."""
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, prepared.vertices.nbytes, prepared.vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, prepared.indices.nbytes, prepared.indices, GL.GL_STATIC_DRAW)
        GL.glBindVertexArray(0)
        self.prepared = prepared
        self.layer_batches = {}
        for batch in prepared.batches:
            self.layer_batches.setdefault(batch.layer, []).append(batch)
        self.sdf.upload(prepared)
        self.labels.upload(prepared.component_batches)
        self.upload_count += 1

    def _indexed(self, start, count):
        GL.glDrawElements(GL.GL_TRIANGLES, count, GL.GL_UNSIGNED_INT, c_void_p(start * 4))
        self.draw_calls += 1

    def draw(
        self,
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
    ):
        """Draw in bottom-to-top layer order, preserving each object's hole ownership."""
        try:
            self._draw_frame(
                scene,
                camera,
                visible_layers,
                opacity,
                net,
                pixel_ratio,
                color_by_net,
                show_components,
                components_on_both_sides,
                annotate_component_names,
                show_grid,
            )
        finally:
            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_SCISSOR_TEST)
            GL.glStencilMask(0xFF)
            GL.glColorMask(True, True, True, True)
            GL.glBindVertexArray(0)
            GL.glUseProgram(0)

    def _draw_frame(
        self,
        scene,
        camera,
        visible_layers,
        opacity,
        net,
        pixel_ratio,
        color_by_net,
        show_components,
        components_on_both_sides,
        annotate_component_names,
        show_grid,
    ):
        # Qt creates its framebuffer after initializeGL. Query the actual FBO
        # attachment here; GL_STENCIL_BITS is not available in core profiles.
        if not self._stencil_checked:
            bits = GL.glGetFramebufferAttachmentParameteriv(
                GL.GL_DRAW_FRAMEBUFFER, GL.GL_STENCIL_ATTACHMENT, GL.GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE
            )
            if bits < 3:
                raise RuntimeError("The layout viewer requires an OpenGL framebuffer with stencil support.")
            self._stencil_checked = True
        GL.glViewport(0, 0, round(camera.width * pixel_ratio), round(camera.height * pixel_ratio))
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_FRAMEBUFFER_SRGB)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glColorMask(True, True, True, True)
        GL.glStencilMask(0xFF)
        GL.glClearStencil(0)
        GL.glClearColor(*BACKGROUND_COLOR)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        self.draw_calls = 0
        self.labels.drawn_count = 0
        self.sdf.drawn_pin_count = 0
        if show_grid:
            self.grid.draw(camera, pixel_ratio)
        if self.prepared is None:
            return
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendEquation(GL.GL_FUNC_ADD)
        GL.glBlendFuncSeparate(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
        u = self.uniforms
        layers = scene.layers if camera.mirror else reversed(scene.layers)
        drill_layers = []
        for layer in layers:
            alpha = layer.color[3] * opacity
            if layer.name not in visible_layers or alpha <= 0:
                continue
            drill_layers.append(layer.name)
            GL.glUseProgram(self.program)
            GL.glUniform4fv(u["camera_split"], 1, split_coordinates([[camera.center_x, camera.center_y]])[0])
            GL.glUniform2f(u["viewport"], camera.width, camera.height)
            GL.glUniform1f(u["scale"], camera.scale)
            GL.glUniform1f(u["mirror_x"], -1.0 if camera.mirror else 1.0)
            # Preserve ordered source-over transparency inside a conductor layer:
            # zones first, traces next, pads last. Each trace group still unions
            # its own segment coverage, so joins do not accumulate opacity.
            for category in ("zone", "trace", "pad"):
                self._polygons(layer, category, camera, pixel_ratio, alpha, net, color_by_net)
                if category != "zone":
                    self.draw_calls += self.sdf.draw(
                        camera,
                        pixel_ratio,
                        [layer.name],
                        (*layer.color[:3], alpha),
                        net,
                        color_by_net=color_by_net,
                        category=category,
                    )
        # Drill marks are separate from copper so a solid zone underneath a via
        # cannot fill its bore. Visibility/net selection also applies to drills.
        self.draw_calls += self.sdf.draw(camera, pixel_ratio, drill_layers, DRILL_COLOR, net, drills=True)
        if show_components and opacity > 0:
            self.draw_calls += self.sdf.draw_components(
                camera, pixel_ratio, drill_layers, 1.0, net, components_on_both_sides
            )
            if annotate_component_names:
                self.draw_calls += self.labels.draw(camera, drill_layers, 1.0, net, components_on_both_sides)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        GL.glStencilMask(0xFF)
        GL.glColorMask(True, True, True, True)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def _polygons(self, layer, category, camera, pixel_ratio, alpha, net, color_by_net):
        GL.glUseProgram(self.program)
        material = (*layer.color[:3], alpha)
        GL.glUniform4f(self.uniforms["color"], *material)
        solid_start = solid_count = 0
        for batch in self.layer_batches.get(layer.name, ()):
            if batch.category != category or (net is not None and batch.net != net) or not camera.visible(batch.bounds):
                continue
            rgb = net_color(self.sdf.net_ids.get(batch.net, 0)) if color_by_net else None
            batch_color = (*(rgb or layer.color[:3]), alpha)
            if batch_color != material:
                if solid_count:
                    self._solid(solid_start, solid_count)
                    solid_count = 0
                material = batch_color
                GL.glUniform4f(self.uniforms["color"], *material)
            if not batch.hole_count:
                if solid_count and solid_start + solid_count != batch.index_start:
                    self._solid(solid_start, solid_count)
                    solid_count = 0
                if not solid_count:
                    solid_start = batch.index_start
                solid_count += batch.outer_count
                continue
            if solid_count:
                self._solid(solid_start, solid_count)
                solid_count = 0
            self._batch(batch, camera, pixel_ratio)
        if solid_count:
            self._solid(solid_start, solid_count)

    def _solid(self, start, count):
        GL.glBindVertexArray(self.vao)
        GL.glUniform1i(self.uniforms["rectangle_pass"], 0)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        self._indexed(start, count)

    def _batch(self, batch, camera, pixel_ratio):
        u = self.uniforms
        GL.glBindVertexArray(self.vao)
        GL.glUniform1i(u["rectangle_pass"], 0)
        a = camera.world_to_screen(*batch.bounds[:2])
        b = camera.world_to_screen(*batch.bounds[2:])
        left, right = max(0.0, min(a[0], b[0])), min(camera.width, max(a[0], b[0]))
        top, bottom = max(0.0, min(a[1], b[1])), min(camera.height, max(a[1], b[1]))
        if left >= right or top >= bottom:
            return
        x0, x1 = math.floor(left * pixel_ratio), math.ceil(right * pixel_ratio)
        y0 = math.floor((camera.height - bottom) * pixel_ratio)
        y1 = math.ceil((camera.height - top) * pixel_ratio)
        GL.glEnable(GL.GL_SCISSOR_TEST)
        GL.glScissor(x0, y0, x1 - x0, y1 - y0)
        GL.glEnable(GL.GL_STENCIL_TEST)
        GL.glStencilMask(3)
        GL.glClear(GL.GL_STENCIL_BUFFER_BIT)
        GL.glColorMask(False, False, False, False)
        GL.glStencilMask(1)
        GL.glStencilFunc(GL.GL_ALWAYS, 1, 3)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_REPLACE)
        self._indexed(batch.index_start, batch.outer_count)
        # Set a second bit for the union of holes. Overlaps do not toggle back on.
        if batch.hole_count:
            GL.glStencilMask(2)
            GL.glStencilFunc(GL.GL_ALWAYS, 2, 3)
            self._indexed(batch.index_start + batch.outer_count, batch.hole_count)
        GL.glColorMask(True, True, True, True)
        GL.glStencilMask(0)
        GL.glStencilFunc(GL.GL_EQUAL, 1, 3)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_KEEP)
        GL.glUniform1i(u["rectangle_pass"], 1)
        GL.glUniform4f(u["rectangle"], left, top, right, bottom)
        GL.glBindVertexArray(self.quad_vao)
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
        self.draw_calls += 1
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glDisable(GL.GL_SCISSOR_TEST)

    def release(self):
        """Release resources explicitly while their owning context is current."""
        if self.vbo or self.ebo:
            GL.glDeleteBuffers(2, [self.vbo, self.ebo])
        if self.vao or self.quad_vao:
            GL.glDeleteVertexArrays(2, [self.vao, self.quad_vao])
        if self.program:
            GL.glDeleteProgram(self.program)
        self.sdf.release()
        self.labels.release()
        self.grid.release()
        self.program = self.vao = self.quad_vao = self.vbo = self.ebo = 0
        self.prepared = None
        self._stencil_checked = False

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

"""Instanced SDF mark/cover passes in the Qt-owned framebuffer.

Stencil bit 4 holds the union of analytic primitives on a layer; bits 1/2
remain reserved for object-local copper masks. Multisample alpha-to-coverage
preserves SDF edge coverage without accumulating opacity at joins.
"""

from ctypes import c_void_p
from pathlib import Path

import numpy as np
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from pyedb.viewer.colors import COMPONENT_COLORS, NET_COLORS
from pyedb.viewer.mesh import SDF_STRIDE
from pyedb.viewer.qt.gl_utils import bind_camera_uniforms


def _shader_source(path):
    """Expand our local GLSL modules; OpenGL 3.3 has no native #include."""
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith('#include "'):
            lines.append(_shader_source(path.parent / line.split('"')[1]))
        else:
            lines.append(line)
    return "\n".join(lines)


class SdfCoverage:
    def __init__(self):
        self.program = self.cover_program = self.vao = self.cover_vao = self.vbo = 0
        self.fbo = self.resolve_fbo = self.texture = self.color_buffer = self.palette = 0
        self._target_key = None
        self.layer_batches = {}
        self.net_ids = {}
        self.component_batches = ()
        self.drawn_pin_count = 0

    def initialize(self):
        shader_dir = Path(__file__).with_name("shaders")
        for name, attribute in (("sdf", "program"), ("coverage", "cover_program")):
            setattr(
                self,
                attribute,
                compileProgram(
                    compileShader(_shader_source(shader_dir / f"{name}.vert"), GL.GL_VERTEX_SHADER),
                    compileShader(_shader_source(shader_dir / f"{name}.frag"), GL.GL_FRAGMENT_SHADER),
                    validate=False,
                ),
            )
        self.uniforms = {
            name: GL.glGetUniformLocation(self.program, name)
            for name in (
                "camera_split",
                "viewport",
                "scale",
                "pixel_ratio",
                "mirror_x",
                "selected_net",
                "drill_pass",
                "multisampled",
                "color_by_net",
                "layer_color",
                "net_palette",
                "component_pass",
            )
        }
        self.cover_color = GL.glGetUniformLocation(self.cover_program, "color")
        self.cover_texture = GL.glGetUniformLocation(self.cover_program, "strokes")
        self.vao, self.cover_vao = (int(v) for v in GL.glGenVertexArrays(2))
        self.vbo = int(GL.glGenBuffers(1))
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        self._attributes(0)
        GL.glBindVertexArray(0)
        self.palette = int(GL.glGenTextures(1))
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_1D, self.palette)
        colors = np.asarray(NET_COLORS, dtype=np.float32)
        GL.glTexImage1D(GL.GL_TEXTURE_1D, 0, GL.GL_RGB8, len(colors), 0, GL.GL_RGB, GL.GL_FLOAT, colors)
        GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_1D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glActiveTexture(GL.GL_TEXTURE0)

    def _target(self, target, width, height, samples):
        """Share Qt's stencil attachment; retain the last material per covered sample.

        The color attachment belongs to this renderer. The Qt framebuffer itself
        is never modified. Color is resolved before sampling in the cover pass.
        """
        key = (target, width, height, samples)
        if key == self._target_key:
            return
        kind = int(
            GL.glGetFramebufferAttachmentParameteriv(
                GL.GL_DRAW_FRAMEBUFFER, GL.GL_STENCIL_ATTACHMENT, GL.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE
            )
        )
        stencil = int(
            GL.glGetFramebufferAttachmentParameteriv(
                GL.GL_DRAW_FRAMEBUFFER, GL.GL_STENCIL_ATTACHMENT, GL.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME
            )
        )
        if not self.fbo:
            self.fbo, self.resolve_fbo = (int(v) for v in GL.glGenFramebuffers(2))
            self.texture = int(GL.glGenTextures(1))
            self.color_buffer = int(GL.glGenRenderbuffers(1))
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.color_buffer)
        if samples:
            GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, samples, GL.GL_RGBA8, width, height)
        else:
            GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_RGBA8, width, height)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.fbo)
        GL.glFramebufferRenderbuffer(
            GL.GL_DRAW_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_RENDERBUFFER, self.color_buffer
        )
        if kind == GL.GL_RENDERBUFFER:
            GL.glFramebufferRenderbuffer(GL.GL_DRAW_FRAMEBUFFER, GL.GL_STENCIL_ATTACHMENT, kind, stencil)
        elif kind == GL.GL_TEXTURE:
            texture_type = GL.GL_TEXTURE_2D_MULTISAMPLE if samples else GL.GL_TEXTURE_2D
            GL.glFramebufferTexture2D(GL.GL_DRAW_FRAMEBUFFER, GL.GL_STENCIL_ATTACHMENT, texture_type, stencil, 0)
        else:
            raise RuntimeError("The Qt framebuffer has no usable stencil attachment.")
        GL.glDrawBuffer(GL.GL_COLOR_ATTACHMENT0)
        if GL.glCheckFramebufferStatus(GL.GL_DRAW_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Unable to create the SDF stroke-mark framebuffer.")
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.resolve_fbo)
        GL.glFramebufferTexture2D(GL.GL_DRAW_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.texture, 0)
        GL.glDrawBuffer(GL.GL_COLOR_ATTACHMENT0)
        if GL.glCheckFramebufferStatus(GL.GL_DRAW_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Unable to create the SDF stroke-cover framebuffer.")
        self._target_key = key

    def _attributes(self, start):
        for location in range(SDF_STRIDE // 4):
            GL.glEnableVertexAttribArray(location)
            GL.glVertexAttribPointer(
                location, 4, GL.GL_FLOAT, False, SDF_STRIDE * 4, c_void_p((start * SDF_STRIDE + location * 4) * 4)
            )
            GL.glVertexAttribDivisor(location, 1)

    def upload(self, prepared):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, prepared.instances.nbytes, prepared.instances, GL.GL_STATIC_DRAW)
        self.layer_batches = {}
        for batch in prepared.sdf_batches:
            self.layer_batches.setdefault(batch.layer, []).append(batch)
        self.net_ids = {net: index for index, net in enumerate(prepared.nets)}
        self.net_ids[""] = 0
        self.component_batches = prepared.component_batches

    def draw_components(self, camera, pixel_ratio, visible_layers, opacity, net, both_sides=False):
        """Draw the same compound-net component selection used for reference labels."""
        groups = {"top": [], "bottom": []}
        for batch in self.component_batches:
            component = batch.component
            if not component.visible_on(visible_layers, camera.mirror, net, both_sides):
                continue
            if not camera.visible(component.bounds):
                continue
            ranges = groups[component.side]
            if ranges and ranges[-1][0] + ranges[-1][1] == batch.instance_start:
                ranges[-1][1] += 1
            else:
                ranges.append([batch.instance_start, 1])
        calls = 0
        for side in ("top", "bottom") if camera.mirror else ("bottom", "top"):
            ranges = groups[side]
            if ranges:
                calls += self.draw(
                    camera,
                    pixel_ratio,
                    (),
                    (*COMPONENT_COLORS[side], opacity),
                    None,
                    component_pass=True,
                    instance_ranges=ranges,
                )
        return calls

    def draw(
        self,
        camera,
        pixel_ratio,
        layers,
        color,
        net,
        *,
        drills=False,
        color_by_net=False,
        component_pass=False,
        instance_ranges=None,
        category=None,
    ):
        """Mark the layer union, then shade each covered sample exactly once."""
        ranges = [] if instance_ranges is None else instance_ranges
        for layer in layers:
            for batch in self.layer_batches.get(layer, ()):
                if category is not None and batch.category != category:
                    continue
                if (drills and not batch.has_drills) or not camera.visible(batch.bounds):
                    continue
                if ranges and ranges[-1][0] + ranges[-1][1] == batch.instance_start:
                    ranges[-1][1] += batch.instance_count
                else:
                    ranges.append([batch.instance_start, batch.instance_count])
        if not ranges:
            return 0
        target = int(GL.glGetIntegerv(GL.GL_DRAW_FRAMEBUFFER_BINDING))
        read_target = int(GL.glGetIntegerv(GL.GL_READ_FRAMEBUFFER_BINDING))
        try:
            samples = int(GL.glGetIntegerv(GL.GL_SAMPLES))
            multisampled = samples > 1
            width, height = round(camera.width * pixel_ratio), round(camera.height * pixel_ratio)
            self._target(target, width, height, samples)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.fbo)
            GL.glEnable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_SCISSOR_TEST)
            GL.glStencilMask(4)
            GL.glClearStencil(0)
            GL.glColorMask(True, True, True, True)
            GL.glClearColor(0, 0, 0, 0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
            GL.glStencilFunc(GL.GL_ALWAYS, 4, 4)
            GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_REPLACE)
            GL.glDisable(GL.GL_BLEND)
            if multisampled:
                GL.glEnable(GL.GL_MULTISAMPLE)
                GL.glEnable(GL.GL_SAMPLE_ALPHA_TO_COVERAGE)
            u = self.uniforms
            bind_camera_uniforms(self.program, u, camera, pixel_ratio)
            GL.glUniform1i(u["selected_net"], -1 if net is None else self.net_ids.get(net, -2))
            GL.glUniform1i(u["drill_pass"], drills)
            GL.glUniform1i(u["component_pass"], component_pass)
            GL.glUniform1i(u["multisampled"], multisampled)
            GL.glUniform1i(u["color_by_net"], color_by_net and not drills)
            GL.glUniform4f(u["layer_color"], *color)
            GL.glActiveTexture(GL.GL_TEXTURE1)
            GL.glBindTexture(GL.GL_TEXTURE_1D, self.palette)
            GL.glUniform1i(u["net_palette"], 1)
            GL.glBindVertexArray(self.vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            for start, count in ranges:
                # Attribute offsets select resident ranges on OpenGL 3.3,
                # without rebuilding packets or requiring base-instance draws.
                self._attributes(start)
                GL.glDrawArraysInstanced(GL.GL_TRIANGLE_STRIP, 0, 4, count)
            GL.glDisable(GL.GL_SAMPLE_ALPHA_TO_COVERAGE)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.fbo)
            GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT0)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.resolve_fbo)
            GL.glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, target)
            GL.glColorMask(True, True, True, True)
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendEquation(GL.GL_FUNC_ADD)
            GL.glBlendFuncSeparate(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glStencilFunc(GL.GL_EQUAL, 4, 4)
            GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_ZERO)
            GL.glUseProgram(self.cover_program)
            GL.glUniform4f(self.cover_color, *color)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glUniform1i(self.cover_texture, 0)
            GL.glBindVertexArray(self.cover_vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
            return len(ranges) + 1
        finally:
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, target)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, read_target)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glDisable(GL.GL_SAMPLE_ALPHA_TO_COVERAGE)
            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_SCISSOR_TEST)
            GL.glColorMask(True, True, True, True)
            GL.glStencilMask(0xFF)
            GL.glEnable(GL.GL_BLEND)

    def release(self):
        if self.vbo:
            GL.glDeleteBuffers(1, [self.vbo])
        if self.vao or self.cover_vao:
            GL.glDeleteVertexArrays(2, [self.vao, self.cover_vao])
        if self.fbo or self.resolve_fbo:
            GL.glDeleteFramebuffers(2, [self.fbo, self.resolve_fbo])
        if self.texture or self.palette:
            GL.glDeleteTextures([self.texture, self.palette])
        if self.color_buffer:
            GL.glDeleteRenderbuffers(1, [self.color_buffer])
        for program in (self.program, self.cover_program):
            if program:
                GL.glDeleteProgram(program)
        self.program = self.cover_program = self.vao = self.cover_vao = self.vbo = 0
        self.fbo = self.resolve_fbo = self.texture = self.palette = self.color_buffer = 0
        self._target_key = None
        self.layer_batches = {}
        self.net_ids = {}
        self.component_batches = ()
        self.drawn_pin_count = 0

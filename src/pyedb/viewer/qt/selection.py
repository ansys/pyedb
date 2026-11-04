# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Vivid interaction colors and screen-space patterns over resident geometry."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from pyedb.viewer.colors import HIGHLIGHT_KEYLINE_COLOR, HOVER_COLOR, SELECTION_COLOR
from pyedb.viewer.qt.coverage import _shader_source
from pyedb.viewer.qt.gl_utils import bind_camera_uniforms

if TYPE_CHECKING:
    from pyedb.viewer.camera import Camera
    from pyedb.viewer.mesh import MeshBatch
    from pyedb.viewer.qt.renderer import Renderer


class SelectionOverlay:
    def __init__(self) -> None:
        self.program = self.vao = 0

    def initialize(self) -> None:
        directory = Path(__file__).with_name("shaders")
        self.program = compileProgram(
            compileShader(_shader_source(directory / "selection.vert"), GL.GL_VERTEX_SHADER),
            compileShader(_shader_source(directory / "selection.frag"), GL.GL_FRAGMENT_SHADER),
            validate=False,
        )
        self.vao = int(GL.glGenVertexArrays(1))
        self.uniforms = {
            name: GL.glGetUniformLocation(self.program, name)
            for name in (
                "mask_texture",
                "viewport",
                "pixel_ratio",
                "hovering",
                "patterned",
                "highlight_color",
                "keyline_color",
            )
        }

    def draw(
        self,
        renderer: Renderer,
        camera: Camera,
        pixel_ratio: float,
        polygons: Sequence[MeshBatch],
        ranges: Sequence[tuple[int, int]],
        *,
        hovering: bool,
        patterned: bool,
    ) -> None:
        if not polygons and not ranges:
            return
        sdf = renderer.sdf
        target = int(GL.glGetIntegerv(GL.GL_DRAW_FRAMEBUFFER_BINDING))
        read_target = int(GL.glGetIntegerv(GL.GL_READ_FRAMEBUFFER_BINDING))
        width, height = round(camera.width * pixel_ratio), round(camera.height * pixel_ratio)
        samples = int(GL.glGetIntegerv(GL.GL_SAMPLES))
        try:
            sdf._target(target, width, height, samples)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, sdf.fbo)
            GL.glViewport(0, 0, width, height)
            GL.glDisable(GL.GL_SCISSOR_TEST)
            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_BLEND)
            GL.glColorMask(True, True, True, True)
            GL.glStencilMask(0xFF)
            GL.glClearColor(0, 0, 0, 0)
            GL.glClearStencil(0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
            bind_camera_uniforms(renderer.program, renderer.uniforms, camera)
            GL.glUniform1i(renderer.uniforms["color_by_net"], False)
            GL.glUniform4f(renderer.uniforms["color"], 1, 1, 1, 1)
            for polygon in polygons:
                if camera.visible(polygon.bounds):
                    renderer._batch(polygon, camera, pixel_ratio)
            if ranges:
                sdf.mark_ranges(camera, pixel_ratio, ranges, samples > 1)
            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_SAMPLE_ALPHA_TO_COVERAGE)
            GL.glColorMask(True, True, True, True)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, sdf.fbo)
            GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT0)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, sdf.resolve_fbo)
            GL.glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, target)
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendEquation(GL.GL_FUNC_ADD)
            GL.glBlendFuncSeparate(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glUseProgram(self.program)
            GL.glUniform2f(self.uniforms["viewport"], width, height)
            GL.glUniform1f(self.uniforms["pixel_ratio"], pixel_ratio)
            GL.glUniform1i(self.uniforms["hovering"], hovering)
            GL.glUniform1i(self.uniforms["patterned"], patterned)
            GL.glUniform3f(self.uniforms["highlight_color"], *(HOVER_COLOR if hovering else SELECTION_COLOR))
            GL.glUniform3f(self.uniforms["keyline_color"], *HIGHLIGHT_KEYLINE_COLOR)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, sdf.texture)
            GL.glUniform1i(self.uniforms["mask_texture"], 0)
            GL.glBindVertexArray(self.vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
            renderer.draw_calls += len(ranges) + 1
        finally:
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, target)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, read_target)
            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glDisable(GL.GL_SCISSOR_TEST)
            GL.glDisable(GL.GL_SAMPLE_ALPHA_TO_COVERAGE)
            GL.glStencilMask(0xFF)
            GL.glColorMask(True, True, True, True)
            GL.glBindVertexArray(0)

    def release(self) -> None:
        if self.program:
            GL.glDeleteProgram(self.program)
        if self.vao:
            GL.glDeleteVertexArrays(1, [self.vao])
        self.program = self.vao = 0

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

"""World-anchored, adaptive shader grid. Navigation updates uniforms only."""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from pyedb.viewer.colors import CANVAS_PALETTES, CanvasPalette
from pyedb.viewer.qt.coverage import _shader_source
from pyedb.viewer.qt.gl_utils import bind_camera_uniforms

if TYPE_CHECKING:
    from pyedb.viewer.camera import Camera


def grid_spacing(scale: float, pixel_ratio: float = 1.0) -> float:
    """Choose a readable 1/2/5 millimeter step at the current zoom."""
    target = 20.0 / (scale * pixel_ratio)
    base = 10.0 ** math.floor(math.log10(target))
    return min((base * multiple for multiple in (1, 2, 5, 10)), key=lambda step: abs(math.log(step / target)))


class GridRenderer:
    def __init__(self) -> None:
        self.program = self.vao = 0
        self.spacing = 1.0

    def initialize(self) -> None:
        shaders = Path(__file__).with_name("shaders")
        self.program = compileProgram(
            compileShader(_shader_source(shaders / "coverage.vert"), GL.GL_VERTEX_SHADER),
            compileShader(_shader_source(shaders / "grid.frag"), GL.GL_FRAGMENT_SHADER),
            validate=False,
        )
        self.uniforms = {
            name: GL.glGetUniformLocation(self.program, name)
            for name in (
                "viewport",
                "scale",
                "pixel_ratio",
                "mirror_x",
                "spacing",
                "minor_phase",
                "major_phase",
                "background",
                "minor_color",
                "major_color",
            )
        }
        self.vao = int(GL.glGenVertexArrays(1))

    def draw(self, camera: Camera, pixel_ratio: float, palette: CanvasPalette | None = None) -> None:
        palette = palette or CANVAS_PALETTES["light"]
        self.spacing = grid_spacing(camera.scale, pixel_ratio)
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_STENCIL_TEST)
        u = self.uniforms
        bind_camera_uniforms(self.program, u, camera, pixel_ratio)
        GL.glUniform1f(u["spacing"], self.spacing)
        GL.glUniform3f(u["background"], *palette.background[:3])
        GL.glUniform3f(u["minor_color"], *palette.grid_minor)
        GL.glUniform3f(u["major_color"], *palette.grid_major)
        # Reduce double coordinates before narrowing to float32; kilometre-scale
        # offsets must not lose the grid phase when zoomed into micrometer detail.
        GL.glUniform2f(u["minor_phase"], camera.center_x % self.spacing, camera.center_y % self.spacing)
        major = self.spacing * 5
        GL.glUniform2f(u["major_phase"], camera.center_x % major, camera.center_y % major)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

    def release(self) -> None:
        if self.vao:
            GL.glDeleteVertexArrays(1, [self.vao])
        if self.program:
            GL.glDeleteProgram(self.program)
        self.program = self.vao = 0

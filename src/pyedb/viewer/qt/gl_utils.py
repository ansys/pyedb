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

"""Shared OpenGL uniform setup for the layout rendering passes."""

from OpenGL import GL

from pyedb.viewer.mesh import split_coordinates


def bind_camera_uniforms(program, uniforms, camera, pixel_ratio=None):
    """Bind a rendering program and upload its camera uniforms."""
    GL.glUseProgram(program)
    if "camera_split" in uniforms:
        GL.glUniform4fv(uniforms["camera_split"], 1, split_coordinates([[camera.center_x, camera.center_y]])[0])
    GL.glUniform2f(uniforms["viewport"], camera.width, camera.height)
    GL.glUniform1f(uniforms["scale"], camera.scale)
    GL.glUniform1f(uniforms["mirror_x"], -1 if camera.mirror else 1)
    if pixel_ratio is not None:
        GL.glUniform1f(uniforms["pixel_ratio"], pixel_ratio)

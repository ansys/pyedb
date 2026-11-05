// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
//
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"

layout(location = 0) in vec4 center_split;
layout(location = 1) in vec4 label_size;
layout(location = 2) in vec4 atlas_rectangle;
layout(location = 0) out vec2 uv;
layout(location = 1) flat out float bottom_side;

#include "common.glsl"

void main() {
    vec2 x = add_pair(center_split.xz, -camera_split.xz);
    vec2 y = add_pair(center_split.yw, -camera_split.yw);
    vec2 corner = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1));
    vec2 center = viewport * 0.5 + vec2(x.x + x.y, y.x + y.y) * vec2(mirror_x, -1.0) * scale;
    vec2 pixel = center + (corner - 0.5) * label_size.xy;
    gl_Position = vec4(pixel / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0, 1);
    uv = mix(atlas_rectangle.xy, atlas_rectangle.zw, corner);
    bottom_side = label_size.z;
    gl_Position = clip_corr * gl_Position;
}

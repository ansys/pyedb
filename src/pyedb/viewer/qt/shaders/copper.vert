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

#version 330 core

layout(location = 0) in vec4 position_split;
uniform vec4 camera_split;
uniform vec2 viewport;
uniform float scale;
uniform float mirror_x;
uniform bool rectangle_pass;
uniform vec4 rectangle;

// Compensated high/low subtraction, keeping geometry resident while the camera moves.
vec2 subtract_pair(vec2 a, vec2 b) {
    float difference = a.x - b.x;
    float virtual_b = difference - a.x;
    float residual = (a.x - (difference - virtual_b)) - (b.x + virtual_b) + a.y - b.y;
    float high = difference + residual;
    return vec2(high, residual - (high - difference));
}

void main() {
    vec2 screen;
    if (rectangle_pass) {
        vec2 corners[4] = vec2[4](vec2(0, 0), vec2(1, 0), vec2(0, 1), vec2(1, 1));
        screen = mix(rectangle.xy, rectangle.zw, corners[gl_VertexID]);
    } else {
        vec2 x = subtract_pair(position_split.xz, camera_split.xz);
        vec2 y = subtract_pair(position_split.yw, camera_split.yw);
        screen = viewport * 0.5 + vec2(x.x + x.y, y.x + y.y) * vec2(mirror_x, -1.0) * scale;
    }
    gl_Position = vec4(screen / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0.0, 1.0);
}

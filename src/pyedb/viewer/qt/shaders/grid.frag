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

uniform vec2 viewport;
uniform float scale;
uniform float pixel_ratio;
uniform float mirror_x;
uniform float spacing;
uniform vec2 minor_phase;
uniform vec2 major_phase;
uniform vec3 background;
uniform vec3 minor_color;
uniform vec3 major_color;
out vec4 fragment_color;

float grid_line(vec2 world, vec2 phase, float step_size, float half_width) {
    vec2 distance = abs(fract((world + phase) / step_size + 0.5) - 0.5) * step_size * scale;
    float aa = 0.4 / pixel_ratio;
    return 1.0 - smoothstep(half_width - aa, half_width + aa, min(distance.x, distance.y));
}

void main() {
    vec2 world = (gl_FragCoord.xy / pixel_ratio - viewport * 0.5) * vec2(mirror_x, 1.0) / scale;
    float minor = grid_line(world, minor_phase, spacing, 0.35);
    float major = grid_line(world, major_phase, spacing * 5.0, 0.55);
    // Theme colors; the light canvas uses the reference #dadaea minor / #c4c4de major lines.
    vec3 color = mix(background, minor_color, minor);
    color = mix(color, major_color, major);
    fragment_color = vec4(color, 1.0);
}

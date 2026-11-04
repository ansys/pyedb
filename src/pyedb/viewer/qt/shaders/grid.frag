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
    // Sampled from the user's reference: #dadaea minor / #c4c4de major.
    vec3 color = mix(vec3(1.0), vec3(218.0, 218.0, 234.0) / 255.0, minor);
    color = mix(color, vec3(196.0, 196.0, 222.0) / 255.0, major);
    fragment_color = vec4(color, 1.0);
}

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

flat in vec4 a;
flat in vec4 b;
flat in vec4 c;
flat in vec4 params;
flat in vec4 flags;
flat in vec4 detail;
flat in vec4 hole;
flat in vec4 tangent;
uniform vec2 viewport;
uniform float scale;
uniform float pixel_ratio;
uniform float mirror_x;
uniform bool drill_pass;
uniform bool multisampled;
uniform bool color_by_net;
uniform vec4 layer_color;
uniform sampler1D net_palette;
out vec4 fragment_color;

#include "common.glsl"
#include "trace.glsl"
#include "pad.glsl"
#include "join.glsl"

void main() {
    // Native stencil_mark's deterministic tie-break keeps pixel-aligned hairlines visible.
    vec2 screen_xy = ((gl_FragCoord.xy + vec2(1.0 / 256.0)) / pixel_ratio - viewport * 0.5)
                     * vec2(mirror_x, 1.0) / scale;
    vec4 screen = vec4(screen_xy, 0, 0);
    float distance;
    float envelope_edge = 0.0;
    if (drill_pass) {
        distance = radial_distance(delta(screen, hole), vec2(detail.y, tangent.z));
    } else if (flags.x < 0.5) {
        distance = line_distance(screen);
    } else if (flags.x < 1.5) {
        distance = arc_distance(screen);
    } else if (flags.x < 3.5) {
        distance = pad_distance(screen);
    } else if (flags.x > 4.5) {
        envelope_edge = abs(pad_distance(screen));
        distance = envelope_edge - 0.8 / (scale * pixel_ratio);
    } else {
        distance = join_distance(screen);
    }
    float aa = 0.65 / (scale * pixel_ratio);
    float coverage = 1.0 - smoothstep(-aa, aa, distance);
    if (coverage <= 0.0) discard;
    if (!multisampled && coverage <= 0.5) discard;
    vec3 material = layer_color.rgb;
    int net = int(flags.w + 0.5);
    if (color_by_net && net > 0)
        material = texelFetch(net_palette, (net - 1) % textureSize(net_palette, 0), 0).rgb;
    fragment_color = vec4(material * coverage, coverage);
}

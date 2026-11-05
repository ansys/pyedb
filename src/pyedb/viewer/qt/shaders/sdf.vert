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

// One resident packet per primitive; gl_VertexIndex expands it to a clipped quad.
layout(location = 0) in vec4 source_a;
layout(location = 1) in vec4 source_b;
layout(location = 2) in vec4 source_c;
layout(location = 3) in vec4 bounds_min;
layout(location = 4) in vec4 bounds_max;
layout(location = 5) in vec4 source_params;
layout(location = 6) in vec4 source_flags;
layout(location = 7) in vec4 source_detail;
layout(location = 8) in vec4 source_hole;
layout(location = 9) in vec4 source_tangent;


layout(location = 0) flat out vec4 a;
layout(location = 1) flat out vec4 b;
layout(location = 2) flat out vec4 c;
layout(location = 3) flat out vec4 params;
layout(location = 4) flat out vec4 flags;
layout(location = 5) flat out vec4 detail;
layout(location = 6) flat out vec4 hole;
layout(location = 7) flat out vec4 tangent;

#include "common.glsl"

vec4 relative(vec4 position) {
    vec2 x = add_pair(position.xz, -camera_split.xz);
    vec2 y = add_pair(position.yw, -camera_split.yw);
    return vec4(x.x, y.x, x.y, y.y);
}

void main() {
    a = relative(source_a);
    b = relative(source_b);
    c = relative(source_c);
    hole = relative(source_hole);
    params = source_params;
    flags = source_flags;
    detail = source_detail;
    tangent = source_tangent;
    if ((selected_net != -1 && int(flags.w + 0.5) != selected_net)
        || (drill_pass && (flags.x < 1.5 || flags.x > 3.5 || detail.y <= 0.0))
        || (!drill_pass && flags.y < -0.5)
        || (component_pass != (flags.x > 4.5))) {
        gl_Position = vec4(2.0, 2.0, 0.0, 1.0);
        return;
    }
    vec4 lo_pair = relative(bounds_min);
    vec4 hi_pair = relative(bounds_max);
    vec2 limit = viewport * 0.5 / scale;
    float aa = 2.0 / (scale * pixel_ratio);
    vec2 lo = clamp(lo_pair.xy + lo_pair.zw - aa, -limit, limit);
    vec2 hi = clamp(hi_pair.xy + hi_pair.zw + aa, -limit, limit);
    vec2 corners[4] = vec2[4](vec2(0, 0), vec2(1, 0), vec2(0, 1), vec2(1, 1));
    vec2 position = mix(lo, hi, corners[gl_VertexIndex]);
    gl_Position = vec4(position * vec2(mirror_x, 1.0) * scale * 2.0 / viewport, 0.0, 1.0);
    gl_Position = clip_corr * gl_Position;
}

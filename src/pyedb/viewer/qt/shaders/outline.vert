// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"
#include "common.glsl"

layout(location = 0) in vec4 start_split;
layout(location = 1) in vec4 end_split;
layout(location = 2) in uint vertex_net;
layout(location = 0) out vec2 stroke_position;
layout(location = 1) flat out float stroke_half_length;
layout(location = 2) flat out uint net_id;

vec2 to_screen(vec4 position) {
    vec4 relative = delta(position, camera_split);
    return viewport * 0.5 + (relative.xy + relative.zw) * vec2(mirror_x, -1.0) * scale;
}

void main() {
    net_id = vertex_net;
    vec2 start = to_screen(start_split);
    vec2 end = to_screen(end_split);
    vec2 difference = end - start;
    float span = length(difference);
    vec2 tangent = span > 1e-6 ? difference / span : vec2(1.0, 0.0);
    vec2 normal = vec2(-tangent.y, tangent.x);
    float margin = 0.5 + 1.0 / pixel_ratio;
    stroke_half_length = span * 0.5;
    vec2 corners[4] = vec2[4](vec2(-1, -1), vec2(-1, 1), vec2(1, -1), vec2(1, 1));
    vec2 corner = corners[gl_VertexIndex];
    stroke_position = vec2(corner.x * (stroke_half_length + margin), corner.y * margin);
    vec2 screen = (start + end) * 0.5 + tangent * stroke_position.x + normal * stroke_position.y;
    gl_Position = clip_corr * vec4(screen / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0, 1);
}

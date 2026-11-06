// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"
layout(location = 0) in vec2 stroke_position;
layout(location = 1) flat in float stroke_half_length;
layout(location = 2) flat in uint net_id;
layout(binding = 1) uniform sampler2D net_palette;
layout(location = 0) out vec4 fragment_color;

void main() {
    vec2 distance_to_segment = vec2(max(abs(stroke_position.x) - stroke_half_length, 0.0), stroke_position.y);
    float distance_to_edge = length(distance_to_segment) - 0.5;
    float coverage = clamp(0.5 - distance_to_edge / max(fwidth(distance_to_edge), 1e-6), 0.0, 1.0);
    if (coverage <= 0.0) discard;
    vec3 rgb = color.rgb;
    if (net_id > 0u)
        rgb = texelFetch(net_palette, ivec2((int(net_id) - 1) % textureSize(net_palette, 0).x, 0), 0).rgb;
    fragment_color = vec4(rgb, coverage);
}

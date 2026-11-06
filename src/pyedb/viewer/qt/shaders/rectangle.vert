// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 440
#extension GL_GOOGLE_include_directive : require
#include "uniforms.glsl"
layout(location = 0) flat out uint net_id;
void main() {
    net_id = 0u;
    vec2 corner = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1));
    vec2 pixel = mix(rectangle.xy, rectangle.zw, corner);
    gl_Position = clip_corr * vec4(pixel / viewport * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0, 1);
}

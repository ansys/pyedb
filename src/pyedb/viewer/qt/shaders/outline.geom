// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 330 core
// Expand each polygon boundary edge into a constant screen-width quad.
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
uniform vec2 viewport;
uniform float line_width;

vec2 to_screen(vec4 position) {
    return (position.xy / position.w * 0.5 + 0.5) * viewport;
}

vec4 to_clip(vec2 screen) {
    return vec4(screen / viewport * 2.0 - 1.0, 0.0, 1.0);
}

void main() {
    vec2 a = to_screen(gl_in[0].gl_Position);
    vec2 b = to_screen(gl_in[1].gl_Position);
    vec2 delta = b - a;
    float span = length(delta);
    vec2 direction = span > 0.0 ? delta / span : vec2(1.0, 0.0);
    // Square caps close the corners between consecutive edges.
    vec2 along = direction * (line_width * 0.5);
    vec2 across = vec2(-direction.y, direction.x) * (line_width * 0.5);
    gl_Position = to_clip(a - along + across);
    EmitVertex();
    gl_Position = to_clip(a - along - across);
    EmitVertex();
    gl_Position = to_clip(b + along + across);
    EmitVertex();
    gl_Position = to_clip(b + along - across);
    EmitVertex();
    EndPrimitive();
}

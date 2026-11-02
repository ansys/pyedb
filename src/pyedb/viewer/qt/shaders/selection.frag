// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 330 core
uniform sampler2D mask_texture;
uniform vec2 viewport;
uniform float pixel_ratio;
uniform bool hovering;
uniform bool patterned;
out vec4 fragment_color;
void main() {
    vec2 uv = gl_FragCoord.xy / viewport;
    vec2 step_uv = vec2(pixel_ratio) / viewport;
    float center = texture(mask_texture, uv).a;
    float left = texture(mask_texture, uv - vec2(step_uv.x, 0)).a;
    float right = texture(mask_texture, uv + vec2(step_uv.x, 0)).a;
    float top = texture(mask_texture, uv + vec2(0, step_uv.y)).a;
    float bottom = texture(mask_texture, uv - vec2(0, step_uv.y)).a;
    float low = min(min(left, right), min(top, bottom));
    float high = max(max(left, right), max(top, bottom));
    float edge = max(center - low, high - center);
    float alpha = edge * .9;
    if (patterned && !hovering) {
        vec2 cell = mod(gl_FragCoord.xy / pixel_ratio, 5.0) - vec2(2.5);
        float dots = 1.0 - smoothstep(.65, 1.25, length(cell));
        alpha = max(alpha, dots * center * .8);
    }
    if (alpha <= 0.0) discard;
    fragment_color = vec4(hovering ? vec3(.63, 1, .85) : vec3(1), alpha);
}

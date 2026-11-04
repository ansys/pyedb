// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 330 core
uniform sampler2D mask_texture;
uniform vec2 viewport;
uniform float pixel_ratio;
uniform bool hovering;
uniform bool patterned;
uniform vec3 highlight_color;
uniform vec3 keyline_color;
out vec4 fragment_color;
float boundary(vec2 uv, vec2 step_uv, float center) {
    float left = texture(mask_texture, uv - vec2(step_uv.x, 0)).a;
    float right = texture(mask_texture, uv + vec2(step_uv.x, 0)).a;
    float top = texture(mask_texture, uv + vec2(0, step_uv.y)).a;
    float bottom = texture(mask_texture, uv - vec2(0, step_uv.y)).a;
    return max(center - min(min(left, right), min(top, bottom)),
               max(max(left, right), max(top, bottom)) - center);
}
void main() {
    vec2 uv = gl_FragCoord.xy / viewport;
    vec2 step_uv = vec2(pixel_ratio) / viewport;
    float center = texture(mask_texture, uv).a;
    float ink = boundary(uv, step_uv, center);
    float halo = boundary(uv, step_uv * 2.0, center);
    if (patterned && !hovering) {
        vec2 cell = mod(gl_FragCoord.xy / pixel_ratio, 5.0) - vec2(2.5);
        float dots = 1.0 - smoothstep(.65, 1.25, length(cell));
        float rim = 1.0 - smoothstep(1.2, 1.65, length(cell));
        ink = max(ink, dots * center);
        halo = max(halo, rim * center);
    }
    float alpha = max(ink * .98, halo * .9);
    if (alpha <= 0.0) discard;
    vec3 color = mix(keyline_color, highlight_color, clamp(ink / max(ink, halo), 0.0, 1.0));
    fragment_color = vec4(color, alpha);
}

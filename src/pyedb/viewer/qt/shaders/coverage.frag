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
layout(binding = 1) uniform sampler2D strokes;
layout(location = 0) out vec4 fragment_color;

float coverage_at(ivec2 texel) {
    return texelFetch(strokes, clamp(texel, ivec2(0), textureSize(strokes, 0) - 1), 0).a;
}

void main() {
    // Preserve the last covered primitive's material.
    ivec2 texel = ivec2(gl_FragCoord.xy);
    vec4 material = texelFetch(strokes, texel, 0);
    if (material.a <= 0.0) discard;
    // Retain the net material for opaque strokes even when the fill uses layer colors.
    vec3 rgb = fill_by_net ? material.rgb : color.rgb;
    float ink = 0.0;
    if (outline) {
        // Ink the inner edge of the layer union, one logical pixel wide.
        int reach = max(1, int(round(pixel_ratio)));
        float lowest = material.a;
        for (int step = 1; step <= reach; ++step) {
            lowest = min(lowest, min(min(coverage_at(texel + ivec2(step, 0)), coverage_at(texel - ivec2(step, 0))),
                                     min(coverage_at(texel + ivec2(0, step)), coverage_at(texel - ivec2(0, step)))));
        }
        ink = clamp(material.a - lowest, 0.0, 1.0);
    }
    fragment_color = vec4(mix(rgb, material.rgb, ink), material.a * mix(color.a, 1.0, ink));
}

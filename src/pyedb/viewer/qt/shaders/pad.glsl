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

// The MIT notice above applies to PyEDB modifications.
// The upstream portions retain their original license below.
// SPDX-License-Identifier: Apache-2.0
// Modified for PyEDB's RHI renderer; see THIRD_PARTY_NOTICES.txt.

float pad_distance(vec4 screen) {
    float distance;
    vec4 p = delta(screen, a);
    if (flags.x < 2.5) {
        distance = radial_distance(p, vec2(params.x * 0.5, tangent.x * 0.5));
    } else {
        vec2 local = p.xy + p.zw;
        float co = cos(params.z), si = sin(params.z);
        local = vec2(co * local.x + si * local.y, -si * local.x + co * local.y);
        float corner = (detail.w > 0.5 && local.x < 0.0) ? 0.0 : detail.x;
        distance = box_distance(local, params.xy * 0.5 - corner) - corner;
    }
    if (detail.y > 0.0)
        distance = max(distance, -radial_distance(delta(screen, hole), vec2(detail.y, tangent.z)));
    return distance;
}

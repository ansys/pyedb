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
// Modified for PyEDB's OpenGL renderer; see THIRD_PARTY_NOTICES.txt.

float line_distance(vec4 screen) {
    vec4 p = delta(screen, a);
    vec4 normal = vec4(-tangent.y, tangent.x, -tangent.w, tangent.z);
    float along = precise_dot(p, tangent);
    float across = precise_dot(p, normal);
    float length_ab = precise_dot(delta(b, a), tangent);
    float r = max(params.x * 0.5, 0.5 / (scale * pixel_ratio));
    if (along < 0.0 && flags.y > 0.5 && flags.y < 1.5)
        return length(vec2(along, across)) - r;
    if (along > length_ab && flags.z > 0.5 && flags.z < 1.5)
        return length(vec2(along - length_ab, across)) - r;
    float distance = abs(across) - r;
    if (flags.y < 0.5 || flags.y > 1.5)
        distance = max(distance, -along - (flags.y > 1.5 ? r : 0.0));
    if (flags.z < 0.5 || flags.z > 1.5)
        distance = max(distance, along - length_ab - (flags.z > 1.5 ? r : 0.0));
    return distance;
}

float arc_cap(vec2 p, vec2 outward, float cap, float r) {
    if (cap > 0.5 && cap < 1.5) return length(p) - r;
    float extension = cap > 1.5 ? r : 0.0;
    return box_distance(vec2(dot(p, outward) - extension * 0.5, dot(p, vec2(-outward.y, outward.x))),
                        vec2(extension * 0.5, r));
}

float arc_distance(vec4 screen) {
    vec4 p = delta(screen, c);
    vec2 local = p.xy + p.zw;
    float direction = sign(params.w);
    float angle = mod((atan(local.y, local.x) - params.z) * direction, 6.28318530718);
    float r = max(params.x * 0.5, 0.5 / (scale * pixel_ratio));
    float radial = radial_distance(p, detail.zw);
    vec4 da = delta(screen, a);
    vec4 db = delta(screen, b);
    vec4 ra = delta(a, c);
    vec4 rb = delta(b, c);
    vec2 ta = normalize(vec2(-ra.y - ra.w, ra.x + ra.z)) * direction;
    vec2 tb = normalize(vec2(-rb.y - rb.w, rb.x + rb.z)) * direction;
    // Endpoint tangent tests preserve tiny sweeps at deep zoom.
    vec4 ta_pair = vec4(-ra.y, ra.x, -ra.w, ra.z);
    vec4 tb_pair = vec4(-rb.y, rb.x, -rb.w, rb.z);
    bool after = precise_dot(da, ta_pair) * direction >= 0.0;
    bool before = precise_dot(db, tb_pair) * direction <= 0.0;
    bool inside = abs(params.w) > 3.14159265359 ? (after || before) : (after && before);
    if (abs(params.w) >= 6.283185) return abs(radial) - r;
    if (inside) {
        float distance = abs(radial) - r;
        float window = min(abs(params.w) * 0.5, 1.57079632679);
        if (angle <= window && (flags.y < 0.5 || flags.y > 1.5))
            distance = max(distance, -dot(da.xy + da.zw, ta) - (flags.y > 1.5 ? r : 0.0));
        if (angle >= abs(params.w) - window && (flags.z < 0.5 || flags.z > 1.5))
            distance = max(distance, dot(db.xy + db.zw, tb) - (flags.z > 1.5 ? r : 0.0));
        return distance;
    }
    return min(arc_cap(da.xy + da.zw, -ta, flags.y, r), arc_cap(db.xy + db.zw, tb, flags.z, r));
}

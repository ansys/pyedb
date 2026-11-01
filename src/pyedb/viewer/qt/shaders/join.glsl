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

float join_distance(vec4 screen) {
    vec4 pa = delta(screen, a);
    vec4 ab = delta(b, a);
    vec4 ac = delta(c, a);
    vec2 p = pa.xy + pa.zw;
    vec4 ad = delta(hole, a);
    vec2 vertices[4] = vec2[4](vec2(0), ab.xy + ab.zw, ac.xy + ac.zw, ad.xy + ad.zw);
    int count = int(flags.y + 0.5);
    float distance_squared = 1e30;
    float low = 1e30;
    float high = -1e30;
    for (int i = 0; i < count; i++) {
        vec2 edge = vertices[(i + 1) % count] - vertices[i];
        vec2 v = p - vertices[i];
        vec2 nearest = v - edge * clamp(dot(v, edge) / max(dot(edge, edge), 1e-30), 0.0, 1.0);
        distance_squared = min(distance_squared, dot(nearest, nearest));
        float cross = edge.x * v.y - edge.y * v.x;
        low = min(low, cross);
        high = max(high, cross);
    }
    return sqrt(distance_squared) * ((low >= 0.0 || high <= 0.0) ? -1.0 : 1.0);
}

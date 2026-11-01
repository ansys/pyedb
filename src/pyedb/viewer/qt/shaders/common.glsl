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

vec2 add_pair(vec2 a, vec2 b) {
    float sum = a.x + b.x;
    float v = sum - a.x;
    float error = (a.x - (sum - v)) + (b.x - v) + a.y + b.y;
    float high = sum + error;
    return vec2(high, error - (high - sum));
}

vec2 multiply_pair(vec2 a, vec2 b) {
    float ca = 4097.0 * a.x;
    float ah = ca - (ca - a.x);
    float al = a.x - ah;
    float cb = 4097.0 * b.x;
    float bh = cb - (cb - b.x);
    float bl = b.x - bh;
    float product = a.x * b.x;
    float error = ((ah * bh - product) + ah * bl + al * bh) + al * bl + a.x * b.y + a.y * b.x;
    return add_pair(vec2(product, 0), vec2(error, 0));
}

vec4 delta(vec4 p, vec4 q) {
    vec2 x = add_pair(p.xz, -q.xz);
    vec2 y = add_pair(p.yw, -q.yw);
    return vec4(x.x, y.x, x.y, y.y);
}

float precise_dot(vec4 p, vec4 q) {
    vec2 sum = add_pair(multiply_pair(p.xz, q.xz), multiply_pair(p.yw, q.yw));
    return sum.x + sum.y;
}

float radial_distance(vec4 p, vec2 radius) {
    vec2 squared = add_pair(multiply_pair(p.xz, p.xz), multiply_pair(p.yw, p.yw));
    vec2 difference = add_pair(squared, -multiply_pair(radius, radius));
    return (difference.x + difference.y) / max(length(p.xy + p.zw) + radius.x + radius.y, 1e-30);
}

float box_distance(vec2 p, vec2 extent) {
    vec2 q = abs(p) - extent;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}

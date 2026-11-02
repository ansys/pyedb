// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
#version 330 core
uniform vec3 outline_color;
out vec4 fragment_color;

void main() {
    fragment_color = vec4(outline_color, 1.0);
}

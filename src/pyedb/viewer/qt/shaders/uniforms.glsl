// Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
// SPDX-License-Identifier: MIT

// Shared std140 layout. Keep offsets synchronized with qt/rhi.py.
layout(std140, binding = 0) uniform Frame {
    mat4 clip_corr;
    vec4 camera_split;
    vec4 view_data;
    vec4 options;
    vec4 color;
    vec4 rectangle;
    vec4 modes;
    vec4 phases;
    vec4 selection_data;
    vec4 highlight;
    vec4 keyline;
    vec4 render_flags;
    vec4 reserved;
};
#define viewport view_data.xy
#define scale view_data.z
#define pixel_ratio view_data.w
#define mirror_x options.x
#define selected_net int(options.y)
#define drill_pass (options.z > 0.5)
#define component_pass (options.w > 0.5)
#define layer_color color
#define opacity color.a
#define label_color color.rgb
#define rectangle_pass (modes.x > 0.5)
#define color_by_net (modes.y > 0.5)
#define spacing modes.z
#define outline (modes.w > 0.5)
#define fill_by_net (render_flags.z > 0.5)
#define minor_phase phases.xy
#define major_phase phases.zw
#define hovering (selection_data.x > 0.5)
#define patterned (selection_data.y > 0.5)
#define highlight_color highlight.rgb
#define keyline_color keyline.rgb
#define multisampled (render_flags.x > 0.5)

// Fragment coordinates use the native framebuffer origin. Analytic geometry
// and the world grid use bottom-up coordinates on every backend.
#define world_fragment vec2(gl_FragCoord.x, render_flags.y > 0.5 ? gl_FragCoord.y : viewport.y * pixel_ratio - gl_FragCoord.y)

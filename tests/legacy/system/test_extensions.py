# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from copy import deepcopy as copy
from pathlib import Path

import pytest

from pyedb.extensions.via_design_backend import Board, ViaDesignBackend

desktop_version = "2025.1"
pytestmark = [pytest.mark.unit, pytest.mark.legacy]

STACKUP = [
    {"name": "PKG_L1", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "22um"},
    {"name": "PKG_DE0", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L2", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE1", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L3", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE2", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L4", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE3", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L5", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE4", "type": "dielectric", "material": "fr4", "thickness": "1200um"},
    {"name": "PKG_L6", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE5", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L7", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE6", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L8", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE7", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L9", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "15um"},
    {"name": "PKG_DE8", "type": "dielectric", "material": "fr4", "thickness": "30um"},
    {"name": "PKG_L10", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "22um"},
    {"name": "AIR", "type": "dielectric", "material": "air", "thickness": "400um"},
    {"name": "PCB_L1", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "50um"},
    {"name": "PCB_DE0", "type": "dielectric", "material": "fr4", "thickness": "100um"},
    {"name": "PCB_L2", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE1", "type": "dielectric", "material": "fr4", "thickness": "125um"},
    {"name": "PCB_L3", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE2", "type": "dielectric", "material": "fr4", "thickness": "100um"},
    {"name": "PCB_L4", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE3", "type": "dielectric", "material": "fr4", "thickness": "125um"},
    {"name": "PCB_L5", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE4", "type": "dielectric", "material": "fr4", "thickness": "100um"},
    {"name": "PCB_L6", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE5", "type": "dielectric", "material": "fr4", "thickness": "125um"},
    {"name": "PCB_L7", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE6", "type": "dielectric", "material": "fr4", "thickness": "100um"},
    {"name": "PCB_L8", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE7", "type": "dielectric", "material": "fr4", "thickness": "125um"},
    {"name": "PCB_L9", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "17um"},
    {"name": "PCB_DE8", "type": "dielectric", "material": "fr4", "thickness": "100um"},
    {"name": "PCB_L10", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "50um"},
]
PADSTACK_DEFS = [
    {
        "name": "CORE_VIA",
        "shape": "circle",
        "pad_diameter": "0.25mm",
        "hole_diameter": "0.1mm",
        "hole_range": "upper_pad_to_lower_pad",
    },
    {
        "name": "MICRO_VIA",
        "shape": "circle",
        "pad_diameter": "0.1mm",
        "hole_diameter": "0.05mm",
        "hole_range": "upper_pad_to_lower_pad",
    },
    {
        "name": "BGA",
        "shape": "circle",
        "pad_diameter": "0.5mm",
        "hole_diameter": "0.4mm",
        "hole_range": "upper_pad_to_lower_pad",
    },
]
FANOUT_UPPER = {
    "layer": "PKG_L1",
    "width": "0.05mm",
    "clearance": "0.05mm",
    "incremental_path": [["0.1mm", "0.1mm"], [0, "0.1mm"]],
    "end_cap_style": "flat",
    "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
}
FANOUT_LOWER = copy(FANOUT_UPPER)
FANOUT_LOWER["layer"] = "PCB_L6"

MICRO_VIA_INSTANCE_L1_L5 = {
    "padstack_def": "MICRO_VIA",
    "start_layer": "PKG_L1",
    "stop_layer": "PKG_L5",
    "dx": "0.05mm",
    "dy": "0.05mm",
    "flip_dx": False,
    "flip_dy": False,
    "anti_pad_diameter": "0.5mm",
    "connection_trace": {"width": "0.1mm", "clearance": "0.15mm"},
    "with_solder_ball": False,
    "backdrill_parameters": None,
    "fanout_trace": None,
}

MICRO_VIA_INSTANCE_L6_L10 = copy(MICRO_VIA_INSTANCE_L1_L5)
MICRO_VIA_INSTANCE_L6_L10["start_layer"] = "PKG_L6"
MICRO_VIA_INSTANCE_L6_L10["stop_layer"] = "PKG_L10"
MICRO_VIA_INSTANCE_L6_L10["fanout_trace"] = None

CORE_VIA_INSTANCE = {
    "padstack_def": "CORE_VIA",
    "start_layer": "PKG_L5",
    "stop_layer": "PKG_L6",
    # "base_x": "0mm",
    # "base_y": "1mm",
    "dx": "0.2mm",
    "dy": "0mm",
    "anti_pad_diameter": "0.5mm",
    "flip_dx": False,
    "flip_dy": False,
    "connection_trace": {"width": "0.1mm", "clearance": "0.15mm"},
    "with_solder_ball": False,
    "backdrill_parameters": None,
    "fanout_trace": None,
}
BGA_INSTANCE = {
    "padstack_def": "BGA",
    "start_layer": "PKG_L10",
    "stop_layer": "PCB_L1",
    # "base_x": "0mm",
    # "base_y": "1mm",
    "dx": "pitch/2",
    "dy": "pitch/2",
    "anti_pad_diameter": "0.8mm",
    "flip_dx": False,
    "flip_dy": False,
    "connection_trace": {"width": "0.3mm", "clearance": "0.15mm"},
    "with_solder_ball": False,
    "backdrill_parameters": None,
    "fanout_trace": None,
}

PCB_VIA_INSTANCE = {
    "padstack_def": "CORE_VIA",
    "start_layer": "PCB_L1",
    "stop_layer": "PCB_L10",
    "dx": 0,
    "dy": 0,
    "anti_pad_diameter": "0.7mm",
    "flip_dx": False,
    "flip_dy": True,
    "connection_trace": None,
    "with_solder_ball": False,
    "backdrill_parameters": None,
    "fanout_trace": None,
}
GND_MICRO_VIA_INSTANCE_L1_L5 = copy(MICRO_VIA_INSTANCE_L1_L5)
GND_MICRO_VIA_INSTANCE_L1_L5["dx"] = 0
GND_MICRO_VIA_INSTANCE_L1_L5["dy"] = 0
GND_MICRO_VIA_INSTANCE_L1_L5["connection_trace"] = None
GND_MICRO_VIA_INSTANCE_L6_L10 = copy(MICRO_VIA_INSTANCE_L6_L10)
GND_MICRO_VIA_INSTANCE_L6_L10["dx"] = 0
GND_MICRO_VIA_INSTANCE_L6_L10["dy"] = 0
GND_MICRO_VIA_INSTANCE_L6_L10["connection_trace"] = None

GND_CORE_VIA_INSTANCE = copy(CORE_VIA_INSTANCE)
GND_CORE_VIA_INSTANCE["connection_trace"] = None


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        working_dir = Path(local_scratch.path)
        self.working_dir = working_dir

        self.cfg = {
            "stackup": {"layers": [], "materials": []},
            "variables": [],
            "ports": [],
            "modeler": {"traces": [], "planes": [], "padstack_definitions": [], "padstack_instances": []},
        }

    def test_board_signal_via(self, edb_examples):
        cfg = copy(self.cfg)
        pin_map = [
            ["GND", "SIG", "GND"],
        ]

        signals = {
            "SIG": {
                "fanout_trace": {
                    0: {
                        "layer": "PKG_L1",
                        "width": "0.05mm",
                        "clearance": "0.05mm",
                        "incremental_path": [[0, "0.5mm"]],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                    4: {
                        "layer": "PCB_L6",
                        "width": "0.1mm",
                        "clearance": "0.2mm",
                        "incremental_path": [[0, "1mm"]],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                },
                "stacked_vias": [
                    copy(MICRO_VIA_INSTANCE_L1_L5),
                    copy(CORE_VIA_INSTANCE),
                    copy(MICRO_VIA_INSTANCE_L6_L10),
                    copy(BGA_INSTANCE),
                    copy(PCB_VIA_INSTANCE),
                ],
            },
            "GND": {
                "fanout_trace": {},
                "stacked_vias": [
                    GND_MICRO_VIA_INSTANCE_L1_L5,
                    copy(CORE_VIA_INSTANCE),
                    GND_MICRO_VIA_INSTANCE_L6_L10,
                    copy(BGA_INSTANCE),
                    copy(PCB_VIA_INSTANCE),
                ],
            },
        }
        board = Board(
            STACKUP,
            PADSTACK_DEFS,
            outline_extent="1mm",
            pitch="1mm",
            pin_map=pin_map,
            signals=signals,
            differential_signals=None,
        )
        board.populate_config(cfg)

        app = edb_examples.create_empty_edb()
        app.configuration.load(cfg, apply_file=True)
        app.close_edb()

    def test_board_diff_pair(self, edb_examples):
        cfg = copy(self.cfg)
        pin_map = [
            ["GND", "SIG_P", "SIG_N", "GND"],
        ]
        signals = {
            "GND": {
                "fanout_trace": {},
                "stacked_vias": [
                    GND_MICRO_VIA_INSTANCE_L1_L5,
                    GND_CORE_VIA_INSTANCE,
                    GND_MICRO_VIA_INSTANCE_L6_L10,
                    copy(BGA_INSTANCE),
                    copy(PCB_VIA_INSTANCE),
                ],
            },
        }
        differential_signals = {
            "SIG": {
                "signals": ["SIG_P", "SIG_N"],
                "fanout_trace": {
                    0: {
                        "layer": "PKG_L1",
                        "width": "0.05mm",
                        "separation": "0.05mm",
                        "clearance": "0.05mm",
                        "incremental_path_dy": ["0.1mm", "0.1mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                    4: {
                        "layer": "PCB_L6",
                        "width": "0.1mm",
                        "separation": "0.15mm",
                        "clearance": "0.2mm",
                        "incremental_path_dy": ["0.1mm", "0.1mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                },
                "stacked_vias": [
                    MICRO_VIA_INSTANCE_L1_L5,
                    CORE_VIA_INSTANCE,
                    MICRO_VIA_INSTANCE_L6_L10,
                    BGA_INSTANCE,
                    PCB_VIA_INSTANCE,
                ],
            }
        }

        board = Board(
            STACKUP,
            PADSTACK_DEFS,
            outline_extent="1mm",
            pitch="1mm",
            pin_map=pin_map,
            signals=signals,
            differential_signals=differential_signals,
        )
        board.populate_config(cfg)

        app = edb_examples.create_empty_edb()
        app.configuration.load(cfg, apply_file=True)
        app.close_edb()

    @pytest.mark.skipif(True, reason="Not ready to test")
    def test_board_two_diff_pairs(self, edb_examples):
        cfg = copy(self.cfg)
        pin_map = [
            ["GND", "SIG_1_P", "SIG_1_N", "GND"],
            ["GND", "GND", "SIG_2_P", "SIG_2_N"],
        ]
        signals = {
            "GND": {
                "fanout_trace": {},
                "stacked_vias": [
                    GND_MICRO_VIA_INSTANCE_L1_L5,
                    GND_CORE_VIA_INSTANCE,
                    GND_MICRO_VIA_INSTANCE_L6_L10,
                    copy(BGA_INSTANCE),
                    copy(PCB_VIA_INSTANCE),
                ],
            },
        }
        differential_signals = {
            "SIG_1": {
                "signals": ["SIG_1_P", "SIG_1_N"],
                "fanout_trace": {
                    0: {
                        "layer": "PKG_L1",
                        "width": "0.05mm",
                        "separation": "0.05mm",
                        "clearance": "0.05mm",
                        "incremental_path_dy": ["0.1mm", "0.1mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                    4: {
                        "layer": "PCB_L6",
                        "width": "0.1mm",
                        "separation": "0.15mm",
                        "clearance": "0.2mm",
                        "incremental_path_dy": ["0.1mm", "0.1mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                },
                "stacked_vias": [
                    MICRO_VIA_INSTANCE_L1_L5,
                    CORE_VIA_INSTANCE,
                    MICRO_VIA_INSTANCE_L6_L10,
                    BGA_INSTANCE,
                    PCB_VIA_INSTANCE,
                ],
            },
            "SIG_2": {
                "signals": ["SIG_2_P", "SIG_2_N"],
                "fanout_trace": {
                    0: {
                        "layer": "PKG_L1",
                        "width": "0.05mm",
                        "separation": "0.05mm",
                        "clearance": "0.05mm",
                        "incremental_path_dy": ["0.3mm", "0.3mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                    4: {
                        "layer": "PCB_L8",
                        "width": "0.1mm",
                        "separation": "0.15mm",
                        "clearance": "0.2mm",
                        "incremental_path_dy": ["0.3mm", "0.3mm"],
                        "end_cap_style": "flat",
                        "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                    },
                },
                "stacked_vias": [
                    MICRO_VIA_INSTANCE_L1_L5,
                    CORE_VIA_INSTANCE,
                    MICRO_VIA_INSTANCE_L6_L10,
                    BGA_INSTANCE,
                    PCB_VIA_INSTANCE,
                ],
            },
        }

        board = Board(
            STACKUP,
            PADSTACK_DEFS,
            outline_extent="1mm",
            pitch="1mm",
            pin_map=pin_map,
            signals=signals,
            differential_signals=differential_signals,
        )
        board.populate_config(cfg)

        app = edb_examples.create_empty_edb()
        app.configuration.load(cfg, apply_file=True)
        app.save_edb()
        app.close_edb()

        import ansys.aedt.core

        h3d = ansys.aedt.core.Hfss3dLayout(project=app.edbpath, version=desktop_version)
        h3d.release_desktop()

    @pytest.mark.skipif(True, reason="Not ready to test")
    def test_backend(self):
        cfg = {
            "Title": "Test Design",
            "General": {
                "version": desktop_version,
                "output_dir": "",
                "outline_extent": "1mm",
                "pitch": "1mm",
            },
            "stackup": STACKUP,
            "padstack_defs": PADSTACK_DEFS,
            "pin_map": [
                ["GND", "SIG", "GND"],
            ],
            "signals": {
                "SIG": {
                    "fanout_trace": {
                        0: {
                            "layer": "PKG_L1",
                            "width": "0.05mm",
                            "clearance": "0.05mm",
                            "incremental_path": [[0, "0.5mm"]],
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                        4: {
                            "layer": "PCB_L6",
                            "width": "0.1mm",
                            "clearance": "0.2mm",
                            "incremental_path": [[0, "1mm"]],
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                    },
                    "stacked_vias": [
                        copy(MICRO_VIA_INSTANCE_L1_L5),
                        copy(CORE_VIA_INSTANCE),
                        copy(MICRO_VIA_INSTANCE_L6_L10),
                        copy(BGA_INSTANCE),
                        copy(PCB_VIA_INSTANCE),
                    ],
                },
                "GND": {
                    "fanout_trace": {},
                    "stacked_vias": [
                        GND_MICRO_VIA_INSTANCE_L1_L5,
                        copy(CORE_VIA_INSTANCE),
                        GND_MICRO_VIA_INSTANCE_L6_L10,
                        copy(BGA_INSTANCE),
                        copy(PCB_VIA_INSTANCE),
                    ],
                },
            },
            "differential_signals": {},
        }
        app = ViaDesignBackend(cfg)
        app.launch_h3d()

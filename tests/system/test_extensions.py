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
from pathlib import Path

import pytest

from pyedb.extensions.via_design_backend import ViaDesignBackend
from tests.conftest import desktop_version

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
        "solder_ball_parameters": {
            "shape": "spheroid",
            "diameter": "0.4mm",
            "mid_diameter": "0.5mm",
            "placement": "above_padstack",
            "material": "solder",
        },
    },
]


class TestClass:
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(cls, request, edb_examples):
        # Set up the EDB app once per class
        pass

        # Finalizer to close the EDB app after all tests
        def teardown():
            cls.edbapp_shared = edb_examples.get_si_verse()
            cls.edbapp_shared.close(terminate_rpc_session=True)

        request.addfinalizer(teardown)

    @pytest.fixture(autouse=True)
    def teardown(self, request, edb_examples):
        """Code after yield runs after each test."""
        yield
        pass

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

    def test_backend_single(self):
        cfg = {
            "title": "Test Design",
            "general": {
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
                    "fanout_trace": [
                        {
                            "via_index": 0,
                            "layer": "PKG_L1",
                            "width": "0.05mm",
                            "clearance": "0.05mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "incremental_path": [[0, "0.5mm"]],
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                        {
                            "via_index": 3,
                            "layer": "PCB_L6",
                            "width": "0.1mm",
                            "clearance": "0.2mm",
                            "flip_dx": False,
                            "flip_dy": True,
                            "incremental_path": [[0, "1mm"]],
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                    ],
                    "stacked_vias": [
                        {
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
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PKG_L5",
                            "stop_layer": "PKG_L6",
                            "dx": "0.2mm",
                            "dy": "0mm",
                            "anti_pad_diameter": "0.5mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.1mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": {"start_angle": 0, "step_angle": 45, "number_of_vias": 6, "distance": 0},
                        },
                        {
                            "padstack_def": "BGA",
                            "start_layer": "PKG_L10",
                            "stop_layer": "PCB_L1",
                            "dx": "pitch/2",
                            "dy": "pitch/2",
                            "anti_pad_diameter": "0.8mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.3mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
                "GND": {
                    "fanout_trace": {},
                    "stacked_vias": [
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "PKG_L1",
                            "stop_layer": "PKG_L5",
                            "dx": 0,
                            "dy": 0,
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PKG_L5",
                            "stop_layer": "PKG_L6",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.5mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "PKG_L6",
                            "stop_layer": "PKG_L10",
                            "dx": 0,
                            "dy": 0,
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "BGA",
                            "start_layer": "PKG_L10",
                            "stop_layer": "PCB_L1",
                            "dx": "pitch/2",
                            "dy": "pitch/2",
                            "anti_pad_diameter": "0.8mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.3mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": True,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
            },
            "differential_signals": {},
        }
        app = ViaDesignBackend(cfg)

    def test_backend_diff(self):
        cfg = {
            "title": "Test Design",
            "general": {
                "version": desktop_version,
                "output_dir": "",
                "outline_extent": "1mm",
                "pitch": "1mm",
            },
            "stackup": STACKUP,
            "padstack_defs": PADSTACK_DEFS,
            "pin_map": [
                ["GND", "SIG_1_P", "SIG_1_N", "GND"],
            ],
            "signals": {
                "GND": {
                    "fanout_trace": {},
                    "stacked_vias": [
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "PKG_L1",
                            "stop_layer": "PKG_L5",
                            "dx": 0,
                            "dy": 0,
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PKG_L5",
                            "stop_layer": "PKG_L6",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.5mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "PKG_L6",
                            "stop_layer": "PKG_L10",
                            "dx": 0,
                            "dy": 0,
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "BGA",
                            "start_layer": "PKG_L10",
                            "stop_layer": "PCB_L1",
                            "dx": "pitch/2",
                            "dy": "pitch/2",
                            "anti_pad_diameter": "0.8mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.3mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": True,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
            },
            "differential_signals": {
                "SIG_1": {
                    "signals": ["SIG_1_P", "SIG_1_N"],
                    "fanout_trace": [
                        {
                            "via_index": 0,
                            "layer": "PKG_L1",
                            "width": "0.05mm",
                            "separation": "0.05mm",
                            "clearance": "0.05mm",
                            "incremental_path_dy": ["0.3mm", "0.3mm"],
                            "end_cap_style": "flat",
                            "flip_dx": False,
                            "flip_dy": False,
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                        {
                            "via_index": 4,
                            "layer": "PCB_L6",
                            "width": "0.1mm",
                            "separation": "0.15mm",
                            "clearance": "0.2mm",
                            "incremental_path_dy": ["0.1mm", "0.5mm"],
                            "flip_dx": False,
                            "flip_dy": True,
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                    ],
                    "stacked_vias": [
                        {
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
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PKG_L5",
                            "stop_layer": "PKG_L6",
                            "dx": "0.2mm",
                            "dy": "0mm",
                            "anti_pad_diameter": "1mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.1mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": {
                                "start_angle": 90,
                                "step_angle": 45,
                                "number_of_vias": 5,
                                "distance": "0.125mm",
                            },
                        },
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "PKG_L6",
                            "stop_layer": "PKG_L10",
                            "dx": "0.05mm",
                            "dy": "0.05mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": {"width": "0.1mm", "clearance": "0.15mm"},
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "BGA",
                            "start_layer": "PKG_L10",
                            "stop_layer": "PCB_L1",
                            "dx": "pitch/2",
                            "dy": "pitch/2",
                            "anti_pad_diameter": "0.8mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": {"width": "0.3mm", "clearance": "0.15mm"},
                            "with_solder_ball": True,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
            },
        }
        app = ViaDesignBackend(cfg)

    def test_backend_diff_pcb(self):
        cfg = {
            "title": "Test Design",
            "general": {
                "version": desktop_version,
                "output_dir": "",
                "outline_extent": "1mm",
                "pitch": "1mm",
            },
            "stackup": STACKUP,
            "padstack_defs": PADSTACK_DEFS,
            "pin_map": [
                ["GND", "SIG_1_P", "SIG_1_N", "GND"],
            ],
            "signals": {
                "GND": {
                    "fanout_trace": {},
                    "stacked_vias": [
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": True,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
            },
            "differential_signals": {
                "SIG_1": {
                    "signals": ["SIG_1_P", "SIG_1_N"],
                    "fanout_trace": [
                        {
                            "via_index": 0,
                            "layer": "PCB_L1",
                            "width": "0.05mm",
                            "separation": "0.05mm",
                            "clearance": "0.05mm",
                            "incremental_path_dy": ["0.3mm", "0.3mm"],
                            "end_cap_style": "flat",
                            "flip_dx": False,
                            "flip_dy": False,
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                        {
                            "via_index": 0,
                            "layer": "PCB_L6",
                            "width": "0.1mm",
                            "separation": "0.15mm",
                            "clearance": "0.2mm",
                            "incremental_path_dy": ["0.1mm", "0.5mm"],
                            "flip_dx": False,
                            "flip_dy": True,
                            "end_cap_style": "flat",
                            "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
                        },
                    ],
                    "stacked_vias": [
                        {
                            "padstack_def": "CORE_VIA",
                            "start_layer": "PCB_L1",
                            "stop_layer": "PCB_L10",
                            "dx": 0,
                            "dy": 0,
                            "anti_pad_diameter": "0.7mm",
                            "flip_dx": False,
                            "flip_dy": False,
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": {
                                "from_bottom": {
                                    "drill_to_layer": "PCB_L6",
                                    "diameter": "1.2mm",
                                    "stub_length": "0.15mm",
                                },
                            },
                            "fanout_trace": list(),
                            "stitching_vias": False,
                        },
                    ],
                },
            },
        }
        app = ViaDesignBackend(cfg)

    def test_arbitrary_wave_ports(self, edb_examples):
        # TODO check later when sever instances is improved.
        import os

        local_path = Path(__file__).parent.parent
        example_folder = os.path.join(local_path, "example_models", "TEDB")
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")

        edbapp = edb_examples.load_edb(source_path_edb)
        assert edbapp.create_model_for_arbitrary_wave_ports(
            temp_directory=edb_examples.test_folder,
            output_edb=os.path.join(edb_examples.test_folder, "wave_ports.aedb"),
            mounting_side="top",
        )
        edb_model = os.path.join(edb_examples.test_folder, "wave_ports.aedb")
        assert os.path.isdir(edb_model)
        edbapp.close(terminate_rpc_session=False)

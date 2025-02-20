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
import json
from pathlib import Path

import pytest

from pyedb.generic.general_methods import is_linux
from pyedb.extensions.pre_layout_design_toolkit.via_design import ViaDesignConfig
from tests.conftest import desktop_version

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

pcb_stackup = [
    {"name": "PCB_TOP", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "50um"},
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
    {"name": "PCB_BOT", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "50um"},
]
pkg_stackup = [
    {"name": "PKG_TOP", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "22um"},
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
    {"name": "PKG_BOT", "type": "signal", "material": "copper", "fill_material": "fr4", "thickness": "22um"},
]
padstacks = [
    {
        "name": "pcb_via",
        "shape": "circle",
        "pad_diameter": "0.5mm",
        "hole_diameter": "0.3mm",
        "anti_pad_diameter": "0.6mm",
        "hole_range": "upper_pad_to_lower_pad",
    },
    {
        "name": "micro_via",
        "shape": "circle",
        "pad_diameter": "0.1mm",
        "x_size": "0.1mm",
        "y_size": "0.15mm",
        "anti_pad_diameter": "0.3mm",
        "hole_diameter": "0.05mm",
        "hole_range": "upper_pad_to_lower_pad",
    },
    {
        "name": "bga",
        "shape": "rectangle",
        "pad_diameter": "0.25mm",
        "x_size": "0.4mm",
        "y_size": "0.4mm",
        "anti_pad_diameter": "0.6mm",
    },
    {
        "name": "blind_via",
        "shape": "circle",
        "pad_diameter": "0.25mm",
        "anti_pad_diameter": "0.6mm",
        "hole_diameter": "0.1mm",
        "hole_range": "upper_pad_to_lower_pad",
        "is_core": True,
    },
]
materials = [
    {"name": "copper", "conductivity": 58000000.0},
    {"name": "fr4", "permittivity": 4.4, "dielectric_loss_tangent": 0.02},
]
technology = {
    "plane_extend": "1mm",
    "pitch": "1mm",
    "bga_component": {
        "enabled": False,
        "solder_ball_shape": "spheroid",
        "solder_ball_diameter": "300um",
        "solder_ball_mid_diameter": "400um",
        "solder_ball_height": "200um",
        "fanout_dx": "0.4mm",
        "fanout_dy": "0.4mm",
        "fanout_width": "0.3mm",
        "fanout_clearance": "0.15mm",
    },
    "pkg_ground_via": {"distance": "0.2mm", "core_via_start_layer": "PKG_L2", "core_via_stop_layer": "PKG_L3"},
}
setup = {
    "name": "hfss_1",
    "type": "hfss",
    "f_adapt": "5GHz",
    "max_num_passes": 10,
    "max_mag_delta_s": 0.02,
    "freq_sweep": [
        {
            "name": "Sweep1",
            "type": "interpolation",
            "frequencies": [{"distribution": "log_scale", "start": 1000000.0, "stop": 1000000000.0, "increment": 20}],
        }
    ],
}
pin_map = {
    "signal_pairs": {"S0": ["S0_P", "S0_N"], "S1": ["S1_P", "S1_N"]},
    "locations": [
        ["GND", "S0_P", "S0_N", "GND", "GND"],
        ["GND", "GND", "S1_P", "S1_N", "GND"],
    ],
}
main = {
    "version": desktop_version,
    "working_directory": None,
    "design_type": "pcb",
    "materials": "materials.json",
    "pcb_stackup": "pcb_stackup.json",
    "padstacks": "padstacks.json",
    "pin_map": "pin_map.json",
    "technology": "technology.json",
    "setup": "setup.json",
}

main_pkg_w_pcb = copy(main)
main_pkg_w_pcb["design_type"] = "pkg"
main_pkg_w_pcb["include_pcb"] = True
main_pkg_w_pcb["pkg_stackup"] = "pkg_stackup.json"

S0 = {
    "pcb_trace": [
        {
            "width": "0.075mm",
            "gap": "0.1mm",
            "length": "0.5mm",
            "clearance": "0.1mm",
            "shift": "0.5mm",
            "layer": "PCB_L3",
            "trace_out_direction": "backward",
        }
    ],
    "pcb_signal_via": [
        {
            "padstack_definition": "pcb_via",
            "start_layer": "PCB_TOP",
            "stop_layer": "PCB_BOT",
            "trace": True,
            "trace_width": "0.4mm",
            "trace_clearance": "0.15mm",
            "dx": "0mm",
            "dy": "0mm",
            "backdrill_parameters": {
                "from_bottom": {
                    "drill_to_layer": "PCB_L3",
                    "diameter": "0.5mm",
                    "stub_length": "0.05mm",
                }
            },
        }
    ],
}
S0_pcb = copy(S0)
S0_pcb["pcb_trace"].append(
    {
        "width": "0.075mm",
        "gap": "0.1mm",
        "length": "0.5mm",
        "clearance": "0.1mm",
        "shift": "0.5mm",
        "layer": "PCB_TOP",
        "trace_out_direction": "forward",
    }
)
S0_pkg_w_pcb = copy(S0)
S0_pkg_w_pcb["pkg_signal_via"] = [
    {
        "padstack_definition": "micro_via",
        "start_layer": "PKG_L7",
        "stop_layer": "PKG_BOT",
        "trace": True,
        "trace_width": "0.05mm",
        "trace_clearance": "0.05mm",
        "dx": "0.05mm",
        "dy": "0mm",
    },
    {
        "padstack_definition": "micro_via",
        "start_layer": "PKG_L6",
        "stop_layer": "PKG_L7",
        "trace": True,
        "trace_width": "0.05mm",
        "trace_clearance": "0.05mm",
        "dx": "0.05mm",
        "dy": "0mm",
    },
    {
        "padstack_definition": "blind_via",
        "start_layer": "PKG_L5",
        "stop_layer": "PKG_L6",
        "trace": True,
        "trace_width": "0.05mm",
        "trace_clearance": "0.05mm",
        "dx": "0.05mm",
        "dy": "0mm",
    },
    {
        "padstack_definition": "micro_via",
        "start_layer": "PKG_L3",
        "stop_layer": "PKG_L5",
        "trace": True,
        "trace_width": "0.05mm",
        "trace_clearance": "0.05mm",
        "dx": "0.1mm",
        "dy": "0mm",
    },
    {
        "padstack_definition": "micro_via",
        "start_layer": "PKG_TOP",
        "stop_layer": "PKG_L3",
        "trace": True,
        "trace_width": "0.05mm",
        "trace_clearance": "0.05mm",
        "dx": "0.05mm",
        "dy": "0.05mm",
    },
]
S0_pkg_w_pcb["pkg_trace"] = [
    {
        "width": "0.05mm",
        "gap": "0.05mm",
        "length": "0.2mm",
        "clearance": "0.05mm",
        "stitching_via_dy": "0.4mm",
        "shift": "0.2mm",
        "layer": "PKG_TOP",
        "trace_out_direction": "forward",
    }
]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        working_dir = Path(local_scratch.path)
        self.working_dir = working_dir

        with open(working_dir / "materials.json", "w") as f:
            json.dump(materials, f, indent=4, ensure_ascii=False)

        with open(working_dir / "padstacks.json", "w") as f:
            json.dump(padstacks, f, indent=4, ensure_ascii=False)

        with open(working_dir / "pcb_stackup.json", "w") as f:
            json.dump(pcb_stackup, f, indent=4, ensure_ascii=False)

        with open(working_dir / "pkg_stackup.json", "w") as f:
            json.dump(pkg_stackup, f, indent=4, ensure_ascii=False)

        with open(self.working_dir / "setup.json", "w") as f:
            json.dump(setup, f, indent=4, ensure_ascii=False)

        with open(self.working_dir / "pin_map.json", "w") as f:
            json.dump(pin_map, f, indent=4, ensure_ascii=False)

        with open(self.working_dir / "main.json", "w") as f:
            json.dump(main, f, indent=4, ensure_ascii=False)

        with open(self.working_dir / "main_pkg_w_pcb.json", "w") as f:
            json.dump(main_pkg_w_pcb, f, indent=4, ensure_ascii=False)

    @pytest.mark.skipif(is_linux, reason="Failing on linux")
    def test_01_pre_layout_design_toolkit_pcb_diff_via(self):
        signal_pair = {
            "S0": S0_pcb,
            "S1": S0_pcb,
        }
        pcb_ground_via = {
            "distance": "0.2mm",
            "core_via_start_layer": "PCB_TOP",
            "core_via_stop_layer": "PCB_BOT",
        }
        local_tech = technology.copy()
        local_tech["signal_pair"] = signal_pair
        local_tech["pcb_ground_via"] = pcb_ground_via
        with open(self.working_dir / "technology.json", "w") as f:
            json.dump(local_tech, f, indent=4, ensure_ascii=False)

        config_file_path = self.working_dir / "main.json"
        app = ViaDesignConfig(config_file_path, desktop_version)
        data = app.create_design()
        app.save_cfg_to_file(data)
        edb_path = app.create_edb(data)

        assert edb_path

    @pytest.mark.skipif(is_linux, reason="Failing on linux")
    def test_02_pre_layout_design_toolkit_pcb_pkg_diff_via(self):
        signal_pair = {
            "S0": S0_pkg_w_pcb,
            "S1": S0_pkg_w_pcb,
        }
        pcb_ground_via = {
            "distance": "0.2mm",
            "core_via_start_layer": "PCB_TOP",
            "core_via_stop_layer": "PCB_BOT",
        }
        local_tech = technology.copy()
        local_tech["signal_pair"] = signal_pair
        local_tech["pcb_ground_via"] = pcb_ground_via
        with open(self.working_dir / "technology.json", "w") as f:
            json.dump(local_tech, f, indent=4, ensure_ascii=False)

        config_file_path = self.working_dir / "main_pkg_w_pcb.json"
        app = ViaDesignConfig(config_file_path, desktop_version)
        data = app.create_design()
        app.save_cfg_to_file(data)
        edb_path = app.create_edb(data)
        assert edb_path

# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

# # DCIR Setup Leveraging EDB Configuration Format

# ## Import the required packages

import json

# +
import os
import tempfile

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.downloads import download_file

from pyedb import Edb

AEDT_VERSION = "2024.2"
NG_MODE = False

# -

# Download the example BGA Package design.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = download_file(source=r"edb/BGA_Package.aedb", destination=temp_folder.name)

# ## Load example layout

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create config file

# Define Component with solderballs.

cfg_components = [
    {
        "reference_designator": "FCHIP",
        "part_type": "other",
        "solder_ball_properties": {
            "shape": "cylinder",
            "diameter": "0.1mm",
            "height": "0.085mm",
            "chip_orientation": "chip_up",
        },
        "port_properties": {
            "reference_offset": 0,
            "reference_size_auto": False,
            "reference_size_x": 0,
            "reference_size_y": 0,
        },
    },
    {
        "reference_designator": "BGA",
        "part_type": "io",
        "solder_ball_properties": {
            "shape": "cylinder",
            "diameter": "0.45mm",
            "height": "0.45mm",
            "chip_orientation": "chip_down",
        },
        "port_properties": {
            "reference_offset": 0,
            "reference_size_auto": False,
            "reference_size_x": 0,
            "reference_size_y": 0,
        },
    },
]

# Define Pin Groups on Components.

cfg_pin_groups = [
    {"name": "BGA_VSS", "reference_designator": "BGA", "net": "VSS"},
    {"name": "BGA_VDD", "reference_designator": "BGA", "net": "VDD"},
]

# Define sources.

cfg_sources = [
    {
        "name": "FCHIP_Current",
        "reference_designator": "FCHIP",
        "type": "current",
        "magnitude": 2,
        "distributed": True,
        "positive_terminal": {"net": "VDD"},
        "negative_terminal": {"nearest_pin": {"reference_net": "VSS", "search_radius": 5e-3}},
    },
    {
        "name": "BGA_Voltage",
        "reference_designator": "BGA",
        "type": "voltage",
        "magnitude": 1,
        "positive_terminal": {"pin_group": "BGA_VDD"},
        "negative_terminal": {"pin_group": "BGA_VSS"},
    },
]

# Define DCIR setup.

cfg_setups = [
    {
        "name": "siwave_dc",
        "type": "siwave_dc",
        "dc_slider_position": 1,
        "dc_ir_settings": {"export_dc_thermal_data": True},
    }
]

# Create final configuration.

cfg = {
    "components": cfg_components,
    "sources": cfg_sources,
    "pin_groups": cfg_pin_groups,
    "setups": cfg_setups,
}

# Create the config file.

file_json = os.path.join(temp_folder.name, "edb_configuration.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Apply Config file

# Apply configuration to the example layout

edbapp.configuration.load(config_file=file_json)
edbapp.configuration.run()

# Save and close EDB.

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# Solve.

h3d.analyze(setup="siwave_dc")

# Plot insertion loss.

h3d.post.create_fieldplot_layers_nets(layers_nets=[["VDD_C1", "VDD"]], quantity="Voltage", setup="siwave_dc")

# Shut Down Electronics Desktop

h3d.close_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.

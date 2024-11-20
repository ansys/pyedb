# # Set up EDB for PCB DC IR Analysis
# This example shows how to set up the electronics database (EDB) for DC IR analysis from a single
# configuration file.

# ## Import the required packages

import json

# +
import os
import tempfile

from IPython.display import Image, display
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.downloads import download_file

from pyedb import Edb

AEDT_VERSION = "2024.2"
NG_MODE = False

# -

# Download the example PCB data.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
file_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", destination=temp_folder.name)

from pathlib import Path
import shutil

# ## Load example layout

edbapp = Edb(file_edb, edbversion=AEDT_VERSION)

# ## Create an empty dictionary to host all configurations

cfg = dict()
cfg["sources"] = []

# ## Define voltage source

cfg["sources"].append(
    {
        "name": "vrm",
        "reference_designator": "U2",
        "type": "voltage",
        "positive_terminal": {"net": "1V0"},
        "negative_terminal": {"net": "GND"},
    }
)

# ## Define current source

cfg["sources"].append(
    {
        "name": "U1_1V0",
        "reference_designator": "U1",
        "type": "current",
        "positive_terminal": {"net": "1V0"},
        "negative_terminal": {"net": "GND"},
    }
)

# ## Define SIwave DC IR analysis setup

cfg["setups"] = [
    {
        "name": "siwave_1",
        "type": "siwave_dc",
        "dc_slider_position": 1,
        "dc_ir_settings": {"export_dc_thermal_data": True},
    }
]

# ## Define Cutout

cfg["operations"] = {
    "cutout": {
        "signal_list": ["1V0"],
        "reference_list": ["GND"],
        "extent_type": "ConvexHull",
    }
}

# ## Write configuration into as json file

file_json = os.path.join(temp_folder.name, "edb_configuration.json")
with open(file_json, "w") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

# ## Import configuration into example layout

edbapp.configuration.load(config_file=file_json)

# Apply configuration to EDB.

edbapp.configuration.run()

# Save and close EDB.

edbapp.save()
edbapp.close()

# The configured EDB file is saved in a temp folder.

print(temp_folder.name)

# ## Load edb into HFSS 3D Layout.

h3d = Hfss3dLayout(edbapp.edbpath, version=AEDT_VERSION, non_graphical=NG_MODE, new_desktop=True)

# ## Analyze

h3d.analyze()

# ## Plot DC voltage

voltage = h3d.post.create_fieldplot_layers_nets(
    layers_nets=[
        ["1_Top", "1V0"],
    ],
    quantity="Voltage",
    setup="siwave_1",
)
file_path_image = os.path.join(temp_folder.name, "voltage.jpg")
voltage.export_image(
    full_path=file_path_image,
    width=1920,
    height=1080,
    orientation="isometric",
    display_wireframe=True,
    selections=None,
    show_region=True,
    show_axis=True,
    show_grid=True,
    show_ruler=True,
)

display(Image(filename=file_path_image))

# ## Plot power density

power_density = h3d.post.create_fieldplot_layers_nets(
    layers_nets=[
        ["1_Top", "1V0"],
    ],
    quantity="Power Density",
    setup="siwave_1",
)

file_path_image = os.path.join(temp_folder.name, "power_density.jpg")
power_density.export_image(
    full_path=file_path_image,
    width=1920,
    height=1080,
    orientation="isometric",
    display_wireframe=True,
    selections=None,
    show_region=True,
    show_axis=True,
    show_grid=True,
    show_ruler=True,
)

display(Image(filename=file_path_image))

# ## Shut Down Electronics Desktop

h3d.close_desktop()

# All project files are saved in the folder ``temp_file.dir``. If you've run this example as a Jupyter notebook you
# can retrieve those project files.

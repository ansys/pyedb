"""
EDB: fully parametrized CPWG design
-----------------------------------
This example shows how you can use HFSS 3D Layout to create a parametric design
for a CPWG (coplanar waveguide with ground).
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports. Importing the ``Hfss3dlayout`` object initializes it
# on version 2023 R2.

import os

import numpy as np

from pyedb.dotnet.edb import Edb
from pyedb.generic.general_methods import (
    generate_unique_folder_name,
    generate_unique_name,
)

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = False

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch EDB.

aedb_path = os.path.join(generate_unique_folder_name(), generate_unique_name("pcb") + ".aedb")
print(aedb_path)
edbapp = Edb(edbpath=aedb_path, edbversion="2023.2")

###############################################################################
# Define parameters
# ~~~~~~~~~~~~~~~~~
# Define parameters.

params = {
    "$ms_width": "0.4mm",
    "$ms_clearance": "0.3mm",
    "$ms_length": "20mm",
}
for par_name in params:
    edbapp.add_project_variable(par_name, params[par_name])

###############################################################################
# Create stackup
# ~~~~~~~~~~~~~~
# Create a symmetric stackup.

edbapp.stackup.create_symmetric_stackup(2)
edbapp.stackup.plot()

###############################################################################
# Draw planes
# ~~~~~~~~~~~
# Draw planes.

plane_lw_pt = ["0mm", "-3mm"]
plane_up_pt = ["$ms_length", "3mm"]

top_layer_obj = edbapp.modeler.create_rectangle(
    "TOP", net_name="gnd", lower_left_point=plane_lw_pt, upper_right_point=plane_up_pt
)
bot_layer_obj = edbapp.modeler.create_rectangle(
    "BOTTOM", net_name="gnd", lower_left_point=plane_lw_pt, upper_right_point=plane_up_pt
)
layer_dict = {"TOP": top_layer_obj, "BOTTOM": bot_layer_obj}

###############################################################################
# Draw trace
# ~~~~~~~~~~
# Draw a trace.

trace_path = [["0", "0"], ["$ms_length", "0"]]
edbapp.modeler.create_trace(
    trace_path, layer_name="TOP", width="$ms_width", net_name="sig", start_cap_style="Flat", end_cap_style="Flat"
)

###############################################################################
# Create trace to plane clearance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a trace to the plane clearance.

poly_void = edbapp.modeler.create_trace(
    trace_path,
    layer_name="TOP",
    net_name="gnd",
    width="{}+2*{}".format("$ms_width", "$ms_clearance"),
    start_cap_style="Flat",
    end_cap_style="Flat",
)
edbapp.modeler.add_void(layer_dict["TOP"], poly_void)

###############################################################################
# Create ground via padstack and place ground stitching vias
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a ground via padstack and place ground stitching vias.

edbapp.padstacks.create(
    padstackname="GVIA",
    holediam="0.3mm",
    paddiam="0.5mm",
)

yloc_u = "$ms_width/2+$ms_clearance+0.25mm"
yloc_l = "-$ms_width/2-$ms_clearance-0.25mm"

for i in np.arange(1, 20):
    edbapp.padstacks.place([str(i) + "mm", yloc_u], "GVIA", net_name="GND")
    edbapp.padstacks.place([str(i) + "mm", yloc_l], "GVIA", net_name="GND")

###############################################################################
# Save and close EDB
# ~~~~~~~~~~~~~~~~~~
# Save and close EDB.
edbapp.save_edb()
edbapp.close_edb()

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

"""
EDB: geometry creation
----------------------
This example shows how to
1, Create a layout layer stackup.
2, Create Padstack definition.
3, Place padstack instances at given location.
4, Create primitives, polygon and trace.
5, Create component from pins.
6, Create HFSS simulation setup and excitation ports.
"""
######################################################################
# Final expected project
# ~~~~~~~~~~~~~~~~~~~~~~
#
# .. image:: ../../_static/connector_example.png
#  :width: 600
#  :alt: Connector from Vias.
######################################################################

######################################################################
# Create connector component from pad-stack
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize an empty EDB layout object on version 2023 R2.
######################################################################

import os

from pyaedt import Hfss3dLayout

import pyedb
from pyedb.generic.general_methods import (
    generate_unique_folder_name,
    generate_unique_name,
)

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = False

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyedb.Edb` class, using EDB 2023 R2.

aedb_path = os.path.join(generate_unique_folder_name(), generate_unique_name("component_example") + ".aedb")
edb = pyedb.Edb(edbpath=aedb_path, edbversion="2023.2")
print("EDB is located at {}".format(aedb_path))

######################
# Initialize variables
# ~~~~~~~~~~~~~~~~~~~~

layout_count = 12
diel_material_name = "FR4_epoxy"
diel_thickness = "0.15mm"
cond_thickness_outer = "0.05mm"
cond_thickness_inner = "0.017mm"
soldermask_thickness = "0.05mm"
trace_in_layer = "TOP"
trace_out_layer = "L10"
trace_width = "200um"
connector_size = 2e-3
conectors_position = [[0, 0], [10e-3, 0]]

################
# Create stackup
# ~~~~~~~~~~~~~~
edb.stackup.create_symmetric_stackup(
    layer_count=layout_count,
    inner_layer_thickness=cond_thickness_inner,
    outer_layer_thickness=cond_thickness_outer,
    soldermask_thickness=soldermask_thickness,
    dielectric_thickness=diel_thickness,
    dielectric_material=diel_material_name,
)

######################
# Create ground planes
# ~~~~~~~~~~~~~~~~~~~~
#

ground_layers = [
    layer_name for layer_name in edb.stackup.signal_layers.keys() if layer_name not in [trace_in_layer, trace_out_layer]
]
plane_shape = edb.modeler.Shape("rectangle", pointA=["-3mm", "-3mm"], pointB=["13mm", "3mm"])
for i in ground_layers:
    edb.modeler.create_polygon(plane_shape, i, net_name="VSS")

######################
# Add design variables
# ~~~~~~~~~~~~~~~~~~~~

edb.add_design_variable("$via_hole_size", "0.3mm")
edb.add_design_variable("$antipaddiam", "0.7mm")
edb.add_design_variable("$paddiam", "0.5mm")
edb.add_design_variable("trace_in_width", "0.2mm", is_parameter=True)
edb.add_design_variable("trace_out_width", "0.1mm", is_parameter=True)

############################
# Create padstack definition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

edb.padstacks.create_padstack(
    padstackname="Via", holediam="$via_hole_size", antipaddiam="$antipaddiam", paddiam="$paddiam"
)

####################
# Create connector 1
# ~~~~~~~~~~~~~~~~~~

component1_pins = [
    edb.padstacks.place_padstack(
        conectors_position[0], "Via", net_name="VDD", fromlayer=trace_in_layer, tolayer=trace_out_layer
    ),
    edb.padstacks.place_padstack(
        [conectors_position[0][0] - connector_size / 2, conectors_position[0][1] - connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[0][0] + connector_size / 2, conectors_position[0][1] - connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[0][0] + connector_size / 2, conectors_position[0][1] + connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[0][0] - connector_size / 2, conectors_position[0][1] + connector_size / 2],
        "Via",
        net_name="VSS",
    ),
]

####################
# Create connector 2
# ~~~~~~~~~~~~~~~~~~

component2_pins = [
    edb.padstacks.place_padstack(
        conectors_position[-1], "Via", net_name="VDD", fromlayer=trace_in_layer, tolayer=trace_out_layer
    ),
    edb.padstacks.place_padstack(
        [conectors_position[1][0] - connector_size / 2, conectors_position[1][1] - connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[1][0] + connector_size / 2, conectors_position[1][1] - connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[1][0] + connector_size / 2, conectors_position[1][1] + connector_size / 2],
        "Via",
        net_name="VSS",
    ),
    edb.padstacks.place_padstack(
        [conectors_position[1][0] - connector_size / 2, conectors_position[1][1] + connector_size / 2],
        "Via",
        net_name="VSS",
    ),
]

####################
# Create layout pins
# ~~~~~~~~~~~~~~~~~~

for padstack_instance in list(edb.padstacks.instances.values()):
    padstack_instance.is_pin = True

############################
# Create component from pins
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

edb.components.create(component1_pins, "connector_1")
edb.components.create(component2_pins, "connector_2")

################################################################################
# Creating ports and adding simulation setup using SimulationConfiguration class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sim_setup = edb.new_simulation_configuration()
sim_setup.solver_type = sim_setup.SOLVER_TYPE.Hfss3dLayout
sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.01
sim_setup.batch_solve_settings.do_cutout_subdesign = False
sim_setup.batch_solve_settings.signal_nets = ["VDD"]
sim_setup.batch_solve_settings.components = ["connector_1", "connector_2"]
sim_setup.batch_solve_settings.power_nets = ["VSS"]
sim_setup.ac_settings.start_freq = "0GHz"
sim_setup.ac_settings.stop_freq = "5GHz"
sim_setup.ac_settings.step_freq = "1GHz"
edb.build_simulation_project(sim_setup)

###############################################################################
# Plot EDB
# ~~~~~~~~
# Plot EDB.

edb.nets.plot(None)

###########################
# Save EDB and open in AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~

edb.save_edb()
edb.close_edb()
h3d = Hfss3dLayout(
    specified_version="2023.2", projectname=aedb_path, non_graphical=non_graphical, new_desktop_session=True
)
h3d.release_desktop(False, False)

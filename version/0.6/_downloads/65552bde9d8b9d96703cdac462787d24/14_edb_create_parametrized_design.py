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
EDB: parameterized design
------------------------
This example shows how to
1, Create an HFSS simulation project using SimulationConfiguration class.
2, Create automatically parametrized design.
"""
######################################################################
# Final expected project
# ~~~~~~~~~~~~~~~~~~~~~~
#
# .. image:: ../../_static/parametrized_design.png
#  :width: 600
#  :alt: Fully automated parametrization.
######################################################################

######################################################################
# Create HFSS simulatio project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load an existing EDB folder.
######################################################################

from pyaedt import Hfss3dLayout

import pyedb
from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.misc.downloads import download_file

project_path = generate_unique_folder_name()
target_aedb = download_file("edb/ANSYS-HSD_V1.aedb", destination=project_path)
print("Project folder will be", target_aedb)

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = False

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyedb.Edb` class, using EDB 2023 R2.

aedt_version = "2023.2"
edb = pyedb.Edb(edbpath=target_aedb, edbversion=aedt_version)
print("EDB is located at {}".format(target_aedb))

########################################################################
# Create SimulationConfiguration object and define simulation parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

simulation_configuration = edb.new_simulation_configuration()
simulation_configuration.signal_nets = ["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N", "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N"]
simulation_configuration.power_nets = ["GND"]
simulation_configuration.components = ["X1", "U1"]
simulation_configuration.do_cutout_subdesign = True
simulation_configuration.start_freq = "OGHz"
simulation_configuration.stop_freq = "20GHz"
simulation_configuration.step_freq = "10MHz"

##########################
# Build simulation project
# ~~~~~~~~~~~~~~~~~~~~~~~~

edb.build_simulation_project(simulation_configuration)

#############################
# Generated design parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

edb.auto_parametrize_design(layers=True, materials=True, via_holes=True, pads=True, antipads=True, traces=True)

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

# Uncomment the following line to open the design in HFSS 3D Layout
hfss = Hfss3dLayout(
    projectname=target_aedb, specified_version=aedt_version, non_graphical=non_graphical, new_desktop_session=True
)
hfss.release_desktop()

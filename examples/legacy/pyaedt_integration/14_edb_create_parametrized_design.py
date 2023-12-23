"""
EDB: parameterized design
------------------------
This example shows how to
1, Create an HFSS simulation project using SimulationConfiguration class.
2, Create automatically parametrized design.
"""
######################################################################
#
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
from pyedb.legacy.downloads import download_file

project_path = generate_unique_folder_name()
target_aedb = download_file("edb/ANSYS-HSD_V1.aedb", destination=project_path)
print("Project folder will be", target_aedb)

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
edb.save_edb()
edb.close_edb()

######################
# Open project in AEDT
# ~~~~~~~~~~~~~~~~~~~~

hfss = Hfss3dLayout(projectname=target_aedb, specified_version=aedt_version)
hfss.release_desktop(False, False)

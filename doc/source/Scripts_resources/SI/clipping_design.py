import pyaedt
from pyaedt import Edb, Hfss3dLayout

# Ansys release version
desktop_version = "2023.2"

# download and copy the layout file from examples
temp_folder = pyaedt.generate_unique_folder_name()
targetfile = pyaedt.downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

# loading EDB
edbapp = Edb(edbpath=targetfile, edbversion=desktop_version)

# selecting signal nets to evaluate the extent for clipping the layout
signal_nets = ["DDR4_DQ0", "DDR4_DQ1", "DDR4_DQ2", "DDR4_DQ3", "DDR4_DQ4", "DDR4_DQ5", "DDR4_DQ6", "DDR4_DQ7"]
# at least one reference net must be inclulded. Reference nets are included in the design but clipped.
reference_nets = ["GND"]
# defining the expansion factor.
# The value gives the distance for evaluating the cutout extent
expansion = 0.01  # 1cm in this case
# processing cutout
edbapp.cutout(signal_list=signal_nets, reference_list=reference_nets, expansion_size=expansion)
# save and close project
edbapp.save_edb()
edbapp.close_edb()
# opening resulting in AEDT to visualize the resulting project.
hfss = Hfss3dLayout(projectname=targetfile, specified_version=desktop_version)
# After opening AEDT with PyAEDT, if you want to be able to close manually the project you have to release
# AEDT from PyAEDT.
hfss.release_desktop(close_desktop=False, close_projects=False)

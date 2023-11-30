from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.legacy.edb import EdbLegacy
from pyedb.misc.downloads import download_file

# Ansys release version
desktop_version = "2023.2"

# download and copy the layout file from examples
temp_folder = generate_unique_folder_name()
targetfile = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

# loading EDB
edbapp = EdbLegacy(edbpath=targetfile, edbversion=desktop_version)

# Some layout statistics
stats = edbapp.get_statistics()

# When edb is loaded, we can access all layout information
nets = edbapp.nets

# net list
nets.netlist

# power nets
nets.power

# Getting components from specific net
nets.power["GND"].components

# Getting pins from components
edbapp.components["U9"].pins

# Getting pins from components connected to given net
u9_gnd_pins = [pin for pin in list(edbapp.components["U9"].pins.values()) if pin.net_name == "GND"]

# Plotting layout in matplotlib
edbapp.nets.plot(None)

# plotting specific net
edbapp.nets.plot("GND")

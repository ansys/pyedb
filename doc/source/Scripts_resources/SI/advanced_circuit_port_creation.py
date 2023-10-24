import pyaedt
from pyaedt import Edb, Hfss3dLayout
from pyaedt.generic.constants import SourceType

# Ansys release version
desktop_version = "2023.2"

# download and copy the layout file from examples
temp_folder = pyaedt.generate_unique_folder_name()
targetfile = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_folder)

# loading EDB
edbapp = Edb(edbpath=targetfile, edbversion=desktop_version)

signal_nets = ["DDR4_DQ0", "DDR4_DQ1", "DDR4_DQ2", "DDR4_DQ3", "DDR4_DQ4", "DDR4_DQ5", "DDR4_DQ6", "DDR4_DQ7"]
reference_nets = ["GND"]

# processing cutout
edbapp.cutout(signal_list=signal_nets, reference_list=reference_nets, expansion_size=0.01)

# creating ports on specific component pins
component = edbapp.components["U1"]
for net in signal_nets:
    pins = [pin for pin in list(component.pins.values()) if pin.net_name == net]
    for pin in pins:
        ref_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=3, component_only=True)
        edbapp.components.create_port_on_pins(refdes="U1", pins=pin, reference_pins=ref_pins)

# save and close project
edbapp.save_edb()
edbapp.close_edb()
hfss = Hfss3dLayout(projectname=targetfile, specified_version=desktop_version)
hfss.release_desktop(close_desktop=False, close_projects=False)

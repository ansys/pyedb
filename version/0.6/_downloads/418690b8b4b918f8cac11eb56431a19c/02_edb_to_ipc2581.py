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
EDB: IPC2581 export
-------------------
This example shows how you can use PyEDB to export an IPC2581 file.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes importing a section.

import os

import pyedb
from pyedb.generic.general_methods import (
    generate_unique_folder_name,
    generate_unique_name,
)
from pyedb.misc.downloads import download_file

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.


temp_folder = generate_unique_folder_name()
targetfile = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)


ipc2581_file = os.path.join(temp_folder, "Ansys_Hsd.xml")

print(targetfile)


###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyedb.Edb` class, using EDB 2023 R2 and SI units.

edb = pyedb.Edb(edbpath=targetfile, edbversion="2023.2")


###############################################################################
# Parametrize net
# ~~~~~~~~~~~~~~~
# Parametrize a net.

edb.modeler.parametrize_trace_width("A0_N", parameter_name=generate_unique_name("Par"), variable_value="0.4321mm")

###############################################################################
# Cutout
# ~~~~~~
# Create a cutout.
signal_list = []
for net in edb.nets.netlist:
    if "PCIe" in net:
        signal_list.append(net)
power_list = ["GND"]
edb.cutout(
    signal_list=signal_list,
    reference_list=power_list,
    extent_type="ConvexHull",
    expansion_size=0.002,
    use_round_corner=False,
    number_of_threads=4,
    remove_single_pin_components=True,
    use_pyaedt_extent_computing=True,
    extent_defeature=0,
)

###############################################################################
# Plot cutout
# ~~~~~~~~~~~
# Plot cutout before exporting to IPC2581 file.

edb.nets.plot(None, None, color_by_net=True)

###############################################################################
# Create IPC2581 file
# ~~~~~~~~~~~~~~~~~~~
# Create the IPC2581 file.

edb.export_to_ipc2581(ipc2581_file, "inch")
print("IPC2581 File has been saved to {}".format(ipc2581_file))

###############################################################################
# Close EDB
# ~~~~~~~~~
# Close EDB.

edb.close_edb()

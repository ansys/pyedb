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
EDB: plot nets with Matplotlib
------------------------------
This example shows how you can use the ``Edb`` class to plot a net or a layout.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes importing a section.

import pyedb
from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.misc.downloads import download_file

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDT file and copy it into the temporary folder.

temp_folder = generate_unique_folder_name()

targetfolder = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)


###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyedb.Edb` class, using EDB 2023 R2 and SI units.

edb = pyedb.Edb(edbpath=targetfolder, edbversion="2023.2")

###############################################################################
# Plot custom set of nets colored by layer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot a custom set of nets colored by layer (default).

edb.nets.plot("AVCC_1V3")

###############################################################################
# Plot custom set of nets colored by nets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot a custom set of nets colored by nets.

edb.nets.plot(["GND", "GND_DP", "AVCC_1V3"], color_by_net=True)

###############################################################################
# Plot all nets on a layer colored by nets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot all nets on a layer colored by nets

edb.nets.plot(None, ["1_Top"], color_by_net=True, plot_components_on_top=True)

###############################################################################
# Plot stackup and some padstack definition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot all nets on a layer colored by nets

edb.stackup.plot(scale_elevation=False, plot_definitions=["c100hn140", "c35"])

###############################################################################
# Close EDB
# ~~~~~~~~~
# Close EDB.

edb.close_edb()

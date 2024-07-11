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
EDB: Differential wave port
---------------------------------
This example shows how to create a simple design with differential pairs and assign wave port on them.
"""


###############################################################################
# Import EDB library
# ~~~~~~~~~~~~~~~~~~
from pyedb import Edb
from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.misc.downloads import download_file

temp_folder = generate_unique_folder_name()
targetfolder = download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

edb_path = r"D:\Data\pyedb\infineon\Ansys_4Layers_TAS_RF_PCB.aedb"
# edb_path = r"D:\Data\pyedb\infineon\via_clustering\test\test_board_extract.aedb"
edb = Edb(edbpath=edb_path, edbversion=edb_version)
edb.padstacks.merge_via_along_lines(net_name="gnd", distance_threshold=0.1e-3, minimum_via_number=4)
edb.save_as(r"D:\Temp\test.aedb")
edb.close()

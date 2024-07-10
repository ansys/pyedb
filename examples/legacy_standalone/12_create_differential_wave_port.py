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

###############################################################################
# Create an empty EDB
# ~~~~~~~~~~~~~~~~~~~
edb = Edb()

###############################################################################
# Define a layer stackup
# ~~~~~~~~~~~~~~~~~~~~~~
edb.stackup.add_layer("GND", "Gap")
edb.stackup.add_layer("Substrat", "GND", layer_type="dielectric", thickness="0.2mm", material="Duroid (tm)")
edb.stackup.add_layer("TOP", "Substrat")

###############################################################################
# Define parameters
# ~~~~~~~~~~~~~~~~~
trace_length = 10e-3
trace_width = 200e-6
design_width = 10e-3
trace_gap = 1e-3

###############################################################################
# Create ground plane
# ~~~~~~~~~~~~~~~~~~~
gnd_plane = edb.modeler.create_polygon(
    main_shape=[
        [-design_width / 2, 0.0],
        [-design_width / 2, trace_length],
        [design_width / 2, trace_length],
        [design_width / 2, 0.0],
    ],
    layer_name="GND",
    net_name="gnd",
)

###############################################################################
# Create differential traces
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
trace1 = edb.modeler.create_trace(
    path_list=[[-trace_gap / 2, 0.0], [-trace_gap / 2, trace_length]],
    layer_name="TOP",
    width=trace_width,
    net_name="signal1",
    start_cap_style="Flat",
    end_cap_style="Flat",
)
trace2 = edb.modeler.create_trace(
    path_list=[[trace_gap / 2, 0.0], [trace_gap / 2, trace_length]],
    layer_name="TOP",
    width=trace_width,
    net_name="signal2",
    start_cap_style="Flat",
    end_cap_style="Flat",
)

###############################################################################
# Create wave ports on traces end
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

edb.hfss.create_bundle_wave_port(
    primitives_id=[trace1.id, trace2.id], points_on_edge=[[-trace_gap / 2, 0.0], [trace_gap / 2, 0.0]]
)
edb.hfss.create_bundle_wave_port(
    primitives_id=[trace1.id, trace2.id], points_on_edge=[[-trace_gap / 2, trace_length], [trace_gap / 2, trace_length]]
)

###############################################################################
# Save and closed EDB
# ~~~~~~~~~~~~~~~~~~~
edb.save()
edb.close()

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

from pyedb.generic.general_methods import ET
from pyedb.ipc2581.ecad.cad_data.layer import Layer
from pyedb.ipc2581.ecad.cad_data.stackup import Stackup
from pyedb.ipc2581.ecad.cad_data.step import Step


class CadData(object):
    def __init__(self, ecad, edb, units, ipc):
        self.design_name = ecad.design_name
        self._pedb = edb
        self._ipc = ipc
        self.units = units
        self._layers = []
        self.stackup = Stackup()
        self.cad_data_step = Step(self, edb, self.units, self._ipc)

    @property
    def layers(self):
        return self._layers

    def add_layer(
        self, layer_name="", layer_function="", layer_side="internal", polarity="positive"
    ):  # pragma no cover
        layer = Layer()
        layer.name = layer_name
        layer.layer_function = layer_function
        layer.layer_side = layer_side
        layer.layer_polarity = polarity
        self.layers.append(layer)

    def write_xml(self, ecad):  # pragma no cover
        self.design_name = self._pedb.cell_names[0]
        cad_data = ET.SubElement(ecad, "CadData")
        for layer in self.layers:
            layer.write_xml(cad_data)
        self.stackup.write_xml(cad_data)
        self.cad_data_step.write_xml(cad_data)

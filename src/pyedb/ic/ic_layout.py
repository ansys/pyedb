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

import pya
from pyedb.ic.gds_data import ICLayoutData, ICLayerData
import os


class ICLayout:
    def __init__(self, gds_file, layermap=None):
        self.editable = True
        self._klayout = pya.Layout(self.editable)
        self._layermap = layermap
        self.db = ICLayoutData(klayout=self._klayout, layers=[])
        if layermap:
            if os.path.splitext(layermap)[-1] == ".layermap":
                self._read_layer_map()
        if gds_file:
            self._klayout.read(gds_file)
            self._read_layer_info()
        self._top_cell = self._klayout.top_cell()

    def _read_layer_info(self):
        for layer_index in range(self._klayout.layers()):
            layer_info = self._klayout.get_info(layer_index)
            if not layer_info.layer == -1:
                if [layer for layer in self.db.layers if layer.index == str(layer_info.layer)]:
                    if not [lay for lay in self.db.layers if lay.data_type == str(layer_info.datatype)]:
                        _layer = ICLayerData(klayout=self._klayout, name=layer_info.name, index=layer_info.layer,
                        data_type = layer_info.datatype, purpose="drawing")
                        self.db.layers.append(_layer)

    def _read_layer_map(self):
        with open(self._layermap, mode='r') as file:
            lines = file.readlines()
            header = ["layer_name", "layer_purpose", "layer_stream_number", "data_type"]
            for line in lines[1:]:
                if line.strip():
                    data = line.replace("\t", " ").split()
                    if len(data) == len(header):
                        layer = ICLayerData(klayout=self._klayout, name=data[0], purpose=data[1],
                                            index=data[2], data_type=data[3])
                        self.db.layers.append(layer)

    def save(self, file_name=None):
        if file_name:
            self._klayout.write(filename=file_name)
            return True
        return False

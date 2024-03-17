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

import klayout.db as kdb
from pyedb.ic.gds_data import ICLayoutData, ICLayerData


class ICLayout:
    def __init__(self, gds_file):
        self.editable = True
        self._klayout = kdb.Layout(self.editable)
        self.db = ICLayoutData([])
        if gds_file:
            self._klayout.read(gds_file)
            self._read_layer_info()
        self._top_cell = self._klayout.top_cell()

    def _read_layer_info(self):
        for layer_index in range(self._klayout.layers()):
            layer_info = self._klayout.get_info(layer_index)
            if not layer_info.layer == -1:
                layer = ICLayerData(name=layer_info.name, index=layer_info.layer, data_type=layer_info.datatype)
                self.db.layers.append(layer)

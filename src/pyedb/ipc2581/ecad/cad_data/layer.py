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


class Layer(object):
    def __init__(self):
        self.name = ""
        self._layer_function = ""
        self._layer_side = ""
        self._layer_polarity = ""
        self.sequence = 0

    @property
    def layer_function(self):
        return self._layer_function

    @layer_function.setter
    def layer_function(self, value):  # pragma no cover
        self._layer_function = value

    @property
    def layer_side(self):
        return self._layer_side

    @layer_side.setter
    def layer_side(self, value):  # pragma no cover
        self._layer_side = value

    @property
    def layer_polarity(self):
        return self._layer_polarity

    @layer_polarity.setter
    def layer_polarity(self, value):  # pragma no cover
        self._layer_polarity = value

    def write_xml(self, cad_data):  # pragma no cover
        layer = ET.SubElement(cad_data, "Layer")
        layer.set("name", self.name)
        layer.set("layerFunction", self.layer_function)
        layer.set("side", self.layer_side)
        layer.set("polarity", self.layer_polarity)

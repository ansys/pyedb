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


class StackupLayer(object):
    def __init__(self):
        self.layer_name = ""
        self.thickness = 0
        self.tol_minus = 0
        self.tol_plus = 0
        self.sequence = ""
        self.spec_ref = "SPEC_{}".format(self.layer_name)

    def write_xml(self, stackup_group):  # pragma no cover
        stackup_layer = ET.SubElement(stackup_group, "StackupLayer")
        stackup_layer.set("layerOrGroupRef", self.layer_name)
        stackup_layer.set("thickness", str(self.thickness))
        stackup_layer.set("tolPlus", str(self.tol_plus))
        stackup_layer.set("tolMinus", str(self.tol_minus))
        stackup_layer.set("sequence", self.sequence)
        spec_ref = ET.SubElement(stackup_layer, "SpecRef")
        spec_ref.set("id", self.layer_name)

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


class PadstackPadDef(object):
    """Class describing an IPC2581 padstack definition."""

    def __init__(self):
        self.layer_ref = ""
        self.pad_use = "REGULAR"
        self.x = 0.0
        self.y = 0.0
        self.primitive_ref = "CIRCLE_DEFAULT"

    def write_xml(self, padstack_def):  # pragma no cover
        pad_def = ET.SubElement(padstack_def, "PadstackPadDef")
        pad_def.set("layerRef", self.layer_ref)
        pad_def.set("padUse", self.pad_use)
        location = ET.SubElement(pad_def, "Location")
        location.set("x", str(self.x))
        location.set("y", str(self.y))
        standard_primitive = ET.SubElement(pad_def, "StandardPrimitiveRef")
        standard_primitive.set("id", self.primitive_ref)


class PadUse(object):
    (Regular, Antipad, Thermal) = range(0, 3)

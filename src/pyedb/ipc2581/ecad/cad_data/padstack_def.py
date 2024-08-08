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
from pyedb.ipc2581.ecad.cad_data.padstack_hole_def import PadstackHoleDef
from pyedb.ipc2581.ecad.cad_data.padstack_pad_def import PadstackPadDef


class PadstackDef(object):
    """Class describing an IPC2581 padstack definition."""

    def __init__(self):
        self.name = ""
        self.padstack_hole_def = PadstackHoleDef()
        self._padstack_pad_def = []

    @property
    def padstack_pad_def(self):
        return self._padstack_pad_def

    @padstack_pad_def.setter
    def padstack_pad_def(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([pad for pad in value if isinstance(pad, PadstackPadDef)]) == len(value):
                self._padstack_pad_def = value

    def add_padstack_pad_def(self, layer="", pad_use="REGULAR", x="0", y="0", primitive_ref=""):  # pragma no cover
        pad = PadstackPadDef()
        pad.layer_ref = layer
        pad.pad_use = pad_use
        pad.x = x
        pad.y = y
        pad.primitive_ref = primitive_ref
        self.padstack_pad_def.append(pad)

    def write_xml(self, step):  # pragma no cover
        padstack_def = ET.SubElement(step, "PadStackDef")
        padstack_def.set("name", self.name)
        self.padstack_hole_def.write_xml(padstack_def)
        for pad in self.padstack_pad_def:
            pad.write_xml(padstack_def)

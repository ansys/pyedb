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
from pyedb.ipc2581.bom.characteristics import Characteristics
from pyedb.ipc2581.bom.refdes import RefDes


class BomItem(object):
    def __init__(self):
        self.part_name = ""
        self.quantity = "1"
        self.pin_count = "1"
        self.category = "ELECTRICAL"
        self.refdes_list = []
        self.charactistics = Characteristics()

    def write_xml(self, bom):  # pragma no cover
        bom_item = ET.SubElement(bom, "BomItem")
        bom_item.set("OEMDesignNumberRef", self.part_name)
        bom_item.set("quantity", str(self.quantity))
        bom_item.set("pinCount", str(self.pin_count))
        bom_item.set("category", self.category)
        bom_item.set("category", self.category)
        for refdes in self.refdes_list:
            refdes.write_xml(bom_item)
        self.charactistics.write_xml(bom_item)

    def add_refdes(self, component_name=None, package_def=None, populate=True, placement_layer=""):  # pragma no cover
        refdes = RefDes()
        refdes.name = component_name
        refdes.populate = str(populate)
        refdes.packaged_def = package_def
        refdes.placement_layer = placement_layer
        self.refdes_list.append(refdes)

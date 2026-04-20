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


class Characteristics(object):
    def __init__(self):
        self.category = "ELECTRICAL"
        self.device_type = ""
        self.component_class = ""
        self.value = ""

    def write_xml(self, bom_item):  # pragma no cover
        characteristic = ET.SubElement(bom_item, "Characteristics")
        characteristic.set("category", self.category)
        component_type = ET.SubElement(characteristic, "Textual")
        component_type.set("definitionSource", "ANSYS")
        component_type.set("textualCharacteristicName", "DEVICE_TYPE")
        component_type.set("textualCharacteristicValue", "{}_{}".format(self.device_type, self.value))
        component_class = ET.SubElement(characteristic, "Textual")
        component_class.set("definitionSource", "ANSYS")
        component_class.set("textualCharacteristicName", "COMP_CLASS")
        component_class.set("textualCharacteristicValue", "{}".format(self.component_class))
        component_value = ET.SubElement(characteristic, "Textual")
        component_value.set("definitionSource", "ANSYS")
        component_value.set("textualCharacteristicName", "VALUE")
        component_value.set("textualCharacteristicValue", "{}".format(self.value))
        component_parent_type = ET.SubElement(characteristic, "Textual")
        component_parent_type.set("definitionSource", "ANSYS")
        component_parent_type.set("textualCharacteristicName", "PARENT_PPT_PART")
        component_parent_type.set("textualCharacteristicValue", "{}_{}".format(self.device_type, self.value))
        component_parent = ET.SubElement(characteristic, "Textual")
        component_parent.set("definitionSource", "ANSYS")
        component_parent.set("textualCharacteristicName", "PARENT_PPT")
        component_parent.set("textualCharacteristicValue", "{}".format(self.device_type))
        component_parent2 = ET.SubElement(characteristic, "Textual")
        component_parent2.set("definitionSource", "ANSYS")
        component_parent2.set("textualCharacteristicName", "PARENT_PART_TYPE")
        component_parent2.set("textualCharacteristicValue", "{}".format(self.device_type))

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


class Component(object):
    """Contains IPC2581 component information."""

    def __init__(self):
        self.refdes = ""
        self.package_ref = ""
        self.layer_ref = ""
        self.part = ""
        self.mount_type = "SMT"
        self.stand_off = "0.0"
        self.height = "0.0"
        self.location = ["0.0", "0.0"]
        self.rotation = "0.0"
        self.type = Type().Rlc
        self.value = ""

    def write_xml(self, step):  # pragma no cover
        component = ET.SubElement(step, "Component")
        component.set("refDes", self.refdes)
        component.set("packageRef", self.package_ref)
        component.set("layerRef", self.layer_ref)
        component.set("part", self.package_ref)
        component.set("mountType", self.mount_type)
        component.set("standoff", self.stand_off)
        component.set("height", self.height)
        non_standard_attribute = ET.SubElement(component, "NonstandardAttribute")
        non_standard_attribute.set("name", "VALUE")
        non_standard_attribute.set("value", str(self.value))
        non_standard_attribute.set("type", "STRING")
        xform = ET.SubElement(component, "Xform")
        xform.set("rotation", str(self.rotation))
        location = ET.SubElement(component, "Location")
        location.set("x", str(self.location[0]))
        location.set("y", str(self.location[1]))


class Type(object):
    (Rlc, Discrete) = range(0, 2)

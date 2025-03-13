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


class PadstackInstance(object):
    """Class describing an IPC2581 padstack instance."""

    def __init__(self):
        self.isvia = False
        self.padstack_def = ""
        self.standard_primimtive_ref = ""
        self.pin = ""
        self.x = ""
        self.y = ""
        self.rotation = ""
        self.refdes = ""
        self.net = ""
        self.mirror = False

    def write_xml(self, net_root):  # pragma no cover
        if self.isvia:
            net_root.set("testPoint", "false")
            net_root.set("plate", "true")
            net_root.set("padUsage", "VIA")
            non_standard_attribute = ET.SubElement(net_root, "NonstandardAttribute")
            non_standard_attribute.set("name", "PADSTACK_USAGE")
            non_standard_attribute.set("value", "Through")
            non_standard_attribute.set("type", "STRING")
            pad = ET.SubElement(net_root, "Pad")
            pad.set("padstackDefRef", self.padstack_def)
            xform = ET.SubElement(pad, "Xform")
            xform.set("rotation", "0")
            xform.set("mirror", str(self.mirror).lower())
            location = ET.SubElement(pad, "Location")
            location.set("x", str(self.x))
            location.set("y", str(self.y))
            primitive_ref = ET.SubElement(pad, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primimtive_ref)
            if self.refdes:
                pin_ref = ET.SubElement(pad, "PinRef")
                pin_ref.set("pin", self.pin)
                pin_ref.set("componentRef", self.refdes)
        else:
            net_root.set("testPoint", "false")
            net_root.set("plate", "true")
            non_standard_attribute = ET.SubElement(net_root, "NonstandardAttribute")
            non_standard_attribute.set("name", "PADSTACK_USAGE")
            non_standard_attribute.set("value", "Through")
            non_standard_attribute.set("type", "STRING")
            pad = ET.SubElement(net_root, "Pad")
            pad.set("padstackDefRef", self.padstack_def)
            xform = ET.SubElement(pad, "Xform")
            xform.set("rotation", str(self.rotation))
            xform.set("mirror", str(self.mirror).lower())
            location = ET.SubElement(pad, "Location")
            location.set("x", str(self.x))
            location.set("y", str(self.y))
            primitive_ref = ET.SubElement(pad, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primimtive_ref)
            if self.refdes:
                pin_ref = ET.SubElement(pad, "PinRef")
                pin_ref.set("pin", self.pin)
                pin_ref.set("componentRef", self.refdes)

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


class Pin(object):
    """Class describing an ICP2581 component pin."""

    def __init__(self):
        self.number = ""
        self.electrical_type = "ELECTRICAL"
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.primitive_def = ""
        self.is_via = False

    def write_xml(self, package):  # pragma no cover
        pin = ET.SubElement(package, "Pin")
        pin.set("number", str(self.number))
        pin.set("type", "THRU")
        pin.set("electricalType", self.electrical_type)
        xform = ET.SubElement(pin, "Xform")
        xform.set("rotation", str(self.rotation))
        location = ET.SubElement(pin, "Location")
        location.set("x", str(self.x))
        location.set("y", str(self.y))
        primitive_ref = ET.SubElement(pin, "StandardPrimitiveRef")
        primitive_ref.set("id", self.primitive_def)


class Type(object):
    (Thru, Surface) = range(0, 2)

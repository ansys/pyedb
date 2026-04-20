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


class StandardCircle(object):
    def __init__(self):
        self.diameter = ""
        self.fill_id = ""

    def write_xml(self, entry_standard):  # pragma no cover
        standard_circle = ET.SubElement(entry_standard, "Circle")
        standard_circle.set("diameter", self.diameter)
        fill = ET.SubElement(standard_circle, "FillDescRef")
        fill.set("id", self.fill_id)


class RectangleDotNet(object):
    def __init__(self):
        self.width = ""
        self.height = ""
        self.fill_id = ""

    def write_xml(self, entry_standard):  # pragma no cover
        standard_rectanlgle = ET.SubElement(entry_standard, "RectCenter")
        standard_rectanlgle.set("width", self.width)
        standard_rectanlgle.set("height", self.height)
        fill = ET.SubElement(standard_rectanlgle, "FillDescRef")
        fill.set("id", self.fill_id)


class Oval(object):
    pass


class Type(object):
    (Circle, Rectangle) = range(0, 2)


class StandardGeometriesDictionary(object):
    def __init__(self, content):
        self.units = content.units
        self.standard_circ_dict = {}
        self.standard_rect_dict = {}
        self.standard_oval_dict = {}

    def write_xml(self, content_section=None):  # pragma no cover
        standard_dict = ET.SubElement(content_section, "DictionaryStandard")
        standard_dict.set("units", self.units)
        for standard_name, circle_val in self.standard_circ_dict.items():
            if circle_val:
                entry_standard = ET.SubElement(standard_dict, "EntryStandard")
                entry_standard.set("id", standard_name)
                circle = ET.SubElement(entry_standard, "Circle")
                circle.set("diameter", str(circle_val))
                fill_descref = ET.SubElement(circle, "FillDescRef")
                fill_descref.set("id", "SOLID_FILL")
        for standard_name, rect_val in self.standard_rect_dict.items():
            if rect_val:
                entry_standard = ET.SubElement(standard_dict, "EntryStandard")
                entry_standard.set("id", standard_name)
                rec_center = ET.SubElement(entry_standard, "RectCenter")
                rec_center.set("width", str(rect_val[0]))
                rec_center.set("height", str(rect_val[1]))
                fill_descref = ET.SubElement(rec_center, "FillDescRef")
                fill_descref.set("id", "SOLID_FILL")

    def add_circle(self, diameter):  # pragma no cover
        circle = StandardCircle()
        circle.diameter = diameter
        circle.fill_id = "SOLID_FILL"
        entry_key = "CIRCLE_{}".format(diameter[0])
        if not entry_key in self.standard_circ_dict:
            self.standard_circ_dict[entry_key] = str(diameter[0])

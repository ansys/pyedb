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
from pyedb.ipc2581.ecad.cad_data.polygon import Polygon


class AssemblyDrawing(object):
    """Class describing an IPC2581 assembly drawing."""

    def __init__(self, ipc):
        self._ipc = ipc
        self.polygon = Polygon(self._ipc)
        self.line_ref = ""

    def write_xml(self, package):  # pragma no cover
        assembly_drawing = ET.SubElement(package, "AssemblyDrawing")
        outline = ET.SubElement(assembly_drawing, "Outline")
        polygon = ET.SubElement(outline, "Polygon")
        polygon_begin = ET.SubElement(polygon, "PolyBegin")
        if self.polygon.poly_steps:
            polygon_begin.set("x", str(self.polygon.poly_steps[0].x))
            polygon_begin.set("y", str(self.polygon.poly_steps[0].y))
            for poly_step in self.polygon.poly_steps[1:]:
                polygon_segment = ET.SubElement(polygon, "PolyStepSegment")
                polygon_segment.set("x", str(poly_step.x))
                polygon_segment.set("y", str(poly_step.y))
        line_desc_ref = ET.SubElement(outline, "LineDescRef")
        line_desc_ref.set("id", self.line_ref)

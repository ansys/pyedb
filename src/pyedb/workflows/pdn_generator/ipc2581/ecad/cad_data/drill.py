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


class Drill(object):
    """Class describing an ICP2581 drill feature."""

    def __init__(self):
        self.net = ""
        self.component = ""
        self.geometry = "VIA"
        self.hole_name = ""
        self.diameter = ""
        self.plating_status = "VIA"
        self.plus_tol = "0.0"
        self.min_tol = "0.0"
        self.x = "0.0"
        self.y = "0.0"

    def write_xml(self, net):  # pragma no cover
        net.set("geometry", "VIA")
        color_ref = ET.SubElement(net, "ColorRef")
        color_ref.set("id", "")
        hole = ET.SubElement(net, "Hole")
        hole.set("name", self.hole_name)
        hole.set("diameter", str(self.diameter))
        hole.set("platingStatus", "VIA")
        hole.set("plusTol", str(self.plus_tol))
        hole.set("minusTol", str(self.min_tol))
        hole.set("x", str(self.x))
        hole.set("y", str(self.y))

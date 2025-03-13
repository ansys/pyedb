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


class PadstackHoleDef(object):
    """Class describing an ICP2581 padstack hole definition."""

    def __init__(self):
        self.name = ""
        self.diameter = 0
        self.plating_status = "PLATED"
        self.plus_tol = 0
        self.minus_tol = 0
        self.x = 0
        self.y = 0

    def write_xml(self, padstackdef):  # pragma no cover
        padstack_hole = ET.SubElement(padstackdef, "PadstackHoleDef")
        padstack_hole.set("name", self.name)
        padstack_hole.set("diameter", str(self.diameter))
        padstack_hole.set("platingStatus", str(self.plating_status))
        padstack_hole.set("plusTol", str(self.plus_tol))
        padstack_hole.set("minusTol", str(self.minus_tol))
        padstack_hole.set("x", str(self.x))
        padstack_hole.set("y", str(self.y))

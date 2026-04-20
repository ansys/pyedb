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
from pyedb.ipc2581.ecad.cad_data.stackup_group import StackupGroup


class Stackup(object):
    def __init__(self):
        self.name = "PRIMARY"
        self.total_thickness = 0.0
        self.tol_plus = 0.0
        self.tol_min = 0.0
        self.where_measured = "METAL"
        self._stackup_group = StackupGroup()

    @property
    def stackup_group(self):
        return self._stackup_group

    @stackup_group.setter
    def stackup_group(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([stack_grp for stack_grp in value if isinstance(stack_grp, StackupGroup)]):
                self._stackup_group = value

    def write_xml(self, cad_data):  # pragma no cover
        stackup = ET.SubElement(cad_data, "Stackup")
        stackup.set("name", self.name)
        stackup.set("overallThickness", str(self.total_thickness))
        stackup.set("tolPlus", str(self.tol_plus))
        stackup.set("tolMinus", str(self.tol_min))
        stackup.set("whereMeasured", self.where_measured)
        self.stackup_group.write_xml(stackup)

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


class LogicalNet(object):
    """Class describing an IPC2581 logical net."""

    def __init__(self):
        self.name = ""
        self.pin_ref = []

    def write_xml(self, step):  # pragma no cover
        if step:
            logical_net = ET.SubElement(step, "LogicalNet")
            logical_net.set("name", self.name)
            for pin in self.pin_ref:
                pin.write_xml(logical_net)

    def get_pin_ref_def(self):  # pragma no cover
        return PinRef()


class PinRef(object):
    """Class describing an IPC2581 logical net."""

    def __init__(self):
        self.pin = ""
        self.component_ref = ""

    def write_xml(self, logical_net):  # pragma no cover
        pin_ref = ET.SubElement(logical_net, "PinRef")
        pin_ref.set("pin", self.pin)
        pin_ref.set("componentRef", self.component_ref)

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


class CfgPinGroup:
    """Manage configuration pin group class."""

    def __init__(self, pdata, pingroup_dict):
        self._pedb = pdata._pedb
        self._pingroup_dict = pingroup_dict
        self.name = self._pingroup_dict.get("name", "")
        self.reference_designator = self._pingroup_dict.get("reference_designator", "")
        self.pins = self._pingroup_dict.get("pins", [])
        self.net = self._pingroup_dict.get("net", [])

    def apply(self):
        """Apply pin group on layout."""
        if self.pins:
            if not self._pedb.siwave.create_pin_group(self.reference_designator, list(self.pins), self.name):
                self._pedb.logger.error(f"Failed to create pin group on pins {self.pins}")
                return False
            self._pedb.logger.info(f"Pin group {self.name} created.")
            return True
        elif self.net:
            if self.reference_designator in self._pedb.components.instances:
                comp = self._pedb.components.instances[self.reference_designator]
            else:
                self._pedb.logger.error("Component not found for creating pin group.")
                return False
            pins = [p for p, obj in comp.pins.items() if obj.net_name in self.net]
            if not self._pedb.siwave.create_pin_group(self.reference_designator, pins, self.name):
                self._pedb.logger.error(f"Failed to create pin group {self.name}")
                return False
            else:
                self._pedb.logger.info(f"Pin group {self.name} created.")
                return True
        else:
            self._pedb.logger.error(f"No net and pins defined for defining pin group {self.name}")
            return False

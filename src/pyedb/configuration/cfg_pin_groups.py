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

from pyedb.configuration.cfg_common import CfgBase


class CfgPinGroups:
    """Manage configuration pin group class."""

    def __init__(self, pedb, pingroup_data):
        self._pedb = pedb
        self.pin_groups = [CfgPinGroup(self._pedb, **pg) for pg in pingroup_data]

    def apply(self):
        for pg in self.pin_groups:
            pg.create()

    def get_data_from_db(self):
        self.pin_groups = []
        for name, pg in self._pedb.siwave.pin_groups.items():
            pins = [p.aedt_name for p in pg.pins.values()]
            cfg_pg = CfgPinGroup(
                self._pedb,
                name=name,
                reference_designator=None,
                pins=pins,
            )
            self.pin_groups.append(cfg_pg)
        return self.export_properties()

    def export_properties(self):
        pin_groups = []
        for pg in self.pin_groups:
            pin_groups.append(pg.export_properties())
        return pin_groups


class CfgPinGroup(CfgBase):
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.reference_designator = kwargs.get("reference_designator")
        self.pins = kwargs.get("pins")
        self.net = kwargs.get("net")

    def create(self):
        """Apply pin group on layout."""
        if self.pins:
            if self.reference_designator is None:
                self._pedb.modeler.create_pin_group(self.name, pins_by_aedt_name=self.pins)
            else:
                self._pedb.siwave.create_pin_group(self.reference_designator, list(self.pins), self.name)
        elif self.net:
            if self.reference_designator in self._pedb.components.instances:
                comp = self._pedb.components.instances[self.reference_designator]
            else:
                raise f"Component not found for creating pin group {self.name}."
            pins = [p for p, obj in comp.pins.items() if obj.net_name in self.net]
            if not self._pedb.siwave.create_pin_group(self.reference_designator, pins, self.name):
                self._pedb.logger.error(f"Failed to create pin group {self.name}")
        else:
            self._pedb.logger.error(f"No net and pins defined for defining pin group {self.name}")

    def export_properties(self):
        if self.pins:
            return {
                "name": self.name,
                "reference_designator": self.reference_designator,
                "pins": self.pins,
            }
        else:
            return {
                "name": self.name,
                "reference_designator": self.reference_designator,
                "net": self.net,
            }

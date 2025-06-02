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

    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent._pedb

        def set_pingroup_to_edb(self):
            for pg in self.parent.pin_groups:
                pg.create()

        def get_data_from_edb(self):
            self.parent.pin_groups = []
            layout_pin_groups = self._pedb.siwave.pin_groups
            for pg_name, pg_obj in layout_pin_groups.items():
                if self._pedb.grpc:
                    pins = list(pg_obj.pins.values())
                    refdes = pins[0].component.name
                    cfg_pg = CfgPinGroup(
                        self._pedb,
                        name=pg_name,
                        reference_designator=refdes,
                        pins=[pin.component_pin for pin in pins],
                    )
                    self.parent.pin_groups.append(cfg_pg)
            return self.parent.export_properties()

    class DotNet(Grpc):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(parent)

        def get_data_from_edb(self):
            self.parent.pin_groups = []
            layout_pin_groups = self._pedb.siwave.pin_groups
            for pg_name, pg_obj in layout_pin_groups.items():
                pins = list(pg_obj.pins.keys())
                refdes = list(pg_obj.pins.values())[0].component.name
                cfg_pg = CfgPinGroup(
                    self._pedb,
                    name=pg_name,
                    reference_designator=refdes,
                    pins=pins,
                )
                self.parent.pin_groups.append(cfg_pg)
            return self.parent.export_properties()

    def __init__(self, pedb, pingroup_data):
        self._pedb = pedb
        if self._pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        self.pin_groups = [CfgPinGroup(self._pedb, **pg) for pg in pingroup_data]

    def apply(self):
        self.api.set_pingroup_to_edb()

    def get_data_from_db(self):
        return self.api.get_data_from_edb()

    def export_properties(self):
        pin_groups = []
        for pg in self.pin_groups:
            pin_groups.append(pg.export_properties())
        return pin_groups


class CfgPinGroup(CfgBase):
    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent._pedb

        def create(self):
            if self.parent.pins:
                pins = self.parent.pins if isinstance(self.parent.pins, list) else [self.parent.pins]
                self._pedb.siwave.create_pin_group(self.parent.reference_designator, pins, self.parent.name)
            elif self.parent.net:
                nets = self.parent.net if isinstance(self.parent.net, list) else [self.parent.net]
                comp = self._pedb.components.instances[self.parent.reference_designator]
                pins = [p for p, obj in comp.pins.items() if obj.net_name in nets]
                if not self._pedb.siwave.create_pin_group(self.parent.reference_designator, pins, self.parent.name):
                    raise RuntimeError(f"Failed to create pin group {self.parent.name}")
            else:
                raise RuntimeError(f"No net and pins defined for defining pin group {self.parent.name}")

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        if self._pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        self.name = kwargs["name"]
        self.reference_designator = kwargs.get("reference_designator")
        self.pins = kwargs.get("pins")
        self.net = kwargs.get("net")

    def create(self):
        """Apply pin group on layout."""
        self.api.create()

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

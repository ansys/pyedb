# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Build named pin-group configuration entries."""

from pyedb.configuration.cfg_common import CfgBase


class CfgPinGroups:
    """Manage configuration pin group class."""

    def set_pingroup_to_edb(self):
        """Write all configured pin groups into the open EDB design."""
        for pg in self.pin_groups:
            pg.create()

    def get_data_from_edb(self):
        """Read existing pin groups from the open EDB design.

        Returns
        -------
        list of dict
            Serialized pin-group payloads.
        """
        self.pin_groups = []
        if self._pedb is None:
            return self.export_properties()
        layout_pin_groups = self._pedb.siwave.pin_groups
        for pg_name, pg_obj in layout_pin_groups.items():
            pins = list(pg_obj.pins.keys())
            if len(pins) == 0:  # pragma: no cover
                continue
            refdes = list(pg_obj.pins.values())[0].component.name
            cfg_pg = CfgPinGroup(
                self._pedb,
                name=pg_name,
                reference_designator=refdes,
                pins=pins,
            )
            self.pin_groups.append(cfg_pg)
        return self.export_properties()

    def __init__(self, pedb=None, pingroup_data=None):
        self._pedb = pedb
        self.pin_groups = [CfgPinGroup(self._pedb, **pg) for pg in (pingroup_data or [])]

    def add(self, name, reference_designator, pins=None, net=None):
        """Add a pin group to this configuration.

        Provide either *pins* (explicit list) **or** *net* (all pins on that
        net), not both.

        Parameters
        ----------
        name : str
            Unique pin-group name, e.g. ``"pg_VDD"``.
        reference_designator : str
            Reference designator of the owning component, e.g. ``"U1"``.
        pins : list of str, optional
            Explicit list of pin names, e.g. ``["A1", "A2", "B1"]``.
        net : str, optional
            Net name.  All component pins on this net are included.

        Returns
        -------
        CfgPinGroup
            The newly created pin-group object.

        Examples
        --------
        >>> cfg.pin_groups.add("pg_VDD", "U1", net="VDD")
        >>> cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])
        """
        pg = CfgPinGroup(self._pedb, name=name, reference_designator=reference_designator, pins=pins, net=net)
        self.pin_groups.append(pg)
        return pg

    def apply(self):
        """Write all configured pin groups into the open EDB design."""
        self.set_pingroup_to_edb()

    def get_data_from_db(self):
        """Read pin groups from the EDB design (alias for :meth:`get_data_from_edb`).

        Returns
        -------
        list of dict
        """
        return self.get_data_from_edb()

    def export_properties(self):
        """Serialize all pin groups to a list of plain dictionaries.

        Returns
        -------
        list of dict
        """
        pin_groups = []
        for pg in self.pin_groups:
            pin_groups.append(pg.export_properties())
        return pin_groups

    def to_list(self):
        """Serialize all configured pin groups."""
        return self.export_properties()


class CfgPinGroup(CfgBase):
    """Represent one pin-group definition bound to a component."""

    def create(self):
        """Write this pin group into the open EDB design.

        Raises
        ------
        RuntimeError
            If no pins and no net are configured, or if EDB creation fails.
        """
        if self._pedb is None:
            return self.export_properties()
        if self.pins:
            pins = self.pins if isinstance(self.pins, list) else [self.pins]
            self._pedb.siwave.create_pin_group(self.reference_designator, pins, self.name)
        elif self.net:
            nets = self.net if isinstance(self.net, list) else [self.net]
            comp = self._pedb.components.instances[self.reference_designator]
            pins = [p for p, obj in comp.pins.items() if obj.net_name in nets]
            if not self._pedb.siwave.create_pin_group(self.reference_designator, pins, self.name):
                raise RuntimeError(f"Failed to create pin group {self.name}")
        else:
            raise RuntimeError(f"No net and pins defined for defining pin group {self.name}")

    def __init__(self, pedb=None, name=None, reference_designator=None, pins=None, net=None, **kwargs):
        if name is None and kwargs.get("name") is not None:
            name = kwargs.get("name")
        if reference_designator is None and kwargs.get("reference_designator") is not None:
            reference_designator = kwargs.get("reference_designator")
        if pins is None and "pins" in kwargs:
            pins = kwargs.get("pins")
        if net is None and "net" in kwargs:
            net = kwargs.get("net")
        self._pedb = pedb
        self.name = name
        self.reference_designator = reference_designator
        self.pins = pins
        self.net = net

    def to_dict(self) -> dict:
        """Serialize the pin-group definition."""
        return self.export_properties()

    def export_properties(self):
        """Serialize this pin group to a plain dictionary.

        Returns
        -------
        dict
            Dictionary with ``name``, ``reference_designator``, and either
            ``pins`` or ``net``.
        """
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

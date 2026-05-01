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

    def get(self, name: str) -> "CfgPinGroup":
        """Return the :class:`CfgPinGroup` for an existing pin group.

        If the group has already been registered via :meth:`add` the cached
        entry is returned.  Otherwise the group is looked up in the live EDB
        session and a new entry is created from its current pin membership.

        Parameters
        ----------
        name : str
            Pin-group name, e.g. ``"pg_VDD"``.

        Returns
        -------
        CfgPinGroup
            Pin-group builder pre-populated with the current pin list.

        Raises
        ------
        KeyError
            If no EDB session is attached or the pin group does not exist.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> pg = cfg.pin_groups.get("pg_VDD")
        >>> print(pg.pins)
        """
        for pg in self.pin_groups:
            if pg.name == name:
                return pg
        if self._pedb is None:
            raise KeyError(
                f"Pin group '{name}' not found in the builder. "
                "Use edb.configuration.create_config_builder() to auto-load from EDB."
            )
        layout_pgs = self._pedb.siwave.pin_groups
        if name not in layout_pgs:
            raise KeyError(f"Pin group '{name}' not found in the EDB layout.")
        pg_obj = layout_pgs[name]
        pins = list(pg_obj.pins.keys())
        refdes = list(pg_obj.pins.values())[0].component.name if pins else None
        pg = CfgPinGroup(self._pedb, name=name, reference_designator=refdes, pins=pins)
        self.pin_groups.append(pg)
        return pg

    def add(self, reference_designator, name=None, pins=None, nets=None):
        """Add one or more pin groups to this configuration.

        Provide either *pins* (explicit list) **or** *nets* (one or more net
        names), not both.

        When *nets* is a single string, one pin group is created using *name*.
        When *nets* is a list of strings, one pin group is created **per net**
        and the auto-generated name follows the convention
        ``"Pingroup_{reference_designator}.{net_name}"``.  The explicit *name*
        argument is ignored in the multi-net case.

        When an EDB session is attached the component pins are resolved
        immediately; otherwise resolution is deferred to :meth:`apply`.

        Parameters
        ----------
        reference_designator : str
            Reference designator of the owning component, e.g. ``"U1"``.
        name : str, optional
            Unique pin-group name.  When omitted the name is auto-generated:
            ``"Pingroup_{reference_designator}.{net_name}"`` for a single net
            and ``"Pingroup_{reference_designator}"`` for explicit pins.
            In the multi-net case the name is always auto-generated.
        pins : list of str, optional
            Explicit list of pin names, e.g. ``["A1", "A2", "B1"]``.
        nets : str or list of str, optional
            Net name(s).  All component pins on each net are collected into a
            dedicated pin group.

        Returns
        -------
        CfgPinGroup or list of CfgPinGroup
            The newly created pin-group object(s).  A single object is
            returned when *nets* is a string or *pins* is used; a list is
            returned when *nets* is a list with more than one entry.

        Examples
        --------
        >>> cfg.pin_groups.add("pg_VDD", "U1", nets="VDD")
        >>> cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])
        >>> cfg.pin_groups.add("", "U1", nets=["VDD", "GND"])
        """
        if nets is not None and pins is None:
            net_list = nets if isinstance(nets, list) else [nets]
            # Auto-generate name for single net when not provided
            if name is None and len(net_list) == 1:
                name = f"Pingroup_{reference_designator}.{net_list[0]}"
            if len(net_list) > 1:
                # Multi-net: create one pin group per net with auto-generated names
                created = []
                for net_name in net_list:
                    pg_name = f"Pingroup_{reference_designator}.{net_name}"
                    resolved_pins = None
                    if self._pedb is not None:
                        comp = self._pedb.components.instances.get(reference_designator)
                        if comp is None:
                            raise KeyError(f"Component '{reference_designator}' not found in the EDB layout.")
                        resolved_pins = [p for p, obj in comp.pins.items() if obj.net_name == net_name]
                        if not resolved_pins:
                            raise ValueError(
                                f"No pins found for net '{net_name}' on component '{reference_designator}'."
                            )
                        if len(resolved_pins) <= 1:
                            self._pedb.logger.warning(
                                f"Skipping pin group '{pg_name}': only {len(resolved_pins)} pin(s) found "
                                f"for net '{net_name}' on component '{reference_designator}'. "
                                "A pin group requires at least 2 pins."
                            )
                            continue
                        pg = CfgPinGroup(
                            self._pedb,
                            name=pg_name,
                            reference_designator=reference_designator,
                            pins=resolved_pins,
                            net=net_name,
                        )
                    else:
                        pg = CfgPinGroup(
                            self._pedb, name=pg_name, reference_designator=reference_designator, net=net_name
                        )
                    self.pin_groups.append(pg)
                    created.append(pg)
                return created
            else:
                # Single net
                net_name = net_list[0]
                if self._pedb is not None:
                    comp = self._pedb.components.instances.get(reference_designator)
                    if comp is None:
                        raise KeyError(f"Component '{reference_designator}' not found in the EDB layout.")
                    pins = [p for p, obj in comp.pins.items() if obj.net_name == net_name]
                    if not pins:
                        raise ValueError(f"No pins found for net '{net_name}' on component '{reference_designator}'.")
                    if len(pins) <= 1:
                        self._pedb.logger.warning(
                            f"Skipping pin group '{name}': only {len(pins)} pin(s) found "
                            f"for net '{net_name}' on component '{reference_designator}'. "
                            "A pin group requires at least 2 pins."
                        )
                        return None
                    pg = CfgPinGroup(
                        self._pedb, name=name, reference_designator=reference_designator, pins=pins, net=net_name
                    )
                else:
                    pg = CfgPinGroup(self._pedb, name=name, reference_designator=reference_designator, net=net_name)
                self.pin_groups.append(pg)
                return pg

        if name is None:
            name = f"Pingroup_{reference_designator}"
        pg = CfgPinGroup(self._pedb, name=name, reference_designator=reference_designator, pins=pins)
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
        data = {
            "name": self.name,
            "reference_designator": self.reference_designator,
        }
        if self.pins:
            data["pins"] = self.pins
        if self.net:
            data["net"] = self.net
        return data

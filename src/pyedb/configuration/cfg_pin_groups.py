# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from typing import Any, Optional

from pydantic import Field, PrivateAttr

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgPinGroups:
    """Manage configuration pin group class."""

    def set_pin_groups_to_edb(self):
        """Write all configured pin groups into the open EDB design."""
        for pg in self.pin_groups:
            pg.create()

    set_pingroup_to_edb = set_pin_groups_to_edb

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
                pedb=self._pedb,
                name=pg_name,
                reference_designator=refdes,
                pins=pins,
            )
            self.pin_groups.append(cfg_pg)
        return self.export_properties()

    def __init__(self, pedb=None, pin_group_data=None, pingroup_data=None):
        self._pedb = pedb
        pin_group_data = pin_group_data if pin_group_data is not None else pingroup_data
        self.pin_groups = [CfgPinGroup(pedb=self._pedb, **pg) for pg in (pin_group_data or [])]

    def get(self, name: str) -> "CfgPinGroup":
        """Return the :class:`CfgPinGroup` for an existing pin group.

        If the group has already been registered via :meth:`add` the cached
        entry is returned, otherwise the group is looked up in the live EDB
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
        cfg = edb.configuration.create_config_builder()
        pg = cfg.pin_groups.get("pg_VDD")
        print(pg.pins)
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
        pg = CfgPinGroup(pedb=self._pedb, name=name, reference_designator=refdes, pins=pins)
        self.pin_groups.append(pg)
        return pg

    def _resolve_pins(self, reference_designator: str, net_name: str, group_name: str) -> list | None:
        """Return pins for *net_name* on *reference_designator*, or ``None`` to skip.

        Raises ``KeyError`` if the component is not found, ``ValueError`` if no
        pins exist on the net.
        """
        comp = self._pedb.components.instances.get(reference_designator)
        if comp is None:
            raise KeyError(f"Component '{reference_designator}' not found in the EDB layout.")
        pins = [p for p, obj in comp.pins.items() if obj.net_name == net_name]
        if not pins:
            raise ValueError(f"No pins found for net '{net_name}' on component '{reference_designator}'.")
        return pins

    def add(self, name=None, reference_designator=None, pins=None, nets=None, net=None):
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
        cfg.pin_groups.add("pg_VDD", "U1", nets="VDD")
        cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])
        cfg.pin_groups.add("", "U1", nets=["VDD", "GND"])
        """
        if nets is None and net is not None and pins is None:
            nets = net
        if nets is not None and pins is None:
            net_list = nets if isinstance(nets, list) else [nets]
            # Auto-generate name for single net when not provided
            if name is None and len(net_list) == 1:
                name = f"Pingroup_{reference_designator}.{net_list[0]}"

            if len(net_list) > 1:
                # Multi-net: create one pin group per net
                created = []
                for net_name in net_list:
                    pg_name = f"Pingroup_{reference_designator}.{net_name}"
                    if self._pedb is not None:
                        resolved_pins = self._resolve_pins(reference_designator, net_name, pg_name)
                        if resolved_pins is None:
                            continue
                        pg = CfgPinGroup(
                            pedb=self._pedb,
                            name=pg_name,
                            reference_designator=reference_designator,
                            pins=resolved_pins,
                            net=net_name,
                        )
                    else:
                        pg = CfgPinGroup(
                            pedb=self._pedb, name=pg_name, reference_designator=reference_designator, net=net_name
                        )
                    self.pin_groups.append(pg)
                    created.append(pg)
                return created
            else:
                # Single net
                net_name = net_list[0]
                if self._pedb is not None:
                    resolved_pins = self._resolve_pins(reference_designator, net_name, name)
                    if resolved_pins is None:
                        return None
                    pg = CfgPinGroup(
                        pedb=self._pedb,
                        name=name,
                        reference_designator=reference_designator,
                        pins=resolved_pins,
                        net=net_name,
                    )
                else:
                    pg = CfgPinGroup(
                        pedb=self._pedb, name=name, reference_designator=reference_designator, net=net_name
                    )
                self.pin_groups.append(pg)
                return pg

        if name is None:
            name = f"Pingroup_{reference_designator}"
        pg = CfgPinGroup(pedb=self._pedb, name=name, reference_designator=reference_designator, pins=pins)
        self.pin_groups.append(pg)
        return pg

    def apply(self):
        """Write all configured pin groups into the open EDB design."""
        self.set_pin_groups_to_edb()

    def get_data_from_db(self):
        """Read pin groups from the EDB design."""
        return self.get_data_from_edb()

    def export_properties(self):
        """Serialize all pin groups to plain dictionaries."""
        return [pg.export_properties() for pg in self.pin_groups]


class CfgPinGroup(CfgBaseModel):
    """Represent one pin-group definition bound to a component."""

    model_config = {"populate_by_name": True, "extra": "ignore", "arbitrary_types_allowed": True}

    name: Optional[str] = None
    reference_designator: Optional[str] = None
    pins: Optional[Any] = None
    net: Optional[Any] = None
    pedb: Optional[Any] = Field(default=None, exclude=True, repr=False)

    # Runtime-only EDB session reference
    # Set as private, not serialized
    _pedb: Any = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Transfer the ``pedb`` field value to the private ``_pedb`` attribute."""
        if self.pedb is not None:
            self._pedb = self.pedb

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

    def export_properties(self):
        """Serialize this pin group to a plain dictionary."""
        return self.model_dump(exclude_none=True, exclude={"pedb"})

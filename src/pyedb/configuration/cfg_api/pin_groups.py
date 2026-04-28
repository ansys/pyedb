# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Pin groups builder API.

Data model: :class:`~pyedb.configuration.cfg_pin_groups.CfgPinGroup`.
Note: ``CfgPinGroup`` requires a live ``pedb`` instance for ``.create()``,

so we build plain dicts that match the schema expected by ``CfgPinGroups``.
"""

from __future__ import annotations

from typing import List, Optional, Union



class PinGroupConfig:
    """Fluent builder for a single pin group.

    Parameters
    ----------
    name : str
    reference_designator : str
    pins : list of str, optional
        Explicit pin names.
    net : str or list of str, optional
        Net name(s) – all component pins on those nets are included.
    """

    def __init__(
        self,
        name: str,
        reference_designator: str,
        pins: Optional[List[str]] = None,
        net: Optional[Union[str, List[str]]] = None,
    ):
        self.name = name
        self.reference_designator = reference_designator
        self.pins = pins
        self.net = net

    def to_dict(self) -> dict:
        data: dict = {"name": self.name, "reference_designator": self.reference_designator}
        if self.pins:
            data["pins"] = self.pins
        elif self.net:
            data["net"] = self.net
        return data



class PinGroupsConfig:
    """Fluent builder for the ``pin_groups`` configuration list."""

    def __init__(self):
        self._pin_groups: List[PinGroupConfig] = []

    def add(
        self,
        name: str,
        reference_designator: str,
        pins: Optional[List[str]] = None,
        net: Optional[Union[str, List[str]]] = None,
    ) -> PinGroupConfig:
        """Add a pin group.

        Parameters
        ----------
        name : str
        reference_designator : str
        pins : list of str, optional
        net : str or list of str, optional

        Returns
        -------
        PinGroupConfig
        """
        pg = PinGroupConfig(name=name, reference_designator=reference_designator, pins=pins, net=net)
        self._pin_groups.append(pg)
        return pg

    def to_list(self) -> List[dict]:
        return [pg.to_dict() for pg in self._pin_groups]

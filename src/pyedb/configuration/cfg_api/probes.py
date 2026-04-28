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

"""Build voltage-probe configuration entries.

The classes in this module create serializable probe definitions for the
``probes`` configuration list.
"""

from __future__ import annotations

from typing import List, Optional, Union


class ProbeConfig:
    """Represent a single voltage probe entry."""

    def __init__(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        reference_designator: Optional[str] = None,
    ):
        """Initialize a probe configuration.

        Parameters
        ----------
        name : str
        positive_terminal : dict
        negative_terminal : dict
        reference_designator : str, optional
        """
        self.name = name
        self.type = "probe"
        self.positive_terminal = positive_terminal
        self.negative_terminal = negative_terminal
        self.reference_designator = reference_designator

    def to_dict(self) -> dict:
        """Serialize the probe definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``probes`` configuration
            list.

        """
        data = {
            "name": self.name,
            "type": self.type,
            "positive_terminal": self.positive_terminal,
            "negative_terminal": self.negative_terminal,
        }
        if self.reference_designator:
            data["reference_designator"] = self.reference_designator
        return data


class ProbesConfig:
    """Collect voltage probe definitions for serialization."""

    def __init__(self):
        self._probes: List[ProbeConfig] = []

    def add(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        reference_designator: Optional[str] = None,
    ) -> ProbeConfig:
        """Add a voltage probe.

        Parameters
        ----------
        name : str
            Probe name.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict
            Negative terminal specifier.
        reference_designator : str, optional
            Component reference designator used to disambiguate pin or net
            terminal specifiers.

        Returns
        -------
        ProbeConfig
            Newly created probe entry.
        """
        probe = ProbeConfig(
            name=name,
            positive_terminal=positive_terminal,
            negative_terminal=negative_terminal,
            reference_designator=reference_designator,
        )
        self._probes.append(probe)
        return probe

    def to_list(self) -> List[dict]:
        """Serialize all configured probes.

        Returns
        -------
        list[dict]
            Probe definitions in insertion order.
        """
        return [p.to_dict() for p in self._probes]

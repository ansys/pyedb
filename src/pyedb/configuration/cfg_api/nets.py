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

"""Build the ``nets`` configuration section.

This module provides a simple fluent API for classifying nets into signal and
power-ground groups before serializing them into the structure expected by
:class:`pyedb.configuration.cfg_nets.CfgNets`.

"""

from __future__ import annotations

from typing import List


class NetsConfig:
    """Fluent builder for the ``nets`` configuration section.

    The dict produced by :meth:`to_dict` is consumed by
    :class:`~pyedb.configuration.cfg_nets.CfgNets`.

    Examples
    --------
    >>> cfg.nets.add_signal_nets(["SIG1", "SIG2"])
    >>> cfg.nets.add_power_ground_nets(["VDD", "GND"])
    >>> cfg.nets.add_reference_nets(["GND"])

    """

    def __init__(self):
        """Initialize the nets configuration."""
        self._signal_nets: List[str] = []
        self._power_ground_nets: List[str] = []
        self._reference_nets: List[str] = []

    @property
    def signal_nets(self) -> List[str]:
        """List of configured signal net names."""
        return list(self._signal_nets)

    @property
    def power_ground_nets(self) -> List[str]:
        """List of configured power/ground net names."""
        return list(self._power_ground_nets)

    @property
    def reference_nets(self) -> List[str]:
        """List of configured reference net names."""
        return list(self._reference_nets)

    def add_signal_nets(self, nets: List[str]):
        """Append signal net names.

        Parameters
        ----------
        nets : list of str
            Net names to classify as signal nets.
        """
        self._signal_nets.extend(nets)

    def add_power_ground_nets(self, nets: List[str]):
        """Append power/ground net names.

        Parameters
        ----------
        nets : list of str
            Net names to classify as power or ground nets.
        """
        self._power_ground_nets.extend(nets)

    def add_reference_nets(self, nets: List[str]):
        """Append reference (ground) net names.

        These are the same nets passed to ``add_cutout(reference_nets=…)``.
        Storing them here allows the cutout configuration to reference
        ``cfg.nets.reference_nets`` directly without duplicating the list.

        Parameters
        ----------
        nets : list of str
            Net names to use as reference / ground nets.
        """
        self._reference_nets.extend(nets)

    def to_dict(self) -> dict:
        """Serialize the configured net classification lists.

        Returns
        -------
        dict
            Dictionary containing ``signal_nets`` and/or
            ``power_ground_nets`` when those lists are non-empty.
            ``reference_nets`` is **not** serialized here; it is passed
            directly to the ``operations.cutout`` configuration.
        """
        data: dict = {}
        if self._signal_nets:
            data["signal_nets"] = list(self._signal_nets)
        if self._power_ground_nets:
            data["power_ground_nets"] = list(self._power_ground_nets)
        return data

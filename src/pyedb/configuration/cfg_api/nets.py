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

"""Net classification builder API.

Data model: :class:`~pyedb.configuration.cfg_nets.CfgNets`.
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
    """

    def __init__(self):
        self._signal_nets: List[str] = []
        self._power_ground_nets: List[str] = []

    def add_signal_nets(self, nets: List[str]):
        """Append signal net names.

        Parameters
        ----------
        nets : list of str
        """
        self._signal_nets.extend(nets)

    def add_power_ground_nets(self, nets: List[str]):
        """Append power/ground net names.

        Parameters
        ----------
        nets : list of str
        """
        self._power_ground_nets.extend(nets)

    def to_dict(self) -> dict:
        """Return dict matching ``CfgNets`` expected keys."""
        data: dict = {}
        if self._signal_nets:
            data["signal_nets"] = list(self._signal_nets)
        if self._power_ground_nets:
            data["power_ground_nets"] = list(self._power_ground_nets)
        return data


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
"""Build the ``nets`` configuration section.

This module provides a fluent API for classifying nets into signal,
power-ground, and reference groups before serializing them into the structure
expected by the configuration runtime.
"""


class CfgNets:
    """Fluent builder for the ``nets`` configuration section."""

    @property
    def power_ground_nets(self):
        """list of str: Power and ground net names (alias for ``power_nets``)."""
        return self.power_nets

    @power_ground_nets.setter
    def power_ground_nets(self, value):
        """Set power/ground net names.

        Parameters
        ----------
        value : list of str
            Replacement list of net names.
        """
        self.power_nets = list(value or [])

    def set_parameter_to_edb(self):
        """Write signal / power-ground net classifications into the open EDB design."""
        if self._pedb is None:
            return
        for signal_net in self.signal_nets:
            if signal_net in self._pedb.nets:
                self._pedb.nets.nets[signal_net].is_power_ground = False
        for power_net in self.power_nets:
            if power_net in self._pedb.nets:
                self._pedb.nets.nets[power_net].is_power_ground = True

    def get_parameter_from_edb(self):
        """Get net information."""
        if self._pedb is None:
            return self.to_dict()
        self.signal_nets = []
        self.power_nets = []
        for net in self._pedb.nets.signal:
            self.signal_nets.append(net)
        for net in self._pedb.nets.power:
            self.power_nets.append(net)
        data = {"signal_nets": self.signal_nets, "power_ground_nets": self.power_nets}
        return data

    def __init__(self, pedb=None, signal_nets=None, power_nets=None, reference_nets=None):
        """Initialize the nets configuration."""
        self._pedb = pedb
        self.signal_nets = list(signal_nets or [])
        self.power_nets = list(power_nets or [])
        self.reference_nets = list(reference_nets or [])

    def add_signal_nets(self, nets):
        """Append signal net names."""
        self.signal_nets.extend(nets)

    def add_power_ground_nets(self, nets):
        """Append power/ground net names."""
        self.power_nets.extend(nets)

    def add_reference_nets(self, nets):
        """Append reference-net names used by cutout helpers."""
        self.reference_nets.extend(nets)

    def to_dict(self) -> dict:
        """Serialize the configured net classification lists."""
        data = {}
        if self.signal_nets:
            data["signal_nets"] = list(self.signal_nets)
        if self.power_nets:
            data["power_ground_nets"] = list(self.power_nets)
        return data

    def apply(self):
        """Apply net configuration on the layout."""
        self.set_parameter_to_edb()

    def get_data_from_db(self):
        """Get net information."""
        return self.get_parameter_from_edb()

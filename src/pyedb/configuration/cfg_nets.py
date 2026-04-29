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

    def get(self, net_name: str) -> dict:
        """Return classification and EDB metadata for an existing net.

        Looks up *net_name* in the live EDB session and returns a plain
        dictionary describing whether the net is a signal or power/ground net,
        plus its current ``is_power_ground`` flag.

        If the net is not yet classified in the builder it is also added to the
        appropriate list (``signal_nets`` or ``power_nets``) so that it will be
        included when the configuration is applied.

        Parameters
        ----------
        net_name : str
            Net name to look up, e.g. ``"GND"`` or ``"CLK"``.

        Returns
        -------
        dict
            ``{"name": str, "is_power_ground": bool, "classification": str}``
            where ``classification`` is ``"signal"`` or ``"power_ground"``.

        Raises
        ------
        KeyError
            If no EDB session is attached or the net does not exist.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> info = cfg.nets.get("GND")
        >>> print(info["classification"])   # 'power_ground'
        """
        if self._pedb is None:
            raise KeyError(
                "No EDB session is attached. "
                "Use edb.configuration.create_config_builder() to get a session-aware builder."
            )
        edb_nets = self._pedb.nets.nets
        if net_name not in edb_nets:
            raise KeyError(f"Net '{net_name}' not found in the EDB layout.")
        net_obj = edb_nets[net_name]
        is_pg = net_obj.is_power_ground
        classification = "power_ground" if is_pg else "signal"
        # Ensure it is registered in the appropriate list
        if is_pg:
            if net_name not in self.power_nets:
                self.power_nets.append(net_name)
        else:
            if net_name not in self.signal_nets:
                self.signal_nets.append(net_name)
        return {"name": net_name, "is_power_ground": is_pg, "classification": classification}

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

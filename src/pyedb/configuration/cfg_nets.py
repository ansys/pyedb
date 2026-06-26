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

"""Build the ``nets`` configuration section."""


class CfgNets:
    """Fluent builder for the ``nets`` configuration section."""

    class CfgNet:
        """Represents a single net in the EDB layout with live session access.

        Parameters
        ----------
        pedb : object
            Live EDB session.
        net_name : str
            Name of the net in the EDB layout.
        """

        def __init__(self, pedb, net_name: str):
            self._pedb = pedb
            self.name = net_name

        @property
        def _net_obj(self):
            return self._pedb.nets.nets[self.name]

        @property
        def is_power_ground(self) -> bool:
            """bool: Whether this net is classified as power/ground."""
            return self._net_obj.is_power_ground

        @is_power_ground.setter
        def is_power_ground(self, value: bool):
            self._net_obj.is_power_ground = value

        @property
        def classification(self) -> str:
            """str: ``"power_ground"`` or ``"signal"`` based on the current EDB flag."""
            return "power_ground" if self.is_power_ground else "signal"

        def __repr__(self) -> str:
            return f"CfgNet(name={self.name!r}, classification={self.classification!r})"

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

    def set_parameters_to_edb(self):
        """Write signal / power-ground net classifications into the open EDB design."""
        if self._pedb is None:
            return
        nets = self._pedb.nets.nets
        for net in self.signal_nets:
            if net in self._pedb.nets:
                nets[net].is_power_ground = False
        for net in self.power_nets:
            if net in self._pedb.nets:
                nets[net].is_power_ground = True

    def get_parameters_from_edb(self):
        """Read net classifications from EDB."""
        if self._pedb is None:
            return {"signal_nets": list(self.signal_nets), "power_ground_nets": list(self.power_nets)}
        self.signal_nets = list(self._pedb.nets.signal)
        self.power_nets = list(self._pedb.nets.power)
        return {"signal_nets": self.signal_nets, "power_ground_nets": self.power_nets}

    def to_dict(self):
        """Serialize the in-memory net classification lists.

        Unlike :meth:`get_parameters_from_edb`, this method does **not** query
        the live EDB session and therefore preserves any pending changes made
        via :meth:`add_power_ground_nets` / :meth:`add_signal_nets` before
        :meth:`set_parameters_to_edb` has been called.

        Returns
        -------
        dict
            Dictionary with ``"signal_nets"`` and ``"power_ground_nets"`` keys.
        """
        return {"signal_nets": list(self.signal_nets), "power_ground_nets": list(self.power_nets)}

    def __init__(self, pedb=None, signal_nets=None, power_nets=None, reference_nets=None):
        """Initialize the net configuration."""
        self._pedb = pedb
        self.signal_nets = list(signal_nets or [])
        self.power_nets = list(power_nets or [])
        self.reference_nets = list(reference_nets or [])

    def get(self, net_name: str):
        """Return a :class:`CfgNet` object for an existing net in the EDB layout.

        Parameters
        ----------
        net_name : str
            Net name to look up, e.g. ``"GND"`` or ``"CLK"``.

        Returns
        -------
        CfgNet or False
            A :class:`CfgNet` instance bound to the live EDB session, or
            ``False`` if the net does not exist in EDB.

        Raises
        ------
        KeyError
            If no EDB session is attached.

        Examples
        --------
        cfg = edb.configuration.create_config_builder()
        net = cfg.nets.get("GND")
        if net:
            print(net.classification)  # 'power_ground'
        """
        if self._pedb is None:
            raise KeyError(
                "No EDB session is attached. "
                "Use edb.configuration.create_config_builder() to get a session-aware builder."
            )
        if net_name not in self._pedb.nets.nets:
            self._pedb.logger.error(f"Net '{net_name}' not found in the EDB layout.")
            return False
        return CfgNets.CfgNet(self._pedb, net_name)

    @staticmethod
    def _to_name_list(nets):
        """Normalise *nets* to a flat list of net name strings."""
        if isinstance(nets, (str, CfgNets.CfgNet)):
            nets = [nets]
        return [n.name if isinstance(n, CfgNets.CfgNet) else n for n in nets]

    def _add_to_list(self, target: list, others: list[list], nets):
        """Add *nets* to *target*, removing them from each list in *others*."""
        for name in self._to_name_list(nets):
            for other in others:
                if name in other:
                    other.remove(name)
            if name not in target:
                target.append(name)

    def add_signal_nets(self, nets):
        """Append signal net names, accepting ``str``, :class:`CfgNet`, or lists thereof.

        Any net already present in ``power_nets`` or ``reference_nets`` is
        removed from those lists before being added here.

        Parameters
        ----------
        nets : str, CfgNet, or list of str/CfgNet
            Net name(s) to classify as signal.
        """
        self._add_to_list(self.signal_nets, [self.power_nets, self.reference_nets], nets)

    def add_power_ground_nets(self, nets):
        """Append power/ground net names, accepting ``str``, :class:`CfgNet`, or lists thereof.

        Any net already present in ``signal_nets`` or ``reference_nets`` is
        removed from those lists before being added here.

        Parameters
        ----------
        nets : str, CfgNet, or list of str/CfgNet
            Net name(s) to classify as power/ground.
        """
        self._add_to_list(self.power_nets, [self.signal_nets, self.reference_nets], nets)

    def add_reference_nets(self, nets):
        """Append reference net names, accepting ``str``, :class:`CfgNet`, or lists thereof.

        Any net already present in ``signal_nets`` or ``power_nets`` is
        removed from those lists before being added here.

        Parameters
        ----------
        nets : str, CfgNet, or list of str/CfgNet
            Net name(s) to use as reference nets.
        """
        self._add_to_list(self.reference_nets, [self.signal_nets, self.power_nets], nets)

    def apply(self):
        """Apply net configuration on the layout."""
        self.set_parameters_to_edb()

    def get_data_from_db(self):
        """Read net classifications from EDB."""
        return self.get_parameters_from_edb()

# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


class CfgNets:
    """Manage configuration net class."""

    def __init__(self, pdata, signal_nets=None, power_nets=None):
        self._pedb = pdata._pedb
        self.signal_nets = []
        self.power_nets = []
        if signal_nets:
            self.signal_nets = signal_nets
        if power_nets:
            self.power_nets = power_nets

    def apply(self):
        """Apply net on layout."""
        for signal_net in self.signal_nets:
            if signal_net in self._pedb.nets:
                self._pedb.nets.nets[signal_net].is_power_ground = False
        for power_net in self.power_nets:
            if power_net in self._pedb.nets:
                self._pedb.nets.nets[power_net].is_power_ground = True

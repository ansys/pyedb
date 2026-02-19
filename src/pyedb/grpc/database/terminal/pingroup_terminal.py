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

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.grpc.database.hierarchy.pingroup import PinGroup
    from pyedb.grpc.database.net.net import Net
from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as CorePinGroupTerminal,
)
from ansys.edb.core.terminal.terminal import BoundaryType as CoreBoundaryType

boundary_type_mapping = {
    "voltage_source": CoreBoundaryType.VOLTAGE_SOURCE,
    "current_source": CoreBoundaryType.CURRENT_SOURCE,
    "port": CoreBoundaryType.PORT,
    "voltage_probe": CoreBoundaryType.VOLTAGE_PROBE,
}
from pyedb.grpc.database.terminal.terminal import Terminal


class PinGroupTerminal(Terminal):
    """Manages pin group terminal properties."""

    def __init__(self, pedb, core):
        super().__init__(pedb, core)

    @property
    def net(self) -> Net:
        """Terminal net.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
            Terminal Net object.

        """
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.net)

    @net.setter
    def net(self, value):
        self.core.net = value

    @property
    def pin_group(self) -> PinGroup:
        """Pingroup.

        Returns
        -------
        :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
            Terminal pingroup.

        """
        from pyedb.grpc.database.hierarchy.pingroup import PinGroup

        return PinGroup(self._pedb, self.core.pin_group)

    @property
    def is_reference_terminal(self) -> bool:
        """Check if the terminal is a reference terminal.

        Returns
        -------
        bool
            True if the terminal is a reference terminal, False otherwise.

        """
        return self.core.is_reference_terminal

    @classmethod
    def create(cls, layout, name, pin_group, net=None, is_ref=False) -> PinGroupTerminal:
        """Create a pin group terminal.
        Parameters
        ----------
        layout : :class:`.Layout`
            Layout to create the pin group terminal in.
        name : :obj:`str`
            Name of the pin group terminal.
        pin_group : :class:`.PinGroup`
            Pin group.
        net : :class:`.Net` or :obj:`str`, optional
            Net.
        is_ref : :obj:`bool`, default: False
            Whether the pin group terminal is a reference terminal.
        Returns
        -------
        PinGroupTerminal
        """
        term = CorePinGroupTerminal.create(layout.core, name, pin_group.core, net.core, is_ref)
        return cls(layout._pedb, term)

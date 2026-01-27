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


from ansys.edb.core.simulation_setup.hfss_pi_simulation_settings import (
    HFSSPINetProcessingSettings as CoreHFSSPINetProcessingSettings,
)


class HFSSPINetProcessingSettings:
    """PyEDB HFSS PI net processing settings class."""

    def __init__(self, pedb, core: "CoreHFSSPINetProcessingSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def auto_select_nets_for_simulation(self) -> bool:
        """Flag indicating whether to automatically select nets for simulation.

        Returns
        -------
        bool
            True if auto select nets for simulation is enabled, False otherwise.

        """
        return self.core.auto_select_nets_for_simulation

    @auto_select_nets_for_simulation.setter
    def auto_select_nets_for_simulation(self, value: bool):
        self.core.auto_select_nets_for_simulation = value

    @property
    def ignore_dummy_nets_for_selected_nets(self) -> bool:
        """Flag indicating whether to ignore dummy nets for selected nets.

        Returns
        -------
        bool
            True if ignore dummy nets for selected nets is enabled, False otherwise.

        """
        return self.core.ignore_dummy_nets_for_selected_nets

    @ignore_dummy_nets_for_selected_nets.setter
    def ignore_dummy_nets_for_selected_nets(self, value: bool):
        self.core.ignore_dummy_nets_for_selected_nets = value

    @property
    def include_nets(self) -> list[str]:
        """List of nets to include in the simulation.

        Returns
        -------
        list[str]
            List of net names to include.

        """
        return self.core.include_nets

    @include_nets.setter
    def include_nets(self, value: list[str]):
        self.core.include_nets = value

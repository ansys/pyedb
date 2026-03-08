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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.raptor_x_simulation_settings import (
        RaptorXGeneralSettings as CoreRaptorXGeneralSettings,
    )


class RaptorXGeneralSettings:
    """Raptor X general settings class."""

    def __init__(self, pedb, core: "CoreRaptorXGeneralSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def global_temperature(self) -> float:
        """Simulation temperature in degrees Celsius.

        Returns
        -------
        float
            Global temperature in Kelvin.
        """
        return self._pedb.value(self.core.global_temperature)

    @global_temperature.setter
    def global_temperature(self, value: float):
        """Set simulation temperature in degrees Celsius.

        Parameters
        ----------
        value : float
            Global temperature in Kelvin.
        """
        self.core.global_temperature = self._pedb.value(value)

    @property
    def max_frequency(self) -> float:
        """Maximum frequency for the simulation in Hz.

        Returns
        -------
        float
            Maximum frequency in Hz.
        """
        return self._pedb.value(self.core.max_frequency)

    @max_frequency.setter
    def max_frequency(self, value: float):
        """Set maximum frequency for the simulation in Hz.

        Parameters
        ----------
        value : float
            Maximum frequency in Hz.
        """
        self.core.max_frequency = str(self._pedb.value(value))

    @property
    def netlist_export_spectre(self) -> bool:
        """Flag indicating if the netlist is exported in Spectre format."""
        return self.core.netlist_export_spectre

    @netlist_export_spectre.setter
    def netlist_export_spectre(self, value: bool):
        self.core.netlist_export_spectre = value

    @property
    def save_netlist(self) -> bool:
        """Flag indicating if the netlist is saved."""
        return self.core.save_netlist

    @save_netlist.setter
    def save_netlist(self, value: bool):
        self.core.save_netlist = value

    @property
    def save_rfm(self) -> bool:
        """Flag indicating if the RFM file is saved."""
        return self.core.save_rfm

    @save_rfm.setter
    def save_rfm(self, value: bool):
        self.core.save_rfm = value

    @property
    def use_gold_em_solver(self) -> bool:
        """Flag indicating if the Gold EM solver is used."""
        return self.core.use_gold_em_solver

    @use_gold_em_solver.setter
    def use_gold_em_solver(self, value: bool):
        self.core.use_gold_em_solver = value

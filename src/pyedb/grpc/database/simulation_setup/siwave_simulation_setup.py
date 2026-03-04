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
from ansys.edb.core.simulation_setup.siwave_simulation_setup import SIWaveSimulationSetup as CoreSIWaveSimulationSetup
import warnings

from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_advanced_settings import SIWaveAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_advanced import SIWaveDCAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_settings import SIWaveDCSettings
from pyedb.grpc.database.simulation_setup.siwave_simulation_settings import SIWaveSimulationSettings

if TYPE_CHECKING:
    from pyedb.grpc.edb import Edb


class SiwaveSimulationSetup(SimulationSetup):
    """SIwave simulation setup class."""

    def __init__(self, pedb, core: "CoreSIWaveSimulationSetup"):
        super().__init__(pedb, core)
        self.core: CoreSIWaveSimulationSetup = core
        self._pedb = pedb

    @classmethod
    def create(cls, edb: "Edb", name: str = "siwave_setup") -> "SiwaveSimulationSetup":
        """Create a SIWave simulation setup object.

        Parameters
        ----------
        edb : :class:`Edb`
            Inherited object.

        name : str, optional
            Name of the simulation setup. The default is "siwave_setup".

        Returns
        -------
        SiwaveSimulationSetup
            The SIWave simulation setup object.
        """
        core = CoreSIWaveSimulationSetup.create(edb.active_cell, name)
        return cls(edb, core)

    @property
    def settings(self) -> SIWaveSimulationSettings:
        """Setup simulation settings."""
        return SIWaveSimulationSettings(self._pedb, self.core.settings)

    @property
    def advanced_settings(self) -> SIWaveAdvancedSettings:
        """Setup advanced settings."""
        return self.settings.advanced

    @property
    def dc_settings(self) -> SIWaveDCSettings:
        """Setup dc settings.

        .. deprecated:: 0.70.0
        Use :attr:`dc_advanced_settings is deprecated. Use :attr:`settings.dc instead.

        """
        warnings.warn("`dc_settings` is deprecated. Use `settings.dc` instead.", DeprecationWarning)
        return self.settings.dc

    @property
    def dc_advanced_settings(self) -> SIWaveDCAdvancedSettings:
        """Setup dc settings.

        .. deprecated:: 0.70.0
        Use :attr:`dc_advanced_settings is deprecated. Use :attr:`settings.dc_advanced instead.

        """
        warnings.warn("`dc_advanced_settings` is deprecated. Use `settings.dc_advanced` instead.", DeprecationWarning)
        return self.settings.dc_advanced

    @property
    def use_si_settings(self) -> bool:
        """Whether to use SI settings.

        .. deprecated:: 0.70.0
        Use :attr:`settings.use_si_settings is deprecated. Use :attr:`settings.general.use_si_settings` instead.

        """
        warnings.warn(
            "`use_si_settings` is deprecated. Use `settings.general.use_si_settings` instead.", DeprecationWarning
        )
        return self.settings.general.use_si_settings

    @use_si_settings.setter
    def use_si_settings(self, value: bool):
        self.settings.general.use_si_settings = value

    @property
    def si_slider_position(self) -> int:
        """SI slider position.

        .. deprecated:: 0.70.0
        Use :attr:`settings.si_slider_position is deprecated. Use :attr:`settings.general.si_slider_position` instead.
        """
        warnings.warn(
            "`si_slider_position` is deprecated. Use `settings.general.si_slider_position` instead.",
        )
        return self.settings.general.si_slider_position

    @si_slider_position.setter
    def si_slider_position(self, value: int):
        self.settings.general.si_slider_position = value

    @property
    def pi_slider_position(self) -> int:
        """I slider position.

        .. deprecated:: 0.70.0
        Use :attr:`settings.pi_slider_position is deprecated. Use :attr:`settings.general.pi_slider_position` instead.
        """
        warnings.warn(
            "`pi_slider_position` is deprecated. Use `settings.general.pi_slider_position` instead.", DeprecationWarning
        )
        return self.settings.general.pi_slider_pos

    @pi_slider_position.setter
    def pi_slider_position(self, value: int):
        self.settings.general.pi_slider_pos = value

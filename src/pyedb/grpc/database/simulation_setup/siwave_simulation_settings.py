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

from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_settings import SIWaveDCSettings
from pyedb.grpc.database.simulation_setup.siwave_general_settings import SIWaveGeneralSettings
from pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings import SIWaveSParameterSettings


class SIWaveSimulationSettings(SimulationSettings):
    @property
    def dc(self) -> SIWaveDCSettings:
        """DC settings class.

        Returns
        -------
        :class:`SIWaveDCSettings <pyedb.grpc.database.simulation_setup.
        siwave_dc_settings.SIWaveDCSettings>`

        """
        return SIWaveDCSettings(self._pedb, self.core.dc)

    @property
    def enabled(self) -> bool:
        """Enabled status of the SIWave simulation.

        Returns
        -------
        bool
            True if enabled, False otherwise.

        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.core.enabled = value

    @property
    def general(self) -> SIWaveGeneralSettings:
        """General settings class.

        Returns
        -------
        :class:`SIWaveGeneralSettings <pyedb.grpc.database.simulation_setup.
        siwave_general_settings.SIWaveGeneralSettings>`

        """
        return SIWaveGeneralSettings(self._pedb, self.core.general)

    @property
    def s_parameter(self) -> SIWaveSParameterSettings:
        """S-Parameter settings class.

        Returns
        -------
        :class:`SIWaveSParameterSettings <pyedb.grpc.database.simulation_setup.
        siwave_s_parameter_settings.SIWaveSParameterSettings>`

        """
        return SIWaveSParameterSettings(self._pedb, self.core.s_parameter)

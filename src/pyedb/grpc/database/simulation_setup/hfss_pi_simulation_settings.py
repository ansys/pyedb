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
    HFSSPISimulationSettings as CoreHFSSPISimulationSettings,
)

from pyedb.grpc.database.simulation_setup.hfss_pi_general_settings import HFSSPIGeneralSettings
from pyedb.grpc.database.simulation_setup.hfss_pi_net_processing_settings import HFSSPINetProcessingSettings
from pyedb.grpc.database.simulation_setup.hfss_pi_power_ground_nets_settings import HFSSPIPowerGroundNetsSettings
from pyedb.grpc.database.simulation_setup.hfss_pi_signal_nets_settings import HFSSPISignalNetsSettings


class HFSSPISimulationSettings:
    """PyEDB HFSS PI simulation setup class."""

    def __init__(self, pedb, core: "CoreHFSSPISimulationSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def enabled(self) -> bool:
        """Get or set the enabled status of the HFSS PI simulation setup.

        Returns
        -------
        bool
            True if the simulation setup is enabled, False otherwise.

        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.core.enabled = value

    @property
    def general(self) -> HFSSPIGeneralSettings:
        """Get the HFSS PI general simulation settings.

        Returns
        -------
        HFSSPIGeneralSettings
            The HFSS PI general simulation settings object.

        """
        return HFSSPIGeneralSettings(self._pedb, self.core.general)

    @property
    def net_processing(self) -> HFSSPINetProcessingSettings:
        """Get the HFSS PI net processing simulation settings.

        Returns
        -------
        HFSSPINetProcessingSettings
            The HFSS PI net processing simulation settings object.

        """
        return HFSSPINetProcessingSettings(self._pedb, self.core.net_processing)

    @property
    def power_ground_nets(self) -> HFSSPIPowerGroundNetsSettings:
        """Get the HFSS PI power and ground nets simulation settings.

        Returns
        -------
        HFSSPIPowerGroundNetsSettings
            The HFSS PI power and ground nets simulation settings object.

        """
        return HFSSPIPowerGroundNetsSettings(self._pedb, self.core.power_ground_nets)

    @property
    def signal_nets(self) -> HFSSPISignalNetsSettings:
        """Get the HFSS PI signal nets simulation settings.

        Returns
        -------
        HFSSPISignalNetsSettings
            The HFSS PI signal nets simulation settings object.

        """
        return HFSSPISignalNetsSettings(self._pedb, self.core.signal_nets)

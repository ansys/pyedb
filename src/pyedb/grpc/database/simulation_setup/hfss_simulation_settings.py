# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    HFSSSimulationSettings as GrpcHFSSSimulationSettings,
)

from pyedb.grpc.database.simulation_setup.hfss_advanced_meshing_settings import (
    HFSSAdvancedMeshingSettings,
)
from pyedb.grpc.database.simulation_setup.hfss_advanced_settings import (
    HFSSAdvancedSettings,
)
from pyedb.grpc.database.simulation_setup.hfss_dcr_settings import HFSSDCRSettings
from pyedb.grpc.database.simulation_setup.hfss_general_settings import (
    HFSSGeneralSettings,
)
from pyedb.grpc.database.simulation_setup.hfss_settings_options import (
    HFSSSettingsOptions,
)
from pyedb.grpc.database.simulation_setup.hfss_solver_settings import HFSSSolverSettings


class HFSSSimulationSettings(GrpcHFSSSimulationSettings):
    """PyEDB-core HFSS simulation settings class."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._edb_object = edb_object
        self._pedb = pedb

    @property
    def advanced(self) -> HFSSAdvancedSettings:
        """HFSS Advanced settings class.


        Returns
        -------
        :class:`HFSSAdvancedSettings <pyedb.grpc.database.simulation_setup.hfss_advanced_settings.HFSSAdvancedSettings>`

        """
        return HFSSAdvancedSettings(self._pedb, self.advanced)

    @property
    def advanced_meshing(self) -> HFSSAdvancedMeshingSettings:
        """Advanced meshing class.

        Returns
        -------
        :class:`HFSSAdvancedMeshingSettings <pyedb.grpc.database.simulation_setup.
        hfss_advanced_meshing_settings.HFSSAdvancedMeshingSettings>`

        """
        return HFSSAdvancedMeshingSettings(self._pedb, self.advanced_meshing)

    @property
    def dcr(self) -> HFSSDCRSettings:
        """Dcr.

        Returns
        -------
        :class:`HFSSDCRSettings <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings>`

        """
        return HFSSDCRSettings(self._pedb, self.dcr)

    @property
    def general(self) -> HFSSGeneralSettings:
        """General settings class.

        Returns
        -------
        :class:`HFSSGeneralSettings <pyedb.grpc.database.simulation_setup.hfss_general_settings.HFSSGeneralSettings>`

        """
        return HFSSGeneralSettings(self._pedb, self.general)

    @property
    def options(self) -> HFSSSettingsOptions:
        """HFSS option class.

        Returns
        -------
        :class:`HFSSSettingsOptions <pyedb.grpc.database.simulation_setup.hfss_settings_options.HFSSSettingsOptions>`

        """
        return HFSSSettingsOptions(self._pedb, self.options)

    @property
    def solver(self) -> HFSSSolverSettings:
        """HFSS solver settings class.

        Returns
        -------
        :class:`HFSSSolverSettings <pyedb.grpc.database.simulation_setup.hfss_solver_settings.HFSSSolverSettings>`

        """
        return HFSSSolverSettings(self._pedb, self.solver)

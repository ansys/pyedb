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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import (
        Q3DSimulationSettings as GrpcQ3DSimulationSettings,
    )
from pyedb.grpc.database.simulation_setup.q3d_acrl_settings import Q3DACRLSettings
from pyedb.grpc.database.simulation_setup.q3d_advanced_meshing_settings import Q3DAdvancedMeshingSettings
from pyedb.grpc.database.simulation_setup.q3d_advanced_settings import Q3DAdvancedSettings
from pyedb.grpc.database.simulation_setup.q3d_cg_settings import Q3DCGSettings
from pyedb.grpc.database.simulation_setup.q3d_dcrl_settings import Q3DDCRLSettings
from pyedb.grpc.database.simulation_setup.q3d_general_settings import Q3DGeneralSettings


class Q3DSimulationSettings:
    """Q3D simulation settings class."""

    def __init__(self, pedb, core: GrpcQ3DSimulationSettings):
        self.core = core
        self._pedb = pedb

    @property
    def acrl(self) -> Q3DACRLSettings:
        """ACRL settings class.

        Returns
        -------
        :class:`Q3DACRLSettings <pyedb.grpc.database.simulation_setup.
        q3d_acrl_settings.Q3DACRLSettings>`

        """
        return Q3DACRLSettings(self._pedb, self.core.acrl)

    @property
    def advanced(self) -> Q3DAdvancedSettings:
        """Advanced settings class.

        Returns
        -------
        :class:`Q3DAdvancedSettings <pyedb.grpc.database.simulation_setup.
        q3d_advanced_settings.Q3DAdvancedSettings>`

        """
        return Q3DAdvancedSettings(self._pedb, self.core.advanced)

    @property
    def advanced_meshing(self) -> Q3DAdvancedMeshingSettings:
        """Advanced meshing settings class.

        Returns
        -------
        :class:`Q3DAdvancedMeshingSettings <pyedb.grpc.database.simulation_setup.
        q3d_advanced_meshing_settings.Q3DAdvancedMeshingSettings>`
        """
        return Q3DAdvancedMeshingSettings(self._pedb, self.core.advanced_meshing)

    @property
    def cg(self) -> Q3DCGSettings:
        """CG settings class.

        Returns
        -------
        :class:`Q3DCGSettings <pyedb.grpc.database.simulation_setup.
        q3d_cg_settings.Q3DCGSettings>`

        """
        return Q3DCGSettings(self._pedb, self.core.cg)

    @property
    def dcrl(self) -> Q3DDCRLSettings:
        """DCRL settings class.

        Returns
        -------
        :class:`Q3DDCRLSettings <pyedb.grpc.database.simulation_setup.
        q3d_dcrl_settings.Q3DDCRLSettings>`

        """
        return Q3DDCRLSettings(self._pedb, self.core.dcrl)

    @property
    def enabled(self) -> bool:
        """Enabled flag.

        Returns
        -------
        bool
            Enabled flag.

        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.core.enabled = value

    @property
    def general(self) -> Q3DGeneralSettings:
        """General settings class.

        Returns
        -------
        :class:`Q3DGeneralSettings <pyedb.grpc.database.simulation_setup.
        q3d_general_settings.Q3DGeneralSettings>`

        """
        return Q3DGeneralSettings(self._pedb, self.core.general)

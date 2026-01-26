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
import warnings

if TYPE_CHECKING:
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


class HFSSSimulationSettings:
    """PyEDB-core HFSS simulation settings class."""

    def __init__(self, pedb, core: "GrpcHFSSSimulationSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def advanced(self) -> HFSSAdvancedSettings:
        """HFSS Advanced settings class.


        Returns
        -------
        :class:`HFSSAdvancedSettings <pyedb.grpc.database.simulation_setup.hfss_advanced_settings.HFSSAdvancedSettings>`

        """
        return HFSSAdvancedSettings(self._pedb, self.core.advanced)

    @property
    def advanced_meshing(self) -> HFSSAdvancedMeshingSettings:
        """Advanced meshing class.

        Returns
        -------
        :class:`HFSSAdvancedMeshingSettings <pyedb.grpc.database.simulation_setup.
        hfss_advanced_meshing_settings.HFSSAdvancedMeshingSettings>`

        """
        return HFSSAdvancedMeshingSettings(self._pedb, self.core.advanced_meshing)

    @property
    def dcr(self) -> HFSSDCRSettings:
        """Dcr.

        Returns
        -------
        :class:`HFSSDCRSettings <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings>`

        """
        return HFSSDCRSettings(self._pedb, self.core.dcr)

    @property
    def general(self) -> HFSSGeneralSettings:
        """General settings class.

        Returns
        -------
        :class:`HFSSGeneralSettings <pyedb.grpc.database.simulation_setup.hfss_general_settings.HFSSGeneralSettings>`

        """
        return HFSSGeneralSettings(self._pedb, self.core.general)

    @property
    def options(self) -> HFSSSettingsOptions:
        """HFSS option class.

        Returns
        -------
        :class:`HFSSSettingsOptions <pyedb.grpc.database.simulation_setup.hfss_settings_options.HFSSSettingsOptions>`

        """
        return HFSSSettingsOptions(self._pedb, self.core.options)

    @property
    def solver(self) -> HFSSSolverSettings:
        """HFSS solver settings class.

        Returns
        -------
        :class:`HFSSSolverSettings <pyedb.grpc.database.simulation_setup.hfss_solver_settings.HFSSSolverSettings>`

        """
        return HFSSSolverSettings(self._pedb, self.core.solver)

    @property
    def enhanced_low_frequency_accuracy(self) -> bool:
        """Enhanced low frequency accuracy flag.

        .. deprecated:: 0.67.0
            This property is deprecated. Please use :attr:`options.enhanced_low_frequency_accuracy`
            instead.
            This attribute was added for dotnet compatibility and will be removed in future releases.
        """
        warnings.warn(
            "The 'enhanced_low_frequency_accuracy' property is deprecated and will be removed in future releases. ",
            DeprecationWarning,
        )
        return self.options.enhanced_low_frequency_accuracy

    @enhanced_low_frequency_accuracy.setter
    def enhanced_low_frequency_accuracy(self, value: bool):
        self.options.enhanced_low_frequency_accuracy = value

    @property
    def relative_residual(self) -> float:
        """Relative residual value.

        .. deprecated:: 0.67.0
            This property is deprecated. Please use :attr:`options.relative_residual`
            instead.
            This attribute was added for dotnet compatibility and will be removed in future releases.
        """
        warnings.warn(
            "The 'relative_residual' property is deprecated and will be removed in future releases.",
            DeprecationWarning,
        )
        return self.options.relative_residual

    @relative_residual.setter
    def relative_residual(self, value: float):
        self.options.relative_residual = value

    @property
    def use_shell_elements(self) -> bool:
        """Use shell elements flag.

        .. deprecated:: 0.67.0
            This property is deprecated. Please use :attr:`options.use_shell_elements`
            instead.
            This attribute was added for dotnet compatibility and will be removed in future releases.
        """
        warnings.warn(
            "The 'use_shell_elements' property is deprecated and will be removed in future releases. ",
            DeprecationWarning,
        )
        return self.options.use_shell_elements

    @use_shell_elements.setter
    def use_shell_elements(self, value: bool):
        self.options.use_shell_elements = value

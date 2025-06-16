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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.edb.core.simulation_setup.raptor_x_simulation_setup import (
    RaptorXSimulationSettings as GrpcRaptorXSimulationSettings,
)

from pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings import (
    RaptorXAdvancedSettings,
)
from pyedb.grpc.database.simulation_setup.raptor_x_general_settings import (
    RaptorXGeneralSettings,
)


class RaptorXSimulationSettings(GrpcRaptorXSimulationSettings):
    """Raptor X simulation settings class."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb

    @property
    def advanced(self) -> RaptorXAdvancedSettings:
        """Advanced class.

        Returns
        -------
        :class:`RaptorXAdvancedSettings <pyedb.grpc.database.simulation_setup.
        raptor_x_advanced_settings.RaptorXAdvancedSettings>`

        """
        return RaptorXAdvancedSettings(self._pedb, self.advanced)

    @property
    def general(self) -> RaptorXGeneralSettings:
        """General settings class.

        Returns
        -------
        :class:`RaptorXGeneralSettings <pyedb.grpc.database.simulation_setup.
        raptor_x_general_settings.RaptorXGeneralSettings>`

        """
        RaptorXGeneralSettings(self._pedb, self.general)

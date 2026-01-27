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
    from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
        SIWaveSParameterSettings as CoreSIWaveSParameterSettings,
    )
from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SParamDCBehavior as CoreSParamDCBehavior,
    SParamExtrapolation as CoreSParamExtrapolation,
    SParamInterpolation as CoreSParamInterpolation,
)

_mapping_dc_behavior = {
    "zero": CoreSParamDCBehavior.ZERO_DC,
    "same": CoreSParamDCBehavior.SAME_DC,
    "linear": CoreSParamDCBehavior.LINEAR_DC,
    "constant": CoreSParamDCBehavior.CONSTANT_DC,
    "one_port_capacitor": CoreSParamDCBehavior.ONE_PORT_CAPACITOR_DC,
    "open": CoreSParamDCBehavior.OPEN_DC,
}

_mapping_s_parameter_extrapolation = {
    "zero": CoreSParamExtrapolation.ZERO_EX,
    "same": CoreSParamExtrapolation.SAME_EX,
    "linear": CoreSParamExtrapolation.LINEAR_EX,
    "constant": CoreSParamExtrapolation.CONSTANT_EX,
}

_mapping_s_parameter_interpolation = {
    "point": CoreSParamInterpolation.POINT_IN,
    "linear": CoreSParamInterpolation.LINEAR_IN,
    "step": CoreSParamInterpolation.STEP_IN,
}


class SIWaveSParameterSettings:
    """SIWave S-Parameter simulation settings class."""

    def __init__(self, pedb, core: "CoreSIWaveSParameterSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def dc_behavior(self) -> str:
        """Get or set the DC behavior for S-Parameter simulation.

        Returns
        -------
        str
            The DC behavior as a string.
        """
        reverse_mapping = {v: k for k, v in _mapping_dc_behavior.items()}
        return reverse_mapping[self.core.dc_behavior]

    @dc_behavior.setter
    def dc_behavior(self, value: str):
        if value not in _mapping_dc_behavior:
            raise ValueError(f"Invalid DC behavior: {value}. Valid options are: {list(_mapping_dc_behavior.keys())}")
        self.core.dc_behavior = _mapping_dc_behavior[value]

    @property
    def extrapolation(self) -> str:
        """Get or set the S-Parameter extrapolation method.

        Returns
        -------
        str
            The S-Parameter extrapolation method as a string.
        """
        reverse_mapping = {v: k for k, v in _mapping_s_parameter_extrapolation.items()}
        return reverse_mapping[self.core.extrapolation]

    @extrapolation.setter
    def extrapolation(self, value: str):
        if value not in _mapping_s_parameter_extrapolation:
            raise ValueError(
                f"Invalid S-Parameter extrapolation: {value}. Valid options are: "
                f"{list(_mapping_s_parameter_extrapolation.keys())}"
            )
        self.core.extrapolation = _mapping_s_parameter_extrapolation[value]

    @property
    def interpolation(self) -> str:
        """Get or set the S-Parameter interpolation method.

        Returns
        -------
        str
            The S-Parameter interpolation method as a string.
        """
        reverse_mapping = {v: k for k, v in _mapping_s_parameter_interpolation.items()}
        return reverse_mapping[self.core.interpolation]

    @interpolation.setter
    def interpolation(self, value: str):
        if value not in _mapping_s_parameter_interpolation:
            raise ValueError(
                f"Invalid S-Parameter interpolation: {value}. Valid options are: "
                f"{list(_mapping_s_parameter_interpolation.keys())}"
            )
        self.core.interpolation = _mapping_s_parameter_interpolation[value]

    @property
    def use_state_space(self) -> bool:
        """Get or set whether to use state space representation.

        Returns
        -------
        bool
            True if state space representation is used, False otherwise.
        """
        return self.core.use_state_space

    @use_state_space.setter
    def use_state_space(self, value: bool):
        self.core.use_state_space = value

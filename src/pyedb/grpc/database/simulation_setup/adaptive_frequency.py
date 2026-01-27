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
    from ansys.edb.core.simulation_setup.adaptive_solutions import (
        AdaptiveFrequency as GrpcAdaptiveFrequency,
    )
from ansys.edb.core.utility.value import Value as GrpcValue


class AdaptiveFrequency:
    """PyEDB Adaptive Frequency class."""

    def __init__(self, core: "GrpcAdaptiveFrequency"):
        self.core = core

    @property
    def adaptive_frequency(self) -> float:
        """Get the adaptive frequency value.

        Returns
        -------
        float
            Adaptive frequency value.
        """
        return GrpcValue(self.core.adaptive_frequency).value

    @adaptive_frequency.setter
    def adaptive_frequency(self, value: float):
        """Set the adaptive frequency value.

        Parameters
        ----------
        value : float
            Adaptive frequency value.
        """
        self.core.adaptive_frequency = str(GrpcValue(value))

    @property
    def max_delta(self):
        """Get the maximum delta value.

        Returns
        -------
        float
            Maximum delta value.
        """
        return float(self.core.max_delta)

    @max_delta.setter
    def max_delta(self, value: float):
        """Set the maximum delta value.

        Parameters
        ----------
        value : float
            Maximum delta value.
        """
        self.core.max_delta = str(value)

    @property
    def output_variables(self) -> dict[str, str]:
        """Map of output variable names to maximum delta S."""
        return self.core.output_variables

    def add_output_variable(self, variable_name: str, max_delta_s: float):
        """Add an output variable with its maximum delta S.

        Parameters
        ----------
        variable_name : str
            Name of the output variable.
        max_delta_s : float
            Maximum delta S for the output variable.
        """
        output_dict = self.output_variables
        output_dict[variable_name] = str(max_delta_s)
        self.output_variables = output_dict

    @output_variables.setter
    def output_variables(self, value: dict[str, str]):
        """Set the output variables map.

        Parameters
        ----------
        value : dict[str, str]
            Map of output variable names to maximum delta S.
        """
        self.core.output_variables = value

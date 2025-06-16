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

import warnings

from ansys.edb.core.simulation_setup.raptor_x_simulation_setup import (
    RaptorXSimulationSetup as GrpcRaptorXSimulationSetup,
)

from pyedb.grpc.database.simulation_setup.sweep_data import SweepData


class RaptorXSimulationSetup(GrpcRaptorXSimulationSetup):
    """RaptorX simulation setup."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def frequency_sweeps(self):
        """Returns Frequency sweeps
        . deprecated:: use sweep_data instead
        """
        warnings.warn(
            "`frequency_sweeps` is deprecated use `sweep_data` instead.",
            DeprecationWarning,
        )
        return self.sweep_data

    def add_frequency_sweep(
        self, name=None, distribution="linear", start_freq="0GHz", stop_freq="20GHz", step="10MHz", discrete=False
    ):
        """Add frequency sweep.

        . deprecated:: pyedb 0.31.0
        Use :func:`add sweep` instead.

        """
        warnings.warn(
            "`add_frequency_sweep` is deprecated use `add_sweep` instead.",
            DeprecationWarning,
        )
        return self.add_sweep(name, distribution, start_freq, stop_freq, step, discrete)

    def add_sweep(
        self, name=None, distribution="linear", start_freq="0GHz", stop_freq="20GHz", step="10MHz", discrete=False
    ) -> bool:
        """Add a HFSS frequency sweep.

        Parameters
        ----------
        name : str, optional
         Sweep name.
        distribution : str, optional
            Type of the sweep. The default is `"linear"`. Options are:
            - `"linear"`
            - `"linear_count"`
            - `"decade_count"`
            - `"octave_count"`
            - `"exponential"`
        start_freq : str, float, optional
            Starting frequency. The default is ``1``.
        stop_freq : str, float, optional
            Stopping frequency. The default is ``1e9``.
        step : str, float, int, optional
            Frequency step. The default is ``1e6``. or used for `"decade_count"`, "linear_count"`, "octave_count"`
            distribution. Must be integer in that case.
        discrete : bool, optional
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        bool
        """
        init_sweep_count = len(self.sweep_data)
        start_freq = self._pedb.number_with_units(start_freq, "Hz")
        stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
        step = str(step)
        if distribution.lower() == "linear":
            distribution = "LIN"
        elif distribution.lower() == "linear_count":
            distribution = "LINC"
        elif distribution.lower() == "exponential":
            distribution = "ESTP"
        elif distribution.lower() == "decade_count":
            distribution = "DEC"
        elif distribution.lower() == "octave_count":
            distribution = "OCT"
        else:
            distribution = "LIN"
        if not name:
            name = f"sweep_{init_sweep_count + 1}"
        sweep_data = [
            SweepData(self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step)
        ]
        if discrete:
            sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
        for sweep in self.sweep_data:
            sweep_data.append(sweep)
        self.sweep_data = sweep_data
        if len(self.sweep_data) == init_sweep_count + 1:
            return True
        else:
            self._pedb.logger.error("Failed to add frequency sweep data")
            return False

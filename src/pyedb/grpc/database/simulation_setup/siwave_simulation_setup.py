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

from ansys.edb.core.simulation_setup.simulation_setup import (
    SimulationSetupType as GrpcSimulationSetupType,
)
from ansys.edb.core.simulation_setup.siwave_simulation_setup import (
    SIWaveSimulationSetup as GrpcSIWaveSimulationSetup,
)

from pyedb.grpc.database.simulation_setup.sweep_data import SweepData


class SiwaveSimulationSetup(GrpcSIWaveSimulationSetup):
    """SIwave simulation setup class."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def advanced_settings(self):
        """Setup advanced settings."""
        return self.settings.advanced

    @property
    def dc_settings(self):
        """Setup dc settings."""
        return self.settings.dc

    @property
    def dc_advanced_settings(self):
        """Setup dc settings."""
        return self.settings.dc_advanced

    @property
    def type(self) -> str:
        """Simulation setup type.

        Returns
        -------
        str
            Simulation type.

        """
        return super().type.name

    @type.setter
    def type(self, value):
        if value.upper() == "SI_WAVE":
            super(SiwaveSimulationSetup, self.__class__).type.__set__(self, GrpcSimulationSetupType.SI_WAVE)
        elif value.upper() == "SI_WAVE_DCIR":
            super(SiwaveSimulationSetup, self.__class__).type.__set__(self, GrpcSimulationSetupType.SI_WAVE_DCIR)

    def add_sweep(
        self,
        name=None,
        distribution="linear",
        start_freq="0GHz",
        stop_freq="20GHz",
        step="10MHz",
        discrete=False,
        frequency_set=None,
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
        frequency_set : List, optional
            Frequency set is a list adding one or more frequency sweeps. If ``frequency_set`` is provided, the other
            arguments are ignored except ``discrete``. Default value is ``None``.
            example of frequency_set : [['linear_scale', '50MHz', '200MHz', '10MHz']].

        Returns
        -------
        bool
        """
        init_sweep_count = len(self.sweep_data)
        if frequency_set:
            for sweep in frequency_set:
                if "linear_scale" in sweep:
                    distribution = "LIN"
                elif "linear_count" in sweep:
                    distribution = "LINC"
                elif "exponential" in sweep:
                    distribution = "ESTP"
                elif "log_scale" in sweep:
                    distribution = "DEC"
                elif "octave_count" in sweep:
                    distribution = "OCT"
                else:
                    distribution = "LIN"
                start_freq = self._pedb.number_with_units(sweep[1], "Hz")
                stop_freq = self._pedb.number_with_units(sweep[2], "Hz")
                step = str(sweep[3])
                if not name:
                    name = f"sweep_{init_sweep_count + 1}"
                sweep_data = [
                    SweepData(
                        self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step
                    )
                ]
                if discrete:
                    sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
                for sweep in self.sweep_data:
                    sweep_data.append(sweep)
                self.sweep_data = sweep_data
                return sweep_data[0]
        else:
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
                SweepData(
                    self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step
                )
            ]
            if discrete:
                sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
            for sweep in self.sweep_data:
                sweep_data.append(sweep)
            self.sweep_data = sweep_data
            if len(self.sweep_data) == init_sweep_count + 1:
                return sweep_data[0]
            else:
                self._pedb.logger.error("Failed to add frequency sweep data")
                return False

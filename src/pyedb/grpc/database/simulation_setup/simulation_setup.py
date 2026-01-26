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


from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.simulation_setup import SimulationSetup as GrpcSimulationSetup

from ansys.edb.core.simulation_setup.simulation_setup import SimulationSetupType as GrpcSimulationSetupType

from pyedb.grpc.database.simulation_setup.sweep_data import SweepData

_mapping_simulation_types = {
    GrpcSimulationSetupType.HFSS: "hfss",
    GrpcSimulationSetupType.SI_WAVE: "siwave",
    GrpcSimulationSetupType.SI_WAVE_DCIR: "siwave_dcir",
    GrpcSimulationSetupType.HFSS_PI: "hfss_pi",
    GrpcSimulationSetupType.RAPTOR_X: "raptor_x",
    GrpcSimulationSetupType.Q3D_SIM: "q3d",
}


class SimulationSetup:
    def __init__(self, pedb, core: "GrpcSimulationSetup"):
        """PyEDB Simulation Setup base class."""
        self.core = core
        self._pedb = pedb

    def cast(self):
        """Cast a core SimulationSetup to PyEDB SimulationSetup."""
        return self.core.cast()

    @property
    def id(self) -> int:
        """Unique ID of the EDB object.

        Returns
        -------
        int
            Simulation setup ID.
        """
        return self.core.id

    @property
    def is_null(self) -> bool:
        """Check if the simulation setup is null.

        Returns
        -------
        bool
            True if the simulation setup is null, False otherwise.
        """
        return self.core.is_null

    @property
    def name(self) -> str:
        """Get or set the name of the simulation setup.

        Returns
        -------
        str
            Simulation setup name.
        """
        return self.core.name

    @name.setter
    def name(self, value: str):
        self.core.name = value

    @property
    def position(self) -> int:
        """Get or set the position of the simulation setup.

        Returns
        -------
        int
            Simulation setup position.
        """
        return self.core.position

    @position.setter
    def position(self, value: int):
        self.core.position = value

    @property
    def sweep_data(self) -> list[SweepData]:
        """Get the sweep data associated with the simulation setup.

        Returns
        -------
        list[SweepData]
            List of sweep data objects.
        """

        return [SweepData(self._pedb, sweep) for sweep in self.core.sweep_data]

    @sweep_data.setter
    def sweep_data(self, sweeps: list[SweepData]):
        self.core.sweep_data = [sweep.core for sweep in sweeps]

    def add_sweep(
        self,
        name=None,
        distribution="linear",
        start_freq="0GHz",
        stop_freq="20GHz",
        step="10MHz",
        discrete=False,
        frequency_set=None,
    ) -> Union[SweepData, None]:
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
                for sweep in self.core.sweep_data:
                    sweep_data.append(sweep)
                self.core.sweep_data = sweep_data
            return None
        else:
            start_freq = self._pedb.number_with_units(start_freq, "Hz")
            stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
            step = str(step)
            if distribution not in ["LIN", "LINC", "ESTP", "DEC", "OCT"]:
                if distribution.lower() == "linear" or distribution.lower() == "linear scale":
                    distribution = "LIN"
                elif distribution.lower() == "linear_count" or distribution.lower() == "linear count":
                    distribution = "LINC"
                elif distribution.lower() == "exponential":
                    distribution = "ESTP"
                elif (
                    distribution.lower() == "decade_count"
                    or distribution.lower() == "decade count"
                    or distribution.lower()
                ) == "log scale":
                    distribution = "DEC"
                elif distribution.lower() == "octave_count" or distribution.lower() == "octave count":
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
            self.core.sweep_data = [sw.core for sw in sweep_data]
            if len(self.sweep_data) == init_sweep_count + 1:
                return self.sweep_data[-1]
            else:
                self._pedb.logger.error("Failed to add frequency sweep data")
                return None

    @property
    def setup_type(self) -> str:
        """Get the type of the simulation setup.

        Returns
        -------
        str
            Simulation setup type.
        """
        return _mapping_simulation_types[self.core.type]

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
    from ansys.edb.core.simulation_setup.simulation_setup import SimulationSetup as CoreSimulationSetup

from ansys.edb.core.simulation_setup.simulation_setup import SimulationSetupType as CoreSimulationSetupType

from pyedb.grpc.database.simulation_setup.sweep_data import SweepData

_mapping_simulation_types = {
    CoreSimulationSetupType.HFSS: "hfss",
    CoreSimulationSetupType.SI_WAVE: "siwave",
    CoreSimulationSetupType.SI_WAVE_DCIR: "siwave_dcir",
    CoreSimulationSetupType.HFSS_PI: "hfss_pi",
    CoreSimulationSetupType.RAPTOR_X: "raptor_x",
    CoreSimulationSetupType.Q3D_SIM: "q3d",
}


class SimulationSetupDeprecated:
    @property
    def type(self):
        self._pedb.logger.warning("The 'type' property is deprecated. Please use 'setup_type' instead.")
        return self.setup_type

    @property
    def sweeps(self):
        return {i.name: i for i in self.sweep_data}


class SimulationSetup(SimulationSetupDeprecated):
    def __init__(self, pedb, core: "CoreSimulationSetup"):
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

        return [SweepData(self._pedb, core=sweep) for sweep in self.core.sweep_data]

    @sweep_data.setter
    def sweep_data(self, sweeps: list[SweepData]):
        self.core.sweep_data = [sweep.core for sweep in sweeps]

    def _normalize_distribution(self, distribution: str) -> str:
        """Normalize user-provided distribution string to internal code.

        Parameters
        ----------
        distribution : str
            User-specified distribution.

        Returns
        -------
        str
            One of: "LIN", "LINC", "ESTP", "DEC", "OCT".
        """
        if not distribution:
            return "LIN"
        d = distribution.lower().strip()
        if d in ("linear", "linear scale"):
            return "LIN"
        if d in ("linear_count", "linear count"):
            return "LINC"
        if d == "exponential":
            return "ESTP"
        if d in ("decade_count", "decade count", "log scale", "log_scale"):
            return "DEC"
        if d in ("octave_count", "octave count"):
            return "OCT"
        # already an internal code?
        if d.upper() in ("LIN", "LINC", "ESTP", "DEC", "OCT"):
            return d.upper()
        return "LIN"

    def _build_sweep_from_params(
        self, name: str, distribution: str, start_freq, stop_freq, step, discrete: bool
    ) -> SweepData:
        """Construct a SweepData object from normalized parameters."""
        start_freq_val = self._pedb.number_with_units(start_freq, "Hz")
        stop_freq_val = self._pedb.number_with_units(stop_freq, "Hz")
        step_val = str(step)
        sweep = SweepData(
            self._pedb, name=name, distribution=distribution, start_f=start_freq_val, end_f=stop_freq_val, step=step_val
        )
        if discrete:
            # Use the string-based setter to avoid direct enum access
            sweep.type = "discrete"
        return sweep

    def _add_sweeps_from_frequency_set(self, frequency_set, name, init_sweep_count, discrete):
        """Handle the legacy frequency_set format.

        This function creates SweepData entries from the provided frequency_set and
        appends them to the existing core.sweep_data.
        """
        new_sweeps = []
        for sweep_item in frequency_set:
            # detect distribution token and map to internal code
            if "linear_scale" in sweep_item:
                distribution = "LIN"
            elif "linear_count" in sweep_item:
                distribution = "LINC"
            elif "exponential" in sweep_item:
                distribution = "ESTP"
            elif "log_scale" in sweep_item:
                distribution = "DEC"
            elif "octave_count" in sweep_item:
                distribution = "OCT"
            else:
                distribution = "LIN"

            start_freq = self._pedb.number_with_units(sweep_item[1], "Hz")
            stop_freq = self._pedb.number_with_units(sweep_item[2], "Hz")
            step = str(sweep_item[3])
            if not name:
                name = f"sweep_{init_sweep_count + 1}"
            new_sweeps.append(
                SweepData(
                    self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step
                )
            )
            if discrete:
                # Use the string-based setter
                new_sweeps[-1].type = "discrete"
        # append existing core sweep data (preserve previous entries)
        for s in self.core.sweep_data:
            new_sweeps.append(s)
        self.core.sweep_data = new_sweeps

    def _add_single_sweep(self, sweep: SweepData) -> Union[SweepData, None]:
        """Insert a single sweep into core.sweep_data preserving existing sweeps.

        Returns the newly added SweepData on success, None otherwise.
        """
        init_count = len(self.sweep_data)
        # Prepend the new sweep keeping previous ones
        sweep_list = [sweep]
        for s in self.sweep_data:
            sweep_list.append(s)
        sweep_data = [sw.core for sw in sweep_list]
        self.core.sweep_data = sweep_data
        if len(self.sweep_data) == init_count + 1:
            return self.sweep_data[-1]
        return None

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

        This method was refactored to reduce complexity. The behaviour is compatible
        with the previous implementation: it accepts either a legacy `frequency_set`
        or single-sweep parameters.

        Returns
        -------
        SweepData | None
            The newly added sweep when single sweep parameters are used, or None when
            `frequency_set` is provided (legacy multi-sweep behavior).
        """
        # Legacy batch mode
        if frequency_set:
            self._add_sweeps_from_frequency_set(frequency_set, name, len(self.sweep_data), discrete)
            return None

        # Single-sweep mode delegated to helper to reduce complexity
        distribution_code = self._normalize_distribution(distribution)
        if not name:
            name = f"sweep_{len(self.sweep_data) + 1}"

        sweep = self._build_sweep_from_params(name, distribution_code, start_freq, stop_freq, step, discrete)
        result = self._add_single_sweep(sweep)
        if result:
            return result
        self._pedb.logger.error("Failed to add frequency sweep data")
        return None

    def clear_sweeps(self):
        """Clear all frequency sweeps from the simulation setup."""
        self.core.sweep_data = []

    @property
    def setup_type(self) -> str:
        """Get the type of the simulation setup.

        Returns
        -------
        str
            Simulation setup type.
        """
        return _mapping_simulation_types[self.core.type]

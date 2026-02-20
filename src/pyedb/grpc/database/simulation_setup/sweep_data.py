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
    from ansys.edb.core.simulation_setup.simulation_setup import SweepData as CoreSweepData
from ansys.edb.core.simulation_setup.simulation_setup import (
    Distribution as CoreDistribution,
    FreqSweepType as CoreSweepType,
    FrequencyData as CoreFrequencyData,
    SweepData as CoreSweepData,
)

_mapping_distribution = {
    "lin": CoreDistribution.LIN,
    "dec": CoreDistribution.DEC,
    "estp": CoreDistribution.ESTP,
    "linc": CoreDistribution.LINC,
    "oct": CoreDistribution.OCT,
    "LIN": CoreDistribution.LIN,
    "DEC": CoreDistribution.DEC,
    "ESTP": CoreDistribution.ESTP,
    "LINC": CoreDistribution.LINC,
    "OCT": CoreDistribution.OCT,
}

_mapping_sweep_type = {
    "interpolating": CoreSweepType.INTERPOLATING_SWEEP,
    "discrete": CoreSweepType.DISCRETE_SWEEP,
    "broadband": CoreSweepType.BROADBAND_SWEEP,
    "INTERPOLATING": CoreSweepType.INTERPOLATING_SWEEP,
    "DISCRETE": CoreSweepType.DISCRETE_SWEEP,
    "BROADBAND": CoreSweepType.BROADBAND_SWEEP,
}


class FrequencyData:
    def __init__(self, core: "CoreFrequencyData"):
        self._core = core

    @property
    def distribution(self) -> str:
        """Get the distribution type of the frequency data.

        Returns
        -------
        str
            Distribution type. Values are: "lin", "dec", "estp", "linc", "oct".
        """
        return self._core.distribution.name.lower()

    @distribution.setter
    def distribution(self, value: str):
        if value not in _mapping_distribution:
            raise ValueError(
                f"Unsupported distribution type: {value}. Supported types are: {list(_mapping_distribution.keys())}"
            )
        self._core.distribution = _mapping_distribution[value]


    @property
    def start_frequency(self) -> str:
        """Get the start frequency in Hz.

        Returns
        -------
        str
            Start frequency in Hz.
        """
        return self._core.start_f

    @start_frequency.setter
    def start_frequency(self, value: float):
        self._core.start_f = str(value)

    @property
    def end_frequency(self) -> str:
        """Get the end frequency in Hz.

        Returns
        -------
        str
            End frequency in Hz.
        """
        return self._core.end_f

    @end_frequency.setter
    def end_frequency(self, value: float):
        self._core.end_f = str(value)

    @property
    def step(self) -> str:
        """Get the frequency step in Hz.

        Returns
        -------
        str
            Frequency step in Hz.
        """
        return self._core.step

    @step.setter
    def step(self, value: float):
        self._core.step = str(value)


class SweepData:
    """Frequency sweep data class.
    PARAMETERS
    ----------
    pedb : Pedb
        Parent EDB object.
    name : str, default: “”
        Name of the sweep data.
    distribution : str, default: “lin”
        Distribution type of the frequency sweep. Supported types are: "lin", "dec", "estp", "linc", "oct".
    start_f : float, default: 0.0
        Start frequency of the sweep in Hz.
    end_f : float, default: 10e9
        End frequency of the sweep in Hz.
    step : float, default: 10e6
        Frequency step of the sweep in Hz.
    """

    def __init__(
        self,
        pedb,
        name="sweep_data",
        distribution="lin",
        start_f=0.0,
        end_f=10e9,
        step=10e6,
        core: "GrpcSweepData" = None,
        simsetup: "SimulationSetup" = None,
    ):
        self._pedb = pedb
        self.simsetup = simsetup
        if core:
            self.core = core
        else:
            if distribution not in _mapping_distribution:
                raise ValueError(
                    f"Unsupported distribution type: {distribution}. "
                    f"Supported types are: {list(_mapping_distribution.keys())}"
                )
            distribution = _mapping_distribution[distribution]
            self.core = CoreSweepData(
                name=name,
                frequency_data=CoreFrequencyData(
                    distribution=distribution,
                    start_f=str(self._pedb.value(start_f)),
                    end_f=str(self._pedb.value(end_f)),
                    step=str(self._pedb.value(step)),
                ),
            )

    @property
    def name(self) -> str:
        """Get the name of the frequency sweep data."""
        return self.core.name

    @name.setter
    def name(self, value: str):
        """Set the name of the frequency sweep data."""
        self.core.name = value
        self._update_sweep()

    @property
    def frequency_data(self) -> CoreFrequencyData:
        """Get the frequency data of the sweep.

        Returns
        -------
        GrpcFrequencyData
            Frequency data object.
        """
        if isinstance(self.core.frequency_data, list):
            # If frequency_data is a list, return the first element as default
            return [FrequencyData(self.core.frequency_data[i]) for i in range(len(self.core.frequency_data))]
        return [FrequencyData(self.core.frequency_data)]

    def add_frequency_data(self, distribution: str, start_f: float, end_f: float, step: float):
        """Add frequency data to the sweep.

        Parameters
        ----------
        distribution : str
            Distribution type of the frequency data. Supported types are: "lin", "dec", "estp", "linc", "oct".
        start_f : float
            Start frequency in Hz.
        end_f : float
            End frequency in Hz.
        step : float
            Frequency step in Hz.
        """
        if distribution not in _mapping_distribution:
            raise ValueError(
                f"Unsupported distribution type: {distribution}. Supported types are: {list(_mapping_distribution.keys())}"
            )
        distribution = _mapping_distribution[distribution]
        frequency_data = CoreFrequencyData(
            distribution=distribution,
            start_f=str(self._pedb.value(start_f)),
            end_f=str(self._pedb.value(end_f)),
            step=str(self._pedb.value(step)),
        )
        if isinstance(self.core.frequency_data, list):
            self.core.frequency_data.append(frequency_data)
        else:
            self.core.frequency_data = [self.core.frequency_data, frequency_data]
        return True

    @property
    def enabled(self) -> bool:
        """Get the enabled status of the frequency sweep.

        Returns
        -------
        bool
            Enabled status.
        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.core.enabled = value
        self._update_sweep()

    @property
    def type(self) -> str:
        """Get the type of the frequency sweep.

        Returns
        -------
        str
            Frequency sweep type. Values are: "interpolating", "discrete", "broadband".
        """
        return self.core.type.name.lower().split("_")[0]

    @type.setter
    def type(self, value: str):
        if value not in _mapping_sweep_type:
            raise ValueError(
                f"Unsupported sweep type: {value}. Supported types are: {list(_mapping_sweep_type.keys())}"
            )
        self.core.type = _mapping_sweep_type[value]
        self._update_sweep()

    @property
    def use_q3d_for_dc(self) -> bool:
        """Get the flag indicating if Q3D is used for DC bias.

        Returns
        -------
        bool
            True if Q3D is used for DC bias, False otherwise.
        """
        return self.core.use_q3d_for_dc

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value: bool):
        self.core.use_q3d_for_dc = value
        self._update_sweep()

    @property
    def save_fields(self) -> bool:
        """Get the flag indicating if fields are saved during the sweep.

        Returns
        -------
        bool
            True if fields are saved, False otherwise.
        """
        return self.core.save_fields

    @save_fields.setter
    def save_fields(self, value: bool):
        self.core.save_fields = value
        self._update_sweep()

    @property
    def save_rad_fields_only(self) -> bool:
        """Get the flag indicating if only radiation fields are saved.

        Returns
        -------
        bool
            True if only radiation fields are saved, False otherwise.
        """
        return self.core.save_rad_fields_only

    @save_rad_fields_only.setter
    def save_rad_fields_only(self, value: bool):
        self.core.save_rad_fields_only = value

    @property
    def compute_dc_point(self) -> bool:
        """Get the flag indicating if DC point is computed.

        Returns
        -------
        bool
            True if DC point is computed, False otherwise.
        """
        return self.core.compute_dc_point

    @compute_dc_point.setter
    def compute_dc_point(self, value: bool):
        self.core.compute_dc_point = value
        self._update_sweep()


    @property
    def siwave_with_3dddm(self) -> bool:
        """Get the flag indicating if SIwave with 3D-DDM is used.

        Returns
        -------
        bool
            True if SIwave with 3D-DDM is used, False otherwise.
        """
        return self.core.siwave_with_3dddm

    @siwave_with_3dddm.setter
    def siwave_with_3dddm(self, value: bool):
        self.core.siwave_with_3dddm = value
        self._update_sweep()

    @property
    def adv_dc_extrapolation(self) -> bool:
        """Get the flag indicating if advanced DC extrapolation is used.

        Returns
        -------
        bool
            True if advanced DC extrapolation is used, False otherwise.
        """
        #to be implemented in edb core, currently does not exist in edb core
        return  False

    @adv_dc_extrapolation.setter
    def adv_dc_extrapolation(self, value: bool):
        #to be implemented in edb core, currently does not exist in edb core
        pass

    @property
    def use_hfss_solver_regions(self) -> bool:
        """Get the flag indicating if HFSS solver regions are used.

        Returns
        -------
        bool
            True if HFSS solver regions are used, False otherwise.
        """
        return self.core.use_hfss_solver_regions

    @use_hfss_solver_regions.setter
    def use_hfss_solver_regions(self, value: bool):
        self.core.use_hfss_solver_regions = value
        self._update_sweep()

    @property
    def frequency_string(self) -> str:
        """Get the frequency sweep string.

        Returns
        -------
        str
            Frequency sweep string.
        """
        return self.core.frequency_string.strip()
    
    @frequency_string.setter
    def frequency_string(self, value: str):
        self.core.frequency_string = value
        self._update_sweep()

    @property
    def enforce_causality(self) -> bool:
        """Get the flag indicating if causality is enforced.

        Returns
        -------
        bool
            True if causality is enforced, False otherwise.
        """
        return self.core.interpolation_data.enforce_causality

    @enforce_causality.setter
    def enforce_causality(self, value: bool):
        self.core.interpolation_data.enforce_causality = value
        self._update_sweep()

    @property
    def enforce_passivity(self) -> bool:
        """Get the flag indicating if passivity is enforced.

        Returns
        -------
        bool
            True if passivity is enforced, False otherwise.
        """
        return self.core.interpolation_data.enforce_passivity

    @enforce_passivity.setter
    def enforce_passivity(self, value: bool):
        self.core.interpolation_data.enforce_passivity = value
        self._update_sweep()

    @property
    def interpolation_data(self):
        """Get the interpolation data points.

        Returns
        -------
        list[float]
            List of interpolation data points in Hz.
        """
        return self.core.interpolation_data

    def _update_sweep(self):
        """Update the sweep."""
        sweepdata = self.simsetup.core.sweep_data
        new_data = []
        for i in sweepdata:
            if i.name == self.name:
                new_data.append(self.core)
            else:
                new_data.append(i)

        self.simsetup.core.sweep_data = new_data
        return

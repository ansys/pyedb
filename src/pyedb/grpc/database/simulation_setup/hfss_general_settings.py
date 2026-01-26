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
        AdaptType as GrpcAdaptType,
        HFSSGeneralSettings as GrpcHFSSGeneralSettings,
    )


class BroadbandAdaptiveSolution:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def high_frequency(self) -> str:
        """High frequency for broadband adaptive solution.

        Returns
        -------
        float
            High frequency value in Hz.

        """
        return self.core.high_frequency

    @high_frequency.setter
    def high_frequency(self, value):
        self.core.high_frequency = str(value)

    @property
    def low_frequency(self) -> str:
        """Low frequency for broadband adaptive solution.

        Returns
        -------
        float
            Low frequency value in Hz.

        """
        return self.core.low_frequency

    @low_frequency.setter
    def low_frequency(self, value):
        self.core.low_frequency = str(value)

    @property
    def max_delta(self) -> str:
        """Maximum delta for broadband adaptive solution.

        Returns
        -------
        float
            Maximum delta value.

        """
        return self.core.max_delta

    @max_delta.setter
    def max_delta(self, value):
        self.core.max_delta = str(value)

    @property
    def max_num_passes(self) -> int:
        """Maximum number of passes for broadband adaptive solution.

        Returns
        -------
        int
            Maximum number of passes.

        """
        return self.core.max_num_passes

    @max_num_passes.setter
    def max_num_passes(self, value):
        self.core.max_num_passes = value


class AdaptiveFrequency:
    def __init__(self, pedb, core):
        """Represents an adaptive frequency."""
        self._pedb = pedb
        self.core = core

    @property
    def adaptive_frequency(self) -> str:
        """Adaptive frequency value.

        Returns
        -------
        float
            Adaptive frequency in Hz.

        """
        return self.core.adaptive_frequency

    @adaptive_frequency.setter
    def adaptive_frequency(self, value):
        self.core.adaptive_frequency = str(value)

    @property
    def max_delta(self) -> str:
        """Maximum delta for the adaptive frequency.

        Returns
        -------
        float
            Maximum delta value.

        """
        return self.core.max_delta

    @max_delta.setter
    def max_delta(self, value):
        self.core.max_delta = str(value)

    @property
    def output_variables(self) -> dict[str, float]:
        """Map of output variable names to maximum delta S.

        Returns
        -------
        dict[str, float]
            Dictionary of output variable names and delta S value.

        """
        return {var_name: self._pedb.value(value) for var_name, value in self.core.output_variables.items()}

    def add_output_variable(self, name: str, delta_s: float):
        """Add an output variable for the adaptive frequency.

        Parameters
        ----------
        name : str
            Name of the output variable.
        delta_s : float
            Delta S value.

        """
        variables = self.output_variables
        variables[name] = delta_s
        self.core.output_variables = variables

    def delete_output_variable(self, name: str) -> bool:
        """Delete an output variable from the adaptive frequency.

        Parameters
        ----------
        name : str
            Name of the output variable to delete.

        Returns
        -------
        bool

        """
        variables = self.output_variables
        if name in variables:
            del variables[name]
            self.core.output_variables = variables
            return True  #
        else:
            self._pedb.logger.warning(f"Output variable '{name}' not found.")
        return False


class MultiFrequencyAdaptiveSolution:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def adaptive_frequencies(self) -> list[AdaptiveFrequency]:
        return [AdaptiveFrequency(self._pedb, freq) for freq in self.core.adaptive_frequencies]

    @property
    def max_passes(self) -> int:
        """Maximum number of passes for multi-frequency adaptive solution.

        Returns
        -------
        int
            Maximum number of passes.

        """
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value):
        self.core.max_passes = value


class MatrixConvergenceDataEntry:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def mag_limit(self) -> float:
        """Magnitude limit for the matrix convergence data entry.

        Returns
        -------
        float
            Magnitude limit value.

        """
        return self._pedb.value(self.core.mag_limit)

    @mag_limit.setter
    def mag_limit(self, value):
        self.core.mag_limit = self._pedb.value(value)

    @property
    def phase_limit(self) -> float:
        """Phase limit for the matrix convergence data entry.

        Returns
        -------
        float
            Phase limit value.

        """
        return self._pedb.value(self.core.phase_limit)

    @phase_limit.setter
    def phase_limit(self, value):
        self.core.phase_limit = self._pedb.value(value)

    @property
    def port_1_name(self) -> str:
        """Name of the first port.

        Returns
        -------
        str
            First port name.

        """
        return self.core.port_1_name

    @port_1_name.setter
    def port_1_name(self, value):
        self.core.port_1_name = value

    @property
    def port_2_name(self) -> str:
        """Name of the second port.

        Returns
        -------
        str
            Second port name.

        """
        return self.core.port_2_name

    @port_2_name.setter
    def port_2_name(self, value):
        self.core.port_2_name = value


class MatrixConvergenceData:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def all_constant(self) -> bool:
        """Indicates whether all matrix convergence data entries are constant.

        Returns
        -------
        bool
            True if all entries are constant, False otherwise.

        """
        return self.core.all_constant

    @all_constant.setter
    def all_constant(self, value: bool):
        self.core.all_constant = value

    @property
    def all_diag_constant(self) -> bool:
        """Indicates whether all diagonal matrix convergence data entries are constant.

        Returns
        -------
        bool
            True if all diagonal entries are constant, False otherwise.

        """
        return self.core.all_diag_constant

    @all_diag_constant.setter
    def all_diag_constant(self, value: bool):
        self.core.all_diag_constant = value

    @property
    def all_off_diag_constant(self) -> bool:
        """Indicates whether all off-diagonal matrix convergence data entries are constant.

        Returns
        -------
        bool
            True if all off-diagonal entries are constant, False otherwise.

        """
        return self.core.all_off_diag_constant

    @all_off_diag_constant.setter
    def all_off_diag_constant(self, value: bool):
        self.core.all_off_diag_constant = value

    @property
    def entry_list(self) -> list[MatrixConvergenceDataEntry]:
        """List of matrix convergence data entries.

        Returns
        -------
        list[MatrixConvergenceDataEntry]
            List of matrix convergence data entries.

        """
        return [MatrixConvergenceDataEntry(self._pedb, entry) for entry in self.core.entry_list]

    @property
    def mag_min_threshold(self) -> float:
        """Magnitude minimum threshold for matrix convergence data.

        Returns
        -------
        float
            Magnitude minimum threshold value.

        """
        return self._pedb.value(self.core.mag_min_threshold)

    @mag_min_threshold.setter
    def mag_min_threshold(self, value):
        self.core.mag_min_threshold = self._pedb.value(value)

    def add_entry(self, port_name_1, port_name_2, mag_limit, phase_limit):
        """Add a matrix convergence data entry.

        Parameters
        ----------
        port_name_1 : str
            Name of the first port.
        port_name_2 : str
            Name of the second port.
        mag_limit : float
            Magnitude limit.
        phase_limit : float
            Phase limit.
        """
        self.core.add_entry(port_name_1, port_name_2, mag_limit, phase_limit)

    def set_all_constant(self, mag_limit, phase_limit, port_names):
        """Set all matrix convergence data entries to constant values.

        Parameters
        ----------
        mag_limit : float
            Magnitude limit.
        phase_limit : float
            Phase limit.
        port_names : list[str]
            List of port names.
        """
        self.core.set_all_constant(mag_limit, phase_limit, port_names)

    def set_all_diag_constant(self, mag_limit, phase_limit, port_names, clear_entries):
        """Set all diagonal matrix convergence data entries to constant values.

        Parameters
        ----------
        mag_limit : float
            Magnitude limit.
        phase_limit : float
            Phase limit.
        port_names : list[str]
            List of port names.
        clear_entries : bool
            Whether to clear existing entries.
        """
        self.core.set_all_diag_constant(mag_limit, phase_limit, port_names, clear_entries)

    def set_all_off_diag_constant(self, mag_limit, phase_limit, port_names, clear_entries):
        """Set all off-diagonal matrix convergence data entries to constant values.

        Parameters
        ----------
        mag_limit : float
            Magnitude limit.
        phase_limit : float
            Phase limit.
        port_names : list[str]
            List of port names.
        clear_entries : bool
            Whether to clear existing entries.
        """
        self.core.set_all_off_diag_constant(mag_limit, phase_limit, port_names, clear_entries)


class SingleFrequencyAdaptiveSolution:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def adaptive_frequency(self) -> float:
        """Adaptive frequency for single frequency adaptive solution.

        Returns
        -------
        float
            Adaptive frequency in Hz.

        """
        return self.core.adaptive_frequency

    @adaptive_frequency.setter
    def adaptive_frequency(self, value):
        self.core.adaptive_frequency = str(self._pedb.value(value))

    @property
    def max_delta(self) -> float:
        """Maximum delta for single frequency adaptive solution.

        Returns
        -------
        float
            Maximum delta value.

        """
        return self.core.max_delta

    @max_delta.setter
    def max_delta(self, value):
        self.core.max_delta = str(value)

    @property
    def max_passes(self) -> int:
        """Maximum number of passes for single frequency adaptive solution.

        Returns
        -------
        int
            Maximum number of passes.

        """
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value):
        self.core.max_passes = value

    @property
    def mx_conv_data(self) -> MatrixConvergenceData:
        """Matrix convergence data for single frequency adaptive solution.

        Returns
        -------
        :class:`MatrixConvergenceData
        <pyedb.grpc.database.simulation_setup.hfss_general_settings.MatrixConvergenceData>`
            Matrix convergence data object.

        """
        return MatrixConvergenceData(self._pedb, self.core.mx_conv_data)

    @property
    def use_mx_conv_data(self) -> bool:
        """Indicates whether to use matrix convergence data.

        Returns
        -------
        bool
            True if matrix convergence data is used, False otherwise.

        """
        return self.core.use_mx_conv_data

    @use_mx_conv_data.setter
    def use_mx_conv_data(self, value: bool):
        self.core.use_mx_conv_data = value


class HFSSGeneralSettings:
    """PyEDB-core HFSS general settings class."""

    def __init__(self, pedb, core: "GrpcHFSSGeneralSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def adapt_type(self) -> str:
        """Adaptation type.

        ..deprecated:: 0.67.0
            This property is deprecated and will be removed in future versions.
            Attribute added for dotnet compatibility.
            Use :attr:`adaptive_solution_type` instead.

        """
        warnings.warn(
            "The 'adapt_type' property is deprecated and will be removed in future versions. "
            "Use 'adaptive_solution_type' instead.",
            DeprecationWarning,
        )
        return self.adaptive_solution_type.name.lower()

    @property
    def adaptive_solution_type(self) -> str:
        """Adaptive solution type.

        Returns
        -------
        str
            Adaptive solution type name. Returned values are `single`, `multi_frequencies`, `broad_band`,
            or `num_adapt_type`.

        """
        return self.core.adaptive_solution_type

    @adaptive_solution_type.setter
    def adaptive_solution_type(self, value):
        if isinstance(value, str):
            if value.lower() == "single":
                self.core.adaptive_solution_type = GrpcAdaptType.SINGLE
            elif value.lower() == "multi_frequencies":
                self.core.adaptive_solution_type = GrpcAdaptType.MULTI_FREQUENCIES
            elif value.lower() == "broad_band":
                self.core.adaptive_solution_type = GrpcAdaptType.BROADBAND
            elif value.lower() == "num_adapt_type":
                self.core.adaptive_solution_type = GrpcAdaptType.NUM_ADAPT_TYPE

    @property
    def broadband_adaptive_solution(self) -> BroadbandAdaptiveSolution:
        """Settings for a broadband adaptive solution.

        Returns
        -------
        :class:`HFSSBroadbandAdaptiveSolution
        <pyedb.grpc.database.simulation_setup.hfss_simulation_settings.HFSSBroadbandAdaptiveSolution>`
            Broadband adaptive solution settings object.

        """
        return BroadbandAdaptiveSolution(self._pedb, self.core.broadband_adaptive_solution)

    @property
    def mesh_region_name(self) -> str:
        """Name of the mesh region to use.

        Returnsself.core.broadband_adaptive_solution
        -------
        str
            Mesh region name.

        """
        return self.core.mesh_region_name

    @mesh_region_name.setter
    def mesh_region_name(self, value):
        self.core.mesh_region_name = value

    @property
    def multi_frequency_adaptive_solution(self) -> MultiFrequencyAdaptiveSolution:
        return MultiFrequencyAdaptiveSolution(self._pedb, self.core)

    @property
    def save_fields(self) -> bool:
        """Indicates whether to save fields.

        Returns
        -------
        bool
            True if fields are to be saved, False otherwise.

        """
        return self.core.save_fields

    @save_fields.setter
    def save_fields(self, value: bool):
        self.core.save_fields = value

    @property
    def save_rad_field_only(self) -> bool:
        """Indicates whether to save radiation field only.

        .. deprecated:: 0.67.0
            This property is deprecated and will be removed in future versions.
            Use :attr:`save_rad_fields_only` instead.

        """
        warnings.warn(
            "The 'save_rad_field_only' property is deprecated and will be removed in future versions. "
            "Use 'save_rad_fields_only' instead.",
            DeprecationWarning,
        )
        return self.save_rad_fields_only

    @save_rad_field_only.setter
    def save_rad_field_only(self, value: bool):
        warnings.warn(
            "The 'save_rad_field_only' property is deprecated and will be removed in future versions. "
            "Use 'save_rad_fields_only' instead.",
            DeprecationWarning,
        )
        self.save_rad_fields_only = value

    @property
    def save_rad_fields_only(self) -> bool:
        """Indicates whether to save radiation fields only.

        Returns
        -------
        bool
            True if only radiation fields are to be saved, False otherwise.

        """
        return self.core.save_rad_fields_only

    @save_rad_fields_only.setter
    def save_rad_fields_only(self, value: bool):
        self.core.save_rad_fields_only = value

    @property
    def single_frequency_adaptive_solution(self):
        return SingleFrequencyAdaptiveSolution(self._pedb, self.core.single_frequency_adaptive_solution)

    @property
    def use_mesh_region(self) -> bool:
        """Indicates whether to use a mesh region.

        Returns
        -------
        bool
            True if a mesh region is used, False otherwise.

        """
        return self.core.use_mesh_region

    @use_mesh_region.setter
    def use_mesh_region(self, value: bool):
        self.core.use_mesh_region = value

    @property
    def use_parallel_refinement(self) -> bool:
        """Indicates whether to use parallel refinement.

        Returns
        -------
        bool
            True if parallel refinement is used, False otherwise.

        """
        return self.core.use_parallel_refinement

    @use_parallel_refinement.setter
    def use_parallel_refinement(self, value: bool):
        self.core.use_parallel_refinement = value

    @property
    def max_refine_per_pass(self) -> float:
        """Maximum refinement per pass.

        .. deprecated:: 0.67.0
        This property is deprecated and will be removed in future versions.
        use settings.options.max_refinement_per_pass instead.

        """
        warnings.warn(
            "Use of 'max_refine_per_pass' is deprecated and will be removed in future versions."
            "Use 'settings.options.max_refinement_per_pass' instead.",
            DeprecationWarning,
        )
        return self._pedb.settings.options.max_refinement_per_pass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value: float):
        self._pedb.settings.options.max_refinement_per_pass = value

    @property
    def min_passes(self) -> int:
        """Minimum number of passes.

        .. deprecated:: 0.67.0
        This property is deprecated and will be removed in future versions.
        use settings.options.min_passes instead.

        """
        warnings.warn(
            "Use of 'min_passes' is deprecated and will be removed in future versions."
            "Use 'settings.options.min_passes' instead.",
            DeprecationWarning,
        )
        return self._pedb.settings.options.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        self._pedb.settings.options.min_passes = value

    @property
    def use_max_refinement(self) -> bool:
        """Indicates whether to use maximum refinement.

        .. deprecated:: 0.67.0
        This property is deprecated and will be removed in future versions.
        use settings.options.use_max_refinement instead.

        """
        warnings.warn(
            "Use of 'use_max_refinement' is deprecated and will be removed in future versions."
            "Use 'settings.options.use_max_refinement' instead.",
            DeprecationWarning,
        )
        return self._pedb.settings.options.use_max_refinement

    @use_max_refinement.setter
    def use_max_refinement(self, value: bool):
        self._pedb.settings.options.use_max_refinement = value

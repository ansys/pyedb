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


from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
    SIWaveAdvancedSettings as GrpcSIWaveAdvancedSettings,
)


class SIWaveAdvancedSettings:
    """SIWave advanced settings class."""

    def __init__(self, pedb, core: "GrpcSIWaveAdvancedSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def ac_dc_merge_mode(self) -> int:
        """AC/DC merge mode.

        Returns
        -------
        int
            AC/DC merge mode.
        """
        return self.core.ac_dc_merge_mode

    @ac_dc_merge_mode.setter
    def ac_dc_merge_mode(self, value: int):
        self.core.ac_dc_merge_mode = value

    @property
    def cross_talk_threshold(self) -> float:
        """Cross talk threshold.

        Returns
        -------
        float
            Cross talk threshold.
        """
        return self._pedb.value(self.core.cross_talk_threshold)

    @cross_talk_threshold.setter
    def cross_talk_threshold(self, value: float):
        self.core.cross_talk_threshold = str(self._pedb.value(value))

    @property
    def ignore_non_functional_pads(self) -> bool:
        """Ignore non-functional pads flag.

        Returns
        -------
        bool
            Ignore non-functional pads flag.
        """
        return self.core.ignore_non_functional_pads

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value: bool):
        self.core.ignore_non_functional_pads = value

    @property
    def include_co_plane_coupling(self) -> bool:
        """Include co-plane coupling flag.

        Returns
        -------
        bool
            Include co-plane coupling flag.
        """
        return self.core.include_co_plane_coupling

    @include_co_plane_coupling.setter
    def include_co_plane_coupling(self, value: bool):
        self.core.include_co_plane_coupling = value

    @property
    def include_fringe_plane_coupling(self) -> bool:
        """Include fringe plane coupling flag.

        Returns
        -------
        bool
            Include fringe plane coupling flag.
        """
        return self.core.include_fringe_plane_coupling

    @include_fringe_plane_coupling.setter
    def include_fringe_plane_coupling(self, value: bool):
        self.core.include_fringe_plane_coupling = value

    @property
    def include_inf_gnd(self) -> bool:
        """Include infinite ground flag.

        Returns
        -------
        bool
            Include infinite ground flag.
        """
        return self.core.include_inf_gnd

    @include_inf_gnd.setter
    def include_inf_gnd(self, value: bool):
        self.core.include_inf_gnd = value

    @property
    def include_inter_plane_coupling(self) -> bool:
        """Include inter-plane coupling flag.

        Returns
        -------
        bool
            Include inter-plane coupling flag.
        """
        return self.core.include_inter_plane_coupling

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value: bool):
        self.core.include_inter_plane_coupling = value

    @property
    def include_split_plane_coupling(self) -> bool:
        """Include split plane coupling flag.

        Returns
        -------
        bool
            Include split plane coupling flag.
        """
        return self.core.include_split_plane_coupling

    @include_split_plane_coupling.setter
    def include_split_plane_coupling(self, value: bool):
        self.core.include_split_plane_coupling = value

    @property
    def include_trace_plane_coupling(self) -> bool:
        """Include trace-plane coupling flag.

        Returns
        -------
        bool
            Include trace-plane coupling flag.
        """
        return self.core.include_trace_plane_coupling

    @include_trace_plane_coupling.setter
    def include_trace_plane_coupling(self, value: bool):
        self.core.include_trace_plane_coupling = value

    @property
    def include_vi_sources(self) -> bool:
        """Include VI sources flag.

        Returns
        -------
        bool
            Include VI sources flag.
        """
        return self.core.include_vi_sources

    @include_vi_sources.setter
    def include_vi_sources(self, value: bool):
        self.core.include_vi_sources = value

    @property
    def inf_gnd_location(self) -> float:
        """Infinite ground location.

        Returns
        -------
        float
            Infinite ground location.
        """
        return self._pedb.value(self.core.inf_gnd_location)

    @inf_gnd_location.setter
    def inf_gnd_location(self, value: float):
        self.core.inf_gnd_location = str(self._pedb.value(value))

    @property
    def max_coupled_lines(self) -> int:
        """Maximum coupled lines.

        Returns
        -------
        int
            Maximum coupled lines.
        """
        return self.core.max_coupled_lines

    @max_coupled_lines.setter
    def max_coupled_lines(self, value: int):
        self.core.max_coupled_lines = value

    @property
    def mesh_automatic(self) -> bool:
        """Automatic mesh flag.

        Returns
        -------
        bool
            Automatic mesh flag.
        """
        return self.core.mesh_automatic

    @mesh_automatic.setter
    def mesh_automatic(self, value: bool):
        self.core.mesh_automatic = value

    @property
    def mesh_frequency(self) -> float:
        """Mesh frequency.

        Returns
        -------
        float
            Mesh frequency.
        """
        return self._pedb.value(self.core.mesh_frequency)

    @mesh_frequency.setter
    def mesh_frequency(self, value: float):
        self.core.mesh_frequency = str(self._pedb.value(value))

    @property
    def min_pad_area_to_mesh(self) -> float:
        """Minimum pad area to mesh.

        Returns
        -------
        float
            Minimum pad area to mesh.
        """
        return self._pedb.value(self.core.min_pad_area_to_mesh)

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value: float):
        self.core.min_pad_area_to_mesh = str(self._pedb.value(value))

    @property
    def min_plane_area_to_mesh(self) -> float:
        """Minimum plane area to mesh.

        Returns
        -------
        float
            Minimum plane area to mesh.
        """
        return self._pedb.value(self.core.min_plane_area_to_mesh)

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value: float):
        self.core.min_plane_area_to_mesh = str(self._pedb.value(value))

    @property
    def min_void_area(self) -> float:
        """Minimum void area.

        Returns
        -------
        float
            Minimum void area.
        """
        return self._pedb.value(self.core.min_void_area)

    @min_void_area.setter
    def min_void_area(self, value: float):
        self.core.min_void_area = str(self._pedb.value(value))

    @property
    def perform_erc(self) -> bool:
        """Perform ERC flag.

        Returns
        -------
        bool
            Perform ERC flag.
        """
        return self.core.perform_erc

    @perform_erc.setter
    def perform_erc(self, value: bool):
        self.core.perform_erc = value

    @property
    def return_current_distribution(self) -> bool:
        """Return current distribution flag.

        Returns
        -------
        bool
            Return current distribution flag.
        """
        return self.core.return_current_distribution

    @return_current_distribution.setter
    def return_current_distribution(self, value: bool):
        self.core.return_current_distribution = value

    @property
    def snap_length_threshold(self) -> float:
        """Snap length threshold.

        Returns
        -------
        float
            Snap length threshold.
        """
        return self._pedb.value(self.core.snap_length_threshold)

    @snap_length_threshold.setter
    def snap_length_threshold(self, value: float):
        self.core.snap_length_threshold = str(self._pedb.value(value))

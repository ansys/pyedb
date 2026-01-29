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
        HFSSSolverSettings as CoreHFSSSolverSettings,
    )


class HFSSSolverSettings:
    """HFSS solver settings class."""

    def __init__(self, pedb, core: "CoreHFSSSolverSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def enable_intra_plane_coupling(self) -> bool:
        """Flag indicating if intra-plane coupling of power/ground nets is enabled to enhance accuracy.."""
        return self.core.enable_intra_plane_coupling

    @enable_intra_plane_coupling.setter
    def enable_intra_plane_coupling(self, value: bool):
        self.core.enable_intra_plane_coupling = value

    @property
    def max_delta_z0(self) -> float:
        """Maximum percent change in characteristic impedance of ports between adaptive passes."""
        return self.core.max_delta_z0

    @max_delta_z0.setter
    def max_delta_z0(self, value: float):
        self.core.max_delta_z0 = value

    @property
    def max_triangles_wave_port(self) -> int:
        """Maximum number of triangles to use for meshing wave-ports."""
        warnings.warn(
            "max_triangles_wave_port is deprecated. Use max_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        return self.core.max_triangles_for_wave_port

    @max_triangles_wave_port.setter
    def max_triangles_wave_port(self, value: int):
        warnings.warn(
            "max_triangles_wave_port is deprecated. Use max_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        self.core.max_triangles_for_wave_port = value

    @property
    def max_triangles_for_wave_port(self) -> int:
        """Maximum number of triangles to use for meshing wave-ports."""
        return self.core.max_triangles_for_wave_port

    @max_triangles_for_wave_port.setter
    def max_triangles_for_wave_port(self, value: int):
        self.core.max_triangles_for_wave_port = value

    @property
    def min_triangles_wave_port(self) -> int:
        """Minimum number of triangles to use for meshing wave-ports."""
        warnings.warn(
            "min_triangles_wave_port is deprecated. Use min_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        return self.core.min_triangles_for_wave_port

    @min_triangles_wave_port.setter
    def min_triangles_wave_port(self, value: int):
        warnings.warn(
            "min_triangles_wave_port is deprecated. Use min_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        self.core.min_triangles_for_wave_port = value

    @property
    def min_triangles_for_wave_port(self) -> int:
        """Minimum number of triangles to use for meshing wave-ports."""
        return self.core.min_triangles_for_wave_port

    @min_triangles_for_wave_port.setter
    def min_triangles_for_wave_port(self, value: int):
        self.core.min_triangles_for_wave_port = value

    @property
    def enable_set_triangles_wave_port(self) -> bool:
        """Flag indicating if the minimum and maximum triangle values for wave-ports are used."""
        warnings.warn(
            "enable_set_triangles_wave_port is deprecated. Use set_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        return self.core.set_triangles_for_wave_port

    @enable_set_triangles_wave_port.setter
    def enable_set_triangles_wave_port(self, value: bool):
        warnings.warn(
            "enable_set_triangles_wave_port is deprecated. Use set_triangles_for_wave_port instead.",
            DeprecationWarning,
        )
        self.core.set_triangles_for_wave_port = value

    @property
    def set_triangles_for_wave_port(self) -> bool:
        """Flag indicating ifthe minimum and maximum triangle values for wave-ports are used."""
        return self.core.set_triangles_for_wave_port

    @set_triangles_for_wave_port.setter
    def set_triangles_for_wave_port(self, value: bool):
        self.core.set_triangles_for_wave_port = value

    @property
    def thin_dielectric_layer_threshold(self) -> float:
        """Value below which dielectric layers are merged with adjacent dielectric layers."""
        return self._pedb.value(self.core.thin_dielectric_layer_threshold)

    @thin_dielectric_layer_threshold.setter
    def thin_dielectric_layer_threshold(self, value: float):
        self.core.thin_dielectric_layer_threshold = str(self._pedb.value(value))

    @property
    def thin_signal_layer_threshold(self) -> float:
        """Value below which signal layers are merged with adjacent signal layers."""
        return self._pedb.value(self.core.thin_signal_layer_threshold)

    @thin_signal_layer_threshold.setter
    def thin_signal_layer_threshold(self, value: float):
        self.core.thin_signal_layer_threshold = str(self._pedb.value(value))

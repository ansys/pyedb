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
    from ansys.edb.core.simulation_setup.siwave_simulation_settings import SIWaveDCSettings as GrpcSIWaveDCSettings


class SIWaveDCSettings:
    def __init__(self, pedb, core: GrpcSIWaveDCSettings):
        """PyEDB SIWave simulation settings class."""
        self.core = core
        self._pedb = pedb

    @property
    def compute_inductance(self) -> bool:
        """Compute inductance flag.

        Returns
        -------
        bool
            True if compute inductance is enabled, False otherwise.

        """
        return self.core.compute_inductance

    @compute_inductance.setter
    def compute_inductance(self, value: bool):
        """Set compute inductance flag.

        Parameters
        ----------
        value : bool
            True to enable compute inductance, False to disable.

        """
        self.core.compute_inductance = value

    @property
    def contact_radius(self) -> float:
        """Contact radius value.

        Returns
        -------
        float
            Contact radius.

        """
        return self._pedb.value(self.core.contact_radius.value)

    @contact_radius.setter
    def contact_radius(self, value: float):
        """Set contact radius value.

        Parameters
        ----------
        value : float
            Contact radius.

        """
        self.core.contact_radius = str(self._pedb.value(value))

    @property
    def dc_slider_pos(self) -> int:
        """DC slider position.

        Returns
        -------
        int
            DC slider position.

        """
        return self.core.dc_slider_pos

    @dc_slider_pos.setter
    def dc_slider_pos(self, value: int):
        self.core.dc_slider_pos = value

    @property
    def plot_jv(self) -> bool:
        """Plot JV flag.

        Returns
        -------
        bool
            True if plot JV is enabled, False otherwise.

        """
        return self.core.plot_jv

    @plot_jv.setter
    def plot_jv(self, value: bool):
        self.core.plot_jv = value

    @property
    def use_dc_custom_settings(self) -> bool:
        """Use DC custom settings flag.

        Returns
        -------
        bool
            True if DC custom settings are used, False otherwise.

        """
        return self.core.use_dc_custom_settings

    @use_dc_custom_settings.setter
    def use_dc_custom_settings(self, value: bool):
        self.core.use_dc_custom_settings = value

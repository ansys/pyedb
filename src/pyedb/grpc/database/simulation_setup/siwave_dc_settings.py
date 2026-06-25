# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
    from ansys.edb.core.simulation_setup.siwave_dcir_simulation_setup import (
        SIWaveDCIRSimulationSettings as CoreSIWaveDCIRSettings,
    )
    from ansys.edb.core.simulation_setup.siwave_simulation_settings import SIWaveDCSettings as CoreSIWaveDCSettings


class SIWaveDCSettings:
    def __init__(self, pedb, core: "CoreSIWaveDCSettings"):
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
    def contact_radius(self) -> str:
        """Contact radius value.

        Returns
        -------
        str
            Contact radius.

        """
        return self.core.contact_radius

    @contact_radius.setter
    def contact_radius(self, value: str):
        self.core.contact_radius = value

    @property
    def dc_slider_position(self) -> int:
        """DC slider position.

        Returns
        -------
        int
            DC slider position.

        """
        return self.core.dc_slider_pos

    @dc_slider_position.setter
    def dc_slider_position(self, value: int):
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


class SIWaveDCIRDCSettings(SIWaveDCSettings):
    """SIWave DC settings for DCIR setups — extends base DC settings with DCIR-specific properties
    accessible via the parent DCIR settings core.
    """

    def __init__(self, pedb, dc_core: "CoreSIWaveDCSettings", dcir_core: "CoreSIWaveDCIRSettings"):
        super().__init__(pedb, dc_core)
        self._dcir_core = dcir_core

    @property
    def dc_report_config_file(self) -> str:
        """DC report configuration file path."""
        return self._dcir_core.dc_report_config_file

    @dc_report_config_file.setter
    def dc_report_config_file(self, value: str):
        self._dcir_core.dc_report_config_file = value

    @property
    def dc_report_show_active_devices(self) -> bool:
        """Whether to show active devices in the DC report."""
        return self._dcir_core.dc_report_show_active_devices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value: bool):
        self._dcir_core.dc_report_show_active_devices = value

    @property
    def export_dc_thermal_data(self) -> bool:
        """Whether to export DC thermal data."""
        return self._dcir_core.export_dc_thermal_data

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value: bool):
        self._dcir_core.export_dc_thermal_data = value

    @property
    def full_dc_report_path(self) -> str:
        """Full DC report path."""
        return self._dcir_core.full_dc_report_path

    @full_dc_report_path.setter
    def full_dc_report_path(self, value: str):
        self._dcir_core.full_dc_report_path = value

    @property
    def icepak_temp_file(self) -> str:
        """Icepak temperature file path."""
        return self._dcir_core.icepak_temp_file

    @icepak_temp_file.setter
    def icepak_temp_file(self, value: str):
        self._dcir_core.icepak_temp_file = value

    @property
    def import_thermal_data(self) -> bool:
        """Whether to import thermal data."""
        return self._dcir_core.import_thermal_data

    @import_thermal_data.setter
    def import_thermal_data(self, value: bool):
        self._dcir_core.import_thermal_data = value

    @property
    def per_pin_res_path(self) -> str:
        """Per-pin resistance file path."""
        return self._dcir_core.per_pin_res_path

    @per_pin_res_path.setter
    def per_pin_res_path(self, value: str):
        self._dcir_core.per_pin_res_path = value

    @property
    def per_pin_use_pin_format(self) -> bool:
        """Whether to use pin format for per-pin resistance."""
        return self._dcir_core.per_pin_use_pin_format

    @per_pin_use_pin_format.setter
    def per_pin_use_pin_format(self, value: bool):
        self._dcir_core.per_pin_use_pin_format = value

    @property
    def source_terms_to_ground(self) -> dict:
        """Source terms to ground mapping."""
        return self._dcir_core.source_terms_to_ground

    @source_terms_to_ground.setter
    def source_terms_to_ground(self, value: dict):
        self._dcir_core.source_terms_to_ground = value

    @property
    def use_loop_res_for_per_pin(self) -> bool:
        """Whether to use loop resistance for per-pin resistance."""
        return self._dcir_core.use_loop_res_for_per_pin

    @use_loop_res_for_per_pin.setter
    def use_loop_res_for_per_pin(self, value: bool):
        self._dcir_core.use_loop_res_for_per_pin = value

    @property
    def via_report_path(self) -> str:
        """Via report file path."""
        return self._dcir_core.via_report_path

    @via_report_path.setter
    def via_report_path(self, value: str):
        self._dcir_core.via_report_path = value

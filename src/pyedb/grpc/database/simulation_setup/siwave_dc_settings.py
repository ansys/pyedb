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
    def __init__(self, pedb, core: "GrpcSIWaveDCSettings"):
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

    @property
    def export_dc_thermal_data(self) -> bool:
        """Export DC thermal data flag.

        Returns
        -------
        bool
            True if export DC thermal data is enabled, False otherwise.

        """
        return self.core.export_dc_thermal_data

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value: bool):
        self.core.export_dc_thermal_data = value

    @property
    def import_thermal_data(self) -> bool:
        """Import thermal data flag.

        Returns
        -------
        bool
            True if import thermal data is enabled, False otherwise.

        """
        return self.core.import_thermal_data

    @import_thermal_data.setter
    def import_thermal_data(self, value: bool):
        self.core.import_thermal_data = value

    @property
    def dc_report_show_active_devices(self) -> bool:
        """DC report show active devices flag.

        Returns
        -------
        bool
            True if DC report show active devices is enabled, False otherwise.

        """
        return self.core.dc_report_show_active_devices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value: bool):
        self.core.dc_report_show_active_devices = value

    @property
    def per_pin_use_pin_format(self) -> bool:
        """Per pin use pin format flag.

        Returns
        -------
        bool
            True if per pin use pin format is enabled, False otherwise.

        """
        return self.core.per_pin_use_pin_format

    @per_pin_use_pin_format.setter
    def per_pin_use_pin_format(self, value: bool):
        self.core.per_pin_use_pin_format = value

    @property
    def use_loop_res_for_per_pin(self) -> bool:
        """Use loop resistance for per pin flag.

        Returns
        -------
        bool
            True if use loop resistance for per pin is enabled, False otherwise.

        """
        return self.core.use_loop_res_for_per_pin

    @use_loop_res_for_per_pin.setter
    def use_loop_res_for_per_pin(self, value: bool):
        self.core.use_loop_res_for_per_pin = value

    @property
    def dc_report_config_file(self) -> str:
        """DC report configuration file.

        Returns
        -------
        str
            DC report configuration file.

        """
        return self.core.dc_report_config_file

    @dc_report_config_file.setter
    def dc_report_config_file(self, value: str):
        self.core.dc_report_config_file = value

    @property
    def full_dc_report_path(self) -> str:
        """Full DC report path.

        Returns
        -------
        str
            Full DC report path.

        """
        return self.core.full_dc_report_path

    @full_dc_report_path.setter
    def full_dc_report_path(self, value: str):
        self.core.full_dc_report_path = value

    @property
    def icepak_temp_file(self) -> str:
        """Icepak temperature file.

        Returns
        -------
        str
            Icepak temperature file.

        """
        return self.core.icepak_temp_file

    @icepak_temp_file.setter
    def icepak_temp_file(self, value: str):
        self.core.icepak_temp_file = value

    @property
    def per_pin_res_path(self) -> bool:
        """Per pin resistance path.

        Returns
        -------
        bool
            True if per pin resistance path is enabled, False otherwise.

        """
        return self.core.per_pin_res_path

    @per_pin_res_path.setter
    def per_pin_res_path(self, value: bool):
        self.core.per_pin_res_path = value

    @property
    def via_report_path(self) -> str:
        """Via report path.

        Returns
        -------
        str
            Via report path.

        """
        return self.core.via_report_path

    @via_report_path.setter
    def via_report_path(self, value: str):
        self.core.via_report_path = value

    @property
    def source_terms_to_ground(self) -> dict[str, int]:
        """Source terms to ground mapping.

        Returns
        -------
        dict[str, int]
            Source terms to ground mapping.

        """
        return self.core.source_terms_to_ground

    @source_terms_to_ground.setter
    def source_terms_to_ground(self, value: dict[str, int]):
        self.core.source_terms_to_ground = value

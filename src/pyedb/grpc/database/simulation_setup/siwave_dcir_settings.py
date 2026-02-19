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

from pyedb.grpc.database.simulation_setup.siwave_advanced_settings import SIWaveAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_advanced import SIWaveDCAdvancedSettings
from pyedb.grpc.database.simulation_setup.siwave_dc_settings import SIWaveDCSettings
from pyedb.grpc.database.simulation_setup.siwave_general_settings import SIWaveGeneralSettings
from pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings import SIWaveSParameterSettings


class SIWaveDCIRSettings:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @property
    def advanced(self):
        return SIWaveAdvancedSettings(self._pedb, self.core)

    @property
    def dc(self):
        return SIWaveDCSettings(self._pedb, self.core)

    @property
    def dc_advanced(self):
        return SIWaveDCAdvancedSettings(self._pedb, self.core)

    @property
    def general(self):
        return SIWaveGeneralSettings(self._pedb, self.core)

    @property
    def s_parameter(self):
        return SIWaveSParameterSettings(self._pedb, self.core)

    @property
    def dc_report_config_file(self) -> str:
        """DC report configuration file path.

        Returns
        -------
        str:
            file path.
        """
        return self.core.dc_report_config_file

    @dc_report_config_file.setter
    def dc_report_config_file(self, value):
        self.core.dc_report_config_file = value

    @property
    def dc_report_show_active_devices(self) -> bool:
        """Whether to show active devices in the DC report.

        Returns
        -------
        bool:
            True if active devices are shown, False otherwise.
        """
        return self.core.dc_report_show_active_devices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value):
        self.core.dc_report_show_active_devices = value

    @property
    def enabled(self):
        """Whether the DC IR simulation is enabled.

        Returns
        -------
        bool:
            True if enabled, False otherwise.
        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value):
        self.core.enabled = value

    @property
    def export_dc_thermal_data(self) -> bool:
        """Whether to export DC thermal data.

        Returns
        -------
        bool:
            True if DC thermal data is exported, False otherwise.
        """
        return self.core.export_dc_thermal_data

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value):
        self.core.export_dc_thermal_data = value

    @property
    def full_dc_report_path(self) -> str:
        """Full DC report path.

        Returns
        -------
        str:
            file path.
        """
        return self.core.full_dc_report_path

    @full_dc_report_path.setter
    def full_dc_report_path(self, value):
        self.core.full_dc_report_path = value

    @property
    def icepak_temp_file(self) -> str:
        """Icepak temperature file path.

        Returns
        -------
        str:
            file path.
        """
        return self.core.icepak_temp_file

    @icepak_temp_file.setter
    def icepak_temp_file(self, value):
        self.core.icepak_temp_file = value

    @property
    def import_thermal_data(self) -> bool:
        """Whether to import thermal data.

        Returns
        -------
        bool:
            True if thermal data is imported, False otherwise.
        """
        return self.core.import_thermal_data

    @import_thermal_data.setter
    def import_thermal_data(self, value):
        self.core.import_thermal_data = value

    @property
    def per_pin_res_path(self) -> str:
        """Per-pin resistance file path.

        Returns
        -------
        str:
            file path.
        """
        return self.core.per_pin_res_path

    @per_pin_res_path.setter
    def per_pin_res_path(self, value):
        self.core.per_pin_res_path = value

    @property
    def per_pin_use_pin_format(self) -> bool:
        """Whether to use pin format for per-pin resistance.

        Returns
        -------
        bool:
            True if pin format is used, False otherwise.
        """
        return self.core.per_pin_use_pin_format

    @per_pin_use_pin_format.setter
    def per_pin_use_pin_format(self, value):
        self.core.per_pin_use_pin_format = value

    @property
    def source_terms_to_ground(self) -> dict[str, int]:
        """Source terms to ground mapping.

        Returns
        -------
        dict[str, int]:
            Mapping of source terms to ground.
        """
        return self.core.source_terms_to_ground

    @source_terms_to_ground.setter
    def source_terms_to_ground(self, value):
        self.core.source_terms_to_ground = value

    @property
    def use_loop_res_for_per_pin(self) -> bool:
        """Whether to use loop resistance for per-pin resistance.

        Returns
        -------
        bool:
            True if loop resistance is used for per-pin resistance, False otherwise.
        """
        return self.core.use_loop_res_for_per_pin

    @use_loop_res_for_per_pin.setter
    def use_loop_res_for_per_pin(self, value):
        self.core.use_loop_res_for_per_pin = value

    @property
    def via_report_path(self) -> str:
        """Via report file path.

        Returns
        -------
        str:
            file path.
        """
        return self.core.via_report_path

    @via_report_path.setter
    def via_report_path(self, value):
        self.core.via_report_path = value

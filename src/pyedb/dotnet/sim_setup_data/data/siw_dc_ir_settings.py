# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


class SiwaveDCIRSettings:
    """Class for DC IR settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def export_dc_thermal_data(self):
        """Export DC Thermal Data.

        Returns
        -------
            bool
            ``True`` when activated, ``False`` deactivated.
        """
        return self._parent.get_sim_setup_info.SimulationSettings.DCIRSettings.ExportDCThermalData

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.SimulationSettings.DCIRSettings.ExportDCThermalData = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def import_thermal_data(self):
        """Import Thermal Data.

        Returns
        -------
            bool
            ``True`` when activated, ``False`` deactivated.
        """
        return self._parent.get_sim_setup_info.SimulationSettings.DCIRSettings.ImportThermalData

    @import_thermal_data.setter
    def import_thermal_data(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.SimulationSettings.DCIRSettings.ImportThermalData = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def dc_report_show_active_devices(self):
        """DC Report Show Active Devices.

        Returns
        -------
            bool
            ``True`` when activated, ``False`` deactivated.
        """
        return self._parent.get_sim_setup_info.SimulationSettings.DCIRSettings.DCReportShowActiveDevices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.SimulationSettings.DCIRSettings.DCReportShowActiveDevices = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def per_pin_use_pin_format(self):
        """Per Pin Use Pin Format.

        Returns
        -------
            bool
            ``True`` when activated, ``False`` deactivated.
        """
        return self._parent.get_sim_setup_info.SimulationSettings.DCIRSettings.PerPinUsePinFormat

    @per_pin_use_pin_format.setter
    def per_pin_use_pin_format(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.SimulationSettings.DCIRSettings.PerPinUsePinFormat = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def use_loop_res_for_per_pin(self):
        """Use loop Res Per Pin.

        Returns
        -------
            bool
            ``True`` when activated, ``False`` deactivated.
        """
        return self._parent.get_sim_setup_info.SimulationSettings.DCIRSettings.UseLoopResForPerPin

    @use_loop_res_for_per_pin.setter
    def per_pin_use_pin_format(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.SimulationSettings.DCIRSettings.UseLoopResForPerPin = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

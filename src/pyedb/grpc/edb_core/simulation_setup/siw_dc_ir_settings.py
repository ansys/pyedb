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

from pyedb.dotnet.edb_core.general import (
    convert_netdict_to_pydict,
    convert_pydict_to_netdict,
)


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
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.ExportDCThermalData

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.ExportDCThermalData = value
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
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.ImportThermalData

    @import_thermal_data.setter
    def import_thermal_data(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.ImportThermalData = value
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
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.DCReportShowActiveDevices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.DCReportShowActiveDevices = value
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
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.PerPinUsePinFormat

    @per_pin_use_pin_format.setter
    def per_pin_use_pin_format(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.PerPinUsePinFormat = value
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
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.UseLoopResForPerPin

    @use_loop_res_for_per_pin.setter
    def use_loop_res_for_per_pin(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.UseLoopResForPerPin = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def dc_report_config_file(self):
        """DC Report Config File.

        Returns
        -------
            str
            path to the DC report configuration file.
        """
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.DCReportConfigFile

    @dc_report_config_file.setter
    def dc_report_config_file(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.DCReportConfigFile = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def full_dc_report_path(self):
        """Full DC Report Path.

        Returns
        -------
            str
            full path to the DC report file.
        """
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.FullDCReportPath

    @full_dc_report_path.setter
    def full_dc_report_path(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.FullDCReportPath = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def icepak_temp_file(self):
        """Icepack Temp File.

        Returns
        -------
            str
            path to the temp Icepak file.
        """
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.IcepakTempFile

    @icepak_temp_file.setter
    def icepak_temp_file(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.IcepakTempFile = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def per_pin_res_path(self):
        """Per Pin Res Path.

        Returns
        -------
            str
            path for per pin res.
        """
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.PerPinResPath

    @per_pin_res_path.setter
    def per_pin_res_path(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.PerPinResPath = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def via_report_path(self):
        """Via Report Path.

        Returns
        -------
            str
            path for the Via Report.
        """
        return self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.ViaReportPath

    @via_report_path.setter
    def via_report_path(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.ViaReportPath = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def source_terms_to_ground(self):
        """A dictionary of SourceName, NodeToGround pairs,
        where NodeToGround is one of 0 (unspecified), 1 (negative), 2 (positive).


        Returns
        -------
            dict <str, int>
                str: source name,
                int: node to ground pairs, 0 (unspecified), 1 (negative), 2 (positive) .
        """
        temp = self._parent.get_sim_setup_info.simulation_settings.DCIRSettings.SourceTermsToGround
        return convert_netdict_to_pydict(temp)

    @source_terms_to_ground.setter
    def source_terms_to_ground(self, value):
        edb_setup_info = self._parent.get_sim_setup_info
        edb_setup_info.simulation_settings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(value)
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

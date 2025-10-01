# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""
This module contains the ``Siwave`` class.

The ``Siwave`` module can be initialized as standalone before launching an app or
automatically initialized by an app to the latest installed AEDT version.

"""

from __future__ import absolute_import  # noreorder

import os
from pathlib import Path
import pkgutil
import shutil
import sys
import tempfile
import time
from typing import Optional, Union
import warnings

from pyedb import Edb
from pyedb.dotnet.clr_module import _clr
from pyedb.generic.general_methods import _pythonver, generate_unique_name, is_windows
from pyedb.generic.settings import settings
from pyedb.misc.misc import list_installed_ansysem
from pyedb.siwave_core.icepak import Icepak


def wait_export_file(flag, file_path, time_sleep=0.5):
    while True:
        if os.path.isfile(file_path):
            break
        else:
            time.sleep(1)
        os.path.getsize(file_path)

    while True:
        file_size = os.path.getsize(file_path)
        if file_size > 0:
            break
        else:
            time.sleep(time_sleep)
    return True


def wait_export_folder(flag, folder_path, time_sleep=0.5):
    while True:
        if os.path.exists(folder_path):
            for root, _, files in os.walk(folder_path):
                if any(os.path.getsize(os.path.join(root, file)) > 0 for file in files):
                    return True

        # Wait before checking again.
        time.sleep(time_sleep)


def parser_file_path(file_path):
    if isinstance(file_path, Path):
        file_path = str(file_path)

    if not Path(file_path).root:
        file_path = str(Path().cwd() / file_path)
    return file_path


class Siwave(object):  # pragma no cover
    """Initializes SIwave based on the inputs provided and manages SIwave release and closing.

    Parameters
    ----------
    specified_version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active setup is used or the latest installed version is used.

    """

    @property
    def version(self):
        ver = self.oSiwave.GetVersion()
        return ".".join(ver.split(".")[:-1])

    @property
    def version_keys(self):
        """Version keys for AEDT."""

        self._version_keys = []
        self._version_ids = {}

        version_list = list_installed_ansysem()
        for version_env_var in version_list:
            try:
                current_version_id = version_env_var.replace("ANSYSEM_ROOT", "").replace("ANSYSEMSV_ROOT", "")
                version = int(current_version_id[0:2])
                release = int(current_version_id[2])
                if version < 20:
                    if release < 3:
                        version -= 1
                    else:
                        release -= 2
                v_key = "20{0}.{1}".format(version, release)
                self._version_keys.append(v_key)
                self._version_ids[v_key] = version_env_var
            except ValueError:
                continue
        return self._version_keys

    @property
    def current_version(self):
        """Current version of AEDT."""
        return self.version_keys[0]

    def __init__(self, specified_version=None):
        self._logger = settings.logger
        if is_windows:  # pragma: no cover
            modules = [tup[1] for tup in pkgutil.iter_modules()]
            if _clr:
                import win32com.client

                _com = "pythonnet_v3"
            elif "win32com" in modules:
                import win32com.client

                _com = "pywin32"
            else:
                raise Exception("Error. No win32com.client or PythonNET modules are found. They need to be installed.")
        self._main = sys.modules["__main__"]
        print("Launching Siwave Init")
        if "oSiwave" in dir(self._main) and self._main.oSiwave is not None:
            self._main.AEDTVersion = self._main.oSiwave.GetVersion()[0:6]
            self._main.oSiwave.RestoreWindow()
            specified_version = self.current_version
            if specified_version not in self.version_keys:
                raise ValueError("Specified version {} is not known.".format(specified_version))
            version_key = specified_version
            base_path = os.getenv(self._version_ids[specified_version])
            self._main.sDesktopinstallDirectory = base_path
        else:
            if specified_version:
                if specified_version not in self.version_keys:
                    raise ValueError("Specified version {} is not known.".format(specified_version))
                version_key = specified_version
            else:
                version_key = self.current_version
            base_path = os.getenv(self._version_ids[version_key])
            self._main = sys.modules["__main__"]
            self._main.sDesktopinstallDirectory = base_path
            version = "Siwave.Application." + version_key
            self._main.AEDTVersion = version_key
            self._main.interpreter = _com
            self._main.interpreter_ver = _pythonver
            if "oSiwave" in dir(self._main):
                del self._main.oSiwave

            if _com == "pythonnet":
                self._main.oSiwave = System.Activator.CreateInstance(System.Type.GetTypeFromProgID(version))

            elif _com == "pythonnet_v3":
                # TODO check if possible to use pythonnet. at the moment the tool open AEDt
                # but doesn't return the wrapper of oApp
                print("Launching Siwave with module win32com.")

                self._main.oSiwave = win32com.client.Dispatch(version)

            self._main.AEDTVersion = version_key
            self.oSiwave = self._main.oSiwave
            self._main.oSiwave.RestoreWindow()
        self._main.siwave_initialized = True
        self._oproject = self.oSiwave.GetActiveProject()
        pass

    @property
    def project_name(self):
        """Project name.

        Returns
        -------
        str
            Name of the project.

        """
        return self._oproject.GetName()

    @property
    def project_path(self):
        """Project path.

        Returns
        -------
        str
            Full absolute path for the project.

        """
        return os.path.normpath(self.oSiwave.GetProjectDirectory())

    @property
    def project_file(self):
        """Project file.

        Returns
        -------
        str
            Full absolute path and name for the project file.

        """
        return os.path.join(self.project_path, self.project_name + ".siw")

    @property
    def lock_file(self):
        """Lock file.

        Returns
        -------
        str
            Full absolute path and name for the project lock file.

        """
        return os.path.join(self.project_path, self.project_name + ".siw.lock")

    @property
    def results_directory(self):
        """Results directory.

        Returns
        -------
        str
            Full absolute path to the ``aedtresults`` directory.
        """
        return os.path.join(self.project_path, self.project_name + ".siwresults")

    @property
    def src_dir(self):
        """Source directory.

        Returns
        -------
        str
            Full absolute path to the ``python`` directory.
        """
        return os.path.dirname(os.path.realpath(__file__))

    @property
    def pyaedt_dir(self):
        """PyAEDT directory.

        Returns
        -------
        str
            Full absolute path to the ``pyaedt`` directory.
        """
        return os.path.realpath(os.path.join(self.src_dir, ".."))

    @property
    def oproject(self):
        """Project."""
        return self._oproject

    @property
    def icepak(self):
        return Icepak(self)

    def open_project(self, proj_path=None):
        """Open a project.

        Parameters
        ----------
        proj_path : str, optional
            Full path to the project. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        file_path = parser_file_path(proj_path)
        if os.path.exists(file_path):
            open_result = self.oSiwave.OpenProject(file_path)
            self._oproject = self.oSiwave.GetActiveProject()
            return open_result
        else:
            return False

    @property
    def file_dir(self) -> str:
        """Directory path of the open project."""
        return self.oproject.GetFileDir()

    @property
    def file_path(self) -> str:
        """Path of the open project file."""
        return self.oproject.GetFilePath()

    def save_project(self, projectpath=None, projectName=None):
        """Save the project.

        Parameters
        ----------
        proj_path : str, optional
            Full path to the project. The default is ``None``.
        projectName : str, optional
             Name of the project. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if projectName and projectpath:
            if not projectName.endswith(".siw"):
                projectName = projectName + ".siw"
            self.oproject.ScrSaveProjectAs(os.path.join(projectpath, projectName))
        else:
            self.oproject.Save()
        return True

    def save(self, file_path: Optional[Union[str, Path]]):
        """Save the project.

        Parameters
        ----------
        file_path : str, optional
            Full path to the project. The default is ``None``.
        """

        if file_path:
            file_path = parser_file_path(file_path)
            file_path = str(Path(file_path).with_suffix(".siw"))
            self.oproject.ScrSaveProjectAs(file_path)
        else:
            self.oproject.Save()

    def close_project(self, save_project=False):
        """Close the project.

        Parameters
        ----------
        save_project : bool, optional
            Whether to save the current project before closing it. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if save_project:
            self.save_project()
        self.oproject.ScrCloseProject()
        self._oproject = None
        return True

    def quit_application(self):
        """Quit the application.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._main.oSiwave.Quit()
        self._main.oSiwave = None
        return True

    def export_element_data(self, simulation_name, file_path, data_type="Vias"):
        """Export element data.

        Parameters
        ----------
        simulation_name : str
            Name of the setup.
        file_path : str
            Path to the exported report.
        data_type : str, optional
            Type of the data. The default is ``"Vias"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        flag = self.oproject.ScrExportElementData(simulation_name, file_path, data_type)
        if flag == 0:
            self._logger.info(f"Exporting element data to {file_path}.")
            return wait_export_file(flag, file_path, time_sleep=1)
        else:
            return False

    def export_siwave_report(self, simulation_name, file_path, bkground_color="White"):
        """Export the Siwave report.

        Parameters
        ----------
        simulation_name : str
            Name of the setup.
        file_path : str
            Path to the exported report.
        bkground_color : str, optional
            Color of the report's background. The default is ``"White"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new property :func:`export_dc_simulation_report` instead.", DeprecationWarning)
        return self.export_dc_simulation_report(simulation_name, file_path, bkground_color)

    def export_dc_simulation_report(self, simulation_name, file_path, background_color="White"):
        """Export the Siwave DC simulation report.

        Parameters
        ----------
        simulation_name : str
            Name of the setup.
        file_path : str
            Path to the exported report.
        background_color : str, optional
            Color of the report's background. The default is ``"White"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not os.path.splitext(file_path)[-1] == ".htm":
            fpath = file_path + ".htm"
        else:
            fpath = file_path
        self.oproject.ScrExportDcSimReportScaling("All", "All", -1, -1, False)
        flag = self.oproject.ScrExportDcSimReport(simulation_name, background_color, fpath)
        if flag == 0:
            self._logger.info(f"Exporting Siwave DC simulation report to {fpath}.")
            return wait_export_file(flag, fpath, time_sleep=1)
        else:
            return False

    def run_dc_simulation(self, export_dc_power_data_to_icepak=False):
        """Run DC simulation."""
        self._logger.info("Running DC simulation.")
        self.oproject.ScrExportDcPowerDataToIcepak(export_dc_power_data_to_icepak)
        return self.oproject.ScrRunDcSimulation(1)

    def export_icepak_project(self, file_path, dc_simulation_name):
        """Exports an Icepak project for standalone use.

        Parameters
        ----------
        file_path : str,
            Path of the Icepak project.
        dc_simulation_name : str
            Name of the DC simulation.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        self.oproject.ScrExportDcPowerDataToIcepak(True)
        self._logger.info("Exporting Icepak project.")
        code = self.oproject.ScrExportIcepakProject(file_path, dc_simulation_name)
        return True if code == 0 else False

    def run_icepak_simulation(self, icepak_simulation_name, dc_simulation_name):
        """Runs an Icepak simulation.

        Parameters
        ----------
        icepak_simulation_name : str
            Name of the Icepak simulation.
        dc_simulation_name : str
            Name of the DC simulation.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        return self.oproject.ScrRunIcepakSimulation(icepak_simulation_name, dc_simulation_name)

    def export_edb(self, file_path: str):
        """Export the layout as EDB.

        Parameters
        ----------
        file_path : str
            Path to the EDB.

        Returns
        -------
        bool
        """
        if isinstance(file_path, Path):
            file_path = str(file_path)
        flag = self.oproject.ScrExportEDB(file_path)
        if flag == 0:
            self._logger.info(f"Exporting EDB to {file_path}.")
            return wait_export_folder(flag, file_path, time_sleep=1)
        else:  # pragma no cover
            raise RuntimeError(f"Failed to export EDB to {file_path}.")

    def import_edb(self, file_path: str):
        """Import layout from EDB.

        Parameters
        ----------
        file_path : Str
            Path to the EDB file.
        Returns
        -------
        bool
        """
        if isinstance(file_path, Path):
            file_path = str(file_path)
        if not Path(file_path).root:
            file_path = str(Path().cwd() / file_path)
        flag = self.oproject.ScrImportEDB(file_path)
        # self.save_project(self.di)
        if flag == 0:
            self._logger.info(f"Importing EDB to {file_path}.")
            return True
        else:  # pragma no cover
            raise RuntimeError(f"Failed to import EDB to {file_path}.")

    def load_configuration(self, file_path: str):
        """Load configuration settings from a configure file.Import

        Parameters
        ----------
        file_path : str
            Path to the configuration file.
        """
        file_path = parser_file_path(file_path)

        # temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
        # temp_edb = os.path.join(temp_folder.name, "temp.aedb")

        temp_edb = os.path.join(tempfile.gettempdir(), generate_unique_name("temp") + ".aedb")

        self.export_edb(temp_edb)
        self.oproject.ScrCloseProject()
        edbapp = Edb(temp_edb, edbversion=self.version)
        edbapp.configuration.load(file_path)
        edbapp.configuration.run()
        edbapp.save()
        edbapp.close()
        self.import_edb(temp_edb)
        shutil.rmtree(Path(temp_edb), ignore_errors=True)

    def export_configuration(self, file_path: str, fix_padstack_names: bool = False):
        """Export layout information into a configuration file.

        Parameters
        ----------
        file_path : str
            Path to the configuration file.
        fix_padstack_names : bool
            Name all the padstacks in edb.
        """
        file_path = parser_file_path(file_path)

        temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
        temp_edb = os.path.join(temp_folder.name, "temp.aedb")

        self.export_edb(temp_edb)
        edbapp = Edb(temp_edb, edbversion=self.current_version)
        if fix_padstack_names:
            edbapp.layout_validation.padstacks_no_name(fix=True)
        edbapp.configuration.export(file_path)
        edbapp.close()

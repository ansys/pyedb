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

import os
from pathlib import Path
import re
import sys
import time
import warnings


class Settings(object):
    """Manages all PyEDB environment variables and global settings."""

    INSTALLED_VERSIONS = None
    INSTALLED_STUDENT_VERSIONS = None
    INSTALLED_CLIENT_VERSIONS = None
    LATEST_VERSION = None
    LATEST_STUDENT_VERSION = None

    specified_version = None
    is_student_version = False

    def __init__(self):
        self.remote_rpc_session = False
        self._enable_screen_logs = True
        self._edb_dll_path = None
        self._enable_logger = True
        self._enable_file_logs = True
        self.pyedb_server_path = ""
        self._logger_file_path = None
        self._logger_formatter = "%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s"
        self._logger_datefmt = "%Y/%m/%d %H.%M.%S"
        self._enable_debug_edb_logger = False
        self._enable_debug_grpc_api_logger = False
        self._enable_debug_methods_argument_logger = False
        self._enable_debug_geometry_operator_logger = False
        self._enable_debug_internal_methods_logger = False
        self._enable_debug_logger = False
        self._enable_error_handler = True
        self.formatter = None
        self._project_properties = {}
        self._project_time_stamp = 0
        self._disable_bounding_box_sat = False
        self._force_error_on_missing_project = False
        self._enable_pandas_output = False
        self.time_tick = time.time()
        self.retry_n_times_time_interval = 0.1
        self._global_log_file_name = "pyedb_{}.log".format(os.path.split(os.path.expanduser("~"))[-1])
        self._enable_global_log_file = True
        self._enable_local_log_file = False
        self._global_log_file_size = 10
        self._lsf_queue = None
        self._edb_environment_variables = {}
        self.logger = None
        self.log_file = None
        self._aedt_version = None

        self.__get_version_information()
        self.__init_logger()

    @property
    def edb_environment_variables(self):
        """Environment variables that are set before launching a new AEDT session,
        including those that enable the beta features."""
        return self._edb_environment_variables

    @edb_environment_variables.setter
    def edb_environment_variables(self, value):
        self._edb_environment_variables = value

    @property
    def aedt_version(self):
        """AEDT version in the form ``"2023.x"``. In AEDT 2022 R2 and later,
        evaluating a bounding box by exporting a SAT file is disabled."""
        return self._aedt_version

    @aedt_version.setter
    def aedt_version(self, value):
        self._aedt_version = value
        if self._aedt_version >= "2023.1":
            self.disable_bounding_box_sat = True

    @property
    def global_log_file_size(self):
        """Global PyEDB log file size in MB. The default value is ``10``."""
        return self._global_log_file_size

    @global_log_file_size.setter
    def global_log_file_size(self, value):
        self._global_log_file_size = value

    @property
    def enable_global_log_file(self):
        """Flag for enabling and disabling the global PyEDB log file located in the global temp folder.
        The default is ``True``."""
        return self._enable_global_log_file

    @enable_global_log_file.setter
    def enable_global_log_file(self, value):
        self._enable_global_log_file = value

    @property
    def enable_local_log_file(self):
        """Flag for enabling and disabling the local PyEDB log file located
        in the ``projectname.pyedb`` project folder. The default is ``True``."""
        return self._enable_local_log_file

    @enable_local_log_file.setter
    def enable_local_log_file(self, value):
        self._enable_local_log_file = value

    @property
    def global_log_file_name(self):
        """Global PyEDB log file path. The default is ``pyedb_username.log``."""
        return self._global_log_file_name

    @global_log_file_name.setter
    def global_log_file_name(self, value):
        self._global_log_file_name = value

    @property
    def enable_debug_methods_argument_logger(self):
        """Flag for whether to write out the method's arguments in the debug logger.
        The default is ``False``."""
        return self._enable_debug_methods_argument_logger

    @enable_debug_methods_argument_logger.setter
    def enable_debug_methods_argument_logger(self, val):
        self._enable_debug_methods_argument_logger = val

    @property
    def enable_error_handler(self):
        """Flag for enabling and disabling the internal PyEDB error handling."""
        return self._enable_error_handler

    @enable_error_handler.setter
    def enable_error_handler(self, val):
        self._enable_error_handler = val

    @property
    def enable_file_logs(self):
        """Flag for enabling and disabling the logging to a file."""
        return self._enable_file_logs

    @enable_file_logs.setter
    def enable_file_logs(self, val):
        self._enable_file_logs = val

    @property
    def enable_logger(self):
        """Flag for enabling and disabling the logging overall."""
        return self._enable_logger

    @enable_logger.setter
    def enable_logger(self, val):
        self._enable_logger = val

    @property
    def logger_file_path(self):
        """PyEDB log file path."""
        return self._logger_file_path

    @logger_file_path.setter
    def logger_file_path(self, val):
        self._logger_file_path = val

    @property
    def logger_formatter(self):
        """Message format of the log entries.
        The default is ``'%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s'``"""
        return self._logger_formatter

    @logger_formatter.setter
    def logger_formatter(self, val):
        self._logger_formatter = val

    @property
    def logger_datefmt(self):
        """Date format of the log entries.
        The default is ``'%Y/%m/%d %H.%M.%S'``"""
        return self._logger_datefmt

    @logger_datefmt.setter
    def logger_datefmt(self, val):
        self._logger_datefmt = val

    @property
    def enable_debug_edb_logger(self):
        """Flag for enabling and disabling the logger for any EDB API methods."""
        return self._enable_debug_edb_logger

    @enable_debug_edb_logger.setter
    def enable_debug_edb_logger(self, val):
        self._enable_debug_edb_logger = val

    @property
    def enable_debug_internal_methods_logger(self):
        """Flag for enabling and disabling the logging for internal methods.
        This setting is useful for debug purposes."""
        return self._enable_debug_internal_methods_logger

    @enable_debug_internal_methods_logger.setter
    def enable_debug_internal_methods_logger(self, val):
        self._enable_debug_internal_methods_logger = val

    @property
    def enable_debug_logger(self):
        """Flag for enabling and disabling the debug level logger."""
        return self._enable_debug_logger

    @enable_debug_logger.setter
    def enable_debug_logger(self, val):
        self._enable_debug_logger = val

    @property
    def enable_screen_logs(self):
        """Flag for enabling and disabling the logging to STDOUT."""
        return self._enable_screen_logs

    @enable_screen_logs.setter
    def enable_screen_logs(self, val):
        self._enable_screen_logs = val

    @property
    def edb_dll_path(self):
        """Optional path for the EDB DLL file."""
        return self._edb_dll_path

    @edb_dll_path.setter
    def edb_dll_path(self, value):
        if os.path.exists(value):
            ver = Path(value).parts[-2]
            version, release = ver[-3:-1], ver[-1]
            self.specified_version = f"20{version}.{release}"
            self._edb_dll_path = value

    @property
    def retry_n_times_time_interval(self):
        """Time interval between the retries by the ``_retry_n_times`` method."""
        return self._retry_n_times_time_interval

    @retry_n_times_time_interval.setter
    def retry_n_times_time_interval(self, value):
        self._retry_n_times_time_interval = float(value)

    def __get_version_information(self):
        """Get the installed AEDT versions.

        This method returns a dictionary, with the version as the key and the installation path
        as the value."""
        version_pattern = re.compile(r"^(ANSYSEM_ROOT|ANSYSEM_PY_CLIENT_ROOT|ANSYSEMSV_ROOT)\d{3}$")
        env_list = sorted([x for x in os.environ if version_pattern.match(x)], reverse=True)
        if not env_list:  # pragma: no cover
            warnings.warn("No installed versions of AEDT are found in the system environment variables.")
            return

        aedt_system_env_variables = {i: os.environ[i] for i in env_list}

        standard_versions = {}
        client_versions = {}
        student_versions = {}
        # version_list is ordered: first normal versions, then client versions, finally student versions
        for var_name, aedt_path in aedt_system_env_variables.items():
            version_id = var_name[-3:]
            version, release = version_id[0:2], version_id[2]
            version_name = f"20{version}.{release}"
            if "ANSYSEM_ROOT" in var_name:
                standard_versions[version_name] = aedt_path
            elif "ANSYSEM_PY_CLIENT_ROOT" in var_name:
                client_versions[version_name] = aedt_path
            else:
                student_versions[version_name] = aedt_path
        self.INSTALLED_VERSIONS = standard_versions
        self.INSTALLED_STUDENT_VERSIONS = student_versions
        self.INSTALLED_CLIENT_VERSIONS = client_versions

        if len(self.INSTALLED_VERSIONS):
            self.LATEST_VERSION = max(standard_versions.keys(), key=lambda x: tuple(map(int, x.split("."))))
        if len(self.INSTALLED_STUDENT_VERSIONS):
            self.LATEST_STUDENT_VERSION = max(student_versions.keys(), key=lambda x: tuple(map(int, x.split("."))))

    @property
    def aedt_installation_path(self):
        if self.edb_dll_path:
            return self.edb_dll_path
        elif self.is_student_version:
            return self.INSTALLED_STUDENT_VERSIONS[self.specified_version]
        elif self.specified_version in self.INSTALLED_VERSIONS.keys():
            return self.INSTALLED_VERSIONS[self.specified_version]
        elif os.name == "posix":
            main = sys.modules["__main__"]
            if "oDesktop" in dir(main):
                return main.oDesktop.GetExeDir()
            else:
                raise RuntimeError(f"Version {self.specified_version} is not installed on the system. ")
        else:
            raise RuntimeError(f"Version {self.specified_version} is not installed on the system. ")

    def __init_logger(self):
        from pyedb.edb_logger import EdbLogger

        self.logger = EdbLogger(to_stdout=self.enable_screen_logs, settings=self)


settings = Settings()

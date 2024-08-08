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

import os
import time


class Settings(object):
    """Manages all PyEDB environment variables and global settings."""

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
        self._use_pyaedt_log = False
        self._logger = None

    @property
    def logger(self):
        """Active logger."""
        return self._logger

    @logger.setter
    def logger(self, val):
        self._logger = val

    @property
    def use_pyaedt_log(self):
        """Flag that disable Edb log when PyAEDT is used."""
        return self._use_pyaedt_log

    @use_pyaedt_log.setter
    def use_pyaedt_log(self, value):
        self._use_pyaedt_log = value

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
            self._edb_dll_path = value

    @property
    def retry_n_times_time_interval(self):
        """Time interval between the retries by the ``_retry_n_times`` method."""
        return self._retry_n_times_time_interval

    @retry_n_times_time_interval.setter
    def retry_n_times_time_interval(self, value):
        self._retry_n_times_time_interval = float(value)


settings = Settings()

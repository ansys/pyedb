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

# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import os
import shutil
import sys
import tempfile
import time

from pyedb.generic.settings import settings


class Msg:
    (INFO, WARNING, ERROR, FATAL) = range(4)


class AppFilter(logging.Filter):
    """Specifies the destination of the logger.

    AEDT exposes three different loggers, which are the global, project, and design loggers.

    Parameters
    ----------
    destination : str, optional
        Logger to write to. Options are ``"Global"`, ``"Project"``, and ``"Design"``.
        The default is ``"Global"``.
    extra : str, optional
        Name of the design or project. The default is ``""``.
    """

    def __init__(self, destination="Global", extra=""):
        self._destination = destination
        self._extra = extra

    def filter(self, record):
        """
        Modify the record sent to the logger.

        Parameters
        ----------
        record : class:`logging.LogRecord`
            Contains information related to the event being logged.
        """
        record.destination = self._destination

        # This will avoid the extra '::' for Global that does not have any extra info.
        if not self._extra:
            record.extra = self._extra
        else:
            record.extra = self._extra + ":"
        return True


class EdbLogger(object):
    """
    Specifies the logger to use for EDB logger.

    This class allows you to add a handler to write messages to a file and to indicate
    whether to write messages to the standard output (stdout).

    Parameters
    ----------
    level : int, optional
        Logging level to filter the message severity allowed in the logger.
        The default is ``logging.DEBUG``.
    filename : str, optional
        Name of the file to write messages to. The default is ``None``.
    to_stdout : bool, optional
        Whether to write log messages to stdout. The default is ``False``.
    """

    def __init__(self, level=logging.DEBUG, filename=None, to_stdout=False):
        self._std_out_handler = None
        self._files_handlers = []
        self.level = level
        self.filename = filename or settings.logger_file_path
        settings.logger_file_path = self.filename

        self._global = logging.getLogger("Global")
        if not settings.enable_logger:
            self._global.addHandler(logging.NullHandler())
            return
        self._global.setLevel(level)
        self._global.addFilter(AppFilter())
        if settings.formatter:
            self.formatter = settings.formatter
        else:
            self.formatter = logging.Formatter(settings.logger_formatter, datefmt=settings.logger_datefmt)
        global_handler = False
        if settings.enable_global_log_file:
            for handler in self._global.handlers:
                if settings.global_log_file_name in str(handler):
                    global_handler = True
                    break
            log_file = os.path.join(tempfile.gettempdir(), settings.global_log_file_name)
            my_handler = RotatingFileHandler(
                log_file,
                mode="a",
                maxBytes=float(settings.global_log_file_size) * 1024 * 1024,
                backupCount=2,
                encoding="utf-8",
                delay=0,
            )
            my_handler.setFormatter(self.formatter)
            my_handler.setLevel(self.level)
            if not global_handler and settings.global_log_file_name:
                self._global.addHandler(my_handler)
            self._files_handlers.append(my_handler)
        if self.filename and os.path.exists(self.filename):
            shutil.rmtree(self.filename, ignore_errors=True)
        if self.filename and settings.enable_local_log_file:
            self.add_file_logger(self.filename)

        if to_stdout:
            settings.enable_screen_logs = True
            self._std_out_handler = logging.StreamHandler(sys.stdout)
            self._std_out_handler.setLevel(level)
            _logger_stdout_formatter = logging.Formatter("PyEDB %(levelname)s: %(message)s")

            self._std_out_handler.setFormatter(_logger_stdout_formatter)
            self._global.addHandler(self._std_out_handler)
        self._timer = time.time()

    def add_file_logger(self, filename):
        """Add a new file to the logger handlers list."""
        _file_handler = logging.FileHandler(filename)
        _file_handler.setFormatter(self.formatter)
        self.info("New logger file {} added to handlers.".format(filename))
        self._files_handlers.append(_file_handler)
        return True

    def remove_file_logger(self, project_name):
        """Remove a file from the logger handlers list."""
        handlers = [i for i in self._global.handlers]
        for handler in self._files_handlers:
            if "pyedb_{}.log".format(project_name) in str(handler):
                handler.close()
                if handler in handlers:
                    self._global.removeHandler(handler)
                self.info("logger file pyedb_{}.log removed from handlers.".format(project_name))

    def remove_all_file_loggers(self):
        """Remove all file loggers."""
        handlers = [i for i in self._global.handlers]
        for handler in handlers:
            if "pyedb_" in str(handler):
                handler.close()
                self._global.removeHandler(handler)

    @property
    def _log_on_file(self):
        return settings.enable_file_logs

    @_log_on_file.setter
    def _log_on_file(self, val):
        settings.enable_file_logs = val

    @property
    def logger(self):
        """EDB logger object."""
        if self._log_on_file:
            return logging.getLogger("Global")
        else:
            return None  # pragma: no cover

    def reset_timer(self, time_val=None):
        """ "Reset actual timer to  actual time or specified time.

        Parameters
        ----------
        time_val : float, optional
            Value time to apply.

        Returns
        -------

        """
        if time_val:
            self._timer = time_val
        else:
            self._timer = time.time()
        return self._timer

    def add_error_message(self, message_text):
        """
        Add a type 2 "Error" message to the message manager tree.

        Also add an error message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the error message.

        """
        self.add_message(2, message_text)

    def add_warning_message(self, message_text):
        """
        Add a type 1 "Warning" message to the message manager tree.

        Also add a warning message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the warning message.

        Examples
        --------
        Add a warning message to the EDB message manager.

        >>> edb.logger.warning("Global warning message")

        """
        self.add_message(1, message_text)

    def add_info_message(self, message_text):
        """Add a type 0 "Info" message to the active design level of the message manager tree.

        Also add an info message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the info message.

        Examples
        --------
        Add an info message at the global level.

        >>> edb.logger.info("Global warning message")

        """
        self.add_message(0, message_text)

    def add_debug_message(self, message_text):
        """
        Parameterized message to the message manager.

        Parameters
        ----------
        message_text : str
            Text to display as the message.
        """

        return self.add_message(3, message_text)

    def add_message(self, message_type, message_text):
        """Add a message to the message manager.

        Parameters
        ----------
        message_type : int
            Type of the message. Options are:
            * ``0`` : Info
            * ``1`` : Warning
            * ``2`` : Error
            * ``3`` : Debug
        message_text : str
            Text to display as the message.
        """
        self._log_on_handler(message_type, message_text)

    def _log_on_handler(self, message_type, message_text, *args, **kwargs):
        if not (self._log_on_file or self._log_on_screen) or not self._global:
            return
        if len(message_text) > 250:
            message_text = message_text[:250] + "..."
        if message_type == 0:
            self._global.info(message_text, *args, **kwargs)
        elif message_type == 1:
            self._global.warning(message_text, *args, **kwargs)
        elif message_type == 2:
            self._global.error(message_text, *args, **kwargs)
        elif message_type == 3:
            self._global.debug(message_text, *args, **kwargs)

    def disable_stdout_log(self):
        """Disable printing log messages to stdout."""
        self._log_on_screen = False
        self._global.removeHandler(self._std_out_handler)
        self.info("StdOut is disabled")

    def enable_stdout_log(self):
        """Enable printing log messages to stdout."""
        self._log_on_screen = True
        if not self._std_out_handler:
            self._std_out_handler = logging.StreamHandler(sys.stdout)
            self._std_out_handler.setLevel(self.level)
            _logger_stdout_formatter = logging.Formatter("pyedb %(levelname)s: %(message)s")

            self._std_out_handler.setFormatter(_logger_stdout_formatter)
            self._global.addHandler(self._std_out_handler)
        self._global.addHandler(self._std_out_handler)
        self.info("StdOut is enabled")

    def disable_log_on_file(self):
        """Disable writing log messages to an output file."""
        self._log_on_file = False
        for _file_handler in self._files_handlers:
            _file_handler.close()
            self._global.removeHandler(_file_handler)
        self.info("Log on file is disabled")

    def enable_log_on_file(self):
        """Enable writing log messages to an output file."""
        self._log_on_file = True
        for _file_handler in self._files_handlers:
            self._global.addHandler(_file_handler)
        self.info("Log on file is enabled")

    def info(self, msg, *args, **kwargs):
        """Write an info message to the global logger."""
        if not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        return self._log_on_handler(0, msg, *args, **kwargs)

    def info_timer(self, msg, start_time=None, *args, **kwargs):
        """Write an info message to the global logger with elapsed time.
        Message will have an appendix of type Elapsed time: time."""
        if not settings.enable_logger:
            return
        if not start_time:
            start_time = self._timer
        td = time.time() - start_time
        m, s = divmod(td, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d > 0:
            msg += " Elapsed time: {}days {}h {}m {}sec".format(round(d), round(h), round(m), round(s))
        elif h > 0:
            msg += " Elapsed time: {}h {}m {}sec".format(round(h), round(m), round(s))
        else:
            msg += " Elapsed time: {}m {}sec".format(round(m), round(s))
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        return self._log_on_handler(0, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Write a warning message to the global logger."""
        if not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        return self._log_on_handler(1, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Write an error message to the global logger."""
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        return self._log_on_handler(2, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Write a debug message to the global logger."""
        if not settings.enable_debug_logger or not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        return self._log_on_handler(3, msg, *args, **kwargs)

    @property
    def glb(self):
        """Global logger."""
        self._global = logging.getLogger("Global")
        return self._global


logger = logging.getLogger("Global")
if any("aedt_logger" in str(i) for i in logger.filters):
    from pyaedt.generic.settings import settings as pyaedt_settings

    from pyedb.generic.settings import settings as pyaedb_settings

    pyedb_logger = pyaedt_settings.logger
    pyaedb_settings.use_pyaedt_log = True
    pyaedb_settings.logger = pyedb_logger

else:
    pyedb_logger = EdbLogger(to_stdout=settings.enable_screen_logs)
    from pyedb.generic.settings import settings as pyaedb_settings

    pyaedb_settings.logger = pyedb_logger

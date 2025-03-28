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
from __future__ import absolute_import

import ast
import codecs
from collections import OrderedDict
import csv
import datetime
import difflib
import fnmatch
import inspect
import itertools
import logging
import math
import os
import random
import re
import string
import sys
import tempfile
import time
import traceback

from pyedb.exceptions import MaterialModelException
from pyedb.generic.constants import CSS4_COLORS
from pyedb.generic.settings import settings

is_linux = os.name == "posix"
is_windows = not is_linux
_pythonver = sys.version_info[0]


try:
    import xml.etree.cElementTree as ET

    ET.VERSION
except ImportError:
    ET = None


class GrpcApiError(Exception):
    """ """

    pass


class MethodNotSupportedError(Exception):
    """ """

    pass


def _exception(ex_info, func, args, kwargs, message="Type Error"):
    """Write the trace stack to the desktop when a Python error occurs.

    Parameters
    ----------
    ex_info :

    func :

    args :

    kwargs :

    message :
         (Default value = "Type Error")

    Returns
    -------

    """

    tb_data = ex_info[2]
    tb_trace = traceback.format_tb(tb_data)
    _write_mes("{} on {}".format(message.upper(), func.__name__))
    try:
        _write_mes(ex_info[1].args[0])
    except (IndexError, AttributeError):
        pass
    for trace in traceback.format_stack():
        if func.__name__ in trace:
            for el in trace.split("\n"):
                _write_mes(el)
    for trace in tb_trace:
        tblist = trace.split("\n")
        for el in tblist:
            if func.__name__ in el:
                _write_mes(el)

    message_to_print = ""
    messages = ""
    if "error" in messages:
        message_to_print = messages[messages.index("[error]") :]
    # _write_mes("{} - {} -  {}.".format(ex_info[1], func.__name__, message.upper()))

    if message_to_print:
        _write_mes("Last Electronics Desktop Message - " + message_to_print)

    args_name = []
    try:
        args_dict = _get_args_dicts(func, args, kwargs)
        first_time_log = True

        for el in args_dict:
            if el != "self" and args_dict[el]:
                if first_time_log:
                    _write_mes("Method arguments: ")
                    first_time_log = False
                _write_mes("    {} = {} ".format(el, args_dict[el]))
    except:
        pass
    args = [func.__name__] + [i for i in args_name if i not in ["self"]]
    if not func.__name__.startswith("_"):
        _write_mes(
            "Check Online documentation on: https://edb.docs.pyansys.com/version/stable/search.html?q={}".format(
                "+".join(args)
            )
        )


def _function_handler_wrapper(user_function):  # pragma: no cover
    def wrapper(*args, **kwargs):  # pragma: no cover
        if not settings.enable_error_handler:
            result = user_function(*args, **kwargs)
            return result
        else:
            try:
                settings.time_tick = time.time()
                out = user_function(*args, **kwargs)
                if settings.enable_debug_logger or settings.enable_debug_edb_logger:
                    _log_method(user_function, args, kwargs)
                return out
            except TypeError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Type Error")
                return False
            except ValueError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Value Error")
                return False
            except AttributeError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Attribute Error")
                return False
            except KeyError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Key Error")
                return False
            except IndexError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Index Error")
                return False
            except AssertionError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Assertion Error")
                return False
            except NameError:
                _exception(sys.exc_info(), user_function, args, kwargs, "Name Error")
                return False
            except IOError:
                _exception(sys.exc_info(), user_function, args, kwargs, "IO Error")
                return False
            except MaterialModelException:
                _exception(sys.exc_info(), user_function, args, kwargs, "Material Model")
                return False

    return wrapper


import functools
import warnings


def deprecate_argument_name(argument_map):
    """Decorator to deprecate certain argument names in favor of new ones."""

    def decorator(func):
        """Decorator that wraps the function to handle deprecated arguments."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function that checks for deprecated arguments."""
            func_name = func.__name__
            for old_arg, new_arg in argument_map.items():
                if old_arg in kwargs:
                    warnings.warn(
                        f"Argument `{old_arg}` is deprecated for method `{func_name}`; use `{new_arg}` instead.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    # NOTE: Use old argument if new argument is not provided
                    if new_arg not in kwargs:
                        kwargs[new_arg] = kwargs.pop(old_arg)
                    else:
                        kwargs.pop(old_arg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_filename_without_extension(path):
    """Get the filename without its extension.

    Parameters
    ----------
    path : str
        Path for the file.


    Returns
    -------
    str
       Name for the file, excluding its extension.

    """
    return os.path.splitext(os.path.split(path)[1])[0]


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i : i + 250] for i in range(0, len(mes_text), 250)]
    for el in parts:
        settings.logger.error(el)


def _log_method(func, new_args, new_kwargs):  # pragma: no cover
    if not settings.enable_debug_internal_methods_logger and str(func.__name__)[0] == "_":
        return
    if not settings.enable_debug_geometry_operator_logger and "GeometryOperators" in str(func):
        return
    if (
        not settings.enable_debug_edb_logger
        and "Edb" in str(func) + str(new_args)
        or "database" in str(func) + str(new_args)
    ):
        return
    line_begin = "ARGUMENTS: "
    message = []
    delta = time.time() - settings.time_tick
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    msec = (s - int(s)) * 1000
    if d > 0:
        time_msg = " {}days {}h {}m {}sec.".format(d, h, m, int(s))
    elif h > 0:
        time_msg = " {}h {}m {}sec.".format(h, m, int(s))
    else:
        time_msg = "  {}m {}sec {}msec.".format(m, int(s), int(msec))
    if settings.enable_debug_methods_argument_logger:
        args_dict = _get_args_dicts(func, new_args, new_kwargs)
        id = 0
        if new_args:
            object_name = str([new_args[0]])[1:-1]
            id = object_name.find(" object at ")
        if id > 0:
            object_name = object_name[1:id]
            message.append("'{}' was run in {}".format(object_name + "." + str(func.__name__), time_msg))
        else:
            message.append("'{}' was run in {}".format(str(func.__name__), time_msg))
        message.append(line_begin)
        for k, v in args_dict.items():
            if k != "self":
                message.append("    {} = {}".format(k, v))
    for m in message:
        settings.logger.debug(m)


def _get_args_dicts(func, args, kwargs):
    if int(sys.version[0]) > 2:
        args_name = list(OrderedDict.fromkeys(inspect.getfullargspec(func)[0] + list(kwargs.keys())))
        args_dict = OrderedDict(list(itertools.zip_longest(args_name, args)) + list(kwargs.items()))
    else:
        args_name = list(OrderedDict.fromkeys(inspect.getargspec(func)[0] + list(kwargs.keys())))
        args_dict = OrderedDict(list(itertools.izip(args_name, args)) + list(kwargs.iteritems()))
    return args_dict


def env_path(input_version):
    """Get the path of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Path for the version environment variable.

    Examples
    --------
    >>> env_path_student("2021.2")
    "C:/Program Files/ANSYSEM/ANSYSEM2021.2/Win64"
    """
    return os.getenv(
        "ANSYSEM_ROOT{0}{1}".format(
            get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
        ),
        "",
    )


def get_version_and_release(input_version):
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    return (version, release)


def env_value(input_version):
    """Get the name of the version environment variable for an AEDT version.

    Parameters
    ----------
    input_version : str
        AEDT version.

    Returns
    -------
    str
        Name for the version environment variable.

    Examples
    --------
    >>> env_value("2021.2")
    "ANSYSEM_ROOT211"
    """
    return "ANSYSEM_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
    )


def generate_unique_name(rootname, suffix="", n=6):
    """Generate a new name given a root name and optional suffix.

    Parameters
    ----------
    rootname :
        Root name to add random characters to.
    suffix : string
        Suffix to add. The default is ``''``.
    n : int
        Number of random characters to add to the name. The default value is ``6``.

    Returns
    -------
    str
        Newly generated name.

    """
    char_set = string.ascii_uppercase + string.digits
    uName = "".join(random.choice(char_set) for _ in range(n))
    unique_name = rootname + "_" + uName
    if suffix:
        unique_name += "_" + suffix
    return unique_name


def normalize_path(path_in, sep=None):
    """Normalize path separators.

    Parameters
    ----------
    path_in : str
        Path to normalize.
    sep : str, optional
        Separator.

    Returns
    -------
    str
        Path normalized to new separator.
    """
    if sep is None:
        sep = os.sep
    return path_in.replace("\\", sep).replace("/", sep)


def check_numeric_equivalence(a, b, relative_tolerance=1e-7):
    """Check if two numeric values are equivalent to within a relative tolerance.

    Paraemters
    ----------
    a : int, float
        Reference value to compare to.
    b : int, float
        Secondary value for the comparison.
    relative_tolerance : float, optional
        Relative tolerance for the equivalence test. The difference is relative to the first value.
        The default is ``1E-7``.

    Returns
    -------
    bool
        ``True`` if the two passed values are equivalent.
    """
    if abs(a) > 0.0:
        reldiff = abs(a - b) / a
    else:
        reldiff = abs(b)
    return True if reldiff < relative_tolerance else False


def check_and_download_file(local_path, remote_path, overwrite=True):
    """Check if a file is remote and either download it or return the path.

    Parameters
    ----------
    local_path : str
        Local path to save the file to.
    remote_path : str
        Path to the remote file.
    overwrite : bool
        Whether to overwrite the file if it already exits locally.
        The default is ``True``.

    Returns
    -------
    str
    """
    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_file(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


def check_if_path_exists(path):
    """Check whether a path exists or not local or remote machine (for remote sessions only).

    Parameters
    ----------
    path : str
        Local or remote path to check.

    Returns
    -------
    bool
    """
    if settings.remote_rpc_session:
        return settings.remote_rpc_session.filemanager.pathexists(path)
    return os.path.exists(path)


def check_and_download_folder(local_path, remote_path, overwrite=True):
    """Check if a folder is remote and either download it or return the path.

    Parameters
    ----------
    local_path : str
        Local path to save the folder to.
    remote_path : str
        Path to the remote folder.
    overwrite : bool
        Whether to overwrite the folder if it already exits locally.
        The default is ``True``.

    Returns
    -------
    str
    """
    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_folder(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


def open_file(file_path, file_options="r"):  # pragma: no cover
    """Open a file and return the object.

    Parameters
    ----------
    file_path : str
        Full absolute path to the file (either local or remote).
    file_options : str, optional
        Options for opening the file.

    Returns
    -------
    object
        Opened file.
    """
    file_path = file_path.replace("\\", "/") if file_path[0] != "\\" else file_path
    dir_name = os.path.dirname(file_path)
    if "r" in file_options:
        if os.path.exists(file_path):
            return open(file_path, file_options)
        elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(
            file_path
        ):  # pragma: no cover
            local_file = os.path.join(tempfile.gettempdir(), os.path.split(file_path)[-1])
            settings.remote_rpc_session.filemanager.download_file(file_path, local_file)
            return open(local_file, file_options)
    elif os.path.exists(dir_name):
        return open(file_path, file_options)
    else:
        settings.logger.error("The file or folder %s does not exist", dir_name)


def get_string_version(input_version):
    output_version = input_version
    if isinstance(input_version, float):
        output_version = str(input_version)
        if len(output_version) == 4:
            output_version = "20" + output_version
    elif isinstance(input_version, int):
        output_version = str(input_version)
        output_version = "20{}.{}".format(output_version[:2], output_version[-1])
    elif isinstance(input_version, str):
        if len(input_version) == 3:
            output_version = "20{}.{}".format(input_version[:2], input_version[-1])
        elif len(input_version) == 4:
            output_version = "20" + input_version
    return output_version


def env_path_student(input_version):
    """Get the path of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
       AEDT student version.

    Returns
    -------
    str
        Path for the student version environment variable.

    Examples
    --------
    >>> env_path_student("2021.2")
    "C:/Program Files/ANSYSEM/ANSYSEM2021.2/Win64"
    """
    return os.getenv(
        "ANSYSEMSV_ROOT{0}{1}".format(
            get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
        ),
        "",
    )


def env_value_student(input_version):
    """Get the name of the version environment variable for an AEDT student version.

    Parameters
    ----------
    input_version : str
        AEDT student version.

    Returns
    -------
    str
         Name for the student version environment variable.

    Examples
    --------
    >>> env_value_student("2021.2")
    "ANSYSEMSV_ROOT211"
    """
    return "ANSYSEMSV_ROOT{0}{1}".format(
        get_version_and_release(input_version)[0], get_version_and_release(input_version)[1]
    )


def generate_unique_folder_name(rootname=None, folder_name=None):  # pragma: no cover
    """Generate a new AEDT folder name given a rootname.

    Parameters
    ----------
    rootname : str, optional
        Root name for the new folder. The default is ``None``.
    folder_name : str, optional
        Name for the new AEDT folder if one must be created.

    Returns
    -------
    str
    """
    if not rootname:
        if settings.remote_rpc_session:
            rootname = settings.remote_rpc_session_temp_folder
        else:
            rootname = tempfile.gettempdir()
    if folder_name is None:
        folder_name = generate_unique_name("pyedb_prj", n=3)
    temp_folder = os.path.join(rootname, folder_name)
    if settings.remote_rpc_session and not settings.remote_rpc_session.filemanager.pathexists(temp_folder):
        settings.remote_rpc_session.filemanager.makedirs(temp_folder)
    elif not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    return temp_folder


def generate_unique_project_name(rootname=None, folder_name=None, project_name=None, project_format="aedt"):
    """Generate a new AEDT project name given a rootname.

    Parameters
    ----------
    rootname : str, optional
        Root name where the new project is to be created.
    folder_name : str, optional
        Name of the folder to create. The default is ``None``, in which case a random folder
        is created. Use ``""`` if you do not want to create a subfolder.
    project_name : str, optional
        Name for the project. The default is ``None``, in which case a random project is
        created. If a project with this name already exists, a new suffix is added.
    project_format : str, optional
        Project format. The default is ``"aedt"``. Options are ``"aedt"`` and ``"aedb"``.

    Returns
    -------
    str
    """
    if not project_name:
        project_name = generate_unique_name("Project", n=3)
    name_with_ext = project_name + "." + project_format
    folder_path = generate_unique_folder_name(rootname, folder_name=folder_name)
    prj = os.path.join(folder_path, name_with_ext)
    if check_if_path_exists(prj):
        name_with_ext = generate_unique_name(project_name, n=3) + "." + project_format
        prj = os.path.join(folder_path, name_with_ext)
    return prj


def _retry_ntimes(n, function, *args, **kwargs):
    """

    Parameters
    ----------
    n :

    function :

    *args :

    **kwargs :


    Returns
    -------

    """
    func_name = None
    if function.__name__ == "InvokeAedtObjMethod":
        func_name = args[1]
    retry = 0
    ret_val = None
    inclusion_list = [
        "CreateVia",
        "PasteDesign",
        "Paste",
        "PushExcitations",
        "Rename",
        "RestoreProjectArchive",
        "ImportGerber",
    ]
    # if func_name and func_name not in inclusion_list and not func_name.startswith("Get"):
    if func_name and func_name not in inclusion_list:
        n = 1
    while retry < n:
        try:
            ret_val = function(*args, **kwargs)
        except:
            retry += 1
            time.sleep(settings.retry_n_times_time_interval)
        else:
            return ret_val
    if retry == n:
        if "__name__" in dir(function):
            raise AttributeError("Error in Executing Method {}.".format(function.__name__))
        else:
            raise AttributeError("Error in Executing Method.")


def time_fn(fn, *args, **kwargs):  # pragma: no cover
    start = datetime.datetime.now()
    results = fn(*args, **kwargs)
    end = datetime.datetime.now()
    fn_name = fn.__module__ + "." + fn.__name__
    delta = (end - start).microseconds * 1e-6
    print(fn_name + ": " + str(delta) + "s")
    return results


def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def is_number(a):
    if isinstance(a, float) or isinstance(a, int):
        return True
    elif isinstance(a, str):
        try:
            float(a)
            return True
        except ValueError:
            return False
    else:
        return False


def is_array(a):  # pragma: no cover
    try:
        v = list(ast.literal_eval(a))
    except (ValueError, TypeError, NameError, SyntaxError):
        return False
    else:
        if type(v) is list:
            return True
        else:
            return False


def is_project_locked(project_path):
    """Check if an AEDT project lock file exists.

    Parameters
    ----------
    project_path : str
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    return check_if_path_exists(project_path + ".lock")


def remove_project_lock(project_path):  # pragma: no cover
    """Check if an AEDT project exists and try to remove the lock file.

    .. note::
       This operation is risky because the file could be opened in another AEDT instance.

    Parameters
    ----------
    project_path : str
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    if os.path.exists(project_path + ".lock"):
        os.remove(project_path + ".lock")
    return True


def read_csv(filename, encoding="utf-8"):  # pragma: no cover
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    list

    """

    lines = []
    with codecs.open(filename, "rb", encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            lines.append(row)
    return lines


def read_csv_pandas(filename, encoding="utf-8"):  # pragma: no cover
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    :class:`pandas.DataFrame`

    """
    try:
        import pandas as pd

        return pd.read_csv(filename, encoding=encoding, header=0, na_values=".")
    except ImportError:
        logging.error("Pandas is not available. Install it.")
        return None


def read_tab(filename):  # pragma: no cover
    """Read information from a TAB file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the TAB file.

    Returns
    -------
    list

    """
    with open(filename) as my_file:
        lines = my_file.readlines()
    return lines


def read_xlsx(filename):  # pragma: no cover
    """Read information from an XLSX file and return a list.

    Parameters
    ----------
    filename : str
            Full path and name for the XLSX file.

    Returns
    -------
    list

    """
    try:
        import pandas as pd

        lines = pd.read_excel(filename)
        return lines
    except ImportError:
        lines = []
        return lines


def write_csv(output, list_data, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL):  # pragma: no cover
    f = open(output, "w", newline="")
    writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
    for data in list_data:
        writer.writerow(data)
    f.close()
    return True


def filter_tuple(value, search_key1, search_key2):  # pragma: no cover
    """Filter a tuple of two elements with two search keywords."""
    ignore_case = True

    def _create_pattern(k1, k2):
        k1a = re.sub(r"\?", r".", k1)
        k1b = re.sub(r"\*", r".*?", k1a)
        k2a = re.sub(r"\?", r".", k2)
        k2b = re.sub(r"\*", r".*?", k2a)
        pattern = r".*\({},{}\)".format(k1b, k2b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key1, search_key2), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key1, search_key2))

    m = compiled_re.search(value)
    if m:
        return True
    return False


def filter_string(value, search_key1):  # pragma: no cover
    """Filter a string"""
    ignore_case = True

    def _create_pattern(k1):
        k1a = re.sub(r"\?", r".", k1.replace("\\", "\\\\"))
        k1b = re.sub(r"\*", r".*?", k1a)
        pattern = r"^{}$".format(k1b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key1), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key1))  # pragma: no cover

    m = compiled_re.search(value)
    if m:
        return True
    return False


def recursive_glob(startpath, filepattern):  # pragma: no cover
    """Get a list of files matching a pattern, searching recursively from a start path.

    Keyword Arguments:
    startpath -- starting path (directory)
    filepattern -- fnmatch-style filename pattern
    """
    if settings.remote_rpc_session:
        files = []
        for i in settings.remote_rpc_session.filemanager.listdir(startpath):
            if settings.remote_rpc_session.filemanager.isdir(os.path.join(startpath, i)):
                files.extend(recursive_glob(os.path.join(startpath, i), filepattern))
            elif fnmatch.fnmatch(i, filepattern):
                files.append(os.path.join(startpath, i))
        return files
    else:
        return [
            os.path.join(dirpath, filename)
            for dirpath, _, filenames in os.walk(startpath)
            for filename in filenames
            if fnmatch.fnmatch(filename, filepattern)
        ]


def number_aware_string_key(s):  # pragma: no cover
    """Get a key for sorting strings that treats embedded digit sequences as integers.

    Parameters
    ----------
    s : str
        String to calculate the key from.

    Returns
    -------
    tuple
        Tuple of key entries.
    """

    def is_digit(c):
        return "0" <= c and c <= "9"

    result = []
    i = 0
    while i < len(s):
        if is_digit(s[i]):
            j = i + 1
            while j < len(s) and is_digit(s[j]):
                j += 1
            key = int(s[i:j])
            result.append(key)
            i = j
        else:
            j = i + 1
            while j < len(s) and not is_digit(s[j]):
                j += 1
            key = s[i:j]
            result.append(key)
            i = j
    return tuple(result)


def compute_fft(time_vals, value):  # pragma: no cover
    """Compute FFT of input transient data.

    Parameters
    ----------
    time_vals : `pandas.Series`
    value : `pandas.Series`

    Returns
    -------
    tuple
        Frequency and Values.
    """
    try:
        import numpy as np
    except ImportError:
        logging.error("NumPy is not available. Install it.")
        return False

    deltaT = time_vals[-1] - time_vals[0]
    num_points = len(time_vals)
    valueFFT = np.fft.fft(value, num_points)
    Npoints = int(len(valueFFT) / 2)
    valueFFT = valueFFT[1 : Npoints + 1]
    valueFFT = valueFFT / len(valueFFT)
    n = np.arange(num_points)
    freq = n / deltaT
    return freq, valueFFT


def parse_excitation_file(
    file_name,
    is_time_domain=True,
    x_scale=1,
    y_scale=1,
    impedance=50,
    data_format="Power",
    encoding="utf-8",
    out_mag="Voltage",
):  # pragma: no cover
    """Parse a csv file and convert data in list that can be applied to Hfss and Hfss3dLayout sources.

    Parameters
    ----------
    file_name : str
        Full name of the input file.
    is_time_domain : bool, optional
        Either if the input data is Time based or Frequency Based. Frequency based data are Mag/Phase (deg).
    x_scale : float, optional
        Scaling factor for x axis.
    y_scale : float, optional
        Scaling factor for y axis.
    data_format : str, optional
        Either `"Power"`, `"Current"` or `"Voltage"`.
    impedance : float, optional
        Excitation impedance. Default is `50`.
    encoding : str, optional
        Csv file encoding.
    out_mag : str, optional
        Output magnitude format. It can be `"Voltage"` or `"Power"` depending on Hfss solution.

    Returns
    -------
    tuple
        Frequency, magnitude and phase.
    """
    try:
        import numpy as np
    except ImportError:
        logging.error("NumPy is not available. Install it.")
        return False
    df = read_csv_pandas(file_name, encoding=encoding)
    if is_time_domain:
        time = df[df.keys()[0]].values * x_scale
        val = df[df.keys()[1]].values * y_scale
        freq, fval = compute_fft(time, val)

        if data_format.lower() == "current":
            if out_mag == "Voltage":
                fval = fval * impedance
            else:
                fval = fval * fval * impedance
        elif data_format.lower() == "voltage":
            if out_mag == "Power":
                fval = fval * fval / impedance
        else:
            if out_mag == "Voltage":
                fval = np.sqrt(fval * impedance)
        mag = list(np.abs(fval))
        phase = [math.atan2(j, i) * 180 / math.pi for i, j in zip(list(fval.real), list(fval.imag))]

    else:
        freq = list(df[df.keys()[0]].values * x_scale)
        if data_format.lower() == "current":
            mag = df[df.keys()[1]].values * df[df.keys()[1]].values * impedance * y_scale * y_scale
        elif data_format.lower() == "voltage":
            mag = df[df.keys()[1]].values * df[df.keys()[1]].values / impedance * y_scale * y_scale
        else:
            mag = df[df.keys()[1]].values * y_scale
        mag = list(mag)
        phase = list(df[df.keys()[2]].values)
    return freq, mag, phase


def tech_to_control_file(tech_path, unit="nm", control_path=None):  # pragma: no cover
    """Convert a TECH file to an XML file for use in a GDS or DXF import.

    Parameters
    ----------
    tech_path : str
        Full path to the TECH file.
    unit : str, optional
        Tech units. If specified in tech file this parameter will not be used. Default is ``"nm"``.
    control_path : str, optional
        Path for outputting the XML file.

    Returns
    -------
    str
        Out xml file.
    """
    result = []
    with open(tech_path) as f:
        vals = list(CSS4_COLORS.values())
        id_layer = 0
        for line in f:
            line_split = line.split()
            if len(line_split) == 5:
                layerID, layer_name, _, elevation, layer_height = line.split()
                x = '      <Layer Color="{}" GDSIIVia="{}" Name="{}" TargetLayer="{}" Thickness="{}"'.format(
                    vals[id_layer],
                    "true" if layer_name.lower().startswith("v") else "false",
                    layerID,
                    layer_name,
                    layer_height,
                )
                x += ' Type="conductor"/>'
                result.append(x)
                id_layer += 1
            elif len(line_split) > 1 and "UNIT" in line_split[0]:
                unit = line_split[1]
    if not control_path:
        control_path = os.path.splitext(tech_path)[0] + ".xml"
    with open(control_path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
        f.write('    <c:Control xmlns:c="http://www.ansys.com/control" schemaVersion="1.0">\n')
        f.write("\n")
        f.write('      <Stackup schemaVersion="1.0">\n')
        f.write('        <Layers LengthUnit="{}">\n'.format(unit))
        for res in result:
            f.write(res + "\n")

        f.write("    </Layers>\n")
        f.write("  </Stackup>\n")
        f.write("\n")
        f.write('  <ImportOptions Flatten="true" GDSIIConvertPolygonToCircles="false" ImportDummyNet="true"/>\n')
        f.write("\n")
        f.write("</c:Control>\n")

    return control_path


class PropsManager(object):
    def __getitem__(self, item):  # pragma: no cover
        """Get the `self.props` key value.

        Parameters
        ----------
        item : str
            Key to search
        """
        item_split = item.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        props = self.props
        found_el = []
        matching_percentage = 1
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                # found_el = difflib.get_close_matches(item_value, list(props.keys()), 1, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    # props = props[found_el[0]]
            if found_el:
                return props
            else:
                matching_percentage -= 0.02
        self._app.logger.warning("Key %s not found.Check one of available keys in self.available_properties", item)
        return None

    def __setitem__(self, key, value):  # pragma: no cover
        """Set the `self.props` key value.

        Parameters
        ----------
        key : str
            Key to apply.
        value : int, float, bool, str, dict
            Value to apply.
        """
        item_split = key.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        found_el = []
        props = self.props
        matching_percentage = 1
        key_path = []
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    key_path.append(found_el[2])
            if found_el:
                if matching_percentage < 1:
                    self._app.logger.info(
                        "Key %s matched internal key '%s' with confidence of %s.",
                        key,
                        "/".join(key_path),
                        round(matching_percentage * 100),
                    )
                matching_percentage = 0

            else:
                matching_percentage -= 0.02
        if found_el:
            found_el[1][found_el[2]] = value
            self.update()
        else:
            props[key] = value
            self.update()
            self._app.logger.warning("Key %s not found. Trying to applying new key ", key)

    def _recursive_search(self, dict_in, key="", matching_percentage=0.8):  # pragma: no cover
        f = difflib.get_close_matches(key, list(dict_in.keys()), 1, matching_percentage)
        if f:
            return True, dict_in, f[0]
        else:
            for v in list(dict_in.values()):
                if isinstance(v, (dict, OrderedDict)):
                    out_val = self._recursive_search(v, key, matching_percentage)
                    if out_val:
                        return out_val
                elif isinstance(v, list) and isinstance(v[0], (dict, OrderedDict)):
                    for val in v:
                        out_val = self._recursive_search(val, key, matching_percentage)
                        if out_val:
                            return out_val
        return False

    def _recursive_list(self, dict_in, prefix=""):  # pragma: no cover
        available_list = []
        for k, v in dict_in.items():
            if prefix:
                name = prefix + "/" + k
            else:
                name = k
            available_list.append(name)
            if isinstance(v, (dict, OrderedDict)):
                available_list.extend(self._recursive_list(v, name))
        return available_list

    @property
    def available_properties(self):  # pragma: no cover
        """Available properties.

        Returns
        -------
        list
        """
        if self.props:
            return self._recursive_list(self.props)
        return []

    def update(self):
        """Update method."""
        pass


clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
rgb_color_codes = {
    "Black": (0, 0, 0),
    "Green": (0, 128, 0),
    "White": (255, 255, 255),
    "Red": (255, 0, 0),
    "Lime": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Silver": (192, 192, 192),
    "Gray": (128, 128, 128),
    "Maroon": (128, 0, 0),
    "Olive": (128, 128, 0),
    "Purple": (128, 0, 128),
    "Teal": (0, 128, 128),
    "Navy": (0, 0, 128),
    "copper": (184, 115, 51),
    "stainless steel": (224, 223, 219),
}


def install_with_pip(package_name, package_path=None, upgrade=False, uninstall=False):  # pragma: no cover
    """Install a new package using pip.
    This method is useful for installing a package from the AEDT Console without launching the Python environment.

    Parameters
    ----------
    package_name : str
        Name of the package to install.
    package_path : str, optional
        Path for the GitHub package to download and install. For example, ``git+https://.....``.
    upgrade : bool, optional
        Whether to upgrade the package. The default is ``False``.
    uninstall : bool, optional
        Whether to install the package or uninstall the package.
    """

    import subprocess

    executable = '"{}"'.format(sys.executable) if is_windows else sys.executable

    commands = []
    if uninstall:
        commands.append([executable, "-m", "pip", "uninstall", "--yes", package_name])
    else:
        if package_path and upgrade:
            commands.append([executable, "-m", "pip", "uninstall", "--yes", package_name])
            command = [executable, "-m", "pip", "install", package_path]
        else:
            command = [executable, "-m", "pip", "install", package_name]
        if upgrade:
            command.append("-U")

        commands.append(command)
    for command in commands:
        if is_linux:
            p = subprocess.Popen(command)
        else:
            p = subprocess.Popen(" ".join(command))
        p.wait()


class Help:  # pragma: no cover
    def __init__(self):
        self._base_path = "https://edb.docs.pyansys.com/version/stable"
        self.browser = "default"

    def _launch_ur(self, url):
        import webbrowser

        if self.browser != "default":
            webbrowser.get(self.browser).open_new_tab(url)
        else:
            webbrowser.open_new_tab(url)

    def search(self, keywords, app_name=None, search_in_examples_only=False):
        """Search for one or more keywords.

        Parameters
        ----------
        keywords : str or list
        app_name : str, optional
            Name of a PyEDB app.
        search_in_examples_only : bool, optional
            Whether to search for the one or more keywords only in the PyEDB examples.
            The default is ``False``.
        """
        if isinstance(keywords, str):
            keywords = [keywords]
        if search_in_examples_only:
            keywords.append("This example")
        if app_name:
            keywords.append(app_name)
        url = self._base_path + "/search.html?q={}".format("+".join(keywords))
        self._launch_ur(url)

    def getting_started(self):
        """Open the PyEDB User guide page."""
        url = self._base_path + "/user_guide/index.html"
        self._launch_ur(url)

    def examples(self):
        """Open the PyEDB Examples page."""
        url = self._base_path + "/examples/index.html"
        self._launch_ur(url)

    def github(self):
        """Open the PyEDB GitHub page."""
        url = "https://github.com/ansys/pyedb"
        self._launch_ur(url)

    def changelog(self, release=None):
        """Open the PyEDB GitHub Changelog for a given release.

        Parameters
        ----------
        release : str, optional
            Release to get the changelog for. For example, ``"0.6.70"``.
        """
        if release is None:
            from pyedb import __version__ as release
        url = "https://github.com/ansys/pyedb/releases/tag/v" + release
        self._launch_ur(url)

    def issues(self):
        """Open the PyEDB GitHub Issues page."""
        url = "https://github.com/ansys/pyedb/issues"
        self._launch_ur(url)

    def ansys_forum(self):
        """Open the PyEDB GitHub Issues page."""
        url = "https://discuss.ansys.com/discussions/tagged/pyedb"
        self._launch_ur(url)

    def developer_forum(self):
        """Open the Discussions page on the Ansys Developer site."""
        url = "https://developer.ansys.com/"
        self._launch_ur(url)


# class Property(property):
#
#
#     def getter(self, fget):
#         """Property getter."""
#         return self.__class__.__base__(fget, self.fset, self.fdel, self.__doc__)
#
#
#     def setter(self, fset):
#         """Property setter."""
#         return self.__class__.__base__(self.fget, fset, self.fdel, self.__doc__)
#
#
#     def deleter(self, fdel):
#         """Property deleter."""
#         return self.__class__.__base__(self.fget, self.fset, fdel, self.__doc__)

# property = Property

online_help = Help()

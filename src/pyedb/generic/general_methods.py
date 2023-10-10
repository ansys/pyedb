# -*- coding: utf-8 -*-
from __future__ import absolute_import

from functools import update_wrapper
import os
import sys
import time
import string
import random
from collections import OrderedDict
import inspect
import itertools
import traceback
from pyedb.generic.settings import settings


def pyedb_function_handler(direct_func=None):
    """Provides an exception handler, logging mechanism, and argument converter for client-server
    communications.

    This method returns the function itself if correctly executed. Otherwise, it returns ``False``
    and displays errors.

    """
    if callable(direct_func):
        user_function = direct_func
        wrapper = _function_handler_wrapper(user_function)
        return update_wrapper(wrapper, user_function)
    elif direct_func is not None:
        raise TypeError("Expected first argument to be a callable, or None")

    def decorating_function(user_function):
        wrapper = _function_handler_wrapper(user_function)
        return update_wrapper(wrapper, user_function)

    return decorating_function


@pyedb_function_handler()
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


def _function_handler_wrapper(user_function):
    def wrapper(*args, **kwargs):
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
    return wrapper


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
        message_to_print = messages[messages.index("[error]"):]
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
            "Check Online documentation on: https://aedt.docs.pyansys.com/version/stable/search.html?q={}".format(
                "+".join(args)
            )
        )


def _write_mes(mes_text):
    mes_text = str(mes_text)
    parts = [mes_text[i: i + 250] for i in range(0, len(mes_text), 250)]
    for el in parts:
        settings.logger.error(el)


def _log_method(func, new_args, new_kwargs):
    if not settings.enable_debug_internal_methods_logger and str(func.__name__)[0] == "_":
        return
    if not settings.enable_debug_geometry_operator_logger and "GeometryOperators" in str(func):
        return
    if (
            not settings.enable_debug_edb_logger
            and "Edb" in str(func) + str(new_args)
            or "edb_core" in str(func) + str(new_args)
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


@pyedb_function_handler()
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


@pyedb_function_handler()
def get_version_and_release(input_version):
    version = int(input_version[2:4])
    release = int(input_version[5])
    if version < 20:
        if release < 3:
            version -= 1
        else:
            release -= 2
    return (version, release)


@pyedb_function_handler()
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


@pyedb_function_handler()
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

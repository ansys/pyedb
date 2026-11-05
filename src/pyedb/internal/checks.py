# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Provides functions for performing common checks."""
import warnings

from collections.abc import Callable
from importlib import import_module
from functools import wraps
from typing import TypeVar
from typing import Any
from typing import cast


_F = TypeVar("_F", bound=Callable[..., Any])

_DEPENDENCY_CACHE: dict[str, bool] = {}
"""Availability cache shared by every dependency check, regardless of target."""

_DEPENDENCY_IMPORT_ALIASES = {
    "pillow": "PIL",
    "visualization_interface": "ansys.tools.visualization_interface",
}
"""Import-module aliases for dependencies whose module differs from their name."""


def install_message(dependency: str | list[str], target: str, level: str = "method") -> str:
    """Generate an installation message for missing dependencies.

    Examples
    --------
    >>> from pyedb.internal.checks import install_message
    >>> install_message("pyvista", "graphics")

    """
    if isinstance(dependency, list):
        msg = f"Dependencies {', '.join(dependency)} are required."
    else:
        msg = f"Dependency {dependency} is required."
    msg += f" Please install the ``{target}`` target to use this {level}."
    msg += f" You can install it by running `pip install pyedb[{target}]`"
    msg += " or `pip install pyedb[all]`." if target != "all" else "."
    return msg


def check_dependency(dependency: str, target: str = "all", warning: bool = False) -> bool:
    """Check whether a Python dependency can be imported.

    Parameters
    ----------
    dependency : str
        Dependency name or importable module path. Known aliases in
        ``_DEPENDENCY_IMPORT_ALIASES`` are resolved to their import module automatically.
    target : str, optional
        PyAEDT installation target to mention in the error message. Defaults to ``"all"``.
    warning : bool, optional
        If True, issue a warning instead of raising an error. Default is False.

    Returns
    -------
    bool
        True if the dependency is available, False if unavailable and warning is True.

    Raises
    ------
    ImportError
        If dependency is not available and warning is False.

    Examples
    --------
    >>> from pyedb.internal.checks import check_dependency
    >>> check_dependency("pyvista", target="graphics")

    """
    available = _DEPENDENCY_CACHE.get(dependency)
    if available is None:
        module_name = _DEPENDENCY_IMPORT_ALIASES.get(dependency, dependency)
        try:
            import_module(module_name)
            available = True
        except ImportError:
            available = False
        _DEPENDENCY_CACHE[dependency] = available

    if not available:
        error_msg = install_message(dependency, target)
        if warning:
            warnings.warn(error_msg, stacklevel=2)
            return False
        raise ImportError(error_msg)
    return True


def _requires_dependency(*dependencies: str, target: str) -> Callable[[_F], _F]:
    """Build a decorator that checks every dependency is importable for the given install target."""
    if not dependencies:
        raise ValueError("At least one dependency must be provided.")

    def decorator(method: _F) -> _F:
        @wraps(method)
        def wrapper(*args, **kwargs):
            for dep in dependencies:
                check_dependency(dep, target=target)
            return method(*args, **kwargs)

        return cast(_F, wrapper)

    return decorator


def requires_dotnet_dependency(*dependencies: str) -> Callable[[_F], _F]:
    """Decorate a method as requiring specific graphics dependencies.

    The main goal of this decorator is to isolate the logic around checking graphics
    dependencies and providing consistent error messages across methods that require
    such dependencies.

    Parameters
    ----------
    *dependencies : str
        Names of required dependencies (e.g., 'pyvista', 'matplotlib', 'vtk').

    Returns
    -------
    callable
        Decorated method.

    Raises
    ------
    ImportError
        If any of the required dependencies are not available.

    Examples
    --------
    >>> from pyedb.internal.checks import requires_dotnet_dependency
    >>> decorator = requires_dotnet_dependency("ansys-pythonnet", "dotnet")
    >>> callable(decorator)
    True

    """
    return _requires_dependency(*dependencies, target="dotnet")
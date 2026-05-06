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

from __future__ import annotations

import functools
import time
from typing import Any, TypeVar
import warnings

from pyedb.generic.settings import settings

_T = TypeVar("_T")


def _mark_deprecated(target: _T, message: str) -> _T:
    """Attach deprecation metadata used by IDEs and tests."""
    setattr(target, "__deprecated__", message)
    return target


def deprecated(reason: str = "", *, category: Any = FutureWarning):
    """Decorator to mark functions or methods as deprecated.

    Parameters
    ----------
    reason : str, optional
        Message to display with the deprecation warning.
    category : Warning, optional
        Warning category to emit. Use ``None`` to disable runtime warnings while preserving metadata.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"Call to deprecated function {func.__name__}."  # <-- Changed from __qualname__ to __name__
            if reason:
                msg += f" {reason}"
            if category is not None:
                warnings.warn(msg, category=FutureWarning, stacklevel=2)
            return func(*args, **kwargs)

        return _mark_deprecated(wrapper, reason)

    return decorator


def deprecated_class(reason: str = "", *, category: Any = FutureWarning):
    """Decorator to mark a class as deprecated.

    Parameters
    ----------
    reason : str, optional
        Message to display with the deprecation warning.
    category : Warning, optional
        Warning category to emit. Use ``None`` to disable runtime warnings while preserving metadata.
    """

    def decorator(cls):
        orig_init = cls.__init__

        @functools.wraps(orig_init)
        def new_init(self, *args, **kwargs):
            msg = f"Call to deprecated class {cls.__qualname__}."
            if reason:
                msg += f" {reason}"
            if category is not None:
                warnings.warn(msg, category=FutureWarning, stacklevel=2)
            orig_init(self, *args, **kwargs)

        cls.__init__ = _mark_deprecated(new_init, reason)
        return _mark_deprecated(cls, reason)

    return decorator


def deprecated_property(message: str, *, category: Any = FutureWarning):
    """
    This decorator marks a property as deprecated.
    It will emit a warning when the property is accessed.

    Parameters
    ----------
    message : str
        Custom message to display after the deprecation warning.
    category : Warning, optional
        Warning category to emit. Use ``None`` to disable runtime warnings while preserving metadata.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if category is not None:
                warnings.warn(
                    f"Accessing deprecated property {func.__name__}. {message}", category=FutureWarning, stacklevel=2
                )
            return func(*args, **kwargs)

        return _mark_deprecated(wrapper, message)

    return decorator


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
                        category=FutureWarning,
                    )
                    # NOTE: Use old argument if new argument is not provided
                    if new_arg not in kwargs:
                        kwargs[new_arg] = kwargs.pop(old_arg)
                    else:
                        kwargs.pop(old_arg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def execution_timer(custom_text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            settings.logger.info(f"{custom_text} completed in {elapsed_time:.4f} seconds.")
            return result

        return wrapper

    return decorator

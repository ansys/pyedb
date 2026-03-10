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

import functools
import inspect
import re
import time
import warnings

from pyedb.generic.settings import settings


def deprecated(reason=None):
    """Decorator to mark functions or methods as deprecated.

    Automatically infers replacement method from return statement when no reason provided.
    Customized reason can be provided to override inferred replacement.

    Examples
    --------
    @deprecated
    def close_edb(self):
        return self.close()
    # -> "Call to deprecated function close_edb(). Use close() instead."
    """

    def _create_wrapper(func, msg_reason):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            msg = f"Call to deprecated function {func_name}()."
            if msg_reason:
                msg += f" {msg_reason}"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    def _infer_replacement(func):
        """Try to infer replacement from return self.xxx.method() statement."""
        try:
            source = inspect.getsource(func)
            lines = source.split("\n")
            def_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    def_idx = i
                    break

            # Get body lines (after def line)
            body_lines = lines[def_idx + 1 :]

            # Find return statement in body
            for line in body_lines:
                stripped = line.strip()
                if stripped.startswith("return "):
                    # Match: return self.xxx.method() or return self.method()
                    # Extract just the method name (last part after last dot)
                    match = re.search(r"return\s+self(?:\.\w+)*\.(\w+)\s*\(", stripped)
                    if match:
                        new_method = match.group(1)
                        return f"Use {new_method}() instead."
                    break

        except (OSError, TypeError, IOError):
            pass
        return ""

    # Handle @deprecated (without parentheses)
    if callable(reason):
        func = reason
        inferred = _infer_replacement(func)
        return _create_wrapper(func, inferred)

    # Handle @deprecated() or @deprecated("reason")
    def decorator(func):
        if reason:
            return _create_wrapper(func, reason)
        inferred = _infer_replacement(func)
        return _create_wrapper(func, inferred)

    return decorator


def deprecated_class(reason: str = ""):
    """Decorator to mark a class as deprecated.

    Parameters
    ----------
    reason : str, optional
        Message to display with the deprecation warning.
    """

    def decorator(cls):
        orig_init = cls.__init__

        @functools.wraps(orig_init)
        def new_init(self, *args, **kwargs):
            msg = f"Call to deprecated class {cls.__qualname__}."
            if reason:
                msg += f" {reason}"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            orig_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator


def deprecated_property(reason=None):
    """Decorator to mark properties as deprecated."""

    def _create_wrapper(func, msg_reason):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            prop_name = func.__name__
            msg = f"Access to deprecated property {prop_name}."
            if msg_reason:
                msg += f" {msg_reason}"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    def _infer_replacement(func):
        """Try to infer replacement from return self.xxx.property statement."""
        try:
            source = inspect.getsource(func)
            lines = source.split("\n")
            def_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    def_idx = i
                    break

            body_lines = lines[def_idx + 1 :]

            for line in body_lines:
                stripped = line.strip()
                if stripped.startswith("return "):
                    # Match: return self.xxx.property or return self.property
                    match = re.search(r"return\s+self(?:\.\w+)*\.(\w+)\s*$", stripped)
                    if match:
                        new_prop = match.group(1)
                        return f"Use {new_prop} instead."
                    break

        except (OSError, TypeError, IOError):
            pass
        return ""

    # handle without parentheses
    if callable(reason):
        func = reason
        inferred = _infer_replacement(func)
        return _create_wrapper(func, inferred)

    def decorator(func):
        if reason:
            return _create_wrapper(func, reason)
        inferred = _infer_replacement(func)
        return _create_wrapper(func, inferred)

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

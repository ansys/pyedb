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

import os
from pathlib import Path
import pkgutil
import sys
import warnings

existing_showwarning = warnings.showwarning


def custom_show_warning(message, category, filename, lineno, file=None, line=None):
    """Custom warning used to remove <stdin>:loc: pattern."""
    print(f"{category.__name__}: {message}")


warnings.showwarning = custom_show_warning

modules = [tup[1] for tup in pkgutil.iter_modules()]
is_linux = os.name == "posix"
is_windows = not is_linux
is_clr = False

if is_linux:  # pragma: no cover
    dotnet_root = None
    runtime_config = None
    runtime_spec = None
    # Use system .NET core runtime
    if os.environ.get("DOTNET_ROOT") is None:
        try:
            from clr_loader import get_coreclr
            from pythonnet import load

            runtime = get_coreclr()
            load(runtime)
            os.environ["DOTNET_ROOT"] = runtime.dotnet_root.as_posix()
            is_clr = True
        except Exception:
            warnings.warn(
                ".NET is not found. PyEDB can only work in gRPC (client) mode. For more information, see "
                "https://aedt.docs.pyansys.com/version/stable/release_1_0.html#dotnet-changes-in-linux"
            )
    # Use specified .NET root folder
    else:
        dotnet_root = Path(os.environ["DOTNET_ROOT"])

        try:
            from clr_loader import find_runtimes

            # Check if the dotnet_root exists and contains the shared subdirectory
            shared_dir = dotnet_root / "shared"
            if not shared_dir.exists():
                warnings.warn(
                    "DOTNET_ROOT is set but does not contain a valid .NET installation. "
                    "PyEDB can only work in gRPC (client) mode."
                )
            else:
                candidates = [rt for rt in find_runtimes() if rt.name == "Microsoft.NETCore.App"]
                candidates.sort(key=lambda spec: spec.version, reverse=True)
                if not candidates:
                    warnings.warn(
                        "Configuration file could not be found from DOTNET_ROOT. "
                        "Please ensure that .NET SDK is correctly installed or "
                        "that DOTNET_ROOT is correctly set."
                    )
                else:
                    runtime_spec = candidates[0]
        except Exception:
            warnings.warn("Could not find .NET runtimes. PyEDB can only work in gRPC (client) mode.")
    # Use specific .NET core runtime
    if dotnet_root is not None and (runtime_config is not None or runtime_spec is not None):
        try:
            from pythonnet import load

            load(
                "coreclr",
                runtime_config=str(runtime_config) if runtime_config else None,
                runtime_spec=runtime_spec,
                dotnet_root=str(dotnet_root),
            )
            os.environ["DOTNET_ROOT"] = dotnet_root.as_posix()
            is_clr = True
        except ImportError:
            msg = "pythonnet not installed. PyEDB can only work in gRPC (client) mode."
            warnings.warn(msg)
else:
    try:
        from pythonnet import load

        load("coreclr")
        is_clr = True
    except:
        warnings.warn("Unable to load .NET core runtime")


try:  # work around a number formatting bug in the EDB API for non-English locales
    # described in #1980
    import clr as _clr  # isort:skip
    from System.Globalization import CultureInfo as _CultureInfo

    _CultureInfo.DefaultThreadCurrentCulture = _CultureInfo.InvariantCulture
    from System import Array, Convert, Double, String, Tuple
    from System.Collections.Generic import Dictionary, List

    edb_initialized = True

except (ImportError, RuntimeError):  # pragma: no cover
    if is_windows:
        warnings.warn(
            "The clr is missing. Please ensure that you have installed the required dependencies. "
            "They can be installed using 'pip install pyedb[dotnet]'."
        )
        edb_initialized = False
    _clr = None
    String = None
    Double = None
    Convert = None
    List = None
    Tuple = None
    Dictionary = None
    Array = None
    edb_initialized = False

if "win32com" in modules:
    try:
        import win32com.client as win32_client
    except ImportError:
        try:
            import win32com.client as win32_client
        except ImportError:
            win32_client = None

warnings.showwarning = existing_showwarning

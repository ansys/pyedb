import os
from pathlib import Path
import pkgutil
import sys
import warnings

import pyedb

LINUX_WARNING = (
    "Due to compatibility issues between .NET Core and libssl on some Linux versions, "
    "for example Ubuntu 22.04, we are going to stop depending on `dotnetcore2`."
    "Instead of using this package which embeds .NET Core 3, users will be required to "
    "install .NET themselves. For more information, see "
    "https://edb.docs.pyansys.com/version/stable/build_breaking_change.html"
)

existing_showwarning = warnings.showwarning


def custom_show_warning(message, category, filename, lineno, file=None, line=None):
    """Custom warning used to remove <stdin>:loc: pattern."""
    print(f"{category.__name__}: {message}")


warnings.showwarning = custom_show_warning

modules = [tup[1] for tup in pkgutil.iter_modules()]
cpython = "IronPython" not in sys.version and ".NETFramework" not in sys.version
is_linux = os.name == "posix"
is_windows = not is_linux
is_clr = False
pyedb_path = Path(pyedb.__file__).parent
sys.path.append(str(pyedb_path / "dlls" / "PDFReport"))


if is_linux:  # pragma: no cover
    from pythonnet import load

    dotnet_root = None
    runtime_config = None
    # Use system .NET core runtime or fall back to dotnetcore2
    if os.environ.get("DOTNET_ROOT") is None:
        try:
            from clr_loader import get_coreclr

            runtime = get_coreclr()
            load(runtime)
            os.environ["DOTNET_ROOT"] = str(runtime.dotnet_root)
            is_clr = True
        # TODO: Fall backing to dotnetcore2 should be removed in a near future.
        except Exception:
            warnings.warn(
                "Unable to set .NET root and locate the runtime configuration file. "
                "Falling back to using dotnetcore2."
            )
            warnings.warn(LINUX_WARNING)

            import dotnetcore2

            dotnet_root = Path(dotnetcore2.__file__).parent / "bin"
            runtime_config = pyedb_path / "misc" / "pyedb.runtimeconfig.json"
    # Use specified .NET root folder
    else:
        dotnet_root = Path(os.environ["DOTNET_ROOT"])
        # Patch the case where DOTNET_ROOT leads to dotnetcore2 for more information
        # see https://github.com/ansys/pyedb/issues/922
        # TODO: Remove once dotnetcore2 is deprecated
        if dotnet_root.parent.name == "dotnetcore2":
            runtime_config = pyedb_path / "misc" / "pyedb.runtimeconfig.json"
        else:
            from clr_loader import find_runtimes

            candidates = [rt for rt in find_runtimes() if rt.name == "Microsoft.NETCore.App"]
            candidates.sort(key=lambda spec: spec.version, reverse=True)
            if not candidates:
                raise RuntimeError(
                    "Configuration file could not be found from DOTNET_ROOT. "
                    "Please ensure that .NET SDK is correctly installed or "
                    "that DOTNET_ROOT is correctly set."
                )
            runtime_config = candidates[0]
    # Use specific .NET core runtime
    if dotnet_root is not None and runtime_config is not None:
        try:
            load("coreclr", runtime_config=str(runtime_config), dotnet_root=str(dotnet_root))
            os.environ["DOTNET_ROOT"] = dotnet_root
            if "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
                warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyedb.")
                warnings.warn("export ANSYSEM_ROOT242=/path/to/AnsysEM/v242/Linux64")
                msg = "export LD_LIBRARY_PATH="
                msg += "$ANSYSEM_ROOT242/common/mono/Linux64/lib64:$LD_LIBRARY_PATH"
                warnings.warn(msg)
            is_clr = True
        except ImportError:
            msg = "pythonnet or dotnetcore not installed. Pyedb will work only in client mode."
            warnings.warn(msg)
else:
    try:
        from pythonnet import load

        load("coreclr")
        is_clr = True
    except:
        warnings.warn("Unable to load DOTNET core runtime")


try:  # work around a number formatting bug in the EDB API for non-English locales
    # described in #1980
    import clr as _clr  # isort:skip
    from System.Globalization import CultureInfo as _CultureInfo

    _CultureInfo.DefaultThreadCurrentCulture = _CultureInfo.InvariantCulture
    from System import Array, Convert, Double, String, Tuple
    from System.Collections.Generic import Dictionary, List

    edb_initialized = True

except ImportError:  # pragma: no cover
    if is_windows:
        warnings.warn(
            "The clr is missing. Install PythonNET or use an IronPython version if you want to use the EDB module."
        )
        edb_initialized = False
    elif sys.version[0] == 3 and sys.version[1] < 7:
        warnings.warn("EDB requires Linux Python 3.8 or later.")
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

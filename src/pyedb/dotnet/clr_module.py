import os
from pathlib import Path
import pkgutil
import shutil
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


def find_dotnet_root() -> Path:
    """Find dotnet root path."""
    dotnet_path = shutil.which("dotnet")
    if not dotnet_path:
        raise FileNotFoundError("The 'dotnet' executable was not found in the PATH.")

    dotnet_path = Path(dotnet_path).resolve()
    dotnet_root = dotnet_path.parent
    return dotnet_root


def find_runtime_config(dotnet_root: Path) -> Path:
    """Find dotnet runtime configuration file path."""
    sdk_path = dotnet_root / "sdk"
    if not sdk_path.is_dir():
        raise EnvironmentError(f"The 'sdk' directory could not be found in: {dotnet_root}")
    sdk_versions = sorted(sdk_path.iterdir(), key=lambda x: x.name, reverse=True)
    if not sdk_versions:
        raise FileNotFoundError("No SDK versions were found.")
    runtime_config = sdk_versions[0] / "dotnet.runtimeconfig.json"
    if not runtime_config.is_file():
        raise FileNotFoundError(f"The configuration file '{runtime_config}' does not exist.")
    return runtime_config


if is_linux:  # pragma: no cover
    from pythonnet import load

    # Use system DOTNET core runtime
    try:
        from clr_loader import get_coreclr

        runtime = get_coreclr()
        load(runtime)
        is_clr = True
    # Define DOTNET root and runtime config file to load DOTNET core runtime
    except Exception:
        if os.environ.get("DOTNET_ROOT") is None:
            try:
                dotnet_root = find_dotnet_root()
                runtime_config = find_runtime_config(dotnet_root)
            except Exception:
                warnings.warn(
                    "Unable to set DOTNET root and locate the runtime configuration file. "
                    "Falling back to using dotnetcore2."
                )
                warnings.warn(LINUX_WARNING)

                import dotnetcore2

                dotnet_root = Path(dotnetcore2.__file__).parent / "bin"
                runtime_config = pyedb_path / "misc" / "pyedb.runtimeconfig.json"
        else:
            dotnet_root = Path(os.environ["DOTNET_ROOT"])
            try:
                runtime_config = find_runtime_config(dotnet_root)
            except Exception as e:
                raise RuntimeError(
                    "Configuration file could not be found from DOTNET_ROOT. "
                    "Please ensure that .NET SDK is correctly installed or "
                    "that DOTNET_ROOT is correctly set."
                )
        try:
            load("coreclr", runtime_config=str(runtime_config), dotnet_root=str(dotnet_root))
            if "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
                warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyedb.")
                warnings.warn("export ANSYSEM_ROOT242=/path/to/AnsysEM/v242/Linux64")
                msg = "export LD_LIBRARY_PATH="
                msg += "$ANSYSEM_ROOT242/common/mono/Linux64/lib64:$LD_LIBRARY_PATH"
                msg += (
                    "If PyEDB is used with AEDT<2023.2 then /path/to/AnsysEM/v2XY/Linux64/Delcross "
                    "should be added to LD_LIBRARY_PATH."
                )
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

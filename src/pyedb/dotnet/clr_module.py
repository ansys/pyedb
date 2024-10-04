import os
import pkgutil
import sys
import warnings

modules = [tup[1] for tup in pkgutil.iter_modules()]
cpython = "IronPython" not in sys.version and ".NETFramework" not in sys.version
is_linux = os.name == "posix"
is_windows = not is_linux
is_clr = False

try:
    import pyedb

    pyedb_path = os.path.dirname(os.path.abspath(pyedb.__file__))
    sys.path.append(os.path.join(pyedb_path, "dlls", "PDFReport"))
except ImportError:
    pyedb_path = None
    warnings.warn("Cannot import pyedb.")

if is_linux and cpython:  # pragma: no cover
    try:
        from pythonnet import load

        if pyedb_path is not None:
            load("coreclr")
            print("DotNet Core correctly loaded.")
            if "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
                warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyedb.")
                warnings.warn("export ANSYSEM_ROOT242=/path/to/AnsysEM/v242/Linux64")
                msg = "export LD_LIBRARY_PATH="
                msg += "$ANSYSEM_ROOT242/common/mono/Linux64/lib64:$LD_LIBRARY_PATH"
                msg += "On AEDT<2023.2, $ANSYSEM_ROOT222/Delcross should also be added to the LD_LIBRARY_PATH."
                warnings.warn(msg)
            is_clr = True
        else:
            print("DotNet Core not correctly loaded.")
    except ImportError:
        msg = "pythonnet or dotnetcore not installed. Pyedb will work only in client mode."
        warnings.warn(msg)
else:
    try:
        from pythonnet import load

        load("coreclr")
        is_clr = True

    except:
        pass


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

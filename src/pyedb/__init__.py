# -*- coding: utf-8 -*-
import functools
import os
import sys
import warnings

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

# By default we use pyedb legacy implementation
if "PYEDB_USE_DOTNET" not in os.environ:
    os.environ["PYEDB_USE_DOTNET"] = "0"

LATEST_DEPRECATED_PYTHON_VERSION = (3, 7)
UBUNTU_22_04_MSG = "The following code is not running on Ubuntu 22.04."


def deprecation_warning():
    """Warning message informing users that some Python versions are deprecated in PyEDB."""
    # Store warnings showwarning
    existing_showwarning = warnings.showwarning

    # Define and use custom showwarning
    def custom_show_warning(message, category, filename, lineno, file=None, line=None):
        """Custom warning used to remove <stdin>:loc: pattern."""
        print(f"{category.__name__}: {message}")

    warnings.showwarning = custom_show_warning

    current_version = sys.version_info[:2]
    if current_version <= LATEST_DEPRECATED_PYTHON_VERSION:
        str_current_version = "{}.{}".format(*sys.version_info[:2])
        warnings.warn(
            "Current python version ({}) is deprecated in PyEDB. We encourage you "
            "to upgrade to the latest version to benefit from the latest features "
            "and security updates.".format(str_current_version),
            PendingDeprecationWarning,
        )

    # Restore warnings showwarning
    warnings.showwarning = existing_showwarning


deprecation_warning()

#

pyedb_path = os.path.dirname(__file__)
__version__ = "0.30.dev0"
version = __version__

#

from pyedb.generic.design_types import Edb, Siwave

#


def get_ubuntu_version():
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VERSION_ID"):
                    version = line.split("=")[1].strip().strip('"')
                    return version
    return None


def check_if_ubuntu_22_04():
    version = get_ubuntu_version()
    if version == "22.04":
        return True
    return False


def ubuntu_22_04_not_allowed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if check_if_ubuntu_22_04():
            raise EnvironmentError(UBUNTU_22_04_MSG)
        return func(*args, **kwargs)

    return wrapper

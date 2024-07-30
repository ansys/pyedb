# -*- coding: utf-8 -*-
import os
import sys
import warnings

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

# By default we use pyedb legacy implementation
if "PYEDB_USE_DOTNET" not in os.environ:
    os.environ["PYEDB_USE_DOTNET"] = "0"

LATEST_DEPRECATED_PYTHON_VERSION = (3, 7)


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
__version__ = "0.23.0"
version = __version__

#

from pyedb.generic.design_types import Edb, Siwave

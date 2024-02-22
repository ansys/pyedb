# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyedb_path = os.path.dirname(__file__)

__version__ = "0.2.0"

version = __version__

# By default we use pyedb legacy implementation
if "PYEDB_USE_DOTNET" not in os.environ:
    os.environ["PYEDB_USE_DOTNET"] = "0"

from pyedb.generic.design_types import Edb

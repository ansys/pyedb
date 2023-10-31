# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyedb_path = os.path.dirname(__file__)

__version__ = "0.0.1"

version = __version__

# By default we use pyedb legacy implementation
if "PYEDB_USE_LEGACY" not in os.environ:
    os.environ["PYEDB_USE_LEGACY"] = "1"

from pyedb.generic.design_types import Edb

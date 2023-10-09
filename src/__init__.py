import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyedb_path = os.path.dirname(__file__)

__version__ = "0.0.1"

version = __version__

from pyedb.generic.design_types import Edb
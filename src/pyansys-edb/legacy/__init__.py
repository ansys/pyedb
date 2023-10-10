# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyaedt_path = os.path.dirname(__file__)

__version__ = "0.8.dev0"

version = __version__

try:
    from pyedb.generic.design_types import Hfss3dLayout
except:
    from pyedb.generic.design_types import Hfss3dLayout


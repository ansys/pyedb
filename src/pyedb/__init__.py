# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyedb_path = os.path.dirname(__file__)

__version__ = "0.0.1"

version = __version__

from pyedb.generic.design_types import Edb


from pyedb.generic.general_methods import _pythonver
from pyedb.generic.general_methods import _retry_ntimes
from pyedb.generic.general_methods import generate_unique_folder_name
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import generate_unique_project_name
from pyedb.generic.general_methods import inside_desktop
from pyedb.generic.general_methods import is_ironpython
from pyedb.generic.general_methods import is_linux
from pyedb.generic.general_methods import is_windows
from pyedb.generic.general_methods import online_help
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.generic.general_methods import settings
from pyedb.misc.misc import current_student_version
from pyedb.misc.misc import current_version
from pyedb.misc.misc import installed_versions

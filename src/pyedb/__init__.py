# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyedb_path = os.path.dirname(__file__)

__version__ = "0.0.1"

version = __version__

from pyedb.generic.design_types import Edb


# import pyedb.legacy.downloads as downloads
# from pyedb.generic import constants
# import pyedb.generic.DataHandlers as data_handler
# import pyedb.generic.general_methods as general_methods
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

# try:
#     from pyedb.generic.design_types import Hfss3dLayout
# except:
#     from pyedb.generic.design_types import Hfss3dLayout
# from pyedb.generic.design_types import Circuit
# from pyedb.generic.design_types import Desktop
# from pyedb.generic.design_types import Emit
# from pyedb.generic.design_types import Hfss
# from pyedb.generic.design_types import Icepak
# from pyedb.generic.design_types import Maxwell2d
# from pyedb.generic.design_types import Maxwell3d
# from pyedb.generic.design_types import MaxwellCircuit
# from pyedb.generic.design_types import Mechanical
# from pyedb.generic.design_types import Q2d
# from pyedb.generic.design_types import Q3d
# from pyedb.generic.design_types import Rmxprt
# from pyedb.generic.design_types import Simplorer
# from pyedb.generic.design_types import Siwave
# from pyedb.generic.design_types import TwinBuilder
# from pyedb.generic.design_types import get_pyedb_app
# from pyedb.generic.design_types import launch_desktop
from pyedb.misc.misc import current_student_version
from pyedb.misc.misc import current_version
from pyedb.misc.misc import installed_versions

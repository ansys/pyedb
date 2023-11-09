# """
# Test Configuration Module
# -------------------------------

# Description
# ===========

# This module contains the configuration and fixture for the pytest-based tests for pyedb.

# The default configuration can be changed by placing a file called local_config.json in the same
# directory as this module. An example of the contents of local_config.json
# {
#   "desktopVersion": "2022.2",
#   "NonGraphical": false,
#   "NewThread": false,
#   "skip_desktop_test": false
# }

# """
import os
import random
import shutil
import string
import tempfile
import pytest

from pyedb.edb_logger import pyedb_logger
from pyedb.generic.filesystem import Scratch
from pyedb.generic.general_methods import generate_unique_name
from pyedb.misc.misc import list_installed_ansysem

logger = pyedb_logger

local_path = os.path.dirname(os.path.realpath(__file__))

# Initialize default desktop configuration
desktop_version = "2024.1"
if "ANSYSEM_ROOT{}".format(desktop_version[2:].replace(".", "")) not in list_installed_ansysem():
    desktop_version = list_installed_ansysem()[0][12:].replace(".", "")
    desktop_version = "20{}.{}".format(desktop_version[:2], desktop_version[-1])


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.sample(characters, length))
    return random_string


def generate_random_ident():
    ident = "-" + generate_random_string(6) + "-" + generate_random_string(6) + "-" + generate_random_string(6)
    return ident


@pytest.fixture(scope="session", autouse=True)
def init_scratch():
    test_folder_name = "unit_test" + generate_random_ident()
    test_folder = os.path.join(tempfile.gettempdir(), test_folder_name)
    try:
        os.makedirs(test_folder, mode=0o777)
    except FileExistsError as e:
        print("Failed to create {}. Reason: {}".format(test_folder, e))

    yield test_folder

    try:
        shutil.rmtree(test_folder, ignore_errors=True)
    except Exception as e:
        print("Failed to delete {}. Reason: {}".format(test_folder, e))


@pytest.fixture(scope="module", autouse=True)
def local_scratch(init_scratch):
    tmp_path = init_scratch
    scratch = Scratch(tmp_path)
    yield scratch
    scratch.remove()

"""
"""

import os
from os.path import dirname
import pytest
from tests.conftest import local_path

from pyedb.generic.general_methods import generate_unique_name
from pyedb.misc.misc import list_installed_ansysem

example_models_path = os.path.join(
    dirname(dirname(dirname(os.path.realpath(__file__)))), "example_models")

# Initialize default desktop configuration
desktop_version = "2023.2"
if "ANSYSEM_ROOT{}".format(desktop_version[2:].replace(".", "")) not in list_installed_ansysem():
    desktop_version = list_installed_ansysem()[0][12:].replace(".", "")
    desktop_version = "20{}.{}".format(desktop_version[:2], desktop_version[-1])

test_subfolder = "TEDB"
test_project_name = "ANSYS-HSD_V1"
bom_example = "bom_example.csv"

@pytest.fixture(scope="module")
def add_grpc_edb(local_scratch):
    from pyedb.grpc.edb import EdbGrpc

    def _method(project_name=None, subfolder=""):
        if project_name:
            example_folder = os.path.join(local_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_folder):
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
                local_scratch.copyfolder(example_folder, target_folder)
            else:
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
        else:
            target_folder = os.path.join(local_scratch.path, generate_unique_name("TestEdb") + ".aedb")
        return EdbGrpc(
            target_folder,
            edbversion=desktop_version,
        )

    return _method


@pytest.fixture(scope="class")
def grpc_edb_app(add_grpc_edb):
    app = add_grpc_edb(test_project_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class", autouse=True)
def target_path(local_scratch):
    example_project = os.path.join(local_path, "example_models", test_subfolder, "example_package.aedb")
    target_path = os.path.join(local_scratch.path, "example_package.aedb")
    local_scratch.copyfolder(example_project, target_path)
    return target_path


@pytest.fixture(scope="class", autouse=True)
def target_path2(local_scratch):
    example_project2 = os.path.join(local_path, "example_models", test_subfolder, "simple.aedb")
    target_path2 = os.path.join(local_scratch.path, "simple_00.aedb")
    local_scratch.copyfolder(example_project2, target_path2)
    return target_path2

@pytest.fixture(scope="class", autouse=True)
def target_path3(local_scratch):
    example_project3 = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
    target_path3 = os.path.join(local_scratch.path, "test_plot.aedb")
    local_scratch.copyfolder(example_project3, target_path3)
    return target_path3


@pytest.fixture(scope="class", autouse=True)
def target_path4(local_scratch):
    example_project4 = os.path.join(local_path, "example_models", test_subfolder, "Package.aedb")
    target_path4 = os.path.join(local_scratch.path, "Package_00.aedb")
    local_scratch.copyfolder(example_project4, target_path4)
    return target_path4

"""
"""
import sys
import os

import pytest

# from pyedb import Edb
# from pyedb.legacy.edb_core.components import resistor_value_parser
# from pyedb.legacy.edb_core.edb_data.edbvalue import EdbValue
# from pyedb.legacy.edb_core.edb_data.simulation_configuration import SimulationConfiguration
# from pyedb.legacy.edb_core.edb_data.sources import Source
# from pyedb.generic.constants import RadiationBoxType
# from pyedb.generic.general_methods import check_numeric_equivalence

# from pyedb.generic.constants import SolverType
# from pyedb.generic.constants import SourceType
# from tests.conftest import config
from tests.conftest import local_path
# from tests.conftest import edb_version

test_subfolder = "TEDB"
test_project_name = "ANSYS-HSD_V1"
bom_example = "bom_example.csv"


@pytest.fixture(scope="class")
def edbapp(add_edb):
    app = add_edb(test_project_name, subfolder=test_subfolder)
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

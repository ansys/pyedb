# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
"""
import json
import os
from pathlib import Path
import random
import shutil
import string
import tempfile

import pytest

from pyedb.generic.design_types import Edb
from pyedb.generic.filesystem import Scratch

local_path = os.path.dirname(os.path.realpath(__file__))
example_models_path = Path(__file__).parent / "example_models"

# Initialize default desktop configuration

use_grpc = False
if "USE_GRPC" in os.environ:
    use_grpc = os.getenv("USE_GRPC")

config = {
    "desktopVersion": "2025.2",
    "use_grpc": use_grpc,
}

# Check for the local config file, override defaults if found
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
    except Exception:  # pragma: no cover
        local_config = {}
    config.update(local_config)

desktop_version = config["desktopVersion"]
GRPC = config["use_grpc"]

test_subfolder = "TEDB"
test_project_name = "ANSYS-HSD_V1"
bom_example = "bom_example.csv"


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


class EdbExamples:
    def __init__(self, local_scratch, grpc=False):
        self.grpc = grpc
        self.local_scratch = local_scratch
        self.example_models_path = example_models_path
        self.test_folder = ""

    def get_local_file_folder(self, name):
        return os.path.join(self.local_scratch.path, name)

    def _create_test_folder(self):
        """Create a local folder under `local_scratch`."""
        self.test_folder = os.path.join(self.local_scratch.path, generate_random_string(6))
        return self.test_folder

    def _copy_file_folder_into_local_folder(self, file_folder_path):
        src = os.path.join(self.example_models_path, file_folder_path)
        local_folder = self._create_test_folder()
        file_folder_name = os.path.join(local_folder, os.path.split(src)[-1])
        dst = self.local_scratch.copyfolder(src, file_folder_name)
        return dst

    def _get_test_board(self, edbapp, additional_files_folders, version, source_file_path):
        """Copy si_verse board file into local folder. A new temporary folder will be created."""
        aedb = self._copy_file_folder_into_local_folder(source_file_path)
        if additional_files_folders:
            files = (
                additional_files_folders if isinstance(additional_files_folders, list) else [additional_files_folders]
            )
            for f in files:
                src = os.path.join(self.example_models_path, f)
                file_folder_name = os.path.join(self.test_folder, os.path.split(src)[-1])
                if os.path.isfile(src):
                    self.local_scratch.copyfile(src, file_folder_name)
                else:
                    self.local_scratch.copyfolder(src, file_folder_name)
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(aedb, edbversion=version, grpc=self.grpc)
        else:
            return aedb

    def get_si_verse(self, edbapp=True, additional_files_folders="", version=None):
        return self._get_test_board(
            edbapp, additional_files_folders, version, source_file_path="si_verse/ANSYS-HSD_V1.aedb"
        )

    def get_si_verse_sfp(self, edbapp=True, additional_files_folders="", version=None):
        return self._get_test_board(
            edbapp, additional_files_folders, version, source_file_path="si_verse/ANSYS_SVP_V1_1_SFP.aedb"
        )

    def get_package(self, edbapp=True, additional_files_folders="", version=None):
        """ "Copy package board file into local folder. A new temporary folder will be created."""
        return self.get_si_verse(
            edbapp, additional_files_folders, version, source_file_path="TEDB/example_package.aedb"
        )

    def create_empty_edb(self):
        local_folder = self._create_test_folder()
        aedb = os.path.join(local_folder, "new_layout.aedb")
        return Edb(aedb, edbversion=desktop_version, grpc=self.grpc)

    def get_multizone_pcb(self):
        aedb = self._copy_file_folder_into_local_folder("multi_zone_project.aedb")
        return Edb(aedb, edbversion=desktop_version, grpc=self.grpc)

    def get_unit_cell(self):
        aedb = self._copy_file_folder_into_local_folder("TEDB/unitcell.aedb")
        return Edb(aedb, edbversion=desktop_version, grpc=self.grpc)

    def get_no_ref_pins_component(self):
        aedb = self._copy_file_folder_into_local_folder("TEDB/component_no_ref_pins.aedb")
        return Edb(aedb, edbversion=desktop_version, grpc=self.grpc)

    def load_edb(self, edb_path, copy_to_temp=True, **kwargs):
        if copy_to_temp:
            aedb = self._copy_file_folder_into_local_folder(edb_path)
        else:
            aedb = edb_path
        return Edb(edbpath=aedb, edbversion=desktop_version, grpc=self.grpc, **kwargs)


@pytest.fixture(scope="class", autouse=True)
def target_path(local_scratch):
    example_project = os.path.join(example_models_path, test_subfolder, "example_package.aedb")
    target_path = os.path.join(local_scratch.path, "example_package.aedb")
    local_scratch.copyfolder(example_project, target_path)
    return target_path


@pytest.fixture(scope="class", autouse=True)
def target_path2(local_scratch):
    example_project2 = os.path.join(example_models_path, test_subfolder, "simple.aedb")
    target_path2 = os.path.join(local_scratch.path, "simple_00.aedb")
    local_scratch.copyfolder(example_project2, target_path2)
    return target_path2


@pytest.fixture(scope="class", autouse=True)
def target_path3(local_scratch):
    example_project3 = os.path.join(example_models_path, test_subfolder, "ANSYS-HSD_V1_cut.aedb")
    target_path3 = os.path.join(local_scratch.path, "test_plot.aedb")
    local_scratch.copyfolder(example_project3, target_path3)
    return target_path3


@pytest.fixture(scope="class", autouse=True)
def target_path4(local_scratch):
    example_project4 = os.path.join(example_models_path, test_subfolder, "Package.aedb")
    target_path4 = os.path.join(local_scratch.path, "Package_00.aedb")
    local_scratch.copyfolder(example_project4, target_path4)
    return target_path4


@pytest.fixture(scope="class", autouse=True)
def edb_examples(local_scratch):
    return EdbExamples(local_scratch, GRPC)

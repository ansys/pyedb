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

import os
from os.path import dirname

import pytest

from pyedb.dotnet.edb import Edb
from pyedb.generic.general_methods import generate_unique_name
from pyedb.misc.misc import list_installed_ansysem
from tests.conftest import generate_random_string

example_models_path = os.path.join(dirname(dirname(dirname(os.path.realpath(__file__)))), "example_models")

# Initialize default desktop configuration
desktop_version = "2025.1"
if "ANSYSEM_ROOT{}".format(desktop_version[2:].replace(".", "")) not in list_installed_ansysem():
    desktop_version = list_installed_ansysem()[0][12:].replace(".", "")
    desktop_version = "20{}.{}".format(desktop_version[:2], desktop_version[-1])

test_subfolder = "TEDB"
test_project_name = "ANSYS-HSD_V1"
bom_example = "bom_example.csv"


class EdbExamples:
    def __init__(self, local_scratch):
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

    def get_si_verse(
        self, edbapp=True, additional_files_folders="", version=None, source_file_path="TEDB/ANSYS-HSD_V1.aedb"
    ):
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
            return Edb(aedb, edbversion=version)
        else:
            return aedb

    def get_package(self, edbapp=True, additional_files_folders="", version=None):
        """ "Copy package board file into local folder. A new temporary folder will be created."""
        return self.get_si_verse(
            edbapp, additional_files_folders, version, source_file_path="TEDB/example_package.aedb"
        )

    def create_empty_edb(self):
        local_folder = self._create_test_folder()
        aedb = os.path.join(local_folder, "new_layout.aedb")
        return Edb(aedb, edbversion=desktop_version)

    def get_multizone_pcb(self):
        aedb = self._copy_file_folder_into_local_folder("multi_zone_project.aedb")
        return Edb(aedb, edbversion=desktop_version)

    def get_no_ref_pins_component(self):
        aedb = self._copy_file_folder_into_local_folder("TEDB/component_no_ref_pins.aedb")
        return Edb(aedb, edbversion=desktop_version)

    def load_edb(self, edb_path):
        aedb = self._copy_file_folder_into_local_folder(edb_path)
        return Edb(aedb, edbversion=desktop_version)


@pytest.fixture(scope="module")
def add_legacy_edb(local_scratch):
    def _method(project_name=None, subfolder=""):
        if project_name:
            example_folder = os.path.join(example_models_path, subfolder, project_name + ".aedb")
            if os.path.exists(example_folder):
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
                local_scratch.copyfolder(example_folder, target_folder)
            else:
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
        else:
            target_folder = os.path.join(local_scratch.path, generate_unique_name("TestEdb") + ".aedb")
        return Edb(
            target_folder,
            edbversion=desktop_version,
        )

    return _method


@pytest.fixture(scope="class")
def legacy_edb_app(add_legacy_edb):
    app = add_legacy_edb(test_project_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def legacy_edb_app_without_material(add_legacy_edb):
    app = add_legacy_edb()
    return app


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
    return EdbExamples(local_scratch)

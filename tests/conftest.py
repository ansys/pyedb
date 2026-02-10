# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

""" """

import json
import os
from pathlib import Path
import secrets
import shutil
import string
import tempfile

import pytest

from pyedb.generic.design_types import Edb
from pyedb.generic.filesystem import Scratch
from pyedb.generic.settings import settings

settings.enable_global_log_file = False

local_path = os.path.dirname(os.path.realpath(__file__))
example_models_path = Path(__file__).parent / "example_models"

# Initialize default desktop configuration

use_grpc = os.getenv("USE_GRPC") in {"1", True}

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
    generator = secrets.SystemRandom()
    random_string = "".join(secrets.SystemRandom.sample(generator, characters, length))
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
    def __init__(self, local_scratch: Scratch, grpc=False):
        self.grpc = grpc
        self.local_scratch = local_scratch
        self.example_models_path = example_models_path
        self.test_folder = ""

    def copy_test_files_into_local_folder(self, file_folder_path):
        """Copy files or folders from example_models into local test folder."""
        source_folder = Path(__file__).parent / "example_models"
        files = file_folder_path if isinstance(file_folder_path, list) else [file_folder_path]
        target_files = []
        for f in files:
            src_files = source_folder / f
            target_file_folder_name = os.path.join(self.test_folder, src_files.name)

            if not src_files.exists():
                raise FileNotFoundError(f"Source file or folder {src_files} does not exist.")
            elif os.path.isfile(src_files):
                self.local_scratch.copyfile(src_files, target_file_folder_name)
            else:
                self.local_scratch.copyfolder(src_files, target_file_folder_name)
            target_files.append(target_file_folder_name)
        return target_files

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

    def get_si_verse(self, edbapp=True, version=None):
        target_file = self.copy_test_files_into_local_folder("si_verse/ANSYS-HSD_V1.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_wirebond_jedec4_project(self, edbapp=True, version=None):
        target_file = self.copy_test_files_into_local_folder("wirebond_projects/ANSYS-test_wb_jedec4.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_si_verse_sfp(self, edbapp=True, additional_files_folders="", version=None):
        target_file = self.copy_test_files_into_local_folder("si_verse/ANSYS-ANSYS_SVP_V1_1_SFP.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_package(self, edbapp=True, additional_files_folders="", version=None):
        """ "Copy package board file into local folder. A new temporary folder will be created."""
        target_file = self.copy_test_files_into_local_folder("TEDB/ANSYS-example_package.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def create_empty_edb(self):
        aedb = os.path.join(self.test_folder, "new_layout.aedb")
        return Edb(aedb, version=desktop_version, grpc=self.grpc)

    def get_multizone_pcb(self, version=None):
        target_file = self.copy_test_files_into_local_folder("multi_zone_project.aedb")[0]
        version = desktop_version if version is None else version
        return Edb(target_file, version=version, grpc=self.grpc)

    def get_unit_cell(self,version=None):
        target_file = self.copy_test_files_into_local_folder("TEDB/unitcell.aedb")[0]
        version = desktop_version if version is None else version
        return Edb(target_file, version=version, grpc=self.grpc)

    def get_no_ref_pins_component(self, version=None):
        target_file = self.copy_test_files_into_local_folder("TEDB/component_no_ref_pins.aedb")[0]
        version = desktop_version if version is None else version
        return Edb(target_file, version=version, grpc=self.grpc)

    def get_si_board(self, edbapp=True, additional_files_folders="", version=None):
        target_file = self.copy_test_files_into_local_folder("si_board/si_board.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def load_edb(self, edb_path, **kwargs):
        return Edb(edbpath=edb_path, edbversion=desktop_version, grpc=self.grpc, **kwargs)

    def load_dxf_edb(self):
        aedb = self.copy_test_files_into_local_folder("dxf_swap/starting_edb/starting_edb.aedb")[0]
        return Edb(edbpath=aedb, version=desktop_version, grpc=True)

    def get_log_file_example(self):
        return os.path.join(self.example_models_path, "test.log")

    def get_siwave_log_file_example(self):
        return os.path.join(self.example_models_path, "siwave.log")


@pytest.fixture(scope="class", autouse=True)
def edb_examples(local_scratch):
    return EdbExamples(local_scratch, GRPC)


@pytest.fixture(scope="session", autouse=True)
def close_rpc_session(init_scratch):
    """Provide a module-scoped scratch directory."""

    yield
    if GRPC:
        scratch = Scratch(init_scratch)
        sub_folder = Path(scratch.path) / generate_random_string(6) / ".aedb"
        dummy_edb = Edb(str(sub_folder), version=desktop_version, grpc=True)
        dummy_edb.close(terminate_rpc_session=True)

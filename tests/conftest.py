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

import json
import os
from pathlib import Path
import secrets
import shutil
import string
import tempfile
import time
from types import TracebackType

import pytest

from pyedb.generic.design_types import Edb
from pyedb.generic.settings import settings

settings.enable_global_log_file = False

local_path = os.path.dirname(os.path.realpath(__file__))
example_models_path = Path(__file__).parent / "example_models"

# Initialize default desktop configuration

use_grpc = os.getenv("USE_GRPC") in {"1", True}

config = {
    "desktopVersion": "2026.1",
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
    def __init__(self, local_scratch: "Scratch", grpc=False):
        self.grpc = grpc
        self.local_scratch = local_scratch
        self.example_models_path = example_models_path
        self.test_folder = ""

    def copy_test_files_into_local_folder(self, file_folder_path):
        """Copy files or folders from example_models into local test folder."""
        time.sleep(0.5)  # To avoid issues with rapid creation/deletion of folders in some environments.
        source_folder = Path(__file__).parent / "example_models"
        files = file_folder_path if isinstance(file_folder_path, list) else [file_folder_path]
        target_files = []
        random_folder_name = "test_" + generate_random_string(6)
        os.makedirs(os.path.join(self.test_folder, random_folder_name), exist_ok=True)
        for f in files:
            src_files = source_folder / f
            target_file_folder_name = os.path.join(self.test_folder, random_folder_name, src_files.name)

            if not src_files.exists():
                raise FileNotFoundError(f"Source file or folder {src_files} does not exist.")
            elif os.path.isfile(src_files):
                self.local_scratch.copyfile(src_files, target_file_folder_name)
            else:
                self.local_scratch.copyfolder(src_files, target_file_folder_name)
            target_files.append(target_file_folder_name)
        return target_files

    def get_si_verse(self, edbapp=True, version=None):
        target_file = self.copy_test_files_into_local_folder("si_verse/ANSYS-HSD_V1.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(edbpath=target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_wirebond_jedec4_project(self, edbapp=True, version=None):
        target_file = self.copy_test_files_into_local_folder("wirebond_projects/test_wb_jedec4.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(edbpath=target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_si_verse_sfp(self, edbapp=True, additional_files_folders="", version=None):
        target_file = self.copy_test_files_into_local_folder("si_verse/ANSYS_SVP_V1_1_SFP.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def get_package(self, edbapp=True, additional_files_folders="", version=None):
        """ "Copy package board file into local folder. A new temporary folder will be created."""
        target_file = self.copy_test_files_into_local_folder("TEDB/example_package.aedb")[0]
        if edbapp:
            version = desktop_version if version is None else version
            return Edb(target_file, version=version, grpc=self.grpc)
        else:
            return target_file

    def create_empty_edb(self):
        aedb = os.path.join(self.test_folder, f"new_layout_{generate_random_string(6)}.aedb")
        edbapp = Edb(aedb, version=desktop_version, grpc=self.grpc)
        edbapp.save_edb()
        return edbapp

    def get_multizone_pcb(self, version=None):
        target_file = self.copy_test_files_into_local_folder("multi_zone_project.aedb")[0]
        version = desktop_version if version is None else version
        return Edb(target_file, version=version, grpc=self.grpc)

    def get_unit_cell(self, version=None):
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
        return Edb(edbpath=aedb, version=desktop_version, grpc=self.grpc)

    def get_log_file_example(self):
        return os.path.join(self.example_models_path, "test.log")

    def get_siwave_log_file_example(self):
        return os.path.join(self.example_models_path, "siwave.log")


@pytest.fixture(scope="class", autouse=True)
def get_edb_examples(local_scratch):
    return EdbExamples(local_scratch, GRPC)


class Scratch:
    """Class for managing a scratch directory."""

    def __init__(self, local_path, permission=0o777, volatile=False):
        self._volatile = volatile
        self._cleaned = True
        char_set = string.ascii_uppercase + string.digits
        generator = secrets.SystemRandom()
        self._scratch_path = os.path.normpath(
            os.path.join(local_path, "scratch" + "".join(secrets.SystemRandom.sample(generator, char_set, 6)))
        )
        if os.path.exists(self._scratch_path):
            try:
                self.remove()
            except:
                self._cleaned = False
        if self._cleaned:
            try:
                os.mkdir(self.path)
                os.chmod(self.path, permission)
            except FileNotFoundError as fnf_error:  # Raise error if folder doesn't exist.
                print(fnf_error)

    def __enter__(self) -> "Scratch":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type or self._volatile:
            self.remove()

    @property
    def path(self) -> str:
        """Get the path of the scratch directory."""
        return self._scratch_path

    @property
    def is_empty(self) -> bool:
        """Check if the scratch directory is empty."""
        return self._cleaned

    def remove(self) -> None:
        """Remove the scratch directory and its contents."""
        try:
            shutil.rmtree(self._scratch_path, ignore_errors=True)
            self._cleaned = True
        except Exception:
            settings.logger.error(f"An error occurred while removing {self._scratch_path}")

    def copyfile(self, src_file: str, dst_filename: str | None = None) -> str:
        """Copy a file to the scratch directory.

        Parameters
        ----------
        src_file : str
            Source file with fullpath.
        dst_filename : str, optional
            Destination filename with the extension. The default is ``None``,
            in which case the destination file is given the same name as the
            source file.

        Returns
        -------
        dst_file : str
            Full path and file name of the copied file.
        """
        if dst_filename:
            dst_file = os.path.join(self.path, dst_filename)
        else:
            dst_file = os.path.join(self.path, os.path.basename(src_file))
        if os.path.exists(dst_file):
            try:
                os.unlink(dst_file)
            except OSError:  # pragma: no cover
                pass
        try:
            shutil.copy2(src_file, dst_file)
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        return dst_file

    def copyfolder(self, src_folder: str, destfolder: str | None = None) -> str:
        """Copy a folder to the scratch directory.

        Parameters
        ----------
        src_folder : str
            Source folder with fullpath.
        destfolder : str, optional
            Destination folder. The default is ``None``, in which case the destination folder
            is given the same name as the source folder.

        Returns
        -------
        destfolder : str
            Full path of the copied folder.
        """
        if not destfolder:
            destfolder = os.path.join(self.path, os.path.split(src_folder)[-1])
        shutil.copytree(src_folder, destfolder, dirs_exist_ok=True)
        return destfolder

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

import os
from pathlib import Path
import shutil
import tempfile
from unittest import mock
import zipfile

import pytest

from pyedb.misc.downloads import (
    download_aedb,
    download_edb_merge_utility,
    download_file,
    download_touchstone,
    download_via_wizard,
)


def test_download_aedb():
    """Test that download_aedb emits a deprecation warning."""
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        download_aedb()

        assert len(w) == 1
        assert "this design has been removed, consider using another one." in str(w[0].message).lower()


def test_download_edb_merge_utility(tmp_path):
    """Test downloading the EDB merge utility."""
    path = download_edb_merge_utility(destination=tmp_path)

    assert Path(path).exists()
    assert path == str(Path(tmp_path) / "wpf_edb_merge/merge_wizard.py")


def test_download_via_wizard(tmp_path):
    """Test downloading via wizard."""
    path = download_via_wizard(destination=tmp_path)

    assert Path(path).exists()
    assert path == str(Path(tmp_path) / "viawizard_vacuum_FR4.aedt")


def test_download_touchstone(tmp_path):
    """Test downloading a touchstone file."""
    path = download_touchstone(destination=tmp_path)

    assert Path(path).exists()
    assert path == str(Path(tmp_path) / "SSN_ssn.s6p")


def test_download_file(tmp_path):
    """Test downloading a file."""
    directory = "pyaedt/edb/ansys_interposer"
    file_name = "dummy_interposer_hbm.map"
    path = download_file(directory, file_name, destination=tmp_path)

    assert Path(path).exists()
    assert path == str(Path(tmp_path) / directory / file_name)


def test_download_file_on_folder(tmp_path):
    """Test downloading a folder."""
    directory = "pyaedt/edb/ansys_interposer"
    path = download_file(directory, destination=tmp_path)

    assert Path(path).exists()
    assert path == str(Path(tmp_path) / directory)

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
from types import SimpleNamespace

import pytest

from pyedb.generic.settings import settings
from pyedb.grpc.edb_init import EdbInit
from tests.conftest import config


def _make_edb_init(edbpath, new_directory):
    """Build a minimal EdbInit instance with a mocked _db."""
    edb = EdbInit.__new__(EdbInit)
    edb.version = config["desktopVersion"]
    edb.logger = settings.logger
    edb.edbpath = edbpath
    edb.log_name = None

    saved_paths = []

    def fake_save_as(path, version):
        saved_paths.append((path, version))

    edb._db = SimpleNamespace(
        save_as=fake_save_as,
        directory=new_directory,
    )
    edb._saved_paths = saved_paths
    return edb


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_save_as_updates_edbpath(tmp_path):
    """save_as() must update self.edbpath to the new location."""
    original = str(tmp_path / "original.aedb")
    copy_dir = tmp_path / "copy.aedb"
    copy_dir.mkdir()
    copy_path = str(copy_dir)

    edb = _make_edb_init(original, copy_path)

    # Patch _wait_for_file_release so it does not block
    edb._wait_for_file_release = lambda file_to_release=None, **kw: True

    result = edb.save_as(copy_path)

    assert result is True
    assert edb.edbpath == copy_path, (
        f"edbpath was not updated after save_as: expected {copy_path!r}, got {edb.edbpath!r}"
    )


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_save_as_updates_edbpath_with_pathlib(tmp_path):
    """save_as() must accept a pathlib.Path and still update self.edbpath."""
    from pathlib import Path

    original = str(tmp_path / "original.aedb")
    copy_dir = tmp_path / "copy_pathlib.aedb"
    copy_dir.mkdir()

    edb = _make_edb_init(original, str(copy_dir))
    edb._wait_for_file_release = lambda file_to_release=None, **kw: True

    result = edb.save_as(copy_dir)

    assert result is True
    assert edb.edbpath == str(copy_dir)


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_save_as_passes_correct_path_to_db(tmp_path):
    """save_as() must forward the resolved path and version to _db.save_as."""
    original = str(tmp_path / "original.aedb")
    copy_dir = tmp_path / "forwarded.aedb"
    copy_dir.mkdir()
    copy_path = str(copy_dir)

    edb = _make_edb_init(original, copy_path)
    edb._wait_for_file_release = lambda file_to_release=None, **kw: True

    edb.save_as(copy_path, version=config["desktopVersion"])

    assert edb._saved_paths == [(copy_path, config["desktopVersion"])]


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_save_as_updates_log_name(tmp_path):
    """save_as() must update self.log_name to match the new path."""
    original = str(tmp_path / "original.aedb")
    copy_dir = tmp_path / "renamed.aedb"
    copy_dir.mkdir()
    copy_path = str(copy_dir)

    edb = _make_edb_init(original, copy_path)
    edb.log_name = os.path.join(str(tmp_path), "pyedb_original.log")
    edb._wait_for_file_release = lambda file_to_release=None, **kw: True

    edb.save_as(copy_path)

    expected_log = os.path.join(str(tmp_path), "pyedb_renamed.log")
    assert edb.log_name == expected_log, f"log_name was not updated: expected {expected_log!r}, got {edb.log_name!r}"


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_save_as_updates_local_file_loggers(tmp_path, monkeypatch):
    """save_as() must rotate local file logger names to match the new AEDB path."""
    original = str(tmp_path / "original.aedb")
    copy_dir = tmp_path / "renamed.aedb"
    copy_dir.mkdir()
    copy_path = str(copy_dir)

    edb = _make_edb_init(original, copy_path)
    edb.log_name = os.path.join(str(tmp_path), "pyedb_original.log")
    edb._wait_for_file_release = lambda file_to_release=None, **kw: True

    added = []
    removed = []
    edb.logger = SimpleNamespace(
        add_file_logger=lambda log_name, logger_name: added.append((log_name, logger_name)),
        remove_file_logger=lambda logger_name: removed.append(logger_name),
    )
    monkeypatch.setattr(settings, "enable_local_log_file", True)

    edb.save_as(copy_path)

    expected_log = os.path.join(str(tmp_path), "pyedb_renamed.log")
    assert edb.log_name == expected_log
    assert added == [(expected_log, "Edb")]
    assert removed == ["pyedb_original"]

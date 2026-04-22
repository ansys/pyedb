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

import sys
from types import ModuleType
from tests.conftest import config
import pytest

from pyedb.generic import design_types
from pyedb.generic.settings import settings


@pytest.fixture
def restore_settings_state():
    original_state = {
        "specified_version": settings.specified_version,
        "is_student_version": settings.is_student_version,
        "is_grpc": settings.is_grpc,
        "is_in_memory": settings.is_in_memory,
        "LATEST_VERSION": settings.LATEST_VERSION,
        "LATEST_STUDENT_VERSION": settings.LATEST_STUDENT_VERSION,
        "INSTALLED_VERSIONS": settings.INSTALLED_VERSIONS,
        "INSTALLED_STUDENT_VERSIONS": settings.INSTALLED_STUDENT_VERSIONS,
        "_edb_dll_path": settings._edb_dll_path,
    }

    settings.LATEST_VERSION = "2026.1"
    settings.LATEST_STUDENT_VERSION = "2026.1"
    settings.INSTALLED_VERSIONS = {"2025.2": "C:/fake/252", "2026.1": "C:/fake/261"}
    settings.INSTALLED_STUDENT_VERSIONS = {"2026.1": "C:/fake/student/261"}
    settings.specified_version = None
    settings.is_student_version = False
    settings.is_grpc = False
    settings.is_in_memory = False
    settings._edb_dll_path = None

    yield

    settings.specified_version = original_state["specified_version"]
    settings.is_student_version = original_state["is_student_version"]
    settings.is_grpc = original_state["is_grpc"]
    settings.is_in_memory = original_state["is_in_memory"]
    settings.LATEST_VERSION = original_state["LATEST_VERSION"]
    settings.LATEST_STUDENT_VERSION = original_state["LATEST_STUDENT_VERSION"]
    settings.INSTALLED_VERSIONS = original_state["INSTALLED_VERSIONS"]
    settings.INSTALLED_STUDENT_VERSIONS = original_state["INSTALLED_STUDENT_VERSIONS"]
    settings._edb_dll_path = original_state["_edb_dll_path"]


@pytest.fixture
def fake_backends(monkeypatch):
    grpc_module = ModuleType("pyedb.grpc.edb")
    dotnet_module = ModuleType("pyedb.dotnet.edb")

    def grpc_edb(**kwargs):
        return "grpc", kwargs

    def dotnet_edb(**kwargs):
        return "dotnet", kwargs

    grpc_module.Edb = grpc_edb
    dotnet_module.Edb = dotnet_edb

    monkeypatch.setitem(sys.modules, "pyedb.grpc.edb", grpc_module)
    monkeypatch.setitem(sys.modules, "pyedb.dotnet.edb", dotnet_module)


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_defaults_to_grpc_for_2026_1_and_later(restore_settings_state, fake_backends):
    with pytest.warns(UserWarning):
        backend, kwargs = design_types.Edb(version="2026.1")

    assert backend == "grpc"
    assert kwargs["version"] == "2026.1"
    assert settings.specified_version == "2026.1"
    assert settings.is_grpc is True


def test_edb_defaults_to_dotnet_before_2026_1(restore_settings_state, fake_backends):
    backend, kwargs = design_types.Edb(version="2025.2")

    assert backend == "dotnet"
    assert "version" not in kwargs
    assert settings.specified_version == "2025.2"
    assert settings.is_grpc is False
    assert settings.is_in_memory is False


def test_edb_uses_resolved_default_version_for_backend_selection(restore_settings_state, fake_backends):
    settings.specified_version = None
    settings.LATEST_VERSION = "2026.1"

    with pytest.warns(UserWarning):
        backend, kwargs = design_types.Edb()

    assert backend == "grpc"
    assert kwargs["version"] is None
    assert settings.specified_version == "2026.1"
    assert settings.is_grpc is True


def test_edb_respects_explicit_grpc_override(restore_settings_state, fake_backends):
    backend, kwargs = design_types.Edb(version="2026.1", grpc=False, in_memory=True)

    assert backend == "dotnet"
    assert "version" not in kwargs
    assert settings.specified_version == "2026.1"
    assert settings.is_grpc is False
    assert settings.is_in_memory is False


def test_edb_prefers_dotnet_when_dll_path_is_forced(restore_settings_state, fake_backends):
    settings._edb_dll_path = "C:/fake/AnsysEM/v261/Win64"

    backend, kwargs = design_types.Edb(version="2026.1")

    assert backend == "dotnet"
    assert "version" not in kwargs
    assert settings.specified_version == "2026.1"
    assert settings.is_grpc is False
    assert settings.is_in_memory is False

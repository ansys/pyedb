# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import patch

from pyedb.generic.settings import Settings

os_environ = {
    "ANSYSEM_ROOT251": "/fake/path251",
    "ANSYSEM_ROOT252": "/fake/path252",
    "ANSYSEMSV_ROOT251": "/fake/pathSV251",
    "ANSYSEMSV_ROOT252": "/fake/pathSV252",
    "ANSYSEM_PY_CLIENT_ROOT252": "/fake/path_py_client",
}


@patch("os.environ", os_environ)
def test_general():
    settings = Settings()
    settings.specified_version = "2025.1"
    assert settings.INSTALLED_VERSIONS == {
        "2025.2": "/fake/path252",
        "2025.1": "/fake/path251",
    }
    assert settings.INSTALLED_STUDENT_VERSIONS == {
        "2025.2": "/fake/pathSV252",
        "2025.1": "/fake/pathSV251",
    }
    assert settings.INSTALLED_CLIENT_VERSIONS == {"2025.2": "/fake/path_py_client"}
    assert settings.LATEST_VERSION == "2025.2"
    assert settings.LATEST_STUDENT_VERSION == "2025.2"
    assert settings.aedt_installation_path == "/fake/path251"


@patch("os.path.exists")
def test_specify_aedt_path(mock_exists):
    settings = Settings()

    mock_exists.return_value = True
    settings.edb_dll_path = "/fake/AnsysEM/v241/Win64"
    assert settings.specified_version == "2024.1"

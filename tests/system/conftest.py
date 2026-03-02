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

"""Test configuration for system tests."""

from pathlib import Path

import pytest

from pyedb.generic.design_types import Edb
from pyedb.generic.filesystem import Scratch
from tests.conftest import GRPC, desktop_version, generate_random_string


@pytest.fixture(scope="session", autouse=True)
def close_rpc_session(init_scratch):
    """Provide a module-scoped scratch directory."""
    yield
    if GRPC:
        scratch = Scratch(init_scratch)
        sub_folder = Path(scratch.path) / generate_random_string(6) / ".aedb"
        dummy_edb = Edb(str(sub_folder), version=desktop_version, grpc=True)
        dummy_edb.close(terminate_rpc_session=True)

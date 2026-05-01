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

from pathlib import Path

from ansys.edb.core.session import session

from pyedb import Edb
from pyedb.generic.settings import settings
from tests.conftest import desktop_version


def test_no_close_existing_session(tmp_path: Path):
    """Test that if a session is already running, it is not ended by Edb.close."""
    # Create a session
    settings.specified_version = desktop_version
    edb_path = tmp_path / "test.edb"
    with session(settings.aedt_installation_path):
        db = Edb(edb_path.as_posix(), version=desktop_version)
        try:
            pass
        finally:
            db.close()
    # session.__exit__ should not fail with "AttributeError: 'NoneType' object has no attribute 'disconnect'"

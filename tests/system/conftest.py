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

import platform
import time

import pytest

from pyedb.grpc.rpc_session import RpcSession
from tests.conftest import GRPC

# Grace period (seconds) after RpcSession.close() before the next test class
# starts a new server.  On Linux the EDB server binary (a Windows-native process
# running under a compatibility layer in CI) takes longer to fully release its
# resources than on Windows, so we apply a longer delay there.
_GRPC_TEARDOWN_GRACE_SECONDS = 2.0 if platform.system() == "Linux" else 1.0


@pytest.fixture(scope="class", autouse=True)
def close_rpc_session(init_scratch):
    """Ensure the RPC server is shut down after each test class.

    The fixture:
    1. Yields control to the test class (setup phase is a no-op).
    2. After all tests in the class have finished, resets the ref-counter
       defensively (in case a crashed test left it non-zero), then closes the
       active RPC session.
    3. Resets ``RpcSession.port`` to ``0`` so that the *next* call to
       ``RpcSession.start()`` will use dynamic port allocation via
       ``socket.bind(('', 0))``, completely avoiding hard-coded port conflicts.
    4. Sleeps for a platform-appropriate grace period so that the OS socket
       TIME_WAIT interval has time to clear before the following test class
       starts a new server.
    """
    yield
    if GRPC:
        # Defensive reset: if tests crashed and left the ref-count dirty,
        # RpcSession.close() would be skipped by the default teardown path.
        # Force it to zero so the explicit close() below always runs.
        RpcSession._open_db_count = 0
        RpcSession.close()
        # Ensure the next session always gets a fresh, OS-assigned port.
        RpcSession.port = 0
        # Platform-aware grace period for OS to release the socket.
        time.sleep(_GRPC_TEARDOWN_GRACE_SECONDS)

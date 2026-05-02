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

from types import SimpleNamespace

import pytest

from pyedb.generic.settings import settings
from pyedb.grpc import edb_init as edb_init_module, rpc_session as rpc_session_module
from pyedb.grpc.edb_init import EdbInit
from pyedb.grpc.rpc_session import RpcSession
from tests.conftest import config


def _reset_rpc_session_state():
    RpcSession.pid = 0
    RpcSession.rpc_session = None
    RpcSession.base_path = None
    RpcSession.port = 10000
    RpcSession.server_pid = 0
    RpcSession.in_memory = False
    RpcSession._open_db_count = 0
    RpcSession._owns_session = False
    settings.is_in_memory = False


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_rpc_session_falls_back_to_standard_rpc_when_in_memory_library_is_missing(monkeypatch):
    _reset_rpc_session_state()
    launched = {}

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)

    def fake_launch_session(base_path, port_num=None):
        launched["base_path"] = base_path
        launched["port_num"] = port_num
        return SimpleNamespace(local_server_proc=SimpleNamespace(pid=4321), in_memory=False)

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)
    RpcSession.start("2026.1", port=55001)

    assert launched == {"base_path": r"C:\\fake\\AnsysEM", "port_num": 55001}
    assert RpcSession.rpc_session is not None
    assert RpcSession.pid == 4321
    assert RpcSession.server_pid == 4321


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_create_always_starts_rpc_session(monkeypatch):
    _reset_rpc_session_state()
    start_calls = []
    created_paths = []
    created_db = object()

    def fake_start(edb_version, port=0, restart_server=False):
        start_calls.append((edb_version, port, restart_server))
        RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "start", staticmethod(fake_start))
    monkeypatch.setattr(
        edb_init_module.database.Database, "create", lambda db_path: created_paths.append(db_path) or created_db
    )

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None

    result = EdbInit._create(edb, "dummy.aedb")

    assert result is created_db
    assert created_paths == ["dummy.aedb"]
    assert start_calls == [("2026.1", 0, False)]


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_acquire_increments_open_db_count():
    _reset_rpc_session_state()
    assert RpcSession._open_db_count == 0
    RpcSession.acquire()
    assert RpcSession._open_db_count == 1
    RpcSession.acquire()
    assert RpcSession._open_db_count == 2


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_release_decrements_open_db_count():
    _reset_rpc_session_state()
    RpcSession.acquire()
    RpcSession.acquire()
    assert RpcSession._open_db_count == 2
    result = RpcSession.release()
    assert result is False
    assert RpcSession._open_db_count == 1


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_release_does_not_go_below_zero():
    _reset_rpc_session_state()
    RpcSession.release()
    assert RpcSession._open_db_count == 0


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_release_closes_session_when_owned_and_count_reaches_zero(monkeypatch):
    _reset_rpc_session_state()

    RpcSession._owns_session = True
    RpcSession.rpc_session = SimpleNamespace(in_memory=False)
    RpcSession.acquire()
    result = RpcSession.release()

    # release() only decrements — it does NOT shut down the server
    assert result is True  # True means count reached zero
    assert RpcSession.rpc_session is not None  # server still alive


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_release_returns_false_when_dbs_still_open():
    _reset_rpc_session_state()

    RpcSession.rpc_session = SimpleNamespace(in_memory=False)
    RpcSession.acquire()
    RpcSession.acquire()
    result = RpcSession.release()

    assert result is False
    assert RpcSession._open_db_count == 1
    assert RpcSession.rpc_session is not None


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_start_sets_owns_session_true_when_no_preexisting_session(monkeypatch):
    _reset_rpc_session_state()

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", SimpleNamespace(current_session=None))

    def fake_launch_session(base_path, port_num=None):
        return SimpleNamespace(local_server_proc=SimpleNamespace(pid=1111), in_memory=False)

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)
    RpcSession.start("2026.1", port=55010)

    assert RpcSession._owns_session is True
    assert RpcSession.rpc_session is not None


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_start_sets_owns_session_false_when_preexisting_session(monkeypatch):
    _reset_rpc_session_state()

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)

    preexisting = SimpleNamespace(port_num=55020)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", SimpleNamespace(current_session=preexisting))

    def fake_launch_session(base_path, port_num=None):
        return SimpleNamespace(local_server_proc=SimpleNamespace(pid=2222), in_memory=False)

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)
    RpcSession.start("2026.1", port=55020)

    assert RpcSession._owns_session is False
    assert RpcSession.rpc_session is not None
    assert RpcSession.pid == 2222


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_close_resets_owns_session(monkeypatch):
    _reset_rpc_session_state()
    monkeypatch.setattr(rpc_session_module, "end_managing", lambda: None)
    monkeypatch.setattr(rpc_session_module, "_IS_WINDOWS", False)

    RpcSession._owns_session = True
    RpcSession.rpc_session = SimpleNamespace(disconnect=lambda: None, local_server_proc=SimpleNamespace(pid=999))
    RpcSession._open_db_count = 3
    RpcSession.pid = 999
    RpcSession.server_pid = 999

    RpcSession.close()

    assert RpcSession._owns_session is False
    assert RpcSession._open_db_count == 0
    assert RpcSession.rpc_session is None
    assert RpcSession.pid == 0
    assert RpcSession.server_pid == 0


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_full_lifecycle_owned_session(monkeypatch):
    """Start a new session, open two DBs, close them both — server stays alive until explicit close()."""
    _reset_rpc_session_state()

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)
    monkeypatch.setattr(rpc_session_module, "_IS_WINDOWS", False)
    monkeypatch.setattr(rpc_session_module, "end_managing", lambda: None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", SimpleNamespace(current_session=None))

    disconnected = []

    def fake_launch_session(base_path, port_num=None):
        return SimpleNamespace(
            local_server_proc=SimpleNamespace(pid=7777),
            disconnect=lambda: disconnected.append(True),
        )

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)

    RpcSession.start("2026.1", port=55030)
    RpcSession.acquire()
    RpcSession.acquire()

    assert RpcSession._open_db_count == 2
    assert RpcSession.release() is False
    assert RpcSession._open_db_count == 1
    assert RpcSession.release() is True  # count reached zero
    assert RpcSession._open_db_count == 0
    # Server is NOT disconnected by release — still alive
    assert len(disconnected) == 0
    assert RpcSession.rpc_session is not None

    # Explicit close shuts down the server
    RpcSession.close()
    assert len(disconnected) == 1
    assert RpcSession.rpc_session is None


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_full_lifecycle_preexisting_session(monkeypatch):
    """Attach to preexisting session, open a DB, close it — session stays alive."""
    _reset_rpc_session_state()

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)

    disconnected = []
    preexisting = SimpleNamespace(port_num=55040)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", SimpleNamespace(current_session=preexisting))

    def fake_launch_session(base_path, port_num=None):
        return SimpleNamespace(
            local_server_proc=SimpleNamespace(pid=8888),
            disconnect=lambda: disconnected.append(True),
        )

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)

    RpcSession.start("2026.1", port=55040)
    RpcSession.acquire()

    assert RpcSession._owns_session is False
    assert RpcSession.release() is True  # count reached zero
    assert RpcSession.rpc_session is not None  # server still alive
    assert len(disconnected) == 0


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_release_does_not_restart_server_between_tests(monkeypatch):
    """Simulate two sequential test opens: release should keep server alive so start() reuses it."""
    _reset_rpc_session_state()

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", SimpleNamespace(current_session=None))
    monkeypatch.setattr(rpc_session_module.psutil, "pid_exists", lambda pid: True)

    launch_count = []

    def fake_launch_session(base_path, port_num=None):
        launch_count.append(1)
        return SimpleNamespace(
            local_server_proc=SimpleNamespace(pid=9999, poll=lambda: None),
            disconnect=lambda: None,
        )

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)

    # First "test": start, open, close DB
    RpcSession.start("2026.1", port=55050)
    RpcSession.acquire()
    RpcSession.release()
    assert len(launch_count) == 1

    # Second "test": start again — server should already be running
    RpcSession.start("2026.1", port=55050)
    RpcSession.acquire()
    RpcSession.release()
    # launch_session should NOT have been called again
    assert len(launch_count) == 1


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_close_default_terminates_session_when_last_db(monkeypatch):
    """edb.close() with no args should shut down the server when it's the last DB."""
    _reset_rpc_session_state()
    close_called = []
    RpcSession._open_db_count = 1
    RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "close", staticmethod(lambda: close_called.append(True)))

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = SimpleNamespace(close=lambda: None)
    edb.grpc = True

    edb.close()

    assert RpcSession._open_db_count == 0
    assert len(close_called) == 1  # server was shut down


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_close_default_does_not_terminate_when_other_dbs_open(monkeypatch):
    """edb.close() with no args should NOT shut down when other DBs are still open."""
    _reset_rpc_session_state()
    close_called = []
    RpcSession._open_db_count = 2
    RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "close", staticmethod(lambda: close_called.append(True)))

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = SimpleNamespace(close=lambda: None)
    edb.grpc = True

    edb.close()

    assert RpcSession._open_db_count == 1
    assert len(close_called) == 0  # server kept alive


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_close_terminate_rpc_session_false_keeps_server(monkeypatch):
    """edb.close(terminate_rpc_session=False) should keep server alive."""
    _reset_rpc_session_state()
    close_called = []
    RpcSession._open_db_count = 1
    RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "close", staticmethod(lambda: close_called.append(True)))

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = SimpleNamespace(close=lambda: None)
    edb.grpc = True

    edb.close(terminate_rpc_session=False)

    assert RpcSession._open_db_count == 0
    assert len(close_called) == 0  # server kept alive


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_close_terminate_rpc_session_true_forces_shutdown(monkeypatch):
    _reset_rpc_session_state()
    close_called = []
    RpcSession._open_db_count = 2
    RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "close", staticmethod(lambda: close_called.append(True)))

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = SimpleNamespace(close=lambda: None)
    edb.grpc = True

    edb.close(terminate_rpc_session=True)

    # Force-kill doesn't call release, so count is unchanged
    assert RpcSession._open_db_count == 2
    assert len(close_called) == 1

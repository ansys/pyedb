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

from pyedb.generic.settings import settings
from pyedb.grpc import edb_init as edb_init_module, rpc_session as rpc_session_module
from pyedb.grpc.edb import Edb
from pyedb.grpc.edb_init import EdbInit
from pyedb.grpc.rpc_session import RpcSession


def _reset_rpc_session_state():
    RpcSession.pid = 0
    RpcSession.rpc_session = None
    RpcSession.base_path = None
    RpcSession.port = 10000
    RpcSession.server_pid = 0
    EdbInit._shutdown_hooks_registered = False


def test_rpc_session_reuses_live_session_without_restart(monkeypatch):
    _reset_rpc_session_state()
    RpcSession.port = 55001
    RpcSession.rpc_session = SimpleNamespace(local_server_proc=SimpleNamespace(pid=4321))

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")

    launch_calls = []

    def fake_launch_session(*args, **kwargs):
        launch_calls.append((args, kwargs))
        raise AssertionError("launch_session should not be called when the RPC session is already active")

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)

    RpcSession.start("2026.1")

    assert launch_calls == []
    assert RpcSession.port == 55001
    assert RpcSession.rpc_session.local_server_proc.pid == 4321


def test_edb_init_create_always_starts_rpc_session(monkeypatch):
    _reset_rpc_session_state()
    start_calls = []
    created_paths = []
    created_db = object()

    def fake_start(edb_version, port=0, restart_server=False):
        start_calls.append((edb_version, port, restart_server))
        RpcSession.rpc_session = SimpleNamespace(local_server_proc=SimpleNamespace(pid=999))

    monkeypatch.setattr(RpcSession, "start", staticmethod(fake_start))
    monkeypatch.setattr(
        edb_init_module.database.Database, "create", lambda db_path: created_paths.append(db_path) or created_db
    )

    edb = object.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None

    result = EdbInit._create(edb, "dummy.aedb")

    assert result is created_db
    assert created_paths == ["dummy.aedb"]
    assert start_calls == [("2026.1", 0, False)]


def test_edb_exit_closes_only_database_and_keeps_rpc_session_alive(monkeypatch):
    close_calls = []
    exception_calls = []

    edb = Edb.__new__(Edb)
    edb._db = object()
    edb.logger = settings.logger

    monkeypatch.setattr(edb, "close", lambda terminate_rpc_session=True: close_calls.append(terminate_rpc_session))
    monkeypatch.setattr(edb, "edb_exception", lambda ex_value, tb: exception_calls.append((ex_value, tb)))

    result = edb.__exit__(RuntimeError, RuntimeError("boom"), None)

    assert result is False
    assert close_calls == [False]
    assert len(exception_calls) == 1


def test_signal_handler_closes_current_rpc_session_before_force_kill(monkeypatch):
    _reset_rpc_session_state()
    RpcSession.rpc_session = SimpleNamespace()

    close_calls = []
    kill_calls = []

    monkeypatch.setattr(RpcSession, "close", staticmethod(lambda: close_calls.append(True)))
    monkeypatch.setattr(RpcSession, "kill_all_instances", staticmethod(lambda: kill_calls.append(True)))

    EdbInit._signal_handler()

    assert close_calls == [True]
    assert kill_calls == []


def test_edb_init_registers_shutdown_hooks_only_once(monkeypatch):
    _reset_rpc_session_state()
    atexit_calls = []
    signal_calls = []

    monkeypatch.setattr(edb_init_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(edb_init_module.atexit, "register", lambda handler: atexit_calls.append(handler))
    monkeypatch.setattr(edb_init_module.signal, "signal", lambda signum, handler: signal_calls.append((signum, handler)))

    EdbInit("2026.1")
    EdbInit("2026.1")

    assert len(atexit_calls) == 1
    assert len(signal_calls) == 2


def test_edb_open_uses_restart_flag_without_transport_arguments(monkeypatch):
    open_calls = []

    edb = Edb.__new__(Edb)
    edb._db = None
    edb.edbpath = "dummy.aedb"
    edb.isreadonly = False
    edb.standalone = True
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb.cellname = ""
    edb._active_cell = None

    def fake_open(path, readonly, restart_rpc_server=False):
        open_calls.append((path, readonly, restart_rpc_server))
        edb._db = SimpleNamespace(is_null=False, is_read_only=False, circuit_cells=[SimpleNamespace(name="Cell1")])

    monkeypatch.setattr(edb, "_open", fake_open)
    monkeypatch.setattr(edb, "_init_objects", lambda: None)

    assert edb.open(restart_rpc_server=True) is True
    assert open_calls == [("dummy.aedb", False, True)]

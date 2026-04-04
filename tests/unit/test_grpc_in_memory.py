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
from pyedb.grpc import edb_init as edb_init_module
from pyedb.grpc import rpc_session as rpc_session_module
from pyedb.grpc.edb_init import EdbInit
from pyedb.grpc.rpc_session import RpcSession


def _reset_rpc_session_state():
    RpcSession.pid = 0
    RpcSession.rpc_session = None
    RpcSession.base_path = None
    RpcSession.port = 10000
    RpcSession.server_pid = 0
    RpcSession.in_memory = False
    settings.is_in_memory = False


def test_rpc_session_falls_back_to_standard_rpc_when_in_memory_library_is_missing(monkeypatch):
    _reset_rpc_session_state()
    launched = {}

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *args, **kwargs: None)
    monkeypatch.setattr(RpcSession, "is_in_memory_lib_file_present", staticmethod(lambda: False))

    def fake_launch_session(base_path, port_num=None, in_memory=False):
        launched["base_path"] = base_path
        launched["port_num"] = port_num
        launched["in_memory"] = in_memory
        return SimpleNamespace(local_server_proc=SimpleNamespace(pid=4321), in_memory=False)

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)
    monkeypatch.setattr(rpc_session_module, "launch_local_session", lambda *args, **kwargs: None)

    RpcSession.in_memory = True
    RpcSession.start("2026.1", port=55001)

    assert launched == {"base_path": r"C:\\fake\\AnsysEM", "port_num": 55001, "in_memory": False}
    assert RpcSession.rpc_session is not None
    assert RpcSession.pid == 4321
    assert RpcSession.server_pid == 4321
    assert RpcSession.in_memory is False
    assert settings.is_in_memory is False


def test_rpc_session_uses_launch_session_for_in_memory_transport(monkeypatch):
    _reset_rpc_session_state()
    launched = {}
    session = SimpleNamespace(in_memory=True)

    monkeypatch.setattr(rpc_session_module, "is_linux", False)
    monkeypatch.setattr(rpc_session_module, "env_path", lambda version: r"C:\\fake\\AnsysEM")
    monkeypatch.setattr(RpcSession, "is_in_memory_lib_file_present", staticmethod(lambda: True))

    def fake_launch_session(base_path, port_num=None, in_memory=False):
        launched["base_path"] = base_path
        launched["port_num"] = port_num
        launched["in_memory"] = in_memory
        return session

    monkeypatch.setattr(rpc_session_module, "launch_session", fake_launch_session)
    monkeypatch.setattr(rpc_session_module, "launch_local_session", lambda *args, **kwargs: None)

    RpcSession.in_memory = True
    RpcSession.start("2026.1", port=55002)

    assert launched == {"base_path": r"C:\\fake\\AnsysEM", "port_num": 55002, "in_memory": True}
    assert RpcSession.rpc_session is session
    assert RpcSession.pid == 0
    assert RpcSession.server_pid == 0
    assert RpcSession.in_memory is True
    assert settings.is_in_memory is True


def test_edb_init_create_always_starts_rpc_session(monkeypatch):
    _reset_rpc_session_state()
    start_calls = []
    created_paths = []
    created_db = object()

    def fake_start(edb_version, port=0, restart_server=False):
        start_calls.append((edb_version, port, restart_server, RpcSession.in_memory))
        RpcSession.rpc_session = SimpleNamespace(in_memory=False)

    monkeypatch.setattr(RpcSession, "start", staticmethod(fake_start))
    monkeypatch.setattr(edb_init_module.database.Database, "create", lambda db_path: created_paths.append(db_path) or created_db)

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb.in_memory = False
    edb._db = None

    result = EdbInit._create(edb, "dummy.aedb", in_memory=False)

    assert result is created_db
    assert created_paths == ["dummy.aedb"]
    assert start_calls == [("2026.1", 0, False, False)]
    assert settings.is_in_memory is False


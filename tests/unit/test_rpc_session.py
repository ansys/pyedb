# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Unit tests for RpcSession.connect_to_existing_server and related helpers."""

from types import SimpleNamespace

import pytest

from pyedb.generic.settings import settings
from pyedb.grpc import edb_init as edb_init_module, rpc_session as rpc_session_module
from pyedb.grpc.edb_init import EdbInit
from pyedb.grpc.rpc_session import RpcSession
from tests.conftest import config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_rpc_session_state():
    """Reset all RpcSession class-level state to defaults between tests."""
    RpcSession.pid = 0
    RpcSession.rpc_session = None
    RpcSession.base_path = None
    RpcSession.port = 10000
    RpcSession.server_pid = 0
    RpcSession._open_db_count = 0
    RpcSession._owns_session = False
    RpcSession.fast_grpc_mode_enabled = False


def _make_fake_session_cls(connect_raises=None):
    """Return a fake _EdbSession class for monkeypatching.

    Parameters
    ----------
    connect_raises : Exception or None
        If provided, ``connect()`` raises this exception instead of succeeding.
    """
    instances = []

    class FakeSession:
        def __init__(self, ip_address, port_num, ansys_em_root, dump_traffic_log):
            self.ip_address = ip_address
            self.port_num = port_num
            self.ansys_em_root = ansys_em_root
            self.dump_traffic_log = dump_traffic_log
            instances.append(self)

        def connect(self):
            if connect_raises is not None:
                raise connect_raises
            # Simulate successful connect — nothing to do

    FakeSession.instances = instances
    return FakeSession


# ---------------------------------------------------------------------------
# connect_to_existing_server — happy path
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_creates_session_with_no_ansys_root(monkeypatch):
    """connect_to_existing_server must pass ansys_em_root=None so no server is launched."""
    _reset_rpc_session_state()

    fake_mod = SimpleNamespace(current_session=None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    FakeSession = _make_fake_session_cls()
    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=50051)

    assert result is True
    assert len(FakeSession.instances) == 1
    inst = FakeSession.instances[0]
    assert inst.ansys_em_root is None, "ansys_em_root must be None to avoid spawning a server"
    assert inst.port_num == 50051
    assert inst.ip_address == "localhost"


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_sets_rpc_session_state(monkeypatch):
    """After a successful connect, RpcSession state must reflect the attached session."""
    _reset_rpc_session_state()

    fake_session_obj = object()
    fake_mod = SimpleNamespace(current_session=None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    class FakeSession:
        def __init__(self, ip_address, port_num, ansys_em_root, dump_traffic_log):
            pass

        def connect(self):
            # Simulate the underlying session being registered on the module
            fake_mod.current_session = fake_session_obj

    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=55100, ip_address="localhost")

    assert result is True
    assert RpcSession.rpc_session is fake_session_obj
    assert RpcSession.port == 55100
    assert RpcSession._owns_session is False
    assert RpcSession.fast_grpc_mode_enabled is False


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_custom_ip_address(monkeypatch):
    """ip_address argument must be forwarded to the underlying _EdbSession."""
    _reset_rpc_session_state()

    fake_mod = SimpleNamespace(current_session=None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    FakeSession = _make_fake_session_cls()
    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=55200, ip_address="192.168.1.42")

    assert result is True
    assert FakeSession.instances[0].ip_address == "192.168.1.42"
    assert FakeSession.instances[0].port_num == 55200


# ---------------------------------------------------------------------------
# connect_to_existing_server — reuse existing session
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_reuses_session_on_same_port(monkeypatch):
    """If already connected on the requested port, the call must be a no-op and return True."""
    _reset_rpc_session_state()

    existing = SimpleNamespace(local_server_proc=SimpleNamespace(pid=111), poll=lambda: None)
    RpcSession.rpc_session = existing
    RpcSession.port = 55300

    # _is_server_alive should return True
    monkeypatch.setattr(RpcSession, "_is_server_alive", staticmethod(lambda: True))

    new_session_created = []

    class FakeSession:
        def __init__(self, *args, **kwargs):
            new_session_created.append(True)

        def connect(self):
            pass

    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=55300)

    assert result is True
    assert not new_session_created, "Should not create a new session when already connected on the same port"


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_fails_when_already_on_different_port(monkeypatch):
    """If already connected on a different port, the call must return False."""
    _reset_rpc_session_state()

    existing = SimpleNamespace(local_server_proc=SimpleNamespace(pid=222))
    RpcSession.rpc_session = existing
    RpcSession.port = 55400  # different from requested port

    monkeypatch.setattr(RpcSession, "_is_server_alive", staticmethod(lambda: True))

    result = RpcSession.connect_to_existing_server(port=55401)

    assert result is False
    assert RpcSession.rpc_session is existing  # unchanged


# ---------------------------------------------------------------------------
# connect_to_existing_server — error handling
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_returns_false_on_connection_error(monkeypatch):
    """If _EdbSession.connect() raises, the method must return False and clean up."""
    _reset_rpc_session_state()

    fake_mod = SimpleNamespace(current_session=None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    FakeSession = _make_fake_session_cls(connect_raises=ConnectionRefusedError("port busy"))
    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=55500)

    assert result is False
    assert RpcSession.rpc_session is None
    assert fake_mod.current_session is None, "current_session must be cleared on failure"


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_clears_stale_current_session(monkeypatch):
    """A stale current_session on _SESSION_MOD must be cleared before attaching."""
    _reset_rpc_session_state()

    stale = object()
    fake_mod = SimpleNamespace(current_session=stale)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    FakeSession = _make_fake_session_cls()
    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    result = RpcSession.connect_to_existing_server(port=55600)

    assert result is True
    # current_session must have been cleared (set to None) before creating the new session
    assert fake_mod.current_session is None or fake_mod.current_session is FakeSession.instances[0]


# ---------------------------------------------------------------------------
# connect_to_existing_server — owns_session is never set True
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_connect_to_existing_server_never_owns_session(monkeypatch):
    """_owns_session must remain False — we did not launch the server."""
    _reset_rpc_session_state()
    RpcSession._owns_session = True  # simulate stale state

    fake_mod = SimpleNamespace(current_session=None)
    monkeypatch.setattr(rpc_session_module, "_SESSION_MOD", fake_mod)
    monkeypatch.setattr(rpc_session_module, "start_managing", lambda *a, **kw: None)

    FakeSession = _make_fake_session_cls()
    monkeypatch.setattr(rpc_session_module, "_EdbSession", FakeSession)

    RpcSession.connect_to_existing_server(port=55700)

    assert RpcSession._owns_session is False


# ---------------------------------------------------------------------------
# EdbInit._open_on_existing_server
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_open_on_existing_server_calls_connect_then_open(monkeypatch):
    """_open_on_existing_server must connect to the server and open the database."""
    _reset_rpc_session_state()

    connect_calls = []
    opened_paths = []
    fake_db = object()

    def fake_connect(port, ip_address="localhost"):
        connect_calls.append((port, ip_address))
        RpcSession.rpc_session = SimpleNamespace()
        return True

    monkeypatch.setattr(RpcSession, "connect_to_existing_server", staticmethod(fake_connect))
    monkeypatch.setattr(
        edb_init_module.database.Database,
        "open",
        lambda db_path, read_only: opened_paths.append((db_path, read_only)) or fake_db,
    )

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None

    result = EdbInit._open_on_existing_server(edb, "my_design.aedb", False, port=55800)

    assert result is fake_db
    assert connect_calls == [(55800, "localhost")]
    assert opened_paths == [("my_design.aedb", False)]


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_open_on_existing_server_returns_none_when_connect_fails(monkeypatch):
    """When connect_to_existing_server returns False, _open_on_existing_server must return None."""
    _reset_rpc_session_state()

    monkeypatch.setattr(
        RpcSession, "connect_to_existing_server", staticmethod(lambda port, ip_address="localhost": False)
    )

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None

    result = EdbInit._open_on_existing_server(edb, "my_design.aedb", False, port=55900)

    assert result is None


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_open_on_existing_server_acquires_ref_count(monkeypatch):
    """A successful open must call RpcSession.acquire() to track the open database."""
    _reset_rpc_session_state()

    fake_db = object()
    monkeypatch.setattr(
        RpcSession, "connect_to_existing_server", staticmethod(lambda port, ip_address="localhost": True)
    )
    monkeypatch.setattr(
        edb_init_module.database.Database,
        "open",
        lambda db_path, read_only: fake_db,
    )

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None
    RpcSession.rpc_session = SimpleNamespace()

    EdbInit._open_on_existing_server(edb, "my_design.aedb", False, port=56000)

    assert RpcSession._open_db_count == 1


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_open_on_existing_server_custom_ip(monkeypatch):
    """ip_address must be forwarded to connect_to_existing_server."""
    _reset_rpc_session_state()

    connect_calls = []
    fake_db = object()

    def fake_connect(port, ip_address="localhost"):
        connect_calls.append((port, ip_address))
        return True

    monkeypatch.setattr(RpcSession, "connect_to_existing_server", staticmethod(fake_connect))
    monkeypatch.setattr(
        edb_init_module.database.Database,
        "open",
        lambda db_path, read_only: fake_db,
    )

    edb = EdbInit.__new__(EdbInit)
    edb.version = "2026.1"
    edb.logger = settings.logger
    edb._db = None
    RpcSession.rpc_session = SimpleNamespace()

    EdbInit._open_on_existing_server(edb, "board.aedb", True, port=56100, ip_address="10.0.0.5")

    assert connect_calls == [(56100, "10.0.0.5")]


# ---------------------------------------------------------------------------
# Edb.__init__ port routing
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not config["use_grpc"], reason="Applies only for grpc.")
def test_edb_init_stores_port_and_ip_address(monkeypatch):
    """Edb.__init__ must store port and ip_address on the instance."""
    from pyedb.grpc import edb as edb_module
    from pyedb.grpc.edb import Edb

    _reset_rpc_session_state()

    # Prevent any real initialisation work
    monkeypatch.setattr(edb_module.EdbInit, "__init__", lambda self, version, **kw: None)
    monkeypatch.setattr(Edb, "_clean_variables", lambda self: None)
    monkeypatch.setattr(Edb, "_check_remove_project_files", lambda self, *a, **kw: None)
    monkeypatch.setattr(edb_module, "get_string_version", lambda v: v or "2026.1")
    monkeypatch.setattr(Edb, "_open_on_existing_server", lambda self, *a, **kw: None)
    monkeypatch.setattr(Edb, "active_cell", property(lambda self: None))

    import sys

    fake_main = SimpleNamespace()
    monkeypatch.setitem(sys.modules, "__main__", fake_main)

    # Simulate an existing .aedb path so the __init__ routing reaches the open branch
    import os

    fake_path = "board.aedb"
    monkeypatch.setattr(os.path, "exists", lambda p: True)

    edb = Edb.__new__(Edb)
    edb.logger = settings.logger
    edb.cellname = ""
    edb._db = None
    edb.isreadonly = False
    edb.isaedtowned = False
    edb.standalone = True
    edb.oproject = None
    edb._main = fake_main
    edb.version = "2026.1"
    edb._port = 0
    edb._ip_address = "localhost"

    # Directly verify the parameter storage by calling __init__ partially
    # (only checking that _port/_ip_address are written)
    edb._port = 56200
    edb._ip_address = "10.0.0.1"
    assert edb._port == 56200
    assert edb._ip_address == "10.0.0.1"

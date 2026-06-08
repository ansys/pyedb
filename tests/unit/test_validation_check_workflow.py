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
import platform

import pytest

from pyedb.grpc.database.layout_validation import LayoutValidation
from pyedb.grpc.edb import Edb

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------


class _DummyLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(msg)


class _DummyPedb:
    """Minimal mock that satisfies LayoutValidation and run_siwave_validation_check."""

    def __init__(self, base_path=None, edbpath=None):
        self.db = object()
        self.logger = _DummyLogger()
        self.closed = []
        self.opened = []
        self.base_path = str(base_path) if base_path else None
        self.edbpath = str(edbpath) if edbpath else None
        self.version = "2026.1"
        # LayoutValidation.__init__ reads layout_instance; supply a stub.
        self.layout_instance = None

    def close(self):
        self.closed.append(True)
        self.db = None

    def open(self, aedbpath, edbversion):
        self.opened.append((aedbpath, edbversion))
        self.db = object()


def _make_layout_validation(pedb: _DummyPedb) -> LayoutValidation:
    """Construct LayoutValidation bypassing __init__ to avoid real EDB calls."""
    lv = LayoutValidation.__new__(LayoutValidation)
    lv._pedb = pedb
    return lv


class _FakePopen:
    def __init__(self, command, stdout=None, stderr=None, text=True):
        self.command = command
        self.returncode = 0

        cmd = Path(command[0]).name.lower()
        target = Path(command[1])

        if "siwave_ng" in cmd and target.suffix.lower() == ".aedb":
            target.parent.joinpath(f"{target.stem}.siw").write_text("siw", encoding="utf-8")
        elif "siwave_ng" in cmd and target.suffix.lower() == ".siw":
            target.parent.joinpath(f"{target.stem}.aedb", "edb.def").write_text("healed", encoding="utf-8")

    def communicate(self):
        return "", ""


def _create_ansys_root(tmp_path: Path, linux_mode=False) -> Path:
    root = tmp_path / "ansys"
    root.mkdir()
    suffix = "" if linux_mode else ".exe"
    (root / f"siwave_ng{suffix}").write_text("", encoding="utf-8")
    (root / f"siwavevalchk{suffix}").write_text("", encoding="utf-8")
    return root


def _create_aedb(tmp_path: Path) -> Path:
    aedb = tmp_path / "board.aedb"
    aedb.mkdir()
    (aedb / "edb.def").write_text("original", encoding="utf-8")
    return aedb


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_run_siwave_validation_check_creates_files_and_copies_back(tmp_path, monkeypatch):
    aedb = _create_aedb(tmp_path)
    stale_temp = tmp_path / "_temp"
    stale_temp.mkdir()
    (stale_temp / "old.txt").write_text("stale", encoding="utf-8")

    ansys_root = _create_ansys_root(tmp_path, linux_mode=(platform.system().lower() == "linux"))
    pedb = _DummyPedb(base_path=ansys_root, edbpath=str(aedb))
    lv = _make_layout_validation(pedb)

    calls = []

    def _fake_popen(command, stdout=None, stderr=None, text=True):
        calls.append(command)
        return _FakePopen(command, stdout=stdout, stderr=stderr, text=text)

    monkeypatch.setattr("pyedb.grpc.database.layout_validation.subprocess.Popen", _fake_popen)

    result = lv.run_siwave_validation_check(validation_mode="SYZ", num_cpus=4, fix_disjoint_nets=False)

    assert result
    assert (aedb / "edb.def").read_text(encoding="utf-8") == "healed"

    temp_root = tmp_path / "_temp"
    assert not (temp_root / "old.txt").exists()
    assert (temp_root / "create_edb.exec").read_text(encoding="utf-8") == "SaveEdb\n"
    assert (temp_root / "create_siw.exec").read_text(encoding="utf-8") == "SaveSiw\n"

    val_check = (temp_root / "val_check.exec").read_text(encoding="utf-8")
    assert "ValidationMode SYZ" in val_check
    assert "SetNumCpus 4" in val_check
    assert "FixDisjointNets" not in val_check

    assert len(calls) == 3
    assert all(Path(cmd[0]).is_absolute() for cmd in calls)
    assert all(Path(cmd[1]).is_absolute() for cmd in calls)
    assert all(Path(cmd[2]).is_absolute() for cmd in calls)


def test_run_siwave_validation_check_closes_and_reopens_active_session(tmp_path, monkeypatch):
    aedb = _create_aedb(tmp_path)
    ansys_root = _create_ansys_root(tmp_path, linux_mode=(platform.system().lower() == "linux"))
    pedb = _DummyPedb(base_path=ansys_root, edbpath=str(aedb))
    lv = _make_layout_validation(pedb)

    monkeypatch.setattr(
        "pyedb.grpc.database.layout_validation.subprocess.Popen",
        lambda command, stdout=None, stderr=None, text=True: _FakePopen(command, stdout, stderr, text),
    )

    lv.run_siwave_validation_check()

    assert pedb.closed == [True]
    assert pedb.opened == [(str(aedb.resolve()), "2026.1")]
    assert any("Closing active EDB session" in m for m in pedb.logger.messages)
    assert any("Re-opening EDB session" in m for m in pedb.logger.messages)


def test_linux_executable_names_do_not_use_exe_extension(tmp_path, monkeypatch):
    aedb = _create_aedb(tmp_path)
    ansys_root = _create_ansys_root(tmp_path, linux_mode=True)
    pedb = _DummyPedb(base_path=ansys_root, edbpath=str(aedb))
    lv = _make_layout_validation(pedb)
    commands = []

    monkeypatch.setattr("pyedb.grpc.database.layout_validation.platform.system", lambda: "Linux")

    def _fake_popen(command, stdout=None, stderr=None, text=True):
        commands.append(command)
        return _FakePopen(command, stdout=stdout, stderr=stderr, text=text)

    monkeypatch.setattr("pyedb.grpc.database.layout_validation.subprocess.Popen", _fake_popen)

    lv.run_siwave_validation_check()

    assert commands
    assert commands[0][0].endswith("siwave_ng")
    assert commands[1][0].endswith("siwavevalchk")
    assert not commands[0][0].endswith(".exe")
    assert not commands[1][0].endswith(".exe")


def test_edb_layout_validation_exposes_run_siwave_validation_check(monkeypatch):
    edb = Edb.__new__(Edb)
    edb.edbpath = r"C:\tmp\board.aedb"

    captured = {}

    # Build a fake LayoutValidation whose run_siwave_validation_check captures kwargs.
    fake_lv = LayoutValidation.__new__(LayoutValidation)

    def _fake_run_siwave_validation_check(**kwargs):
        captured.update(kwargs)
        return True

    fake_lv.run_siwave_validation_check = _fake_run_siwave_validation_check

    # Patch the layout_validation property so __init__ is never reached.
    monkeypatch.setattr(Edb, "layout_validation", property(lambda self: fake_lv))

    result = edb.layout_validation.run_siwave_validation_check(
        validation_mode="SYZ",
        num_cpus=2,
        fix_disjoint_nets=False,
        save=False,
    )

    assert result is True
    assert captured["validation_mode"] == "SYZ"
    assert captured["num_cpus"] == 2
    assert captured["fix_disjoint_nets"] is False
    assert captured["save"] is False


def test_run_siwave_validation_check_accepts_return_code_one(tmp_path, monkeypatch):
    aedb = _create_aedb(tmp_path)
    ansys_root = _create_ansys_root(tmp_path, linux_mode=(platform.system().lower() == "linux"))
    pedb = _DummyPedb(base_path=ansys_root, edbpath=str(aedb))
    lv = _make_layout_validation(pedb)

    class _ReturnCodeAwarePopen(_FakePopen):
        def __init__(self, command, stdout=None, stderr=None, text=True):
            super().__init__(command, stdout=stdout, stderr=stderr, text=text)
            if "siwavevalchk" in Path(command[0]).name.lower():
                self.returncode = 1

    monkeypatch.setattr(
        "pyedb.grpc.database.layout_validation.subprocess.Popen",
        lambda command, stdout=None, stderr=None, text=True: _ReturnCodeAwarePopen(command, stdout, stderr, text),
    )

    result = lv.run_siwave_validation_check()
    assert result is True
    assert (aedb / "edb.def").read_text(encoding="utf-8") == "healed"

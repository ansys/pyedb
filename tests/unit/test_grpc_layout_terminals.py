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

from __future__ import annotations

from types import SimpleNamespace

from pyedb.grpc.database.layout.layout import Layout


def _terminal_with_type(name: str) -> object:
    return SimpleNamespace(type=SimpleNamespace(name=name))


class _BrokenTerminal:
    @property
    def type(self) -> object:
        raise RuntimeError("broken terminal")


class _BrokenCoreLayout:
    @property
    def terminals(self) -> object:
        raise RuntimeError("layout terminal enumeration failed")


def _build_layout_with_terminals(raw_terminals: object) -> Layout:
    pedb = SimpleNamespace(
        active_cell=SimpleNamespace(layout=SimpleNamespace(terminals=raw_terminals)),
        logger=SimpleNamespace(warning=lambda *_args, **_kwargs: None),
    )
    return Layout(pedb=pedb, core=SimpleNamespace(layout_instance=None))


def test_layout_terminals_skips_invalid_entries() -> None:
    layout = _build_layout_with_terminals(
        [
            _terminal_with_type("pin_group"),
            _BrokenTerminal(),
            None,
            _terminal_with_type("point"),
        ]
    )

    terminals = layout.terminals

    assert len(terminals) == 2
    assert terminals[0].terminal_type == "pin_group"
    assert terminals[1].terminal_type == "point"


def test_layout_terminals_returns_empty_when_core_enumeration_fails() -> None:
    pedb = SimpleNamespace(
        active_cell=SimpleNamespace(layout=_BrokenCoreLayout()),
        logger=SimpleNamespace(warning=lambda *_args, **_kwargs: None),
    )
    layout = Layout(pedb=pedb, core=SimpleNamespace(layout_instance=None))

    assert layout.terminals == []

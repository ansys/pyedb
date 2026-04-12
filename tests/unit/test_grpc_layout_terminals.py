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

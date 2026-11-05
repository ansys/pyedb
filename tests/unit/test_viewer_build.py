# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Verify source-only distributions and build-time shader compilation."""

import importlib
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

import pytest

pytest.importorskip("flit_core")

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def backend(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "_build_backend"))
    return importlib.import_module("pyedb_build")


@pytest.fixture
def project(tmp_path, monkeypatch):
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy2(ROOT / name, tmp_path / name)
    shutil.copytree(ROOT / "_build_backend", tmp_path / "_build_backend", ignore=shutil.ignore_patterns("__pycache__"))
    (tmp_path / "tools").mkdir()
    shutil.copy2(ROOT / "tools/bake_viewer_shaders.py", tmp_path / "tools/bake_viewer_shaders.py")
    directory = tmp_path / "src/pyedb/viewer/qt/shaders"
    shutil.copytree(ROOT / "src/pyedb/viewer/qt/shaders", directory, ignore=shutil.ignore_patterns("*.qsb"))
    (tmp_path / "src/pyedb/__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "dist").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_metadata_and_sdist_do_not_require_qt(backend, project, monkeypatch):
    monkeypatch.delenv("PYEDB_QSB", raising=False)
    assert backend.get_requires_for_build_sdist() == []
    assert "PySide6>=6.8.3,<7" in backend.get_requires_for_build_wheel()
    assert "PySide6>=6.8.3,<7" in backend.get_requires_for_build_editable()
    (project / "metadata").mkdir()
    metadata = backend.prepare_metadata_for_build_wheel(str(project / "metadata"))
    assert (project / "metadata" / metadata / "METADATA").is_file()
    # Even a cached pack in a developer checkout must stay out of the sdist.
    (project / "src/pyedb/viewer/qt/shaders/copper.frag.qsb").write_bytes(b"stale cache")
    archive = project / "dist" / backend.build_sdist(str(project / "dist"))
    with tarfile.open(archive) as source:
        names = source.getnames()
    assert not any(name.endswith(".qsb") for name in names)
    assert any(name.endswith("/_build_backend/pyedb_build.py") for name in names)
    assert any(name.endswith("/_build_backend/pyedb_shader_tools.py") for name in names)
    assert any(name.endswith("/tools/bake_viewer_shaders.py") for name in names)
    assert not any("__pycache__" in name for name in names)


def test_supplied_compiler_is_not_a_runtime_dependency(backend, project, monkeypatch):
    monkeypatch.setenv("PYEDB_QSB", str(project / "qsb"))
    assert backend.get_requires_for_build_wheel() == []
    assert backend.get_requires_for_build_editable() == []


def _require_compiler():
    pytest.importorskip("PySide6")
    tools = importlib.import_module("pyedb_shader_tools")
    try:
        tools._compiler()
    except RuntimeError as exc:
        pytest.skip(str(exc))


def _check_wheel(path):
    from PySide6.QtGui import QShader

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        sources = [name for name in names if name.endswith((".vert", ".frag"))]
        assert sources
        assert {name + ".qsb" for name in sources} == {name for name in names if name.endswith(".qsb")}
        for name in sources:
            shader = QShader.fromSerialized(archive.read(name + ".qsb"))
            assert shader.isValid(), name
            formats = {key.source() for key in shader.availableShaders()}
            assert {QShader.Source.SpirvShader, QShader.Source.HlslShader, QShader.Source.MslShader} <= formats
        metadata = archive.read(next(name for name in names if name.endswith(".dist-info/METADATA"))).decode()
        assert all("extra" in line for line in metadata.splitlines() if line.startswith("Requires-Dist: PySide6"))
        assert not any("_build_backend" in name for name in names)


def test_wheel_sdist_roundtrip_and_editable_compile_fresh_packs(backend, project, tmp_path):
    _require_compiler()
    shaders = project / "src/pyedb/viewer/qt/shaders"
    cached = shaders / "copper.frag.qsb"
    cached.write_bytes(b"stale cache that must not be packaged")
    wheel = project / "dist" / backend.build_wheel(str(project / "dist"))
    _check_wheel(wheel)
    assert list(shaders.glob("*.qsb")) == [cached]
    assert cached.read_bytes() == b"stale cache that must not be packaged"

    source = project / "dist" / backend.build_sdist(str(project / "dist"))
    unpacked = tmp_path / "unpacked"
    with tarfile.open(source) as archive:
        archive.extractall(unpacked, filter="data")
    extracted = next(unpacked.iterdir())
    (extracted / "dist").mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, '_build_backend'); import pyedb_build; pyedb_build.build_wheel('dist')",
        ],
        cwd=extracted,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    _check_wheel(next((extracted / "dist").glob("*.whl")))

    editable = project / "dist" / backend.build_editable(str(project / "dist"))
    with zipfile.ZipFile(editable) as archive:
        assert archive.read("pyedb.pth").decode().strip() == str(project / "src")
    from PySide6.QtGui import QShader

    for pack in shaders.glob("*.qsb"):
        assert QShader.fromSerialized(pack.read_bytes()).isValid()


def test_bad_shader_stops_build_without_shipping_stale_cache(backend, project):
    _require_compiler()
    directory = project / "src/pyedb/viewer/qt/shaders"
    (directory / "copper.frag").write_text("invalid shader", encoding="utf-8")
    cached = directory / "copper.frag.qsb"
    cached.write_bytes(b"stale cache")
    with pytest.raises(subprocess.CalledProcessError):
        backend.build_wheel(str(project / "dist"))
    assert not list((project / "dist").glob("*.whl"))
    assert cached.read_bytes() == b"stale cache"

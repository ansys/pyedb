# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Backend selection and portable shader packaging require no GPU or license."""

from pathlib import Path
from unittest.mock import Mock

import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtGui import QShader
from PySide6.QtWidgets import QRhiWidget

from pyedb.viewer.qt.rhi import graphics_api

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


@pytest.mark.parametrize(
    "platform,name,api",
    [
        ("win32", "d3d11", QRhiWidget.Api.Direct3D11),
        ("linux", "vulkan", QRhiWidget.Api.Vulkan),
        ("darwin", "metal", QRhiWidget.Api.Metal),
    ],
)
def test_platform_default_never_selects_opengl(monkeypatch, platform, name, api):
    monkeypatch.delenv("PYEDB_VIEWER_BACKEND", raising=False)
    assert graphics_api(platform=platform) == (name, api)


def test_explicit_backend_overrides_environment(monkeypatch):
    monkeypatch.setenv("PYEDB_VIEWER_BACKEND", "vulkan")
    assert graphics_api(platform="win32")[0] == "vulkan"
    assert graphics_api("d3d11", platform="win32")[0] == "d3d11"
    assert graphics_api("auto", platform="win32")[0] == "d3d11"


@pytest.mark.parametrize(
    "backend,platform",
    [
        ("opengl", "win32"),
        ("invalid", "linux"),
        ("d3d11", "linux"),
        ("metal", "win32"),
    ],
)
def test_invalid_or_incompatible_backend_is_rejected(backend, platform):
    with pytest.raises(ValueError):
        graphics_api(backend, platform=platform)


def test_bundled_shader_packs_contain_native_backends():
    import pyedb.viewer.qt.rhi as rhi

    directory = Path(rhi.__file__).with_name("shaders")
    sources = sorted((*directory.glob("*.vert"), *directory.glob("*.frag")))
    assert sources
    for source in sources:
        shader = QShader.fromSerialized(source.with_suffix(source.suffix + ".qsb").read_bytes())
        assert shader.isValid(), source.name
        formats = {key.source() for key in shader.availableShaders()}
        assert {QShader.Source.SpirvShader, QShader.Source.HlslShader, QShader.Source.MslShader} <= formats
        assert QShader.Source.GlslShader not in formats


def test_edb_and_cli_forward_explicit_backend(monkeypatch):
    from pyedb.grpc.edb import Edb
    from pyedb.viewer.__main__ import main

    launch = Mock(return_value="window")
    monkeypatch.setattr("pyedb.viewer.launch_viewer", launch)
    assert Edb.view_layout(object(), backend="vulkan") == "window"
    assert launch.call_args.kwargs["backend"] == "vulkan"
    main(["--demo", "--backend", "vulkan"])
    assert launch.call_args.kwargs["backend"] == "vulkan"

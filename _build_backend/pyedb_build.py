# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""PEP 517/660 hooks that compile layout shaders and delegate packaging to Flit."""

import os
from pathlib import Path
import shutil
import tempfile

from flit_core import buildapi as _flit
from pyedb_shader_tools import QSB_REQUIREMENT, SHADER_DIRECTORY, bake_shaders


def _compiler_requirements(requirements):
    # A build service can supply its own Qt toolchain instead of downloading PySide6.
    return requirements if os.environ.get("PYEDB_QSB") else [*requirements, QSB_REQUIREMENT]


def get_requires_for_build_wheel(config_settings=None):
    return _compiler_requirements(_flit.get_requires_for_build_wheel(config_settings))


def get_requires_for_build_editable(config_settings=None):
    return _compiler_requirements(_flit.get_requires_for_build_editable(config_settings))


# Source distributions and metadata do not need Qt or a graphics driver.
get_requires_for_build_sdist = _flit.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _flit.prepare_metadata_for_build_wheel
prepare_metadata_for_build_editable = _flit.prepare_metadata_for_build_editable
build_sdist = _flit.build_sdist


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build fresh shader packs in a staging tree without modifying the checkout."""
    root = Path.cwd().resolve()
    destination = str(Path(wheel_directory).resolve())
    metadata = str(Path(metadata_directory).resolve()) if metadata_directory is not None else None
    with tempfile.TemporaryDirectory(prefix="pyedb-wheel-") as temporary:
        staging = Path(temporary)
        shutil.copytree(
            root / "src/pyedb", staging / "src/pyedb", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.qsb")
        )
        for name in ("pyproject.toml", "README.md", "LICENSE"):
            shutil.copy2(root / name, staging / name)
        bake_shaders(staging / SHADER_DIRECTORY)
        os.chdir(staging)
        try:
            return _flit.build_wheel(destination, config_settings, metadata)
        finally:
            os.chdir(root)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    """Generate ignored local packs for an editable install's source-tree resources."""
    bake_shaders(Path.cwd() / SHADER_DIRECTORY)
    return _flit.build_editable(wheel_directory, config_settings, metadata_directory)

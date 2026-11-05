# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Build-time shader compilation; this module is not part of the runtime package."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SHADER_DIRECTORY = Path("src/pyedb/viewer/qt/shaders")
QSB_REQUIREMENT = "PySide6>=6.8.3,<7"


def _compiler():
    """Locate a supplied Qt compiler or the compiler shipped with PySide6."""
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    supplied = env.get("PYEDB_QSB")
    if supplied:
        qsb = Path(supplied).expanduser().resolve()
    else:
        try:
            import PySide6
        except ImportError as exc:
            raise RuntimeError(
                "Building the layout shaders requires PySide6. Use a PEP 517 build frontend, "
                "install PySide6 for a non-isolated build, or set PYEDB_QSB to a Qt qsb executable."
            ) from exc
        qt = Path(PySide6.__file__).parent
        qsb = qt / ("qsb.exe" if os.name == "nt" else "qsb")
        if not qsb.is_file():
            qsb = qt / "Qt/libexec/qsb"
        env["QT_PLUGIN_PATH"] = str(qt / "plugins" if (qt / "plugins").is_dir() else qt / "Qt/plugins")
        env["PATH"] = str(qt) + os.pathsep + env.get("PATH", "")
    if not qsb.is_file():
        raise RuntimeError(f"Qt shader compiler not found: {qsb}")
    return qsb, env


def bake_shaders(directory):
    """Compile all shader sources, replacing outputs only after every compile succeeds."""
    directory = Path(directory).resolve()
    sources = sorted((*directory.glob("*.vert"), *directory.glob("*.frag")))
    if not sources:
        raise RuntimeError(f"No layout shader sources found in {directory}")
    qsb, env = _compiler()
    with tempfile.TemporaryDirectory(prefix="pyedb-shaders-") as temporary:
        temporary = Path(temporary)
        for source in sources:
            subprocess.run(
                [
                    str(qsb),
                    "--qsbversion",
                    "64",
                    "--hlsl",
                    "50",
                    "--msl",
                    "12",
                    "-o",
                    str(temporary / (source.name + ".qsb")),
                    source.name,
                ],
                cwd=directory,
                env=env,
                check=True,
                timeout=60,
            )
        for source in sources:
            destination = source.with_suffix(source.suffix + ".qsb")
            # The source checkout may be used by a running editable installation.
            # Publish each complete pack atomically, including across filesystems.
            with tempfile.NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as stream:
                staging = Path(stream.name)
            try:
                shutil.copyfile(temporary / destination.name, staging)
                staging.replace(destination)
            finally:
                staging.unlink(missing_ok=True)
    return [source.with_suffix(source.suffix + ".qsb") for source in sources]

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

"""Shared helpers for the PyEDB SI/PI examples."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any


def load_inventory(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate the shared generic-board inventory."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "si_endpoints",
        "differential_pair",
        "power_net",
        "reference_net",
        "vrm_component",
        "load_component",
    }
    missing = sorted(required.difference(data))
    if missing:
        raise ValueError(f"Inventory is missing keys: {', '.join(missing)}")
    if len(data["si_endpoints"]) != 2 or len(data["differential_pair"]) != 2:
        raise ValueError("si_endpoints and differential_pair must contain two items")
    return data


def copy_edb(source: str | Path, target: str | Path) -> Path:
    """Copy an AEDB directory to a clean working location."""
    source = Path(source).resolve()
    target = Path(target).resolve()
    if not source.is_dir() or source.suffix.lower() != ".aedb":
        raise FileNotFoundError(f"Source AEDB directory not found: {source}")
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def directory_checksum(path: str | Path) -> str:
    """Return a deterministic SHA-256 checksum for an AEDB directory."""
    root = Path(path)
    digest = hashlib.sha256()
    for item in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(item.relative_to(root)).encode("utf-8"))
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def require_names(existing: Any, required: list[str], kind: str) -> None:
    """Raise a useful error when required names are absent."""
    names = set(existing.keys() if hasattr(existing, "keys") else existing)
    missing = [name for name in required if name not in names]
    if missing:
        raise ValueError(f"Missing {kind}: {', '.join(missing)}")

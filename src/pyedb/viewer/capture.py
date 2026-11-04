# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""One-shot source capture; every launch reads the current EDB session."""

from __future__ import annotations

from typing import Any, Callable


class SourceCapture:
    def __init__(self, loader: Callable[..., Any], progressive: bool = True) -> None:
        self.loader = loader
        self.progressive = progressive
        self.preview = None

    def set_preview(self, callback: Callable[..., Any] | None) -> None:
        if self.progressive:
            self.preview = callback

    def __call__(self, progress: Callable[[str, int, int], None] | None) -> Any:
        return self.loader(progress, preview=self.preview)

    def release_source(self) -> None:
        self.preview = self.loader = None

# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""One-shot source capture; every launch reads the current EDB session."""


class SourceCapture:
    def __init__(self, loader, progressive=True):
        self.loader = loader
        self.progressive = progressive
        self.preview = None

    def set_preview(self, callback):
        if self.progressive:
            self.preview = callback

    def __call__(self, progress):
        return self.loader(progress, preview=self.preview)

    def release_source(self):
        self.preview = self.loader = None

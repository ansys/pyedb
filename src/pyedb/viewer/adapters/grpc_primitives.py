# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Enumerate layout primitives through the pyedb gRPC layout."""


class PrimitiveReader:
    """Read all core primitives of a pyedb gRPC layout."""

    def __init__(self, edb):
        self.edb = edb

    def read(self):
        return [i for i in self.edb.layout.core.primitives if not i.net.is_null]

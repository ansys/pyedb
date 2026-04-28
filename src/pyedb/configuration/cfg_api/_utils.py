# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal helpers shared by the ``cfg_api`` package."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union


class _DictProxy:
    """Wrap a raw dictionary with a ``to_dict`` method.

    Some builder collections store either rich builder objects or already
    materialized dictionaries. This wrapper gives the latter the same
    ``to_dict`` surface so parent serializers can treat both cases uniformly.
    """

    def __init__(self, data: dict):
        self._data = data

    def to_dict(self) -> dict:
        """Return the wrapped dictionary unchanged.

        Returns
        -------
        dict
            Original dictionary payload.
        """
        return self._data



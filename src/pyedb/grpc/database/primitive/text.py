# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import Union

from ansys.edb.core.primitive.text import Text as CoreText

from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import Value


class Text(Primitive):
    def __init__(self, pedb, core=None):
        if core:
            self.core = core
            Primitive.__init__(self, pedb, core)
        self._pedb = pedb

    @classmethod
    def create(
        cls,
        layout,
        layer: Union[str, Layer] = None,
        center_x: float = None,
        center_y: float = None,
        text: str = None,
    ):
        if not layout:
            raise Exception("Layout not defined.")
        if not layer:
            raise ValueError("Layer must be provided to create a Text object.")
        if center_x is None or center_y is None:
            raise ValueError("Center x and y values must be provided to create a Text object.")
        if text is None:
            raise ValueError("Text value must be provided to create a Text object.")
        edb_object = CoreText.create(
            layout=layout.core,
            layer=layer,
            center_x=Value(center_x),
            center_y=Value(center_y),
            text=text,
        )
        new_text = cls(layout._pedb, edb_object)
        return new_text

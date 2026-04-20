# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyedb.generic.general_methods import ET
from pyedb.ipc2581.content.content import Content
from pyedb.ipc2581.content.fill import FillDesc


class DictionaryFill(Content):
    def __init__(self):
        self._dict_fill = {}

    @property
    def dict_fill(self):
        return self._dict_fill

    @dict_fill.setter
    def dict_fill(self, value):  # pragma no cover
        if isinstance(value, list):
            self._dict_fill = value

    def add_fill(self, value):  # pragma no cover
        if isinstance(value, FillDesc):
            self._dict_fill.append(value)

    def write_xml(self, content=None):  # pragma no cover
        if content:
            dict_fill = ET.SubElement(content, "DictionaryFillDesc")
            dict_fill.set("units", self.units)
            for fill in self._dict_fill.keys():
                self._dict_fill[fill].write_xml()

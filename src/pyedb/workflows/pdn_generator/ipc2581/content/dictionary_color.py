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
from pyedb.ipc2581.content.entry_color import EntryColor


class DictionaryColor(object):
    def __init__(self):
        self._dict_colors = []

    @property
    def dict_colors(self):
        return self._dict_colors

    @dict_colors.setter
    def dict_colors(self, value):  # pragma no cover
        if isinstance(value, list):
            self._dict_colors = value

    def add_color(self, name="", r=1, g=1, b=1):  # pragma no cover
        entry_color = EntryColor()
        entry_color.name = name
        entry_color.color.r = r
        entry_color.color.g = g
        entry_color.color.b = b
        self._dict_colors.append(entry_color)

    def write_xml(self, content=None):  # pragma no cover
        dict_color = ET.SubElement(content, "DictionaryColor")
        for _color in self.dict_colors:
            _color.write_xml(dict_color)

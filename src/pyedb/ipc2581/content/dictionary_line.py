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
from pyedb.ipc2581.content.entry_line import EntryLine


class DictionaryLine(object):
    def __init__(self, content):
        self._dict_lines = {}
        self.units = content.units

    @property
    def dict_lines(self):
        return self._dict_lines

    @dict_lines.setter
    def dict_lines(self, value):  # pragma no cover
        if isinstance(value, EntryLine):
            self._dict_lines = value

    def add_line(self, width=None):  # pragma no cover
        if width:
            line = EntryLine()
            line._line_width = width
            if not "ROUND_{}".format(width) in self._dict_lines:
                self._dict_lines["ROUND_{}".format(width)] = line

    def write_xml(self, content=None):  # pragma no cover
        dict_line = ET.SubElement(content, "DictionaryLineDesc")
        dict_line.set("units", self.units)
        for line in list(self._dict_lines.values()):
            line.write_xml(dict_line)

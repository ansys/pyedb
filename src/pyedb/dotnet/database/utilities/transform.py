# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pyedb.dotnet.database.utilities.obj_base import ObjBase


class Transform(ObjBase):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @classmethod
    def create(cls, pedb):
        return cls(pedb, pedb.core.Utility.Transform())

    @property
    def rotation(self):
        return self._pedb.value(self._edb_object.Rotation)

    @property
    def x_offset(self):
        return self._pedb.value(self._edb_object.XOffset)

    @property
    def y_offset(self):
        return self._pedb.value(self._edb_object.YOffset)

    @property
    def mirror(self):
        return self._edb_object.Mirror

    def set_rotation(self, rotation):
        return self._edb_object.SetRotationValue(self._pedb.value(rotation)._edb_object)

    def set_x_offset(self, x_offset):
        return self._edb_object.SetXOffsetValue(self._pedb.value(x_offset)._edb_object)

    def set_y_offset(self, y_offset):
        return self._edb_object.SetYOffsetValue(self._pedb.value(y_offset)._edb_object)

    def set_mirror(self, mirror:bool):
        return self._edb_object.SetMirror(mirror)
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


class WirebondDef:
    def __init__(self, edb, edb_object):
        self._edb_object = edb_object
        self._pedb = edb

    @property
    def name(self):
        return self._edb_object.GetName()

    def delete(self):
        self._edb_object.delete()

    @property
    def height(self):
        return self._edb_object.GetParameters().ToDouble()

    @height.setter
    def height(self, value: float):
        self._edb_object.SetParameters(self._pedb.edb_value(value))


class Jedec4BondwireDef(WirebondDef):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._edb_object = edb_object
        self._pedb = pedb

    @classmethod
    def find_by_name(cls, edb, name: str):
        jedec4_def = next((wb_def for wb_def in list(edb._db.Jedec4BondwireDefs) if wb_def.GetName() == name), None)
        if jedec4_def is None:
            return None
        return cls(edb, jedec4_def)

    @classmethod
    def create(cls, edb, name: str, top_to_die_distance: float = 30e-6):
        jedec4_def = edb._db.Jedec4BondwireDefs.Create(edb._db, name, edb.edb_value(top_to_die_distance))
        return cls(edb, jedec4_def)


class Jedec5BondwireDefs(WirebondDef):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._pedb = pedb
        self._edb_object = edb_object

    @classmethod
    def find_by_name(cls, edb, name: str):
        jedec4_def = next((wb_def for wb_def in list(edb._db.Jedec4BondwireDefs) if wb_def.GetName() == name), None)
        if jedec4_def is None:
            return None
        return cls(edb, jedec4_def)

    @classmethod
    def create(cls, edb, name: str, top_to_die_distance: float = 30e-6):
        jedec5_def = edb._db.Jedec5BondwireDefs.Create(edb._db, name, edb.edb_value(top_to_die_distance))
        return cls(edb, jedec5_def)


class ApdBondwireDef(WirebondDef):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._pedb = pedb
        self._edb_object = edb_object

    @classmethod
    def find_by_name(cls, edb, name: str):
        Apd_def = next((wb_def for wb_def in list(edb._db.ApdBondwireDefs) if wb_def.GetName() == name), None)
        if Apd_def is None:
            return None
        return cls(edb, Apd_def)

    @classmethod
    def create(cls, edb, name: str, top_to_die_distance: float = 30e-6):
        Apd_def = edb._db.ApdBondwireDefs.Create(edb._db, name, edb.edb_value(top_to_die_distance))
        return cls(edb, Apd_def)

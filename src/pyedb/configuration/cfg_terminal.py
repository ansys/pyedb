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

from enum import Enum

from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance


class CfgNegTerm:
    """Manage negative terminal."""

    class CfgTermType(Enum):
        """Terminal types."""

        pin = [list, str]
        net = [str]
        pin_group = [str]

    @property
    def pedb(self):
        """Edb."""
        return self.pport.pedb

    def __init__(self, pport, **kwargs):
        self.pport = pport
        self.type = kwargs.get("type", None)
        self.value = kwargs.get("value", None)

    def _get_candidates(self, distributed):
        """Get list of objects."""

        def get_pin_obj(pin_name):
            port_name = "{}_{}".format(self.pport.reference_designator, pin_name)
            return {port_name: self.pport.pdata.edb_comps[self.pport.reference_designator].pins[pin_name]}

        def get_pin_group_obj(pin_group_name):
            pin_group_obj = self.pedb.siwave.pin_groups[pin_group_name]
            return {pin_group_obj.name: pin_group_obj}

        term_objs = dict()
        if self.type in "pin":
            term_objs.update(get_pin_obj(self.value))
        elif self.type == "pin_group":
            term_objs.update(get_pin_group_obj(self.value))
        elif self.type == "net":
            pins = self.pport.pdata.pedb.components.get_pin_from_component(self.pport.reference_designator, self.value)
            pins = [EDBPadstackInstance(p, self.pedb) for p in pins]

            pin_objs = {f"{self.value}_{p.GetName()}": p for p in pins}
            if distributed:
                term_objs.update(pin_objs)
            else:
                pg_name = f"pg_{self.pport.reference_designator}_{self.value}"
                pin_objs = {p.GetName(): p for p in pin_objs.values()}
                if self.pport.type == "coax":
                    term_objs.update(get_pin_obj(pins[0].GetName()))
                else:
                    temp = self.pport.pdata.pedb.siwave.create_pin_group(
                        self.pport.reference_designator, list(pin_objs.keys()), pg_name
                    )
                    term_objs.update({temp[0]: temp[1]})
        return term_objs

    def get_candidates(self):
        """Get list of objects."""
        return self._get_candidates(False)


class CfgPosTerm(CfgNegTerm):
    """Manage positive terminal."""

    def __init__(self, pport, **kwargs):
        super().__init__(pport, **kwargs)

    def get_candidates(self):
        """Get list of objects."""
        return self._get_candidates(self.pport.distributed)

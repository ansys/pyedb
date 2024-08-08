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

import logging

from pyedb.dotnet.edb_core.cell.connectable import Connectable


class HierarchyObj(Connectable):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def component_def(self):
        """Component definition."""
        return self._edb_object.GetComponentDef().GetName()

    @property
    def location(self):
        """XY Coordinates."""
        flag, x, y = self._edb_object.GetLocation()
        if flag:
            return [x, y]
        else:  # pragma no cover
            logging.warning(f"Failed to get location of '{self.name}'.")
            return


class Group(HierarchyObj):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

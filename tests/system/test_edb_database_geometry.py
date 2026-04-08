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


import pytest

from tests import conftest
from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

if config["use_grpc"]:
    from pyedb.grpc.database.geometry.point_data import PointData
else:
    from pyedb.dotnet.database.geometry.point_data import PointData

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


# @pytest.mark.skipif(config["use_grpc"], reason="bug #2005")
@pytest.mark.usefixtures("close_rpc_session")
class TestPointData(BaseTestClass):
    def test_create(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["X"] = 1
        pdata = PointData.create(edbapp, "X", 2)
        assert str(pdata.x) == "X"
        assert pdata.x == 1
        assert pdata.y == 2

        pdata2 = PointData.create_arc_point(edbapp, "X")
        assert str(pdata2.arc_height) == "X"
        assert pdata2.arc_height == 1
        assert pdata2.is_arc

        edbapp.close(terminate_rpc_session=False)

    def test_operations(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["X"] = 1
        edbapp["Y"] = 2
        edbapp["angle"] = "90deg"
        pdata = PointData.create(edbapp, "X", "Y")
        pdata2 = pdata.rotate("angle", [1, 1])
        assert pdata2.x == pytest.approx(0)
        assert pdata2.y == pytest.approx(1)

        edbapp.close(terminate_rpc_session=False)

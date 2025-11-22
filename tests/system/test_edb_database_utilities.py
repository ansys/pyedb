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


import pytest

from tests import conftest
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestDatabaseUtilities(BaseTestClass):
    def test_value(self, edb_examples):
        edbapp = edb_examples.create_empty_edb()
        if conftest.config["use_grpc"]:
            edb_value = edbapp.core.utility.value.Value

        else:
            edb_value = edbapp.core.Utility.Value

        value = edbapp.value("1mm")
        value2 = edbapp.value(edb_value("1mm"))
        assert value == value2

        value = edbapp.value("1mm")
        value2 = edbapp.value("100um")
        assert value + value2 == pytest.approx(0.0011)
        assert str(value + value2) == "(1mm)+(100um)"

        assert "100um" + value == pytest.approx(0.0011)
        assert str("100um" + value) == "(100um)+(1mm)"

        assert value - value2 == pytest.approx(0.0009)
        assert str(value - value2) == "(1mm)-(100um)"

        assert "100um" - value == pytest.approx(-0.0009)
        assert str("100um" - value) == "(100um)-(1mm)"

        assert value * value2 == pytest.approx(1e-7)
        assert str(value * value2) == "(1mm)*(100um)"

        assert "100um" * value == pytest.approx(1e-7)
        assert str("100um" * value) == "(100um)*(1mm)"

        assert value / value2 == pytest.approx(10)
        assert str(value / value2) == "(1mm)/(100um)"

        assert "100um" / value == pytest.approx(0.1)
        assert str("100um" / value) == "(100um)/(1mm)"

        value = edbapp.value("4000mm")
        assert value == pytest.approx(4)
        assert str(value) == "4000mm"
        assert value + 1 == pytest.approx(5)
        value2 = value.sqrt()
        assert value2 == pytest.approx(2)
        assert str(value2) == "(4000mm)**0.5"

        value = edbapp.value("10mm")
        value2 = value.log10()
        assert value2 == pytest.approx(-2)
        assert str(value2) == "log10(10mm)"

        value = edbapp.value("pi/6")
        value2 = value.sin()
        assert value2 == pytest.approx(0.5)
        assert str(value2) == "sin(pi/6)"

        value = edbapp.value("pi/3")
        value2 = value.cos()
        assert value2 == pytest.approx(0.5)
        assert str(value2) == "cos(pi/3)"

        value = edbapp.value(1)
        value2 = value.asin()
        assert value2 == pytest.approx(1.570796327)

        value = edbapp.value(0)
        value2 = value.acos()
        assert value2 == pytest.approx(1.570796327)

        value = edbapp.value("pi/4")
        value2 = value.tan()
        assert value2 == pytest.approx(1)
        assert str(value2) == "tan(pi/4)"

        value = edbapp.value(1)
        value2 = value.atan()
        assert value2 == pytest.approx(0.785398163)

        edbapp.add_design_variable("var1", "1mm")
        value = edbapp.value("var1")
        value2 = value.sqrt()
        assert str(value2) == "(var1)**0.5"

        edbapp.close(terminate_rpc_session=False)

    pytest.skipif(conftest.config["use_grpc"], reason="Only applicable to dotnet.")

    def test_transform(self, edb_examples):
        edbapp = edb_examples.create_empty_edb()
        transform = edbapp.pedb_class.database.utilities.transform.Transform.create(edbapp)
        transform.rotation = "180deg"
        assert transform.rotation == pytest.approx(3.141592653589793)
        transform.offset_x = "1mm"
        assert transform.offset_x == pytest.approx(0.001)
        transform.offset_y = "1mm"
        assert transform.offset_y == pytest.approx(0.001)
        transform.mirror = True
        assert transform.mirror
        transform.scale = 2
        assert transform.scale == 2
        edbapp.close(terminate_rpc_session=False)

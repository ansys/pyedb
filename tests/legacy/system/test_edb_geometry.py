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


import pytest

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, edb_examples):
        edbapp = edb_examples.get_si_verse()
        path = edbapp.layout.find_primitive(name="line_272")[0]
        self.path_center_line_polygon_data = path.get_center_line_polygon_data()
        self.point_data = self.path_center_line_polygon_data.get_point(1)
        pass

    def test_point_data(self):
        assert isinstance(self.point_data.x_evaluated, float)
        assert isinstance(self.point_data.y_evaluated, float)
        self.point_data.x = "1mm"
        assert self.point_data.x == "1mm"

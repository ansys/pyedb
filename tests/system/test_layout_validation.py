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
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(cls, request, edb_examples):
        # Set up the EDB app once per class
        cls.edbapp_shared = edb_examples.get_si_verse()

        # Finalizer to close the EDB app after all tests
        def teardown():
            cls.edbapp_shared.close(terminate_rpc_session=True)

        request.addfinalizer(teardown)

    @pytest.fixture(autouse=True)
    def init(self, edb_examples):
        """init runs before each test."""
        pass

    @pytest.fixture(autouse=True)
    def teardown(self, request, edb_examples):
        """Code after yield runs after each teste."""
        yield
        pass

    @pytest.mark.skipif(reason="Test need to bre refactored")
    def test_disjoint_nets(self):
        self.edbapp_shared.layout_validation.disjoint_nets()

    @pytest.mark.skipif(reason="Test need to bre refactored")
    def test_dc_shorts(self):
        self.edbapp_shared.layout_validation.dc_shorts()

    @pytest.mark.skipif(reason="Test need to bre refactored")
    def test_fix_self_intersecting(self):
        self.edbapp_shared.layout_validation.fix_self_intersections()

    @pytest.mark.skipif(reason="Test need to bre refactored")
    def test_illegal_net_names(self):
        self.edbapp_shared.layout_validation.illegal_net_names()

    @pytest.mark.skipif(reason="Test need to bre refactored")
    def test_padstacks_no_name(self):
        self.edbapp_shared.layout_validation.padstacks_no_name()

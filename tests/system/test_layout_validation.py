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
        pass

        # Finalizer to close the EDB app after all tests
        def teardown():
            cls.edbapp_shared = edb_examples.get_si_verse()
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

    def test_disjoint_nets(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.disjoint_nets()
        edbapp.close(terminate_rpc_session=False)

    def test_dc_shorts(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.dc_shorts(fix=True)
        edbapp.close(terminate_rpc_session=False)

    def test_fix_self_intersecting(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.fix_self_intersections()
        edbapp.close(terminate_rpc_session=False)

    def test_illegal_net_names(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.illegal_net_names(fix=True)
        edbapp.close(terminate_rpc_session=False)

    def test_padstacks_no_name(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.padstacks_no_name(fix=True)
        edbapp.close(terminate_rpc_session=False)

    def test_padstacks_no_layer(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.illegal_rlc_values(fix=True)
        edbapp.close(terminate_rpc_session=False)

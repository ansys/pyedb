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

from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    @pytest.mark.skipif(True, reason="fails randomly.")
    def test_disjoint_nets(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.layout_validation.disjoint_nets()
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="fails randomly.")
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

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Not implemented with grpc")
    def test_empty_pin_groups(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        _, pg = edbapp.siwave.create_pin_group("U9", ["32", "33"])
        pg.remove_pins(["32", "33"])
        assert len(edbapp.siwave.pin_groups) == 1
        edbapp.layout_validation.delete_empty_pin_groups()
        assert len(edbapp.siwave.pin_groups) == 0
        edbapp.close(terminate_rpc_session=False)

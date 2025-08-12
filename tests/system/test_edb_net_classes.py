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

"""Tests related to Edb net classes
"""

import pytest

from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass(BaseTestClass):
    def test_net_classes_queries(self, edb_examples):
        """Evaluate net classes queries"""
        edbapp = edb_examples.get_si_verse()
        assert edbapp.net_classes.items
        assert edbapp.net_classes.create("DDR4_ADD", ["DDR4_A0", "DDR4_A1"])
        assert edbapp.net_classes["DDR4_ADD"].name == "DDR4_ADD"
        assert edbapp.net_classes["DDR4_ADD"].nets
        edbapp.net_classes["DDR4_ADD"].name = "DDR4_ADD_RENAMED"
        assert not edbapp.net_classes["DDR4_ADD_RENAMED"].is_null
        edbapp.close(terminate_rpc_session=False)

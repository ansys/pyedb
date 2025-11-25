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

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class BaseTestClass:
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(cls, request, edb_examples):
        # Set up the EDB app once per class

        # Finalizer to close the EDB app after all tests
        yield
        dummy_edb = edb_examples.create_empty_edb()
        dummy_edb.close(terminate_rpc_session=True)

    @pytest.fixture(autouse=True)
    def init(self, edb_examples):
        """init runs before each test."""
        return

    @pytest.fixture(autouse=True)
    def teardown(self, request, edb_examples):
        """Code after yield runs after each test."""
        yield
        return

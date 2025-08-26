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
from mock import MagicMock, PropertyMock, patch

from pyedb.dotnet.database.padstack import EdbPadstacks

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.padstacks = EdbPadstacks(MagicMock())

    # for padstack_def in list(self.definitions.values()):
    #         if padstack_def.hole_plating_ratio <= minimum_value_to_replace:
    #             padstack_def.hole_plating_ratio = default_plating_ratio
    #             self._logger.info(
    #                 "Padstack definition with zero plating ratio, defaulting to 20%".format(padstack_def.name)
    #             )
    # def test_132_via_plating_ratio_check(self):
    #     assert self.edbapp.padstacks.check_and_fix_via_plating()
    # minimum_value_to_replace=0.0, default_plating_ratio=0.2

    @patch("pyedb.dotnet.database.padstack.EdbPadstacks.definitions", new_callable=PropertyMock)
    def test_padstack_plating_ratio_fixing(self, mock_definitions):
        """Fix hole plating ratio."""
        mock_definitions.return_value = {
            "definition_0": MagicMock(hole_plating_ratio=-0.1),
            "definition_1": MagicMock(hole_plating_ratio=0.3),
        }
        assert self.padstacks["definition_0"].hole_plating_ratio == -0.1
        self.padstacks.check_and_fix_via_plating()
        assert self.padstacks["definition_0"].hole_plating_ratio == 0.2
        assert self.padstacks["definition_1"].hole_plating_ratio == 0.3

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

import json
from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_general import CfgGeneral

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


# ---------------------------------------------------------------------------
# GeneralConfig
# ---------------------------------------------------------------------------


class TestGeneralConfig:
    def test_defaults(self):
        g = CfgGeneral()
        assert g.spice_model_library == ""
        assert g.s_parameter_library == ""
        assert g.anti_pads_always_on is None
        assert g.suppress_pads is None

    def test_to_dict_empty(self):
        assert CfgGeneral().to_dict() == {}

    def test_to_dict_partial(self):
        g = CfgGeneral()
        g.spice_model_library = "/spice"
        d = g.to_dict()
        assert d == {"spice_model_library": "/spice"}

    def test_to_dict_full(self):
        g = CfgGeneral()
        g.spice_model_library = "/spice"
        g.s_parameter_library = "/snp"
        g.anti_pads_always_on = True
        g.suppress_pads = False
        d = g.to_dict()
        assert d["spice_model_library"] == "/spice"
        assert d["s_parameter_library"] == "/snp"
        assert d["anti_pads_always_on"] is True
        assert d["suppress_pads"] is False

    def test_anti_pads_false_preserved(self):
        g = CfgGeneral()
        g.anti_pads_always_on = False
        d = g.to_dict()
        # False (bool) must be kept – not omitted
        assert "anti_pads_always_on" in d
        assert d["anti_pads_always_on"] is False
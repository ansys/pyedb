# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_general import CfgGeneral

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestGeneralConfig:
    def test_to_dict_partial(self):
        g = CfgGeneral()
        g.spice_model_library = "/spice"
        d = g.get_parameters_from_edb()
        assert d == {"spice_model_library": "/spice"}

    def test_to_dict_full(self):
        g = CfgGeneral()
        g.spice_model_library = "/spice"
        g.s_parameter_library = "/snp"
        g.anti_pads_always_on = True
        g.suppress_pads = False
        d = g.get_parameters_from_edb()
        assert d["spice_model_library"] == "/spice"
        assert d["s_parameter_library"] == "/snp"
        assert d["anti_pads_always_on"] is True
        assert d["suppress_pads"] is False

    def test_anti_pads_false_preserved(self):
        g = CfgGeneral()
        g.anti_pads_always_on = False
        d = g.get_parameters_from_edb()
        # False (bool) must be kept – not omitted
        assert "anti_pads_always_on" in d
        assert d["anti_pads_always_on"] is False

    def test_defaults(self):
        g = CfgGeneral()
        assert g.spice_model_library == ""
        assert g.s_parameter_library == ""
        assert g.anti_pads_always_on is None
        assert g.suppress_pads is None

    def test_init_with_kwargs(self):
        g = CfgGeneral(spice_model_library="/spice", suppress_pads=True)
        assert g.spice_model_library == "/spice"
        assert g.suppress_pads is True

    def test_init_with_data_dict(self):
        g = CfgGeneral(data={"spice_model_library": "/spice", "anti_pads_always_on": True})
        assert g.spice_model_library == "/spice"
        assert g.anti_pads_always_on is True

    def test_init_data_overridden_by_kwargs(self):
        g = CfgGeneral(data={"spice_model_library": "/data"}, spice_model_library="/kwarg")
        assert g.spice_model_library == "/kwarg"

    def test_coerce_none_to_empty_string(self):
        """None passed for library fields is coerced to empty string."""
        g = CfgGeneral(spice_model_library=None)
        assert g.spice_model_library == ""

    def test_coerce_none_s_parameter(self):
        g = CfgGeneral(s_parameter_library=None)
        assert g.s_parameter_library == ""

    def test_model_dump_excludes_none(self):
        g = CfgGeneral(spice_model_library="/spice")
        d = g.model_dump(exclude_none=True)
        assert d["spice_model_library"] == "/spice"
        assert "anti_pads_always_on" not in d

    def test_model_dump_full(self):
        g = CfgGeneral(
            spice_model_library="/spice",
            s_parameter_library="/snp",
            anti_pads_always_on=True,
            suppress_pads=False,
        )
        d = g.model_dump(exclude_none=True)
        assert d["spice_model_library"] == "/spice"
        assert d["s_parameter_library"] == "/snp"
        assert d["anti_pads_always_on"] is True
        assert d["suppress_pads"] is False

    def test_bool_false_preserved_in_dump(self):
        """False bool values must not be omitted."""
        g = CfgGeneral(anti_pads_always_on=False)
        d = g.model_dump(exclude_none=True)
        assert "anti_pads_always_on" in d
        assert d["anti_pads_always_on"] is False

    def test_get_parameters_from_edb_without_pedb_empty(self):
        g = CfgGeneral()
        d = g.get_parameters_from_edb()
        assert d == {}

    def test_get_parameters_from_edb_without_pedb_with_values(self):
        g = CfgGeneral(spice_model_library="/spice", anti_pads_always_on=True)
        d = g.get_parameters_from_edb()
        assert d["spice_model_library"] == "/spice"
        assert d["anti_pads_always_on"] is True
        assert "s_parameter_library" not in d  # empty string excluded

    def test_get_data_from_db_without_pedb(self):
        g = CfgGeneral(suppress_pads=True)
        d = g.get_data_from_db()
        assert d["suppress_pads"] is True

    def test_apply_without_pedb(self):
        """apply() with no pedb is a no-op — should not raise."""
        g = CfgGeneral(anti_pads_always_on=True)
        g.apply()  # no error

    def test_set_parameters_to_edb_anti_pads(self):
        mock_pedb = MagicMock()
        g = CfgGeneral(pedb=mock_pedb, anti_pads_always_on=True)
        g.set_parameters_to_edb()
        assert mock_pedb.design_options.anti_pads_always_on is True

    def test_set_parameters_to_edb_suppress_pads(self):
        mock_pedb = MagicMock()
        g = CfgGeneral(pedb=mock_pedb, suppress_pads=False)
        g.set_parameters_to_edb()
        assert mock_pedb.design_options.suppress_pads is False

    def test_set_parameters_to_edb_skips_none(self):
        """Fields that are None must not be written to EDB."""
        mock_pedb = MagicMock()
        g = CfgGeneral(pedb=mock_pedb)  # all None
        g.set_parameters_to_edb()
        mock_pedb.design_options.anti_pads_always_on  # not assigned
        assert not hasattr(mock_pedb.design_options, "_mock_calls") or all(
            "anti_pads_always_on" not in str(c)
            for c in mock_pedb.design_options.mock_calls
            if "anti_pads_always_on" not in str(c)
        )

    def test_apply_calls_set_parameters(self):
        mock_pedb = MagicMock()
        g = CfgGeneral(pedb=mock_pedb, suppress_pads=True)
        g.apply()
        assert mock_pedb.design_options.suppress_pads is True

    def test_extra_fields_ignored(self):
        """extra='ignore' — unknown keys must not raise."""
        g = CfgGeneral(unknown_field="value")
        assert not hasattr(g, "unknown_field")

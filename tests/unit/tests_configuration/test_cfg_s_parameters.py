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

import pytest

from pyedb.configuration.cfg_s_parameter_models import CfgSParameterModel, CfgSParameters

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgSParameterModel:
    def test_basic(self):
        m = CfgSParameterModel(name="model1", component_definition="CAP_100nF", file_path="/path/c.s2p")
        d = m.model_dump()
        assert d["name"] == "model1"
        assert d["component_definition"] == "CAP_100nF"
        assert d["file_path"] == "/path/c.s2p"
        assert d["apply_to_all"] is True

    def test_with_components(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", apply_to_all=False, components=["C1", "C2"]
        )
        d = m.model_dump()
        assert d["apply_to_all"] is False
        assert d["components"] == ["C1", "C2"]

    def test_reference_net_per_component(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", reference_net_per_component={"C1": "GND1"}
        )
        d = m.model_dump()
        assert d["reference_net_per_component"] == {"C1": "GND1"}

    def test_pin_order(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p", pin_order=["1", "2"])
        assert m.model_dump()["pin_order"] == ["1", "2"]

    def test_pin_order_none_by_default(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p")
        assert m.model_dump()["pin_order"] is None

    def test_no_pin_order_key_when_none(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p")
        assert "pin_order" not in m.model_dump(exclude_none=True)


class TestCfgSParameters:
    def test_empty(self):
        sc = CfgSParameters()
        assert sc.models == []

    def test_add(self):
        sc = CfgSParameters()
        m = sc.add("model1", "CAP", "f.s2p")
        assert isinstance(m, CfgSParameterModel)
        assert sc.models[0].name == "model1"

    def test_add_returns_model_with_correct_fields(self):
        sc = CfgSParameters()
        m = sc.add("m1", "DEF", "f.s2p", reference_net="GND", apply_to_all=False, components=["C1"])
        assert m.reference_net == "GND"
        assert m.apply_to_all is False
        assert m.components == ["C1"]

    def test_get_data_from_db_no_pedb(self):
        sc = CfgSParameters()
        sc.add("m1", "DEF", "f.s2p")
        result = sc.get_data_from_db([])
        assert isinstance(result, list)
        assert result[0]["name"] == "m1"

    def test_s_parameters_models_deprecated_property(self):
        """s_parameters_models is a deprecated alias for models."""
        import warnings

        sc = CfgSParameters()
        sc.add("m1", "DEF", "f.s2p")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            models = sc.s_parameters_models
        assert models is sc.models

    def test_s_parameters_models_setter(self):
        """s_parameters_models setter assigns to models."""
        import warnings

        sc = CfgSParameters()
        new_models = [CfgSParameterModel(name="x", component_definition="D", file_path="f.s2p")]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sc.s_parameters_models = new_models
        assert sc.models is new_models

    def test_to_list(self):
        sc = CfgSParameters()
        sc.add("m1", "DEF", "f.s2p")
        result = sc.to_list()
        assert isinstance(result, list)
        assert result[0]["name"] == "m1"

    def test_apply_with_pedb_apply_to_all(self):
        from unittest.mock import MagicMock

        mock_comp1 = MagicMock()
        mock_comp2 = MagicMock()
        mock_comp_def = MagicMock()
        mock_comp_def.components = {"C1": mock_comp1, "C2": mock_comp2}
        mock_pedb = MagicMock()
        mock_pedb.definitions.component = {"CAP_100nF": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb, path_lib="/lib")
        m = sc.add("cap_model", "CAP_100nF", "/abs/f.s2p", reference_net="GND", apply_to_all=True)
        sc.apply()
        mock_comp_def.add_n_port_model.assert_called_once_with("/abs/f.s2p", "cap_model")
        mock_comp1.use_s_parameter_model.assert_called_once_with("cap_model", reference_net="GND")
        mock_comp2.use_s_parameter_model.assert_called_once_with("cap_model", reference_net="GND")

    def test_apply_with_pedb_selective_components(self):
        from unittest.mock import MagicMock

        mock_comp1 = MagicMock()
        mock_comp2 = MagicMock()
        mock_comp_def = MagicMock()
        mock_comp_def.components = {"C1": mock_comp1, "C2": mock_comp2}
        mock_pedb = MagicMock()
        mock_pedb.definitions.component = {"CAP": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb)
        sc.add("m1", "CAP", "/abs/f.s2p", reference_net="GND", apply_to_all=False, components=["C1"])
        sc.apply()
        mock_comp1.use_s_parameter_model.assert_called_once()
        mock_comp2.use_s_parameter_model.assert_not_called()

    def test_apply_with_pin_order(self):
        from unittest.mock import MagicMock

        mock_comp = MagicMock()
        mock_comp_def = MagicMock()
        mock_comp_def.components = {"C1": mock_comp}
        mock_pedb = MagicMock()
        mock_pedb.definitions.component = {"CAP": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb)
        sc.add("m1", "CAP", "/abs/f.s2p", apply_to_all=True, pin_order=["1", "2"])
        sc.apply()
        mock_comp_def.set_properties.assert_called_once_with(pin_order=["1", "2"])

    def test_apply_with_reference_net_per_component(self):
        from unittest.mock import MagicMock

        mock_comp1 = MagicMock()
        mock_comp_def = MagicMock()
        mock_comp_def.components = {"C1": mock_comp1}
        mock_pedb = MagicMock()
        mock_pedb.definitions.component = {"CAP": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb)
        sc.add(
            "m1",
            "CAP",
            "/abs/f.s2p",
            reference_net="GND",
            apply_to_all=True,
            reference_net_per_component={"C1": "AGND"},
        )
        sc.apply()
        mock_comp1.use_s_parameter_model.assert_called_once_with("m1", reference_net="AGND")

    def test_apply_relative_path_resolved(self):
        from unittest.mock import MagicMock

        mock_comp = MagicMock()
        mock_comp_def = MagicMock()
        mock_comp_def.components = {"C1": mock_comp}
        mock_pedb = MagicMock()
        mock_pedb.definitions.component = {"CAP": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb, path_lib="/lib/models")
        sc.add("m1", "CAP", "f.s2p", apply_to_all=True)
        sc.apply()
        called_path = mock_comp_def.add_n_port_model.call_args[0][0]
        assert "lib" in called_path and "f.s2p" in called_path

    def test_get_data_from_db_with_pedb(self):
        from unittest.mock import MagicMock

        mock_model_obj = MagicMock()
        mock_model_obj.reference_file = "/f.s2p"
        mock_comp_def = MagicMock()
        mock_comp_def.component_models = {"m1": mock_model_obj}
        mock_comp_def.get_properties.return_value = {"pin_order": None}
        mock_pedb = MagicMock()
        mock_pedb.definitions.components = {"CAP": mock_comp_def}
        sc = CfgSParameters(pedb=mock_pedb)
        cfg_components = [
            {
                "reference_designator": "C1",
                "definition": "CAP",
                "s_parameter_model": {"model_name": "m1", "reference_net": "GND"},
            }
        ]
        result = sc.get_data_from_db(cfg_components)
        assert isinstance(result, list)
        assert result[0]["name"] == "m1"
        assert result[0]["components"] == ["C1"]

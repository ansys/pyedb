# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Unit tests for wirebond_def, utility/layer_map, and definition/component_model (no EDB license)."""

from unittest.mock import MagicMock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
class TestBondwireDef:
    def _make(self):
        from pyedb.grpc.database.definition.wirebond_def import BondwireDef

        core = MagicMock()
        name_mock = MagicMock()
        name_mock.value = "bw1"
        core.name = name_mock
        pedb = MagicMock()
        pedb.value.side_effect = lambda x: x
        return BondwireDef(pedb, core), core, pedb

    def test_name_get(self):
        bd, core, _ = self._make()
        assert bd.name == "bw1"

    def test_name_set(self):
        bd, core, pedb = self._make()
        bd.name = "new_bw"
        pedb.value.assert_called_once_with("new_bw")

    def test_delete(self):
        bd, core, _ = self._make()
        bd.delete()
        core.delete.assert_called_once()


@pytest.mark.grpc
class TestJedec4BondwireDef:
    def _make(self):
        from pyedb.grpc.database.definition.wirebond_def import Jedec4BondwireDef

        core = MagicMock()
        result_mock = MagicMock()
        result_mock.value = 0.05
        core.get_parameters.return_value = result_mock
        pedb = MagicMock()
        pedb.value.side_effect = lambda x: x
        return Jedec4BondwireDef(pedb, core), core, pedb

    def test_get_parameters(self):
        bd, core, _ = self._make()
        assert bd.get_parameters() == pytest.approx(0.05)

    def test_height_get(self):
        bd, core, _ = self._make()
        assert bd.height == pytest.approx(0.05)

    def test_set_parameters(self):
        bd, core, pedb = self._make()
        bd.set_parameters(0.1)
        core.set_parameters.assert_called_once_with(0.1)

    def test_height_set(self):
        bd, core, pedb = self._make()
        bd.height = 0.2
        core.set_parameters.assert_called_once_with(0.2)

    def test_find_by_name_returns_none_when_null(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.wirebond_def import Jedec4BondwireDef

        edb = MagicMock()
        with patch("pyedb.grpc.database.definition.wirebond_def.CoreJedec4BondwireDef") as MockCore:
            null_core = MagicMock()
            null_core.is_null = True
            MockCore.find_by_name.return_value = null_core
            result = Jedec4BondwireDef.find_by_name(edb, "nonexistent")
            assert result is None

    def test_find_by_name_returns_instance_when_found(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.wirebond_def import Jedec4BondwireDef

        edb = MagicMock()
        with patch("pyedb.grpc.database.definition.wirebond_def.CoreJedec4BondwireDef") as MockCore:
            found_core = MagicMock()
            found_core.is_null = False
            MockCore.find_by_name.return_value = found_core
            result = Jedec4BondwireDef.find_by_name(edb, "bw1")
            assert isinstance(result, Jedec4BondwireDef)


@pytest.mark.grpc
class TestJedec5BondwireDef:
    def _make(self):
        from pyedb.grpc.database.definition.wirebond_def import Jedec5BondwireDef

        core = MagicMock()
        h_mock = MagicMock()
        h_mock.value = 0.05
        angle1_mock = MagicMock()
        angle1_mock.value = 30.0
        angle2_mock = MagicMock()
        angle2_mock.value = 45.0
        core.get_parameters.return_value = [h_mock, angle1_mock, angle2_mock]
        pedb = MagicMock()
        pedb.value.side_effect = lambda x: x
        return Jedec5BondwireDef(pedb, core), core, pedb

    def test_get_parameters(self):
        bd, core, _ = self._make()
        h, a1, a2 = bd.get_parameters()
        assert h == pytest.approx(0.05)
        assert a1 == pytest.approx(30.0)
        assert a2 == pytest.approx(45.0)

    def test_height_get(self):
        bd, core, _ = self._make()
        assert bd.height == pytest.approx(0.05)

    def test_height_set(self):
        bd, core, pedb = self._make()
        bd.height = 0.1
        core.set_parameters.assert_called_once_with(0.1, 30.0, 45.0)

    def test_set_parameters(self):
        bd, core, pedb = self._make()
        bd.set_parameters(0.1, 20.0, 35.0)
        core.set_parameters.assert_called_once_with(0.1, 20.0, 35.0)

    def test_find_by_name_returns_none(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.wirebond_def import Jedec5BondwireDef

        edb = MagicMock()
        with patch("pyedb.grpc.database.definition.wirebond_def.CoreJedec5BondwireDef") as MockCore:
            null_core = MagicMock()
            null_core.is_null = True
            MockCore.find_by_name.return_value = null_core
            result = Jedec5BondwireDef.find_by_name(edb, "nonexistent")
            assert result is None


@pytest.mark.grpc
class TestApdBondwireDef:
    def _make(self):
        from pyedb.grpc.database.definition.wirebond_def import ApdBondwireDef

        core = MagicMock()
        result_mock = MagicMock()
        result_mock.value = "bwd_block_data"
        core.get_parameters.return_value = result_mock
        pedb = MagicMock()
        return ApdBondwireDef(pedb, core), core, pedb

    def test_height_raises(self):
        bd, _, _ = self._make()
        with pytest.raises(AttributeError):
            _ = bd.height

    def test_height_setter_raises(self):
        bd, _, _ = self._make()
        with pytest.raises(AttributeError):
            bd.height = 0.1

    def test_get_parameters(self):
        bd, core, _ = self._make()
        assert bd.get_parameters() == "bwd_block_data"

    def test_parameter_block_get(self):
        bd, core, _ = self._make()
        assert bd.parameter_block == "bwd_block_data"

    def test_parameter_block_set(self):
        bd, core, _ = self._make()
        bd.parameter_block = "new_block"
        core.set_parameters.assert_called_once_with("new_block")

    def test_set_parameters(self):
        bd, core, _ = self._make()
        bd.set_parameters("block_xyz")
        core.set_parameters.assert_called_once_with("block_xyz")

    def test_find_by_name_returns_none(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.wirebond_def import ApdBondwireDef

        edb = MagicMock()
        with patch("pyedb.grpc.database.definition.wirebond_def.CoreApdBondwireDef") as MockCore:
            null_core = MagicMock()
            null_core.is_null = True
            MockCore.find_by_name.return_value = null_core
            result = ApdBondwireDef.find_by_name(edb, "nonexistent")
            assert result is None

    def test_find_by_name_returns_instance(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.wirebond_def import ApdBondwireDef

        edb = MagicMock()
        with patch("pyedb.grpc.database.definition.wirebond_def.CoreApdBondwireDef") as MockCore:
            found_core = MagicMock()
            found_core.is_null = False
            MockCore.find_by_name.return_value = found_core
            result = ApdBondwireDef.find_by_name(edb, "apd1")
            assert isinstance(result, ApdBondwireDef)


@pytest.mark.grpc
class TestNPortComponentModel:
    def _make(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.component_model import NPortComponentModel

        mock_core_class = MagicMock()
        mock_core_instance = MagicMock()
        mock_core_instance.is_null = False
        mock_core_instance.name = "nport_1"
        mock_core_instance.reference_file = "model.s4p"
        mock_core_class.return_value = mock_core_instance

        with patch("pyedb.grpc.database.definition.component_model.CoreComponentModel", mock_core_class):
            raw = MagicMock()
            raw.msg = "msg_stub"
            obj = NPortComponentModel(raw)

        obj.core = mock_core_instance
        return obj, mock_core_instance

    def test_is_null(self):
        obj, core = self._make()
        assert obj.is_null is False

    def test_name(self):
        obj, core = self._make()
        assert obj.name == "nport_1"

    def test_reference_file(self):
        obj, core = self._make()
        assert obj.reference_file == "model.s4p"

    def test_find_by_id_returns_none_when_null(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.component_model import NPortComponentModel

        comp_def = MagicMock()
        with patch("pyedb.grpc.database.definition.component_model.CoreNPortComponentModel") as MockCore:
            null_model = MagicMock()
            null_model.is_null = True
            MockCore.find_by_id.return_value = null_model
            result = NPortComponentModel.find_by_id(comp_def, 1)
            assert result is None

    def test_find_by_name_returns_none_when_null(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.component_model import NPortComponentModel

        comp_def = MagicMock()
        with patch("pyedb.grpc.database.definition.component_model.CoreNPortComponentModel") as MockCore:
            null_model = MagicMock()
            null_model.is_null = True
            MockCore.find_by_name.return_value = null_model
            result = NPortComponentModel.find_by_name(comp_def, "nonexistent")
            assert result is None

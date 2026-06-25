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

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

pytest.importorskip("pyedb.dotnet.database.stackup", reason="Requires .NET runtime")
from pyedb.dotnet.database.stackup import Stackup

pytestmark = [pytest.mark.unit]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.stackup = Stackup(MagicMock())

    def test_stackup_int_to_layer_types(self):
        """Evaluate mapping from integer to layer type."""
        signal_layer = self.stackup._int_to_layer_types(0)
        assert signal_layer == self.stackup.layer_types.SignalLayer
        dielectric_layer = self.stackup._int_to_layer_types(1)
        assert dielectric_layer == self.stackup.layer_types.DielectricLayer
        conducting_layer = self.stackup._int_to_layer_types(2)
        assert conducting_layer == self.stackup.layer_types.ConductingLayer
        airlines_layer = self.stackup._int_to_layer_types(3)
        assert airlines_layer == self.stackup.layer_types.AirlinesLayer
        errors_layer = self.stackup._int_to_layer_types(4)
        assert errors_layer == self.stackup.layer_types.ErrorsLayer
        symbol_layer = self.stackup._int_to_layer_types(5)
        assert symbol_layer == self.stackup.layer_types.SymbolLayer
        measure_layer = self.stackup._int_to_layer_types(6)
        assert measure_layer == self.stackup.layer_types.MeasureLayer
        assembly_layer = self.stackup._int_to_layer_types(8)
        assert assembly_layer == self.stackup.layer_types.AssemblyLayer
        silkscreen_layer = self.stackup._int_to_layer_types(9)
        assert silkscreen_layer == self.stackup.layer_types.SilkscreenLayer
        solder_mask_layer = self.stackup._int_to_layer_types(10)
        assert solder_mask_layer == self.stackup.layer_types.SolderMaskLayer
        solder_paste_layer = self.stackup._int_to_layer_types(11)
        assert solder_paste_layer == self.stackup.layer_types.SolderPasteLayer
        glue_layer = self.stackup._int_to_layer_types(12)
        assert glue_layer == self.stackup.layer_types.GlueLayer
        wirebond_layer = self.stackup._int_to_layer_types(13)
        assert wirebond_layer == self.stackup.layer_types.WirebondLayer
        user_layer = self.stackup._int_to_layer_types(14)
        assert user_layer == self.stackup.layer_types.UserLayer
        siwave_hfss_solver_regions = self.stackup._int_to_layer_types(16)
        assert siwave_hfss_solver_regions == self.stackup.layer_types.SIwaveHFSSSolverRegions
        outline_layer = self.stackup._int_to_layer_types(18)
        assert outline_layer == self.stackup.layer_types.OutlineLayer

    def test_stackup_layer_types_to_int(self):
        """Evaluate mapping from layer type to int."""
        signal_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.SignalLayer)
        assert signal_layer == 0
        dielectric_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.DielectricLayer)
        assert dielectric_layer == 1
        conducting_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.ConductingLayer)
        assert conducting_layer == 2
        airlines_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.AirlinesLayer)
        assert airlines_layer == 3
        errors_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.ErrorsLayer)
        assert errors_layer == 4
        symbol_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.SymbolLayer)
        assert symbol_layer == 5
        measure_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.MeasureLayer)
        assert measure_layer == 6
        assembly_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.AssemblyLayer)
        assert assembly_layer == 8
        silkscreen_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.SilkscreenLayer)
        assert silkscreen_layer == 9
        solder_mask_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.SolderMaskLayer)
        assert solder_mask_layer == 10
        solder_paste_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.SolderPasteLayer)
        assert solder_paste_layer == 11
        glue_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.GlueLayer)
        assert glue_layer == 12
        wirebond_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.WirebondLayer)
        assert wirebond_layer == 13
        user_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.UserLayer)
        assert user_layer == 14
        siwave_hfss_solver_regions = self.stackup._layer_types_to_int(self.stackup.layer_types.SIwaveHFSSSolverRegions)
        assert siwave_hfss_solver_regions == 16
        outline_layer = self.stackup._layer_types_to_int(self.stackup.layer_types.OutlineLayer)
        assert outline_layer == 18

    @patch("pyedb.dotnet.database.stackup.Stackup.layers", new_callable=PropertyMock)
    def test_110_layout_tchickness(self, mock_stackup_layers):
        """"""
        mock_stackup_layers.return_value = {"layer": MagicMock(upper_elevation=42, lower_elevation=0)}
        assert self.stackup.get_layout_thickness() == 42
        mock_stackup_layers.return_value = {"layer": MagicMock(upper_elevation=0, lower_elevation=0)}
        assert self.stackup.get_layout_thickness() == 0


@pytest.mark.grpc
class TestGrpcStackupUnit:
    """Unit tests for grpc Stackup that can run without a live EDB server."""

    def _make_grpc_stackup(self):
        """Create a minimal grpc Stackup with a mocked pedb and core."""
        from pyedb.grpc.database.stackup import Stackup as GrpcStackup

        pedb = MagicMock()
        pedb.logger = MagicMock()
        core = MagicMock()
        stackup = GrpcStackup.__new__(GrpcStackup)
        stackup._pedb = pedb
        stackup.core = core
        # Provide a minimal layer_collection
        from pyedb.grpc.database.stackup import LayerCollection

        lc = LayerCollection.__new__(LayerCollection)
        lc.core = core
        lc._pedb = pedb
        stackup.layer_collection = lc
        return stackup

    def test_grpc_get_layout_thickness_multiple_layers(self):
        """get_layout_thickness returns difference between top upper and bottom lower elevation."""
        stackup = self._make_grpc_stackup()
        layer_a = MagicMock()
        layer_a.lower_elevation = 0.0
        layer_a.upper_elevation = 35e-6
        layer_b = MagicMock()
        layer_b.lower_elevation = 100e-6
        layer_b.upper_elevation = 135e-6
        with patch.object(type(stackup), "layers", new_callable=PropertyMock) as mock_layers:
            mock_layers.return_value = {"A": layer_a, "B": layer_b}
            thickness = stackup.get_layout_thickness()
        assert abs(thickness - 135e-6) < 1e-12

    def test_grpc_get_layout_thickness_empty(self):
        """get_layout_thickness returns 0 when there are no layers."""
        stackup = self._make_grpc_stackup()
        with patch.object(type(stackup), "layers", new_callable=PropertyMock) as mock_layers:
            mock_layers.return_value = {}
            thickness = stackup.get_layout_thickness()
        assert thickness == 0

    def test_grpc_thickness_property_calls_get_layout_thickness(self):
        """thickness property should delegate to get_layout_thickness."""
        stackup = self._make_grpc_stackup()
        with patch.object(stackup, "get_layout_thickness", return_value=42.0) as mock_method:
            result = stackup.thickness
        mock_method.assert_called_once()
        assert result == 42.0

    def test_grpc_num_layers_counts_layers(self):
        """num_layers returns the count of stackup layers."""
        stackup = self._make_grpc_stackup()
        layer_a = MagicMock()
        layer_b = MagicMock()
        with patch.object(type(stackup), "layers", new_callable=PropertyMock) as mock_layers:
            mock_layers.return_value = {"A": layer_a, "B": layer_b}
            assert stackup.num_layers == 2

    def test_grpc_mode_getter(self):
        """mode property returns the string name of the core mode in lowercase."""
        stackup = self._make_grpc_stackup()
        stackup.core.mode.name = "LAMINATE"
        assert stackup.mode == "laminate"

    def test_grpc_export_unsupported_format_returns_false(self):
        """export returns False for an unsupported file format."""
        stackup = self._make_grpc_stackup()
        result = stackup.export("output.txt")
        assert result is False

    def test_grpc_load_unsupported_format_returns_false(self):
        """load returns False for an unsupported file extension."""
        stackup = self._make_grpc_stackup()
        result = stackup.load("output.unsupported")
        assert result is False

    def test_grpc_load_from_xml_delegates_to_load(self):
        """load_from_xml delegates to load."""
        stackup = self._make_grpc_stackup()
        with patch.object(stackup, "load", return_value=True) as mock_load:
            result = stackup.load_from_xml("stackup.xml")
        mock_load.assert_called_once_with("stackup.xml")
        assert result is True

    def test_grpc_load_dict_calls_import_dict(self):
        """load with a dict argument calls _import_dict."""
        stackup = self._make_grpc_stackup()
        with patch.object(stackup, "_import_dict", return_value=True) as mock_import:
            result = stackup.load({"layers": {}})
        mock_import.assert_called_once()
        assert result is True

    def test_grpc_add_outline_layer_delegates_to_add_layer(self):
        """add_outline_layer delegates to add_layer with layer_type 'outline'."""
        stackup = self._make_grpc_stackup()
        with patch.object(stackup, "add_layer", return_value=True) as mock_add:
            stackup.add_outline_layer()
        mock_add.assert_called_once_with(layer_name="Outline", layer_type="outline")

    def test_grpc_create_symmetric_stackup_odd_count_returns_false(self):
        """create_symmetric_stackup returns False for odd layer count."""
        stackup = self._make_grpc_stackup()
        result = stackup.create_symmetric_stackup(3)
        assert result is False

    def test_grpc_null_safe_layer_cast_returns_self_on_is_null(self):
        """_null_safe_layer_cast returns self when layer is_null."""
        from pyedb.grpc.database.stackup import _null_safe_layer_cast

        mock_layer = MagicMock()
        mock_layer.is_null = True
        result = _null_safe_layer_cast(mock_layer)
        assert result is mock_layer

    def test_grpc_null_safe_layer_cast_returns_self_on_exception(self):
        """_null_safe_layer_cast returns self when is_null raises an exception."""
        from pyedb.grpc.database.stackup import _null_safe_layer_cast

        mock_layer = MagicMock()
        type(mock_layer).is_null = PropertyMock(side_effect=Exception("Cannot access"))
        result = _null_safe_layer_cast(mock_layer)
        assert result is mock_layer

    def test_grpc_get_layers_filters_null(self):
        """_get_layers skips layers where is_null is True."""
        stackup = self._make_grpc_stackup()
        good_layer = MagicMock()
        good_layer.is_null = False
        bad_layer = MagicMock()
        bad_layer.is_null = True
        stackup.core.get_layers.return_value = [good_layer, bad_layer]
        result = stackup._get_layers(MagicMock())
        assert len(result) == 1
        assert result[0] is good_layer

    def test_grpc_get_layers_returns_empty_on_exception(self):
        """_get_layers returns empty list when get_layers raises an exception."""
        stackup = self._make_grpc_stackup()
        stackup.core.get_layers.side_effect = Exception("gRPC error")
        result = stackup._get_layers(MagicMock())
        assert result == []

    def test_grpc_all_layers_merges_stackup_and_non_stackup(self):
        """all_layers merges layers and non_stackup_layers dicts."""
        stackup = self._make_grpc_stackup()
        layer_a = MagicMock()
        layer_b = MagicMock()
        with (
            patch.object(type(stackup), "layers", new_callable=PropertyMock) as mock_layers,
            patch.object(type(stackup), "non_stackup_layers", new_callable=PropertyMock) as mock_non_stackup,
        ):
            mock_layers.return_value = {"A": layer_a}
            mock_non_stackup.return_value = {"B": layer_b}
            all_l = stackup.all_layers
        assert "A" in all_l
        assert "B" in all_l

    def test_grpc_getitem_returns_none_for_unknown_layer(self):
        """__getitem__ returns None for an unknown layer name."""
        stackup = self._make_grpc_stackup()
        with (
            patch.object(type(stackup), "layers", new_callable=PropertyMock) as mock_layers,
            patch.object(type(stackup), "non_stackup_layers", new_callable=PropertyMock) as mock_non_stackup,
        ):
            mock_layers.return_value = {}
            mock_non_stackup.return_value = {}
            result = stackup["unknown_layer"]
        assert result is None

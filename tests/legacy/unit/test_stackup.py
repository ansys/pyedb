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

from mock import MagicMock, PropertyMock, patch
import pytest

from pyedb.dotnet.database.stackup import Stackup

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


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

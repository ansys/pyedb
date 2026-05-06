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

import pytest

from pyedb.dotnet.database.edb_data.sources import SourceBuilder
from pyedb.grpc.database.inner.layout_obj import (
    HorizontalWavePortProperty,
    parse_horizontal_wave_port_string,
)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    # @pytest.fixture(autouse=True)
    # def init(self,local_scratch,):
    #     self.local_scratch = local_scratch

    def test_source_change_values(self):
        """Create source and change its values"""
        source = SourceBuilder()
        source.l_value = 1e-9
        assert source.l_value == 1e-9
        source.r_value = 1.3
        assert source.r_value == 1.3
        source.c_value = 1e-13
        assert source.c_value == 1e-13
        source.create_physical_resistor = True
        assert source.create_physical_resistor

    def test_create_with_multiple_vias(self):
        """Test creating a property with multiple vias."""
        prop = HorizontalWavePortProperty(
            port_type="Pad Port",
            arms=2,
            hfss_last_type=8,
            port_names=("pos_via", "neg_via"),
            horizontal_wave_primary=True,
            is_gap_source=True,
        )

        assert prop.port_type == "Pad Port"
        assert prop.arms == 2
        assert prop.hfss_last_type == 8
        assert prop.port_names == ("pos_via", "neg_via")
        assert prop.horizontal_wave_primary is True
        assert prop.is_gap_source is True

    def test_serialize_to_string(self):
        """Test serializing to string format."""
        prop = HorizontalWavePortProperty(
            port_type="Pad Port",
            arms=2,
            hfss_last_type=8,
            port_names=("pos_via", "neg_via"),
            horizontal_wave_primary=True,
            is_gap_source=True,
        )

        result = prop.to_property_string()
        assert isinstance(result, str)
        assert "Type='Pad Port'" in result
        assert "Arms=2" in result
        assert "HFSSLastType=8" in result
        assert "HorizWavePort('pos_via', 'neg_via')" in result
        assert "HorizWavePrimary=true" in result
        assert "IsGapSource=true" in result

    def test_parse_from_string(self):
        """Test parsing from string format."""
        input_str = (
            "$begin ''\n"
            "\tType='Pad Port'\n"
            "\tArms=2\n"
            "\tHFSSLastType=8\n"
            "\tHorizWavePort('pos_via', 'neg_via')\n"
            "\tHorizWavePrimary=true\n"
            "\tIsGapSource=true\n"
            "$end ''\n"
        )

        parsed = parse_horizontal_wave_port_string(input_str)

        assert parsed.port_type == "Pad Port"
        assert parsed.arms == 2
        assert parsed.hfss_last_type == 8
        assert parsed.port_names == ("pos_via", "neg_via")
        assert parsed.horizontal_wave_primary is True
        assert parsed.is_gap_source is True

    def test_roundtrip(self):
        """Test serializing and then parsing back."""
        original = HorizontalWavePortProperty(
            port_type="Pad Port",
            arms=2,
            hfss_last_type=8,
            port_names=("pos_via_name", "neg_via_name"),
            horizontal_wave_primary=True,
            is_gap_source=True,
        )

        # Serialize to string
        serialized = original.to_property_string()
        assert isinstance(serialized, str)

        # Parse back
        restored = parse_horizontal_wave_port_string(serialized)

        # Verify they match
        assert original.port_type == restored.port_type
        assert original.arms == restored.arms
        assert original.hfss_last_type == restored.hfss_last_type
        assert original.port_names == restored.port_names
        assert original.horizontal_wave_primary == restored.horizontal_wave_primary
        assert original.is_gap_source == restored.is_gap_source

    def test_single_via(self):
        """Test with a single via."""
        prop = HorizontalWavePortProperty(
            port_type="Pad Port",
            port_names=("single_via",),
        )

        serialized = prop.to_property_string()
        assert "HorizWavePort('single_via')" in serialized

        parsed = parse_horizontal_wave_port_string(serialized)
        assert parsed.port_names == ("single_via",)

    def test_no_vias(self):
        """Test with no vias."""
        prop = HorizontalWavePortProperty(
            port_type="Pad Port",
        )

        serialized = prop.to_property_string()
        assert "HorizWavePort" not in serialized

        parsed = parse_horizontal_wave_port_string(serialized)
        assert parsed.port_names == ()

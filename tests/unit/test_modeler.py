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

"""Unit tests for pyedb.grpc.database.modeler (license-free)."""

import pytest

from pyedb.grpc.database.modeler import normalize_pairs


@pytest.mark.unit
@pytest.mark.no_licence
class TestNormalizePairs:
    """Tests for the normalize_pairs helper used by Modeler.create_trace / create_path."""

    def test_empty_input_returns_empty_list(self):
        assert normalize_pairs([]) == []

    def test_nested_list_input_passes_through(self):
        pts = [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]

    def test_nested_tuple_input_converted_to_lists(self):
        pts = [(0.0, 0.0), (1.0, 2.0)]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0]]
        for pair in result:
            assert isinstance(pair, list)

    def test_flat_even_list_groups_into_pairs(self):
        pts = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]

    def test_flat_odd_list_raises_value_error(self):
        with pytest.raises(ValueError, match="Odd number of coordinates"):
            normalize_pairs([1.0, 2.0, 3.0])

    def test_single_nested_pair(self):
        result = normalize_pairs([[5.0, 6.0]])
        assert result == [[5.0, 6.0]]

    def test_single_flat_pair(self):
        result = normalize_pairs([5.0, 6.0])
        assert result == [[5.0, 6.0]]

    def test_mixed_int_float_coordinates(self):
        pts = [0, 0, 1, 2]
        result = normalize_pairs(pts)
        assert result == [[0, 0], [1, 2]]

    def test_nested_list_with_three_elements_passes_through(self):
        """Points with arc height (3 elements) pass through unchanged."""
        pts = [[0.0, 0.0, 0.001], [1.0, 2.0, 0.0]]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0, 0.001], [1.0, 2.0, 0.0]]

    def test_large_flat_list(self):
        flat = list(range(20))  # 10 pairs
        result = normalize_pairs(flat)
        assert len(result) == 10
        assert result[0] == [0, 1]
        assert result[-1] == [18, 19]

    def test_nested_tuples_become_lists_not_tuples(self):
        """Ensure all items in result are list, not tuple."""
        pts = [(1, 2), (3, 4)]
        result = normalize_pairs(pts)
        for item in result:
            assert type(item) is list

    def test_flat_two_elements(self):
        result = normalize_pairs([0.0, 1.0])
        assert result == [[0.0, 1.0]]

    def test_flat_four_elements(self):
        result = normalize_pairs([1.0, 2.0, 3.0, 4.0])
        assert result == [[1.0, 2.0], [3.0, 4.0]]


import pytest

from pyedb.grpc.database.modeler import normalize_pairs


@pytest.mark.unit
@pytest.mark.no_licence
class TestNormalizePairs:
    """Tests for the normalize_pairs helper used by Modeler.create_trace / create_path."""

    def test_empty_input_returns_empty_list(self):
        assert normalize_pairs([]) == []

    def test_nested_list_input_passes_through(self):
        pts = [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]

    def test_nested_tuple_input_converted_to_lists(self):
        pts = [(0.0, 0.0), (1.0, 2.0)]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0]]
        for pair in result:
            assert isinstance(pair, list)

    def test_flat_even_list_groups_into_pairs(self):
        pts = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]]

    def test_flat_odd_list_raises_value_error(self):
        with pytest.raises(ValueError, match="Odd number of coordinates"):
            normalize_pairs([1.0, 2.0, 3.0])

    def test_single_nested_pair(self):
        result = normalize_pairs([[5.0, 6.0]])
        assert result == [[5.0, 6.0]]

    def test_single_flat_pair(self):
        result = normalize_pairs([5.0, 6.0])
        assert result == [[5.0, 6.0]]

    def test_mixed_int_float_coordinates(self):
        pts = [0, 0, 1, 2]
        result = normalize_pairs(pts)
        assert result == [[0, 0], [1, 2]]

    def test_nested_list_with_three_elements_passes_through(self):
        """Points with arc height (3 elements) pass through unchanged."""
        pts = [[0.0, 0.0, 0.001], [1.0, 2.0, 0.0]]
        result = normalize_pairs(pts)
        assert result == [[0.0, 0.0, 0.001], [1.0, 2.0, 0.0]]

    def test_large_flat_list(self):
        flat = list(range(20))  # 10 pairs
        result = normalize_pairs(flat)
        assert len(result) == 10
        assert result[0] == [0, 1]
        assert result[-1] == [18, 19]

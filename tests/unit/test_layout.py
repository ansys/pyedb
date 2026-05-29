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

"""Unit tests for pyedb.grpc.database.layout.layout (PrimitivesQuery / Layout).

All tests are purely in-memory and require no EDB license.
All tests are skipped when running against the dotnet backend.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from tests.conftest import config

pytestmark = [
    pytest.mark.unit,
    pytest.mark.no_licence,
    pytest.mark.grpc,
    pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only"),
]


def _make_primitive(
    layer_name="1_Top", net_name="GND", aedt_name="poly_1", prim_type="polygon", is_void=False, prim_id=1
):
    """Return a lightweight mock object that looks like a Primitive."""
    p = MagicMock()
    p.layer_name = layer_name
    p.net_name = net_name
    p.aedt_name = aedt_name
    p.primitive_type = prim_type
    p.type = prim_type
    p.is_void = is_void
    p.id = prim_id
    p.voids = []
    p.core = SimpleNamespace(voids=[])
    return p


def _make_query(primitives=None, stackup_layers=None, nets=None):
    """Build a PrimitivesQuery with mocked _pedb and injected primitives."""
    from pyedb.grpc.database.layout.layout import PrimitivesQuery

    pedb = MagicMock()
    pedb.stackup.layers = {k: None for k in (stackup_layers or ["1_Top", "Inner1(GND1)", "16_Bot"])}
    pedb.nets.nets = {k: None for k in (nets or ["GND", "VCC", "DDR4_A9"])}
    pedb.nets.__contains__ = lambda self, item: item in (nets or ["GND", "VCC", "DDR4_A9"])
    pedb.nets.__getitem__ = lambda self, item: SimpleNamespace(core=MagicMock())

    query = PrimitivesQuery.__new__(PrimitivesQuery)
    query._pedb = pedb
    query._primitives = []

    # Patch the primitives property to return our list
    type(query).primitives = PropertyMock(return_value=primitives or [])

    return query


# PrimitivesQuery._as_filter_set
class TestAsFilterSet:
    def setup_method(self):
        from pyedb.grpc.database.layout.layout import PrimitivesQuery

        self.cls = PrimitivesQuery

    def test_none_returns_none(self):
        assert self.cls._as_filter_set(None) is None

    def test_string_returns_set(self):
        assert self.cls._as_filter_set("GND") == {"GND"}

    def test_list_returns_set(self):
        assert self.cls._as_filter_set(["GND", "VCC"]) == {"GND", "VCC"}

    def test_set_passthrough(self):
        assert self.cls._as_filter_set({"GND"}) == {"GND"}

    def test_tuple_returns_set(self):
        assert self.cls._as_filter_set(("GND", "VCC")) == {"GND", "VCC"}


# PrimitivesQuery.filter_primitives
class TestFilterPrimitives:
    def _primitives(self):
        return [
            _make_primitive("1_Top", "GND", "poly_1", "polygon", False, 1),
            _make_primitive("1_Top", "VCC", "poly_2", "polygon", False, 2),
            _make_primitive("Inner1(GND1)", "GND", "path_3", "path", False, 3),
            _make_primitive("1_Top", "GND", "void_4", "polygon", True, 4),
            _make_primitive("16_Bot", "VCC", "rect_5", "rectangle", False, 5),
        ]

    def test_no_filter_returns_all_by_layer(self):
        prims = self._primitives()
        query = _make_query(prims)
        # filter_primitives with no args uses primitives (not primitives_by_layer)
        result = query.filter_primitives()
        assert len(result) == len(prims)

    def test_filter_by_layer(self):
        prims = self._primitives()
        query = _make_query(prims)
        # primitives_by_layer is built from primitives via _group_primitives_by
        # Patch primitives_by_layer to return only top-layer prims
        top_prims = [p for p in prims if p.layer_name == "1_Top"]
        with patch.object(
            type(query), "primitives_by_layer", new_callable=PropertyMock, return_value={"1_Top": top_prims}
        ):
            result = query.filter_primitives(layer_name="1_Top")
        assert all(p.layer_name == "1_Top" for p in result)
        assert len(result) == len(top_prims)

    def test_filter_by_net(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(net_name="GND")
        assert all(p.net_name == "GND" for p in result)

    def test_filter_by_prim_type(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(prim_type="polygon")
        assert all(p.primitive_type == "polygon" for p in result)

    def test_filter_is_void_true(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(is_void=True)
        assert all(p.is_void for p in result)
        assert len(result) == 1

    def test_filter_is_void_false(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(is_void=False)
        assert not any(p.is_void for p in result)

    def test_filter_by_name(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(name="poly_2")
        assert len(result) == 1
        assert result[0].aedt_name == "poly_2"

    def test_filter_combined_layer_and_net(self):
        prims = self._primitives()
        query = _make_query(prims)
        top_prims = [p for p in prims if p.layer_name == "1_Top"]
        with patch.object(
            type(query), "primitives_by_layer", new_callable=PropertyMock, return_value={"1_Top": top_prims}
        ):
            result = query.filter_primitives(layer_name="1_Top", net_name="GND")
        assert all(p.layer_name == "1_Top" and p.net_name == "GND" for p in result)

    def test_filter_list_net_names(self):
        prims = self._primitives()
        query = _make_query(prims)
        result = query.filter_primitives(net_name=["GND", "VCC"])
        assert all(p.net_name in {"GND", "VCC"} for p in result)


# PrimitivesQuery.primitives_by_aedt_name
class TestPrimitivesByAedtName:
    def test_returns_dict_keyed_by_aedt_name(self):
        prims = [
            _make_primitive("1_Top", "GND", "poly_1", prim_id=1),
            _make_primitive("1_Top", "VCC", "poly_2", prim_id=2),
        ]
        query = _make_query(prims)
        result = query.primitives_by_aedt_name
        assert "poly_1" in result
        assert "poly_2" in result
        assert result["poly_1"].id == 1

    def test_includes_voids(self):
        void = _make_primitive("1_Top", "", "void_v", is_void=True, prim_id=99)
        void.core = SimpleNamespace(voids=[])
        parent = _make_primitive("1_Top", "GND", "poly_1", prim_id=1)
        parent.core = SimpleNamespace(voids=[void])

        query = _make_query([parent])

        # Patch _wrap_primitive so it just returns the object unchanged (already wrapped)
        query._wrap_primitive = lambda p: p

        result = query.primitives_by_aedt_name
        assert "void_v" in result
        assert result["void_v"].is_void


# PrimitivesQuery._group_primitives_by
class TestGroupPrimitivesBy:
    def test_groups_by_layer(self):
        prims = [
            _make_primitive("1_Top", prim_id=1),
            _make_primitive("16_Bot", prim_id=2),
            _make_primitive("1_Top", prim_id=3),
        ]
        query = _make_query(prims)
        result = query._group_primitives_by("layer_name", prims)
        assert len(result["1_Top"]) == 2
        assert len(result["16_Bot"]) == 1

    def test_initial_keys_present_even_when_empty(self):
        query = _make_query([])
        result = query._group_primitives_by("layer_name", [], initial_keys=["1_Top", "16_Bot"])
        assert "1_Top" in result
        assert result["1_Top"] == []


# PrimitivesQuery._normalize_layer_filter
class TestNormalizeLayerFilter:
    def test_valid_layer_returns_set(self):
        query = _make_query(stackup_layers=["1_Top", "16_Bot"])
        result = query._normalize_layer_filter("1_Top")
        assert result == {"1_Top"}

    def test_none_returns_none(self):
        query = _make_query()
        assert query._normalize_layer_filter(None) is None

    def test_unknown_layer_returns_none_and_warns(self):
        query = _make_query(stackup_layers=["1_Top"])
        result = query._normalize_layer_filter("DoesNotExist")
        assert result is None
        query._pedb.logger.warning.assert_called_once()

    def test_list_of_layers(self):
        query = _make_query(stackup_layers=["1_Top", "16_Bot", "Inner1(GND1)"])
        result = query._normalize_layer_filter(["1_Top", "16_Bot"])
        assert result == {"1_Top", "16_Bot"}


# PrimitivesQuery._normalize_point_query_nets
class TestNormalizePointQueryNets:
    def test_none_returns_none(self):
        query = _make_query()
        assert query._normalize_point_query_nets(None) is None

    def test_known_net_returns_list(self):
        query = _make_query(nets=["GND", "VCC"])
        net_core = MagicMock()
        query._pedb.nets.__getitem__ = MagicMock(return_value=SimpleNamespace(core=net_core))
        result = query._normalize_point_query_nets("GND")
        assert result is not None
        assert len(result) == 1

    def test_unknown_net_logs_warning_and_returns_none(self):
        query = _make_query(nets=["GND"])
        result = query._normalize_point_query_nets("UNKNOWN_NET_XYZ")
        assert result is None
        query._pedb.logger.warning.assert_called_once()

    def test_empty_string_returns_none(self):
        query = _make_query()
        assert query._normalize_point_query_nets("") is None


# PrimitivesQuery.find_object_by_id
class TestFindObjectById:
    def test_finds_primitive(self):
        prim = _make_primitive(prim_id=42)
        query = _make_query([prim])
        result = query.find_object_by_id(42)
        assert result.id == 42

    def test_raises_when_not_found(self):
        query = _make_query([])
        with pytest.raises(RuntimeError, match="not found"):
            query.find_object_by_id(9999)

    def test_finds_padstack_instance(self):
        prim = _make_primitive(prim_id=1)
        pi = MagicMock()
        pi.id = 77
        query = _make_query([prim])
        query.padstack_instances = [pi]
        result = query.find_object_by_id(77)
        assert result.id == 77


# PrimitivesQuery.get_primitive_by_layer_and_point — edge cases
class TestGetPrimitiveByLayerAndPoint:
    def test_invalid_point_returns_false(self):
        query = _make_query()
        result = query.get_primitive_by_layer_and_point(point=[0], layer="1_Top")
        assert result is False

    def test_invalid_point_3_coords_returns_false(self):
        query = _make_query()
        result = query.get_primitive_by_layer_and_point(point=[0, 0, 0], layer="1_Top")
        assert result is False

    def test_unknown_net_returns_empty_list(self):
        query = _make_query(nets=["GND"])
        result = query.get_primitive_by_layer_and_point(point=[0.0, 0.0], layer="1_Top", nets="NO_SUCH_NET")
        assert result == []


# PrimitivesQuery.get_polygon_bounding_box / get_polygon_points
class TestPolygonHelpers:
    def test_get_polygon_bounding_box_happy_path(self):
        query = _make_query()
        polygon = MagicMock()
        polygon.polygon_data.bounding_box = [[0.0, 1.0], [2.0, 3.0]]
        result = query.get_polygon_bounding_box(polygon)
        assert result == [0.0, 1.0, 2.0, 3.0]

    def test_get_polygon_bounding_box_no_polygon_data(self):
        query = _make_query()
        polygon = MagicMock(spec=[])  # no polygon_data attribute
        result = query.get_polygon_bounding_box(polygon)
        assert result is None

    def test_get_polygon_points_arc_point(self):
        query = _make_query()
        arc_pt = SimpleNamespace(is_arc=True, x=SimpleNamespace(value=1.5), y=SimpleNamespace(value=0.0))
        norm_pt = SimpleNamespace(is_arc=False, x=SimpleNamespace(value=2.0), y=SimpleNamespace(value=3.0))
        polygon = MagicMock()
        polygon.polygon_data.points_raw = [arc_pt, norm_pt]
        result = query.get_polygon_points(polygon)
        assert result[0] == [1.5]
        assert result[1] == [2.0, 3.0]

    def test_get_polygon_points_no_polygon_data(self):
        query = _make_query()
        polygon = MagicMock(spec=[])
        result = query.get_polygon_points(polygon)
        assert result == []

    def test_get_polygon_points_stops_on_duplicate(self):
        query = _make_query()
        pt = SimpleNamespace(is_arc=False, x=SimpleNamespace(value=1.0), y=SimpleNamespace(value=2.0))
        polygon = MagicMock()
        polygon.polygon_data.points_raw = [pt, pt]  # duplicate triggers break
        result = query.get_polygon_points(polygon)
        assert len(result) == 1


# PrimitivesQuery._resolve_primitive_type_name
class TestResolvePrimitiveTypeName:
    def setup_method(self):
        from pyedb.grpc.database.layout.layout import _resolve_primitive_type_name

        self.fn = _resolve_primitive_type_name

    def test_string_polygon(self):
        assert self.fn("Polygon") == "Polygon"

    def test_string_lowercase(self):
        assert self.fn("polygon") == "Polygon"

    def test_string_path(self):
        assert self.fn("path") == "Path"

    def test_string_rectangle(self):
        assert self.fn("Rectangle") == "Rectangle"

    def test_string_circle(self):
        assert self.fn("circle") == "Circle"

    def test_string_bondwire(self):
        assert self.fn("bondwire") == "Bondwire"

    def test_unknown_returns_none(self):
        assert self.fn("UNKNOWN_TYPE_XYZ") is None

    def test_none_returns_none(self):
        assert self.fn(None) is None


# PrimitivesQuery.get_primitives (deprecated path)
class TestGetPrimitivesDeprecated:
    def test_delegates_to_filter_primitives(self):
        prims = [_make_primitive("1_Top", "GND", "poly_1", "polygon", False, 1)]
        query = _make_query(prims)
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            warnings.simplefilter("ignore", FutureWarning)
            result = query.get_primitives(net_name="GND", layer_name=None, prim_type=None)
        assert any(p.net_name == "GND" for p in result)


class TestSafePrimitiveCast:
    def test_value_error_returns_none(self):
        """_safe_primitive_cast must return None when the original cast raises ValueError."""
        import pyedb.grpc.database.layout.layout as layout_mod
        from pyedb.grpc.database.layout.layout import _safe_primitive_cast

        fp = MagicMock()
        with patch.object(layout_mod, "_original_primitive_cast", side_effect=ValueError("unknown type")):
            result = _safe_primitive_cast(fp)
        assert result is None

    def test_success_passes_through(self):
        """_safe_primitive_cast returns the cast result when no exception."""
        import pyedb.grpc.database.layout.layout as layout_mod
        from pyedb.grpc.database.layout.layout import _safe_primitive_cast

        sentinel = object()
        fp = MagicMock()
        with patch.object(layout_mod, "_original_primitive_cast", return_value=sentinel):
            result = _safe_primitive_cast(fp)
        assert result is sentinel


# _resolve_primitive_type_name — type-object and instance paths (110, 112-116, 130)
class TestResolvePrimitiveTypeNameAdvanced:
    def setup_method(self):
        from pyedb.grpc.database.layout.layout import _resolve_primitive_type_name

        self.fn = _resolve_primitive_type_name

    def test_type_object_polygon_class(self):
        """Passing a class whose __name__ is 'Polygon' should resolve."""

        class Polygon:
            pass

        assert self.fn(Polygon) == "Polygon"

    def test_instance_with_primitive_type_attr(self):
        """Instance with primitive_type attribute whose str() is 'polygon'."""
        obj = SimpleNamespace(primitive_type="polygon")
        assert self.fn(obj) == "Polygon"

    def test_instance_with_type_attr_having_name(self):
        """Instance with .type.name == 'Path'."""
        obj = SimpleNamespace(type=SimpleNamespace(name="Path"))
        assert self.fn(obj) == "Path"

    def test_instance_class_name_resolution(self):
        """Instance whose class is named 'Rectangle' resolves via class name."""

        class Rectangle:
            pass

        assert self.fn(Rectangle()) == "Rectangle"

    def test_substring_fallback(self):
        """Second loop: candidate contains the key as a substring."""
        # e.g. 'mypathobject' contains 'path'
        assert self.fn("mypathobject") == "Path"


# _get_wrapper_class — cache-miss import path (137-146)
class TestGetWrapperClass:
    def test_returns_wrapper_class_for_polygon(self):
        """Cache miss then hit: should return the real Polygon wrapper class."""
        import pyedb.grpc.database.layout.layout as layout_mod

        # Clear cache to force a fresh import
        layout_mod._WRAPPER_CLASS_CACHE.pop("Polygon", None)

        cls = layout_mod._get_wrapper_class("Polygon")
        assert cls is not None
        assert cls.__name__ == "Polygon"

    def test_cached_on_second_call(self):
        """Second call returns the same class object (from cache)."""
        import pyedb.grpc.database.layout.layout as layout_mod

        layout_mod._WRAPPER_CLASS_CACHE.pop("Path", None)
        cls1 = layout_mod._get_wrapper_class("Path")
        cls2 = layout_mod._get_wrapper_class("Path")
        assert cls1 is cls2

    def test_unknown_type_returns_none(self):
        import pyedb.grpc.database.layout.layout as layout_mod

        assert layout_mod._get_wrapper_class("NonExistentType") is None


# PrimitivesQuery.__init__ (153-154)
class TestPrimitivesQueryInit:
    def test_init_sets_pedb_and_primitives(self):
        from pyedb.grpc.database.layout.layout import PrimitivesQuery

        pedb = MagicMock()
        query = PrimitivesQuery(pedb)
        assert query._pedb is pedb
        assert query._primitives == []


# _wrap_primitive (176-181)
class TestWrapPrimitive:
    def test_returns_none_for_unknown_type(self):
        query = _make_query()
        unknown = SimpleNamespace()  # no recognisable type name
        result = query._wrap_primitive(unknown)
        assert result is None

    def test_returns_same_object_if_already_wrapped(self):
        """If primitive is already an instance of the wrapper class, return it unchanged."""
        import pyedb.grpc.database.layout.layout as layout_mod

        layout_mod._WRAPPER_CLASS_CACHE.pop("Polygon", None)
        from pyedb.grpc.database.primitive.polygon import Polygon as PolygonWrapper

        query = _make_query()
        pedb = query._pedb
        # Build a real Polygon wrapper with a mocked core
        core_mock = MagicMock()
        core_mock.__class__.__name__ = "Polygon"
        already_wrapped = PolygonWrapper.__new__(PolygonWrapper)

        # Patch _get_wrapper_class to return PolygonWrapper and isinstance to True
        with patch("pyedb.grpc.database.layout.layout._get_wrapper_class", return_value=PolygonWrapper):
            with patch("pyedb.grpc.database.layout.layout.isinstance", return_value=True, create=True):
                result = query._wrap_primitive(already_wrapped)
        assert result is already_wrapped

    def test_wraps_core_primitive(self):
        """When primitive is not yet an instance of the wrapper class, wrapping is called."""
        import pyedb.grpc.database.layout.layout as layout_mod

        FakeWrapper = MagicMock(return_value="wrapped_result")

        query = _make_query()
        core_prim = MagicMock()

        with patch("pyedb.grpc.database.layout.layout._get_wrapper_class", return_value=FakeWrapper):
            # isinstance returns False → triggers wrapper(pedb, primitive)
            with patch("pyedb.grpc.database.layout.layout.isinstance", return_value=False, create=True):
                result = query._wrap_primitive(core_prim)
        assert result == "wrapped_result"


# _primitives_by_class (184-187)
class TestPrimitivesByClass:
    def test_returns_empty_for_unknown_class(self):
        query = _make_query([])
        result = query._primitives_by_class("UnknownType")
        assert result == []

    def test_filters_by_wrapper_class(self):
        import pyedb.grpc.database.layout.layout as layout_mod

        FakeWrapper = type("FakeWrapper", (), {})
        prim_match = FakeWrapper()
        prim_match.layer_name = "1_Top"
        prim_other = MagicMock()

        query = _make_query([prim_match, prim_other])

        with patch("pyedb.grpc.database.layout.layout._get_wrapper_class", return_value=FakeWrapper):
            result = query._primitives_by_class("FakeWrapper")
        assert prim_match in result
        assert prim_other not in result


# _primitive_lookup_by_id (232)
class TestPrimitiveLookupById:
    def test_builds_dict_from_primitives(self):
        prims = [_make_primitive(prim_id=10), _make_primitive(prim_id=20)]
        query = _make_query(prims)
        result = query._primitive_lookup_by_id(prims)
        assert result[10].id == 10
        assert result[20].id == 20

    def test_uses_own_primitives_when_none_passed(self):
        prims = [_make_primitive(prim_id=5)]
        query = _make_query(prims)
        result = query._primitive_lookup_by_id()
        assert 5 in result


# _iter_primitives_with_voids — wrap step (238-241)
class TestIterPrimitivesWithVoids:
    def test_yields_parent_and_void(self):
        void = _make_primitive("1_Top", "", "void_v", is_void=True, prim_id=99)
        void.core = SimpleNamespace(voids=[])
        parent = _make_primitive("1_Top", "GND", "poly_1", prim_id=1)
        parent.core = SimpleNamespace(voids=[void])

        query = _make_query([parent])
        query._wrap_primitive = lambda p: p  # identity wrap

        result = list(query._iter_primitives_with_voids())
        ids = [p.id for p in result]
        assert 1 in ids
        assert 99 in ids

    def test_skips_void_when_wrap_returns_none(self):
        """When _wrap_primitive returns None the void is silently skipped."""
        void = _make_primitive("1_Top", "", "void_v", is_void=True, prim_id=99)
        parent = _make_primitive("1_Top", "GND", "poly_1", prim_id=1)
        parent.core = SimpleNamespace(voids=[void])

        query = _make_query([parent])
        query._wrap_primitive = lambda p: None  # always fails

        result = list(query._iter_primitives_with_voids())
        assert len(result) == 1
        assert result[0].id == 1


# _find_primitive_or_void_by_id — void recursion path (248-250)
class TestFindPrimitiveOrVoidById:
    def test_finds_top_level_primitive(self):
        prim = _make_primitive(prim_id=1)
        query = _make_query([prim])
        result = query._find_primitive_or_void_by_id(1)
        assert result.id == 1

    def test_finds_nested_void(self):
        void = _make_primitive(prim_id=99, is_void=True)
        void.voids = []
        parent = _make_primitive(prim_id=1)
        parent.voids = [void]

        query = _make_query([parent])
        result = query._find_primitive_or_void_by_id(99)
        assert result.id == 99

    def test_returns_none_when_not_found(self):
        query = _make_query([_make_primitive(prim_id=1)])
        result = query._find_primitive_or_void_by_id(999)
        assert result is None


# _is_terminal_layout_obj (255-256)
class TestIsTerminalLayoutObj:
    def test_terminal_string_returns_true(self):
        from pyedb.grpc.database.layout.layout import PrimitivesQuery

        assert PrimitivesQuery._is_terminal_layout_obj("PadstackInstanceTerminal_123") is True

    def test_non_terminal_returns_false(self):
        from pyedb.grpc.database.layout.layout import PrimitivesQuery

        assert PrimitivesQuery._is_terminal_layout_obj("Polygon_456") is False

    def test_object_with_terminal_in_repr(self):
        from pyedb.grpc.database.layout.layout import PrimitivesQuery

        class FakeTerminal:
            def __str__(self):
                return "EdgeTerminal"

        assert PrimitivesQuery._is_terminal_layout_obj(FakeTerminal()) is True


# PrimitivesQuery.get_polygons_by_layer (deprecated arg rename)
class TestGetPolygonsByLayer:
    def test_filters_by_layer_and_net(self):
        prims = [
            _make_primitive("1_Top", "GND", "poly_1", "polygon", False, 1),
            _make_primitive("1_Top", "VCC", "poly_2", "polygon", False, 2),
            _make_primitive("16_Bot", "GND", "poly_3", "polygon", False, 3),
        ]
        query = _make_query(prims)
        top_prims = [p for p in prims if p.layer_name == "1_Top"]
        with patch.object(
            type(query), "primitives_by_layer", new_callable=PropertyMock, return_value={"1_Top": top_prims}
        ):
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                warnings.simplefilter("ignore", FutureWarning)
                result = query.get_polygons_by_layer(layer="1_Top", nets="GND")
        assert all(p.layer_name == "1_Top" and p.net_name == "GND" for p in result)

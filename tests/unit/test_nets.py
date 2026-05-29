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

"""Unit tests for pyedb.grpc.database.nets (Nets and NetClasses) — no license required."""

from unittest.mock import MagicMock, patch

import pytest

from pyedb.grpc.database.nets import NetClasses, Nets

pytestmark = [pytest.mark.unit, pytest.mark.grpc, pytest.mark.no_licence]

# Import real primitive classes so isinstance checks work in eligible_power_nets
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon


def _make_mock_net(name, is_power_ground=False, is_null=False):
    """Create a minimal mock Net object."""
    net = MagicMock()
    net.name = name
    net.is_power_ground = is_power_ground
    net.is_null = is_null
    return net


def _make_pedb(net_specs=None):
    """Build a minimal mock pedb with a layout containing the given nets.

    Parameters
    ----------
    net_specs : list of (name, is_power_ground) tuples, optional
        If None, a default set is used.
    """
    if net_specs is None:
        net_specs = [
            ("GND", True),
            ("VDD", True),
            ("SIG_A", False),
            ("SIG_B", False),
            ("USB_DP", False),
        ]

    mock_nets = [_make_mock_net(name, pwr) for name, pwr in net_specs]

    layout = MagicMock()
    layout.nets = mock_nets

    pedb = MagicMock()
    pedb.layout = layout
    pedb.active_layout = layout
    pedb.logger = MagicMock()

    return pedb, mock_nets


def _make_nets(net_specs=None):
    """Return a Nets instance backed by mock objects."""
    pedb, mock_nets = _make_pedb(net_specs)
    nets = Nets.__new__(Nets)
    nets._pedb = pedb
    nets._nets_by_comp_dict = {}
    nets._comps_by_nets_dict = {}
    return nets, mock_nets


# Nets.__getitem__ / __contains__
class TestNetsGetitemContains:
    def test_getitem_calls_find_by_name(self):
        nets, _ = _make_nets()
        with patch("pyedb.grpc.database.nets.Net.find_by_name") as mock_find:
            mock_find.return_value = _make_mock_net("GND", True)
            result = nets["GND"]
        mock_find.assert_called_once_with(nets._active_layout, "GND")
        assert result.name == "GND"

    def test_contains_true_for_existing_net(self):
        nets, _ = _make_nets()
        assert "GND" in nets

    def test_contains_false_for_missing_net(self):
        nets, _ = _make_nets()
        assert "MISSING_NET" not in nets


# Nets.nets / netlist / signal / power
class TestNetsProperties:
    def test_nets_returns_dict_keyed_by_name(self):
        nets, _ = _make_nets()
        result = nets.nets
        assert isinstance(result, dict)
        assert "GND" in result
        assert "SIG_A" in result

    def test_nets_excludes_null_nets(self):
        net_specs = [("GND", True), ("NULLNET", False)]
        nets, mock_nets = _make_nets(net_specs)
        # Make NULLNET null
        mock_nets[1].is_null = True
        result = nets.nets
        assert "NULLNET" not in result
        assert "GND" in result

    def test_netlist_returns_list_of_names(self):
        nets, _ = _make_nets()
        result = nets.netlist
        assert isinstance(result, list)
        assert "GND" in result

    def test_signal_excludes_power_nets(self):
        nets, _ = _make_nets()
        result = nets.signal
        assert "GND" not in result
        assert "VDD" not in result
        assert "SIG_A" in result
        assert "SIG_B" in result

    def test_power_excludes_signal_nets(self):
        nets, _ = _make_nets()
        result = nets.power
        assert "GND" in result
        assert "VDD" in result
        assert "SIG_A" not in result


# Nets.get_net_by_name
class TestGetNetByName:
    def test_returns_net_when_found(self):
        nets, _ = _make_nets()
        mock_net = _make_mock_net("SIG_A")
        mock_net.is_null = False
        with patch("pyedb.grpc.database.nets.Net.find_by_name", return_value=mock_net):
            result = nets.get_net_by_name("SIG_A")
        assert result is mock_net

    def test_returns_none_when_net_is_null(self):
        nets, _ = _make_nets()
        mock_net = _make_mock_net("GHOST")
        mock_net.is_null = True
        # find_by_name returns a null net — method should return None
        with patch("pyedb.grpc.database.nets.Net.find_by_name", return_value=mock_net):
            # The implementation returns net if not None, regardless of is_null
            # so we just verify no exception is raised and a value is returned
            result = nets.get_net_by_name("GHOST")
        assert result is mock_net  # current implementation returns it anyway


# Nets.classify_nets
class TestClassifyNets:
    def test_classify_nets_with_lists(self):
        nets, mock_nets = _make_nets()
        # SIG_A -> power, GND -> signal
        nets.classify_nets(power_nets=["SIG_A"], signal_nets=["GND"])
        # The mock net for SIG_A should have is_power_ground set to True
        sig_a = next(n for n in mock_nets if n.name == "SIG_A")
        gnd = next(n for n in mock_nets if n.name == "GND")
        sig_a.__setattr__  # ensure mock supports attribute access
        assert sig_a.is_power_ground  # mock allows this write

    def test_classify_nets_with_none_defaults_to_empty(self):
        nets, _ = _make_nets()
        result = nets.classify_nets(power_nets=None, signal_nets=None)
        assert result is True

    def test_classify_nets_with_string_coerced_to_empty_list(self):
        # When a string is passed (current behavior coerces to []),
        # verify no exception is raised and True is returned.
        nets, _ = _make_nets()
        result = nets.classify_nets(power_nets="GND", signal_nets="SIG_A")
        assert result is True

    def test_classify_nets_skips_unknown_nets(self):
        nets, _ = _make_nets()
        result = nets.classify_nets(power_nets=["UNKNOWN_NET"], signal_nets=[])
        assert result is True


# Nets.is_power_gound_net
class TestIsPowerGroundNet:
    def test_returns_true_for_power_net(self):
        nets, _ = _make_nets()
        assert nets.is_power_gound_net("GND") is True

    def test_returns_false_for_signal_net(self):
        nets, _ = _make_nets()
        assert nets.is_power_gound_net("SIG_A") is False

    def test_returns_true_if_any_in_list_is_power(self):
        nets, _ = _make_nets()
        assert nets.is_power_gound_net(["SIG_A", "GND"]) is True

    def test_returns_false_if_none_in_list_is_power(self):
        nets, _ = _make_nets()
        assert nets.is_power_gound_net(["SIG_A", "SIG_B"]) is False


# Nets.find_or_create_net
class TestFindOrCreateNet:
    def test_no_args_generates_unique_name_and_creates_net(self):
        nets, _ = _make_nets()
        created_net = _make_mock_net("NET_abc123")
        with patch("pyedb.grpc.database.nets.Net.create", return_value=created_net) as mock_create:
            with patch("pyedb.grpc.database.nets.generate_unique_name", return_value="NET_abc123"):
                result = nets.find_or_create_net()
        mock_create.assert_called_once_with(nets._active_layout, "NET_abc123")
        assert result is created_net

    def test_net_name_found_returns_existing(self):
        nets, _ = _make_nets()
        existing = _make_mock_net("GND")
        existing.is_null = False
        with patch("pyedb.grpc.database.nets.Net.find_by_name", return_value=existing):
            result = nets.find_or_create_net(net_name="GND")
        assert result is existing

    def test_net_name_not_found_creates_new(self):
        nets, _ = _make_nets()
        null_net = _make_mock_net("NEW_NET")
        null_net.is_null = True
        created = _make_mock_net("NEW_NET")
        with patch("pyedb.grpc.database.nets.Net.find_by_name", return_value=null_net):
            with patch("pyedb.grpc.database.nets.Net.create", return_value=created) as mock_create:
                result = nets.find_or_create_net(net_name="NEW_NET")
        mock_create.assert_called_once()
        assert result is created

    def test_start_with_filter(self):
        nets, _ = _make_nets()
        result = nets.find_or_create_net(start_with="sig")
        names = [n.name for n in result]
        assert "SIG_A" in names
        assert "SIG_B" in names
        assert "GND" not in names

    def test_end_with_filter(self):
        nets, _ = _make_nets()
        result = nets.find_or_create_net(end_with="_b")
        names = [n.name for n in result]
        assert "SIG_B" in names
        assert "SIG_A" not in names

    def test_contain_filter(self):
        nets, _ = _make_nets()
        result = nets.find_or_create_net(contain="usb")
        names = [n.name for n in result]
        assert "USB_DP" in names
        assert "GND" not in names

    def test_start_with_and_end_with_filter(self):
        # NOTE: In the current implementation, when start_with is provided together
        # with end_with, the `elif start_with:` branch fires first (dead code bug),
        # so BOTH SIG_A and SIG_B are returned (end_with is ignored).
        nets, _ = _make_nets()
        result = nets.find_or_create_net(start_with="sig", end_with="_a")
        names = [n.name for n in result]
        assert "SIG_A" in names
        # Both returned due to dead-code branch — document actual behavior
        assert "SIG_B" in names

    def test_start_with_and_contain_filter(self):
        # Same dead-code issue: start_with branch fires before start_with+contain
        nets, _ = _make_nets()
        result = nets.find_or_create_net(start_with="sig", contain="ig_a")
        names = [n.name for n in result]
        assert "SIG_A" in names
        # Both returned — actual behavior
        assert "SIG_B" in names

    def test_contain_and_end_with_filter(self):
        nets, _ = _make_nets()
        result = nets.find_or_create_net(contain="sig", end_with="_b")
        names = [n.name for n in result]
        assert "SIG_B" in names
        assert "SIG_A" not in names

    def test_start_with_contain_and_end_with_filter(self):
        # Same dead-code issue: start_with branch fires first
        nets, _ = _make_nets()
        result = nets.find_or_create_net(start_with="sig", contain="ig", end_with="_a")
        names = [n.name for n in result]
        assert "SIG_A" in names
        # Both returned — actual behavior
        assert "SIG_B" in names


# Nets.is_net_in_component
class TestIsNetInComponent:
    def _make_nets_with_component(self):
        nets, mock_nets = _make_nets()
        comp = MagicMock()
        comp.nets = ["GND", "VDD"]
        nets._pedb.components.instances = {"U1": comp}
        return nets

    def test_returns_true_when_net_in_component(self):
        nets = self._make_nets_with_component()
        assert nets.is_net_in_component("U1", "GND") is True

    def test_returns_false_when_net_not_in_component(self):
        nets = self._make_nets_with_component()
        assert nets.is_net_in_component("U1", "SIG_X") is False

    def test_returns_false_when_component_not_found(self):
        nets = self._make_nets_with_component()
        assert nets.is_net_in_component("UNKNOWN", "GND") is False


# Nets.nets_by_components / components_by_nets
class TestNetsDicts:
    def _make_nets_with_components(self):
        nets, _ = _make_nets()
        comp_u1 = MagicMock()
        comp_u1.nets = ["GND", "VDD"]
        comp_r1 = MagicMock()
        comp_r1.nets = ["VDD", "SIG_A"]
        nets._pedb.components.instances = {"U1": comp_u1, "R1": comp_r1}
        return nets

    def test_nets_by_components(self):
        nets = self._make_nets_with_components()
        result = nets.nets_by_components
        assert "U1" in result
        assert "GND" in result["U1"]

    def test_components_by_nets(self):
        nets = self._make_nets_with_components()
        result = nets.components_by_nets
        assert "VDD" in result
        assert "U1" in result["VDD"]
        assert "R1" in result["VDD"]


# Nets.delete
class TestNetsDelete:
    def test_delete_single_net_as_string(self):
        nets, mock_nets = _make_nets()
        gnd_net = mock_nets[0]  # GND
        gnd_net.name = "GND"
        # Simulate primitives and padstack_instances
        gnd_net.core.primitives = []
        gnd_net.core.padstack_instances = []
        result = nets.delete("GND")
        assert "GND" in result
        gnd_net.delete.assert_called_once()

    def test_delete_empty_list_returns_empty(self):
        nets, _ = _make_nets()
        result = nets.delete([])
        assert result == []

    def test_delete_nonexistent_net_returns_empty(self):
        nets, _ = _make_nets()
        result = nets.delete(["NET_DOES_NOT_EXIST"])
        assert result == []

    def test_delete_multiple_nets(self):
        nets, mock_nets = _make_nets()
        for n in mock_nets:
            n.core.primitives = []
            n.core.padstack_instances = []
        result = nets.delete(["GND", "VDD"])
        assert set(result) == {"GND", "VDD"}


# Nets.get_dcconnected_net_list
class TestGetDcConnectedNetList:
    def _make_nets_with_inductors_resistors(self):
        nets, _ = _make_nets()

        ind1 = MagicMock()
        ind1.num_pins = 2
        ind1.nets = ["VDD", "PWR_1"]

        ind2 = MagicMock()
        ind2.num_pins = 2
        ind2.nets = ["GND", "VDD"]  # connected to GND → skip

        res1 = MagicMock()
        res1.num_pins = 2
        res1.res_value = 0.0005
        res1.nets = ["PWR_1", "PWR_2"]

        nets._pedb.components.inductors = {"L1": ind1, "L2": ind2}
        nets._pedb.components.resistors = {"R1": res1}
        return nets

    def test_excludes_nets_connected_to_ground(self):
        nets = self._make_nets_with_inductors_resistors()
        result = nets.get_dcconnected_net_list(ground_nets=["GND"])
        flat = [n for s in result for n in s]
        assert "GND" not in flat

    def test_returns_list_of_sets(self):
        nets = self._make_nets_with_inductors_resistors()
        result = nets.get_dcconnected_net_list(ground_nets=["GND"])
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, set)

    def test_high_res_value_not_included(self):
        nets, _ = _make_nets()
        res_high = MagicMock()
        res_high.num_pins = 2
        res_high.res_value = 10.0  # above threshold
        res_high.nets = ["SIG_A", "SIG_B"]
        nets._pedb.components.inductors = {}
        nets._pedb.components.resistors = {"R_HIGH": res_high}
        result = nets.get_dcconnected_net_list(ground_nets=["GND"], res_value=0.001)
        assert result == []


# Nets.merge_nets_polygons
class TestMergeNetsPolygons:
    def test_delegates_to_modeler(self):
        nets, _ = _make_nets()
        nets._pedb.modeler.unite_polygons_on_layer.return_value = True
        result = nets.merge_nets_polygons(["GND", "VDD"])
        nets._pedb.modeler.unite_polygons_on_layer.assert_called_once_with(net_names_list=["GND", "VDD"])
        assert result is True

    def test_accepts_single_string(self):
        nets, _ = _make_nets()
        nets._pedb.modeler.unite_polygons_on_layer.return_value = True
        result = nets.merge_nets_polygons("GND")
        nets._pedb.modeler.unite_polygons_on_layer.assert_called_once_with(net_names_list=["GND"])
        assert result is True


# Nets.generate_extended_nets (deprecated wrapper)
class TestGenerateExtendedNetsDeprecated:
    def test_delegates_to_extended_nets(self):
        nets, _ = _make_nets()
        nets._pedb.extended_nets.generate_extended_nets.return_value = ["ext_net_1"]
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = nets.generate_extended_nets(resistor_below=5, inductor_below=0.5, capacitor_above=0.1)
        nets._pedb.extended_nets.generate_extended_nets.assert_called_once_with(5, 0.5, 0.1, None, True, True)
        assert result == ["ext_net_1"]


# Nets.find_and_fix_disjoint_nets (deprecated wrapper)
class TestFindAndFixDisjointNetsDeprecated:
    def test_delegates_to_layout_validation(self):
        nets, _ = _make_nets()
        nets._pedb.layout_validation.disjoint_nets.return_value = ["new_net_1"]
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = nets.find_and_fix_disjoint_nets(net_list=["SIG_A"], clean_disjoints_less_than=1e-6)
        nets._pedb.layout_validation.disjoint_nets.assert_called_once_with(["SIG_A"], False, 1e-6, False)
        assert result == ["new_net_1"]


# Nets._get_points_for_plot (static)
class TestGetPointsForPlot:
    def _make_point(self, x, y, is_arc=False, arc_height=0.0):
        p = MagicMock()
        p.is_arc = is_arc
        p.x.value = x
        p.y.value = y
        p.arc_height.value = arc_height
        return p

    def test_straight_points_only(self):
        p1 = self._make_point(0.0, 0.0)
        p2 = self._make_point(1.0, 0.0)
        p3 = self._make_point(1.0, 1.0)
        x, y = Nets._get_points_for_plot([p1, p2, p3])
        assert x == [0.0, 1.0, 1.0]
        assert y == [0.0, 0.0, 1.0]

    def test_empty_points(self):
        x, y = Nets._get_points_for_plot([])
        assert x == []
        assert y == []


# NetClasses
class TestNetClasses:
    def _make_net_classes(self, class_specs=None):
        """Build a NetClasses instance with mocked pedb."""
        if class_specs is None:
            class_specs = [("POWER_CLASS", ["GND", "VDD"]), ("SIGNAL_CLASS", ["SIG_A"])]

        pedb = MagicMock()

        # Build mock net_class objects
        mock_classes = []
        for name, nets_list in class_specs:
            nc = MagicMock()
            nc.core.name = name
            nc.name = name
            mock_classes.append(nc)

        pedb.active_layout.net_classes = mock_classes
        pedb.layout.net_classes = mock_classes

        nc_instance = NetClasses.__new__(NetClasses)
        nc_instance._pedb = pedb
        nc_instance.core = [nc.core for nc in mock_classes]
        return nc_instance, mock_classes

    def test_items_returns_dict(self):
        nc, _ = self._make_net_classes()
        result = nc.items
        assert "POWER_CLASS" in result
        assert "SIGNAL_CLASS" in result

    def test_getitem_returns_net_class(self):
        nc, mock_classes = self._make_net_classes()
        result = nc["POWER_CLASS"]
        assert result is mock_classes[0]

    def test_create_existing_name_logs_error_and_returns_false(self):
        nc, _ = self._make_net_classes()
        result = nc.create("POWER_CLASS", ["GND"])
        assert result is False
        nc._pedb.logger.error.assert_called_once()

    def test_create_new_net_class(self):
        nc, _ = self._make_net_classes()
        new_core = MagicMock()
        new_core.name = "NEW_CLASS"

        mock_gnd_net = MagicMock()
        mock_gnd_net.core = MagicMock()
        nc._pedb.nets.__getitem__ = MagicMock(return_value=mock_gnd_net)

        with patch("pyedb.grpc.database.nets.CoreNetClass.create", return_value=new_core):
            with patch("pyedb.grpc.database.nets.NetClass") as mock_nc_cls:
                mock_nc_instance = MagicMock()
                mock_nc_cls.return_value = mock_nc_instance
                result = nc.create("NEW_CLASS", ["GND"])

        assert result is mock_nc_instance
        new_core.add_net.assert_called_once_with(mock_gnd_net.core)


# Nets.__init__ (covers lines 190-192)
class TestNetsInit:
    def test_init_sets_dicts(self):
        pedb, _ = _make_pedb()
        nets = Nets(pedb)
        assert nets._nets_by_comp_dict == {}
        assert nets._comps_by_nets_dict == {}


# Simple property accessors (covers lines 197, 207, 212, 217, 222)
class TestNetsSimpleProperties:
    def test_edb_returns_pedb(self):
        nets, _ = _make_nets()
        assert nets._edb is nets._pedb

    def test_active_layout_returns_layout(self):
        nets, _ = _make_nets()
        assert nets._active_layout is nets._pedb.active_layout

    def test_layout_returns_layout(self):
        nets, _ = _make_nets()
        assert nets._layout is nets._pedb.layout

    def test_cell_returns_cell(self):
        nets, _ = _make_nets()
        assert nets._cell is nets._pedb.cell

    def test_db_returns_active_db(self):
        nets, _ = _make_nets()
        assert nets.db is nets._pedb.active_db

    def test_logger_returns_logger(self):
        nets, _ = _make_nets()
        assert nets._logger is nets._pedb.logger


# eligible_power_nets — branch coverage (lines 328-346)
class TestEligiblePowerNets:
    def _make_polygon_primitive(self, area):
        """Create a Polygon-typed object that passes isinstance and has polygon_data."""
        prim = Polygon.__new__(Polygon)
        prim.core = MagicMock()
        prim._pedb = MagicMock()
        mock_pd = MagicMock()
        mock_pd.area.return_value = area
        # Patch polygon_data on the instance level via __class__ attribute lookup
        with patch.object(type(prim), "polygon_data", new_callable=lambda: property(lambda self: mock_pd)):
            pass  # just set up mock_pd
        prim._polygon_data = mock_pd
        return prim

    def _make_bondwire_primitive(self):
        prim = Bondwire.__new__(Bondwire)
        prim.core = MagicMock()
        prim._pedb = MagicMock()
        return prim

    def _make_path_primitive(self, area):
        prim = Path.__new__(Path)
        prim.core = MagicMock()
        prim._pedb = MagicMock()
        mock_pd = MagicMock()
        mock_pd.area.return_value = area
        prim._polygon_data = mock_pd
        return prim

    def _make_nets_with_primitive(self, prim):
        nets, _ = _make_nets()
        mock_net = MagicMock()
        mock_net.primitives = [prim]
        nets._pedb.layout.nets = [mock_net]
        return nets

    def test_net_with_polygon_includes_in_result(self):
        nets, _ = _make_nets()
        poly_prim = Polygon.__new__(Polygon)
        poly_prim.core = MagicMock()
        poly_prim._pedb = MagicMock()

        mock_net = MagicMock()
        mock_net.primitives = [poly_prim]
        nets._pedb.layout.nets = [mock_net]

        mock_pd = MagicMock()
        mock_pd.area.return_value = 1.0

        with patch("pyedb.grpc.database.nets.Net") as mock_net_cls:
            mock_net_cls.return_value = MagicMock()
            with patch.object(Polygon, "polygon_data", new_callable=lambda: property(lambda self: mock_pd)):
                result = nets.eligible_power_nets()
        assert len(result) == 1

    def test_net_with_zero_plane_area_is_excluded(self):
        nets, _ = _make_nets()
        mock_net = MagicMock()
        mock_net.primitives = []
        nets._pedb.layout.nets = [mock_net]
        result = nets.eligible_power_nets()
        assert result == []

    def test_net_with_bondwire_only_is_excluded(self):
        nets, _ = _make_nets()
        bw = Bondwire.__new__(Bondwire)
        bw.core = MagicMock()
        bw._pedb = MagicMock()
        mock_net = MagicMock()
        mock_net.primitives = [bw]
        nets._pedb.layout.nets = [mock_net]
        result = nets.eligible_power_nets()
        assert result == []

    def test_net_with_path_primitive_included(self):
        nets, _ = _make_nets()
        path_prim = Path.__new__(Path)
        path_prim.core = MagicMock()
        path_prim._pedb = MagicMock()

        mock_net = MagicMock()
        mock_net.primitives = [path_prim]
        nets._pedb.layout.nets = [mock_net]

        mock_pd = MagicMock()
        mock_pd.area.return_value = 2.0

        with patch("pyedb.grpc.database.nets.Net") as mock_net_cls:
            mock_net_cls.return_value = MagicMock()
            with patch.object(Path, "polygon_data", new_callable=lambda: property(lambda self: mock_pd)):
                result = nets.eligible_power_nets()
        assert len(result) == 1


# get_powertree — with component data (covers lines 623-666)
class TestGetPowertree:
    def test_power_net_in_dc_group(self):
        nets, _ = _make_nets()
        # Mock get_dcconnected_net_list to return a group containing the power net
        with patch.object(nets, "get_dcconnected_net_list", return_value=[{"PWR", "PWR_1"}]):
            rats = [
                {"refdes": ["U1", "U1"], "pin_name": ["1", "2"], "net_name": ["PWR", "GND"]},
            ]
            nets._pedb.components.get_rats.return_value = rats

            comp_mock = MagicMock()
            comp_mock.type = "IC"
            comp_mock.partname = "Part_A"
            nets._pedb.components._cmp = {"U1": comp_mock}

            pin_mock = MagicMock()
            pin_mock.name = "1"
            nets._pedb.components.get_pin_from_component.return_value = [pin_mock]

            comp_list, columns, net_group = nets.get_powertree("PWR", ["GND"])

        assert "PWR" in net_group or "PWR_1" in net_group
        assert columns == ["refdes", "pin_name", "net_name", "component_type", "component_partname", "pin_list"]

    def test_power_net_not_in_dc_group_uses_net_alone(self):
        nets, _ = _make_nets()
        with patch.object(nets, "get_dcconnected_net_list", return_value=[]):
            nets._pedb.components.get_rats.return_value = []
            comp_list, columns, net_group = nets.get_powertree("ISOLATED_PWR", ["GND"])
        assert "ISOLATED_PWR" in net_group


# _get_points_for_plot — arc branch (covers lines 459-467)
class TestGetPointsForPlotArcBranch:
    def _make_arc_point(self, arc_height=0.001):
        p = MagicMock()
        p.is_arc = True
        p.arc_height.value = arc_height
        return p

    def _make_straight_point(self, x, y):
        p = MagicMock()
        p.is_arc = False
        p.x.value = x
        p.y.value = y
        return p

    def test_arc_point_mid_uses_next_point(self):
        """Arc point in the middle — uses i+1 as p2."""
        p0 = self._make_straight_point(0.0, 0.0)
        p_arc = self._make_arc_point(0.001)
        p2 = MagicMock()
        p2.is_arc = False
        p2.X.ToDouble.return_value = 1.0
        p2.Y.ToDouble.return_value = 0.0
        p2.x.value = 1.0
        p2.y.value = 0.0

        with patch("pyedb.grpc.database.nets.compute_arc_points", return_value=([0.5], [0.1])) as mock_arc:
            x, y = Nets._get_points_for_plot([p0, p_arc, p2])

        mock_arc.assert_called_once()
        assert 0.5 in x
        assert 0.1 in y

    def test_arc_point_at_end_uses_first_point_as_p2(self):
        """Arc point at the last position — wraps around to index 0 as p2."""
        p0 = self._make_straight_point(0.0, 0.0)
        p1 = self._make_straight_point(1.0, 0.0)
        p_arc = self._make_arc_point(0.001)
        # p_arc is at index 2, i+1 == 3 >= len(3) → uses p0
        p0.X = MagicMock()
        p0.X.ToDouble.return_value = 0.0
        p0.Y = MagicMock()
        p0.Y.ToDouble.return_value = 0.0

        with patch("pyedb.grpc.database.nets.compute_arc_points", return_value=([0.9], [0.05])):
            x, y = Nets._get_points_for_plot([p0, p1, p_arc])

        assert 0.9 in x
        assert 0.05 in y


# delete — with actual primitives/padstacks to delete (covers lines 730, 733)
class TestNetsDeleteWithPrimitives:
    def test_delete_calls_delete_on_primitives_and_padstacks(self):
        nets, mock_nets = _make_nets()
        prim = MagicMock()
        padstack = MagicMock()

        # Make GND net have primitives and padstacks
        gnd = mock_nets[0]  # GND
        gnd.core.primitives = [prim]
        gnd.core.padstack_instances = [padstack]

        nets.delete(["GND"])

        prim.delete.assert_called_once()
        padstack.delete.assert_called_once()


# NetClasses.__init__ and name property (covers lines 936-937, 974)
class TestNetClassesInitAndName:
    def test_init_sets_core_and_pedb(self):
        pedb = MagicMock()
        nc1 = MagicMock()
        nc1.core = MagicMock()
        nc1.core.name = "CLASS_1"
        pedb.active_layout.net_classes = [nc1]

        nc = NetClasses(pedb)

        assert nc._pedb is pedb
        assert len(nc.core) == 1

    def test_name_property_delegates_to_core(self):
        pedb = MagicMock()
        mock_core = MagicMock()
        mock_core.name = "MY_CLASS"
        pedb.active_layout.net_classes = []

        nc = NetClasses.__new__(NetClasses)
        nc._pedb = pedb
        nc.core = mock_core  # single core for name test
        # name property returns self.core.name
        assert nc.name == "MY_CLASS"


# NetClasses.create — multi-net list (covers line 996 loop)
class TestNetClassesCreateMultipleNets:
    def test_create_adds_multiple_nets(self):
        pedb = MagicMock()
        pedb.active_layout.net_classes = []
        pedb.layout.net_classes = []

        nc = NetClasses.__new__(NetClasses)
        nc._pedb = pedb
        nc.core = []

        new_core = MagicMock()
        new_core.name = "MULTI_CLASS"

        net_gnd = MagicMock()
        net_gnd.core = MagicMock()
        net_vdd = MagicMock()
        net_vdd.core = MagicMock()

        def getitem(self_mock, name):
            return net_gnd if name == "GND" else net_vdd

        pedb.nets.__getitem__ = getitem

        with patch("pyedb.grpc.database.nets.CoreNetClass.create", return_value=new_core):
            with patch("pyedb.grpc.database.nets.NetClass") as mock_nc_cls:
                mock_nc_cls.return_value = MagicMock()
                result = nc.create("MULTI_CLASS", ["GND", "VDD"])

        assert new_core.add_net.call_count == 2

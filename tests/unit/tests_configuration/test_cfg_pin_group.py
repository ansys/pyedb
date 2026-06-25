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

from pyedb.configuration.cfg_pin_groups import CfgPinGroup, CfgPinGroups

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgPinGroup:
    def test_with_pins(self):
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pins=["A1", "A2"])
        d = pg.export_properties()
        assert d["pins"] == ["A1", "A2"]
        assert "net" not in d

    def test_with_net(self):
        pg = CfgPinGroup(name="pg2", reference_designator="U1", net="VDD")
        d = pg.export_properties()
        assert d["net"] == "VDD"
        assert "pins" not in d

    def test_with_both_pins_and_net(self):
        pg = CfgPinGroup(name="pg3", reference_designator="U1", pins=["A1"], net="GND")
        d = pg.export_properties()
        assert d["pins"] == ["A1"]
        assert d["net"] == "GND"

    def test_pedb_excluded_from_export(self):
        mock_pedb = MagicMock()
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pins=["A1"], pedb=mock_pedb)
        d = pg.export_properties()
        assert "pedb" not in d

    def test_pedb_transferred_to_private(self):
        mock_pedb = MagicMock()
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pedb=mock_pedb)
        assert pg._pedb is mock_pedb

    def test_create_no_pedb_returns_export(self):
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pins=["A1", "A2"])
        result = pg.create()
        assert result == pg.export_properties()

    def test_create_with_pedb_and_pins(self):
        mock_pedb = MagicMock()
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pins=["A1", "A2"], pedb=mock_pedb)
        pg.create()
        mock_pedb.siwave.create_pin_group.assert_called_once_with("U1", ["A1", "A2"], "pg1")

    def test_create_with_pedb_and_net(self):
        mock_pin = MagicMock()
        mock_pin.net_name = "VDD"
        mock_comp = MagicMock()
        mock_comp.pins = {"A1": mock_pin, "A2": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.components.instances = {"U1": mock_comp}
        mock_pedb.siwave.create_pin_group.return_value = True
        pg = CfgPinGroup(name="pg1", reference_designator="U1", net="VDD", pedb=mock_pedb)
        pg.create()
        mock_pedb.siwave.create_pin_group.assert_called_once()

    def test_create_with_pedb_net_raises_on_failure(self):
        mock_pin = MagicMock()
        mock_pin.net_name = "VDD"
        mock_comp = MagicMock()
        mock_comp.pins = {"A1": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.components.instances = {"U1": mock_comp}
        mock_pedb.siwave.create_pin_group.return_value = False
        pg = CfgPinGroup(name="pg1", reference_designator="U1", net="VDD", pedb=mock_pedb)
        with pytest.raises(RuntimeError):
            pg.create()

    def test_create_no_pins_no_net_raises(self):
        mock_pedb = MagicMock()
        pg = CfgPinGroup(name="pg1", reference_designator="U1", pedb=mock_pedb)
        with pytest.raises(RuntimeError):
            pg.create()

    def test_minimal_export(self):
        pg = CfgPinGroup(name="pg1")
        d = pg.export_properties()
        assert d == {"name": "pg1"}


class TestCfgPinGroups:
    def test_empty(self):
        assert CfgPinGroups().export_properties() == []

    def test_add_with_net(self):
        pgs = CfgPinGroups()
        pg = pgs.add(name="pg1", reference_designator="U1", net="VDD")
        assert isinstance(pg, CfgPinGroup)
        lst = pgs.export_properties()
        assert len(lst) == 1
        assert lst[0]["name"] == "pg1"

    def test_add_with_pins(self):
        pgs = CfgPinGroups()
        pgs.add(name="pg1", reference_designator="U1", pins=["A1", "A2"])
        assert pgs.export_properties()[0]["pins"] == ["A1", "A2"]

    def test_add_auto_name_from_net(self):
        pgs = CfgPinGroups()
        pg = pgs.add(reference_designator="U1", nets="VDD")
        assert pg.name == "Pingroup_U1.VDD"

    def test_add_auto_name_from_pins(self):
        pgs = CfgPinGroups()
        pg = pgs.add(reference_designator="U1", pins=["A1"])
        assert pg.name == "Pingroup_U1"

    def test_add_nets_alias(self):
        """net= kwarg is accepted as alias for nets=."""
        pgs = CfgPinGroups()
        pg = pgs.add(name="pg1", reference_designator="U1", net="GND")
        assert pg.net == "GND"

    def test_add_multi_net(self):
        pgs = CfgPinGroups()
        result = pgs.add(reference_designator="U1", nets=["VDD", "GND"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "Pingroup_U1.VDD"
        assert result[1].name == "Pingroup_U1.GND"

    def test_multiple(self):
        pgs = CfgPinGroups()
        pgs.add(name="pg1", reference_designator="U1", pins=["A1"])
        pgs.add(name="pg2", reference_designator="U2", net="GND")
        assert len(pgs.export_properties()) == 2

    def test_init_from_data(self):
        data = [{"name": "pg1", "reference_designator": "U1", "pins": ["A1", "A2"]}]
        pgs = CfgPinGroups(pin_group_data=data)
        assert len(pgs.pin_groups) == 1
        assert pgs.pin_groups[0].name == "pg1"

    def test_init_pingroup_data_alias(self):
        data = [{"name": "pg1", "reference_designator": "U1"}]
        pgs = CfgPinGroups(pingroup_data=data)
        assert len(pgs.pin_groups) == 1

    def test_get_cached(self):
        pgs = CfgPinGroups()
        pg = pgs.add(name="pg1", reference_designator="U1", pins=["A1"])
        result = pgs.get("pg1")
        assert result is pg

    def test_get_raises_without_pedb(self):
        pgs = CfgPinGroups()
        with pytest.raises(KeyError):
            pgs.get("missing")

    def test_get_raises_when_not_found_in_edb(self):
        mock_pedb = MagicMock()
        mock_pedb.siwave.pin_groups = {}
        pgs = CfgPinGroups(pedb=mock_pedb)
        with pytest.raises(KeyError):
            pgs.get("missing")

    def test_get_data_from_edb_without_pedb(self):
        pgs = CfgPinGroups()
        pgs.add(name="pg1", reference_designator="U1", pins=["A1"])
        result = pgs.get_data_from_edb()
        assert result == []

    def test_get_data_from_db_delegates(self):
        pgs = CfgPinGroups()
        result = pgs.get_data_from_db()
        assert result == []

    def test_apply_calls_create(self):
        mock_pedb = MagicMock()
        pgs = CfgPinGroups(pedb=mock_pedb)
        pgs.add(name="pg1", reference_designator="U1", pins=["A1", "A2"])
        pgs.apply()
        mock_pedb.siwave.create_pin_group.assert_called_once_with("U1", ["A1", "A2"], "pg1")

    def test_set_pingroup_to_edb_alias(self):
        """set_pingroup_to_edb is an alias for set_pin_groups_to_edb."""
        pgs = CfgPinGroups()
        assert pgs.set_pingroup_to_edb == pgs.set_pin_groups_to_edb

    def test_add_multi_net_with_pedb(self):
        """Multi-net add with pedb resolves pins via _resolve_pins."""
        mock_pin_vdd = MagicMock()
        mock_pin_vdd.net_name = "VDD"
        mock_pin_gnd = MagicMock()
        mock_pin_gnd.net_name = "GND"
        mock_comp = MagicMock()
        mock_comp.pins = {"A1": mock_pin_vdd, "A2": mock_pin_vdd, "B1": mock_pin_gnd, "B2": mock_pin_gnd}
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = mock_comp
        pgs = CfgPinGroups(pedb=mock_pedb)
        result = pgs.add(reference_designator="U1", nets=["VDD", "GND"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "Pingroup_U1.VDD"
        assert result[1].name == "Pingroup_U1.GND"

    def test_add_single_net_with_pedb(self):
        """Single-net add with pedb resolves pins via _resolve_pins."""
        mock_pin = MagicMock()
        mock_pin.net_name = "VDD"
        mock_comp = MagicMock()
        mock_comp.pins = {"A1": mock_pin, "A2": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = mock_comp
        pgs = CfgPinGroups(pedb=mock_pedb)
        pg = pgs.add(name="pg_VDD", reference_designator="U1", nets="VDD")
        assert pg is not None
        assert pg.name == "pg_VDD"
        assert "A1" in pg.pins or "A2" in pg.pins

    def test_resolve_pins_component_not_found(self):
        """_resolve_pins raises KeyError when component is missing."""
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = None
        pgs = CfgPinGroups(pedb=mock_pedb)
        with pytest.raises(KeyError, match="U_MISSING"):
            pgs._resolve_pins("U_MISSING", "VDD", "pg")

    def test_resolve_pins_no_matching_pins(self):
        """_resolve_pins raises ValueError when no pins on net."""
        mock_comp = MagicMock()
        mock_comp.pins = {}
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = mock_comp
        pgs = CfgPinGroups(pedb=mock_pedb)
        with pytest.raises(ValueError, match="No pins found"):
            pgs._resolve_pins("U1", "MISSING_NET", "pg")

    def test_get_from_edb(self):
        """get() loads pin group from EDB when not cached."""
        mock_pin = MagicMock()
        mock_pin.component.name = "U1"
        mock_pg_obj = MagicMock()
        mock_pg_obj.pins = {"A1": mock_pin, "A2": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.siwave.pin_groups = {"pg_VDD": mock_pg_obj}
        pgs = CfgPinGroups(pedb=mock_pedb)
        pg = pgs.get("pg_VDD")
        assert pg.name == "pg_VDD"
        assert pg.reference_designator == "U1"

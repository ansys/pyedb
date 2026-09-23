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

from contextlib import ExitStack
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

pytest.importorskip("pyedb.dotnet.database.padstack", reason="Requires .NET runtime")
from pyedb.dotnet.database.padstack import EdbPadstacks

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.padstacks = EdbPadstacks(MagicMock())

    @patch("pyedb.dotnet.database.padstack.EdbPadstacks.definitions", new_callable=PropertyMock)
    def test_padstack_plating_ratio_fixing(self, mock_definitions):
        """Fix hole plating ratio."""
        mock_definitions.return_value = {
            "definition_0": MagicMock(hole_plating_ratio=-0.1),
            "definition_1": MagicMock(hole_plating_ratio=0.3),
        }
        assert self.padstacks["definition_0"].hole_plating_ratio == -0.1
        self.padstacks.check_and_fix_via_plating()
        assert self.padstacks["definition_0"].hole_plating_ratio == 0.2
        assert self.padstacks["definition_1"].hole_plating_ratio == 0.3


# Unit tests for the gRPC Padstacks class (no EDB licence required)
@pytest.mark.unit
@pytest.mark.no_licence
@pytest.mark.grpc
class TestGrpcPadstacksStatic:
    """Tests for pure-static / licence-free helpers in the gRPC Padstacks class."""

    @pytest.fixture(autouse=True)
    def import_padstacks(self):
        """Import the gRPC Padstacks class; skip if ansys-edb-core is unavailable."""
        pytest.importorskip("ansys.edb.core", reason="ansys-edb-core not installed")
        from pyedb.grpc.database.padstacks import GEOMETRY_MAP, PAD_TYPE_MAP, Padstacks

        self.Padstacks = Padstacks
        self.GEOMETRY_MAP = GEOMETRY_MAP
        self.PAD_TYPE_MAP = PAD_TYPE_MAP

    # int_to_pad_type
    def test_int_to_pad_type_known_values(self):
        """int_to_pad_type maps 0..4 to the correct CorePadType members."""
        from ansys.edb.core.definition.padstack_def_data import PadType as CorePadType

        assert self.Padstacks.int_to_pad_type(0) == CorePadType.REGULAR_PAD
        assert self.Padstacks.int_to_pad_type(1) == CorePadType.ANTI_PAD
        assert self.Padstacks.int_to_pad_type(2) == CorePadType.THERMAL_PAD
        assert self.Padstacks.int_to_pad_type(3) == CorePadType.HOLE
        assert self.Padstacks.int_to_pad_type(4) == CorePadType.UNKNOWN_GEOM_TYPE

    def test_int_to_pad_type_unknown_passthrough(self):
        """int_to_pad_type returns the raw value for an unmapped integer."""
        sentinel = 99
        assert self.Padstacks.int_to_pad_type(sentinel) == sentinel

    # int_to_geometry_type
    def test_int_to_geometry_type_known_values(self):
        """int_to_geometry_type maps 0..11 to the correct CorePadGeometryType members."""
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType as CorePadGeometryType

        assert self.Padstacks.int_to_geometry_type(0) == CorePadGeometryType.PADGEOMTYPE_NO_GEOMETRY
        assert self.Padstacks.int_to_geometry_type(1) == CorePadGeometryType.PADGEOMTYPE_CIRCLE
        assert self.Padstacks.int_to_geometry_type(7) == CorePadGeometryType.PADGEOMTYPE_POLYGON
        assert self.Padstacks.int_to_geometry_type(11) == CorePadGeometryType.PADGEOMTYPE_SQUARE90

    def test_int_to_geometry_type_unknown_passthrough(self):
        """int_to_geometry_type returns the raw value for an unmapped integer."""
        assert self.Padstacks.int_to_geometry_type(42) == 42

    # layers_between
    def test_layers_between_full_span(self):
        """layers_between returns all layers when start/stop are first/last."""
        layers = ["L1", "L2", "L3", "L4"]
        padstacks = self.Padstacks.__new__(self.Padstacks)
        result = padstacks.layers_between(layers, start_layer="L1", stop_layer="L4")
        assert result == layers

    def test_layers_between_partial_span(self):
        """layers_between returns the correct sub-list."""
        layers = ["L1", "L2", "L3", "L4", "L5"]
        padstacks = self.Padstacks.__new__(self.Padstacks)
        result = padstacks.layers_between(layers, start_layer="L2", stop_layer="L4")
        assert result == ["L2", "L3", "L4"]

    def test_layers_between_reversed_order(self):
        """layers_between works regardless of which end is start vs stop."""
        layers = ["L1", "L2", "L3", "L4"]
        padstacks = self.Padstacks.__new__(self.Padstacks)
        result = padstacks.layers_between(layers, start_layer="L3", stop_layer="L1")
        assert result == ["L1", "L2", "L3"]

    def test_layers_between_empty_input(self):
        """layers_between returns an empty list when layers is empty."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        assert padstacks.layers_between([], start_layer="L1", stop_layer="L2") == []

    def test_layers_between_missing_start_defaults_to_zero(self):
        """layers_between uses index 0 when start_layer is not in the list."""
        layers = ["L1", "L2", "L3"]
        padstacks = self.Padstacks.__new__(self.Padstacks)
        assert padstacks.layers_between(layers, start_layer="MISSING", stop_layer="L2") == ["L1", "L2"]

    def test_layers_between_missing_stop_defaults_to_last(self):
        """layers_between uses the last index when stop_layer is not in the list."""
        layers = ["L1", "L2", "L3"]
        padstacks = self.Padstacks.__new__(self.Padstacks)
        assert padstacks.layers_between(layers, start_layer="L2", stop_layer="MISSING") == ["L2", "L3"]

    # dbscan
    def test_dbscan_single_cluster(self):
        """dbscan groups tightly spaced points into one cluster."""
        padstack = {i: [i * 0.0001, 0.0] for i in range(10)}
        clusters = self.Padstacks.dbscan(padstack, max_distance=1e-3, min_samples=3)
        # All 10 points fit within max_distance; one cluster (label 0)
        assert 0 in clusters
        assert len(clusters[0]) == 10

    def test_dbscan_noise_points(self):
        """dbscan marks isolated points as noise (label -1)."""
        # 6 tight points and 1 outlier far away
        padstack = {i: [i * 0.0001, 0.0] for i in range(6)}
        padstack[99] = [1.0, 1.0]  # isolated outlier
        clusters = self.Padstacks.dbscan(padstack, max_distance=1e-3, min_samples=3)
        assert -1 in clusters
        assert 99 in clusters[-1]

    def test_dbscan_two_clusters(self):
        """dbscan identifies two spatially separated clusters."""
        group1 = {i: [i * 0.0001, 0.0] for i in range(6)}
        group2 = {100 + i: [1.0 + i * 0.0001, 0.0] for i in range(6)}
        padstack = {**group1, **group2}
        clusters = self.Padstacks.dbscan(padstack, max_distance=1e-3, min_samples=3)
        cluster_labels = [k for k in clusters if k >= 0]
        assert len(cluster_labels) == 2
        total = sum(len(v) for k, v in clusters.items() if k >= 0)
        assert total == 12

    def test_dbscan_empty_input(self):
        """dbscan returns an empty dict for an empty input."""
        clusters = self.Padstacks.dbscan({}, max_distance=1e-3, min_samples=3)
        assert clusters == {}

    # clear_instances_cache
    def test_clear_instances_cache(self):
        """clear_instances_cache resets both instance caches to empty dicts."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        padstacks._instances_by_name = {"a": MagicMock()}
        padstacks._instances_by_net = {"GND": [MagicMock()]}
        padstacks.clear_instances_cache()
        assert padstacks._instances_by_name == {}
        assert padstacks._instances_by_net == {}

    # __getitem__
    def test_getitem_by_definition_name(self):
        """__getitem__ returns a definition when name matches a definition key."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        mock_def = MagicMock()
        with (
            patch.object(type(padstacks), "instances", new_callable=PropertyMock) as mock_inst,
            patch.object(type(padstacks), "definitions", new_callable=PropertyMock) as mock_defs,
        ):
            mock_defs.return_value = {"myVia": mock_def}
            mock_inst.return_value = {}
            result = padstacks["myVia"]
        assert result is mock_def

    def test_getitem_by_instance_id(self):
        """__getitem__ returns an instance when an integer ID is provided."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        mock_instance = MagicMock()
        with (
            patch.object(type(padstacks), "instances", new_callable=PropertyMock) as mock_inst,
            patch.object(type(padstacks), "definitions", new_callable=PropertyMock) as mock_defs,
        ):
            mock_inst.return_value = {42: mock_instance}
            mock_defs.return_value = {}
            result = padstacks[42]
        assert result is mock_instance

    def test_getitem_by_instance_name(self):
        """__getitem__ searches instances by name when key is a string not in definitions."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        mock_instance = MagicMock()
        mock_instance.name = "Via123"
        mock_instance.aedt_name = "Via123"
        with (
            patch.object(type(padstacks), "instances", new_callable=PropertyMock) as mock_inst,
            patch.object(type(padstacks), "definitions", new_callable=PropertyMock) as mock_defs,
        ):
            mock_inst.return_value = {1: mock_instance}
            mock_defs.return_value = {}
            result = padstacks["Via123"]
        assert result is mock_instance

    def test_getitem_returns_none_when_not_found(self):
        """__getitem__ returns None when neither a definition nor an instance matches."""
        padstacks = self.Padstacks.__new__(self.Padstacks)
        mock_instance = MagicMock()
        mock_instance.name = "Other"
        mock_instance.aedt_name = "Other"
        with (
            patch.object(type(padstacks), "instances", new_callable=PropertyMock) as mock_inst,
            patch.object(type(padstacks), "definitions", new_callable=PropertyMock) as mock_defs,
        ):
            mock_inst.return_value = {1: mock_instance}
            mock_defs.return_value = {}
            result = padstacks["nonexistent"]
        assert result is None


@pytest.mark.unit
@pytest.mark.no_licence
@pytest.mark.grpc
class TestGrpcPadstackInstanceConvertHoleToConicalShape:
    """Regression tests for ``PadstackInstance.convert_hole_to_conical_shape``.

    With the gRPC backend, ``Structure3D.set_material`` raises a ``RuntimeError`` when called with an
    empty string (``"string value 'material name' cannot be empty."``). This can happen when the padstack
    definition hole material is not set. The method must default to ``"copper"`` in that case, matching
    the behaviour already implemented in :class:`PadstackDef`.
    """

    @pytest.fixture(autouse=True)
    def import_padstack_instance(self):
        """Import the gRPC PadstackInstance class; skip if ansys-edb-core is unavailable."""
        pytest.importorskip("ansys.edb.core", reason="ansys-edb-core not installed")
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        self.PadstackInstance = PadstackInstance

    def _build_instance(self, material):
        """Build a bare PadstackInstance with the minimal mocked context required by the method."""
        instance = self.PadstackInstance.__new__(self.PadstackInstance)
        instance.core = MagicMock()

        pedb = MagicMock()
        pedb._value_setter = lambda value: value

        top_layer = MagicMock(thickness=0.0)
        diel_layer = MagicMock(thickness=0.0002)
        bottom_layer = MagicMock(thickness=0.0)
        pedb.stackup.layers = {"top": top_layer, "diel": diel_layer, "bottom": bottom_layer}
        pedb.stackup.signal_layers = {"top": top_layer, "bottom": bottom_layer}
        instance._pedb = pedb

        definition = MagicMock()
        definition.hole_diameter = 0.001
        definition.material = material
        definition.name = "PadstackDef1"
        return instance, definition

    def _run_with_mocks(self, instance, definition):
        """Run convert_hole_to_conical_shape with all required attributes patched, returning the mocked s3d."""
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(type(instance), "definition", new_callable=PropertyMock, return_value=definition)
            )
            stack.enter_context(
                patch.object(type(instance), "start_layer", new_callable=PropertyMock, return_value="top")
            )
            stack.enter_context(
                patch.object(type(instance), "stop_layer", new_callable=PropertyMock, return_value="bottom")
            )
            stack.enter_context(
                patch.object(type(instance), "position", new_callable=PropertyMock, return_value=[0.0, 0.0])
            )
            stack.enter_context(
                patch.object(type(instance), "net", new_callable=PropertyMock, return_value=MagicMock())
            )
            stack.enter_context(
                patch.object(type(instance), "aedt_name", new_callable=PropertyMock, return_value="via_1")
            )
            mock_circle_cls = stack.enter_context(patch("pyedb.grpc.database.primitive.padstack_instance.Circle"))
            mock_s3d_cls = stack.enter_context(patch("pyedb.grpc.database.primitive.padstack_instance.CoreStructure3D"))

            mock_circle_cls.return_value.create.return_value = MagicMock()
            mock_s3d = MagicMock()
            mock_s3d_cls.create.return_value = mock_s3d

            instance.convert_hole_to_conical_shape(angle=75)

        return mock_s3d

    def test_convert_hole_to_conical_shape_defaults_material_when_empty(self):
        """An empty hole material must be defaulted to copper before calling set_material (gRPC backend)."""
        instance, definition = self._build_instance(material="")
        instance._pedb.materials.__contains__ = MagicMock(return_value=False)
        instance._pedb.materials.default_conductor_property_values = {"conductivity": 58000000}

        mock_s3d = self._run_with_mocks(instance, definition)

        assert definition.material == "copper"
        instance._pedb.materials.add_conductor_material.assert_called_once_with("copper", 58000000)
        mock_s3d.set_material.assert_called_once_with("copper")

    def test_convert_hole_to_conical_shape_skips_add_material_when_copper_already_defined(self):
        """If ``copper`` is already defined in the material library, it must not be re-added."""
        instance, definition = self._build_instance(material="")
        instance._pedb.materials.__contains__ = MagicMock(return_value=True)

        mock_s3d = self._run_with_mocks(instance, definition)

        assert definition.material == "copper"
        instance._pedb.materials.add_conductor_material.assert_not_called()
        mock_s3d.set_material.assert_called_once_with("copper")

    def test_convert_hole_to_conical_shape_keeps_existing_material(self):
        """An already defined hole material must be passed through unchanged to set_material."""
        instance, definition = self._build_instance(material="gold")

        mock_s3d = self._run_with_mocks(instance, definition)

        assert definition.material == "gold"
        instance._pedb.materials.add_conductor_material.assert_not_called()
        mock_s3d.set_material.assert_called_once_with("gold")

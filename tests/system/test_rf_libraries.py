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

"""System tests for RF library components"""

import os

import pytest

from pyedb.libraries.common import MicroStripTechnologyStackup
from pyedb.libraries.rf_libraries.base_functions import (
    CPW,
    DifferentialTLine,
    HatchGround,
    InterdigitalCapacitor,
    MicroStripLine,
    RadialStub,
    RatRace,
    SpiralInductor,
)
from pyedb.libraries.rf_libraries.planar_antennas import (
    CircularPatch,
    RectangularPatch,
    TriangularPatch,
)
from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_stackup(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        stackup = MicroStripTechnologyStackup(edb)
        stackup.substrate.material.permittivity = 11.9
        assert stackup.substrate.material.permittivity == 11.9
        assert stackup.top_metal.name == "TOP_METAL"
        assert edb.stackup.layers["TOP_METAL"].material == "Gold"
        assert stackup.top_metal.material.conductivity == 5.8e7
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_cpw(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        cpw = CPW(
            edb_cell=edb,
            width=10e-6,
            gap=5e-6,
            layer="METAL_TOP",
            ground_net="GND",
            ground_layer="METAL_BOT",
            length=1e-3,
        )
        cpw.substrate.er = edb.materials["Silicon"].permittivity
        cpw.substrate.h = 100e-6
        cpw.create()
        assert round(cpw.analytical_z0, 3) == 10.678
        assert cpw.gap == 5e-6
        assert cpw.ground_layer == "METAL_BOT"
        assert len(edb.modeler.rectangles) == 4
        assert edb.modeler.rectangles[0].net.name == "SIG"
        assert edb.modeler.rectangles[0].bbox == [-5e-06, 0.0, 5e-06, 0.001]
        assert edb.variables["g"] == 5e-06
        assert edb.variables["w"] == 1e-05
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_diff_tline(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        pair = DifferentialTLine(edb, layer="METAL_TOP", length=10e-3, width=0.2e-3, spacing=0.18e-3)
        pair.create()
        assert round(pair.diff_impedance, 3) == 95.723
        assert len(edb.modeler.paths) == 2
        assert edb.modeler.paths[0].net.name == "P"
        assert edb.modeler.paths[0].center_line == [[0.0, 0.0], [0.01, 0.0]]
        edb.close(terminate_rpc_session=False)

    def test_hatch_grounded(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb, botton_layer_name="METAL_BOT")
        hatch = HatchGround(
            edb_cell=edb,
            width=100e-6,
            pitch=225e-6,
            fill_target=50.0,
            layer_gnd="METAL_BOT",
            ground_length=10e-3,
            ground_width=5e-3,
        )
        hatch.create()
        assert round(hatch.copper_fill_ratio, 2) == 69.75
        assert hatch.board_size == 0.01
        assert edb.modeler.polygons[0].net.name == "GND"
        assert len(edb.modeler.polygons[0].arcs) == 4
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_interdigited_capacitor(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        idc = InterdigitalCapacitor(
            edb_cell=edb,
            fingers=12,
            finger_length="0.9mm",
            finger_width="0.08mm",
            gap="0.04mm",
            comb_gap="0.06mm",
            bus_width="0.25mm",
            layer="METAL_TOP",
            net_a="P1",
            net_b="P2",
        )
        idc.substrate.er = edb.materials["Silicon"].permittivity
        idc.create()
        assert round(idc.capacitance_pf, 3) == 2.276
        assert len(edb.modeler.rectangles) == 26
        assert edb.modeler.rectangles[0].net.name == "P1"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_radial_stud(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        stub = RadialStub(edb, layer="METAL_TOP", width=200e-6, radius=1e-3)
        stub.create()
        assert round(stub.electrical_length_deg, 3) == 5.038
        assert edb.modeler.polygons[0].net.name == "RF"
        assert edb.modeler.rectangles[0].net.name == "RF"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_rat_race(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        rat_race = RatRace(
            edb_cell=edb,
            z0=50,
            freq=10e9,
            layer="METAL_TOP",
            net="RR",
            width=0.2e-3,
            nr_segments=32,
            bottom_layer="METAL_BOT",
        )
        rat_race.substrate.er = edb.materials["Silicon"].permittivity
        rat_race.create()
        assert round(rat_race.circumference, 3) == 0.013
        assert len(edb.modeler.paths) == 5
        assert edb.modeler.paths[0].net.name == "RR"
        edb.close(terminate_rpc_session=False)

    def test_spiral_inductor(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        edb.materials.add_dielectric_material(name="SiO2", permittivity=4, dielectric_loss_tangent=0)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        MicroStripTechnologyStackup(edb)
        edb.stackup.add_layer(
            layer_name="oxyde", base_layer="TOP_METAL", material="SiO2", thickness="4um", layer_type="dielectric"
        )
        edb.stackup.add_layer(
            layer_name="BRIDGE",
            base_layer="oxyde",
            material="Gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )
        edb.stackup.mode = "Overlapping"
        edb.stackup.add_layer(
            layer_name="via", material="Gold", thickness="4um", layer_type="signal", base_layer="BRIDGE"
        )
        edb.stackup.layers["via"].lower_elevation = edb.stackup.layers["TOP_METAL"].upper_elevation
        spiral = SpiralInductor(
            edb_cell=edb, turns=10, layer="TOP_METAL", bridge_layer="BRIDGE", via_layer="via", ground_layer="BOT_METAL"
        )
        spiral.substrate.er = edb.materials["Silicon"].permittivity
        spiral.substrate.h = 100e-6  # 100um
        assert round(spiral.inductance_nh, 3) == 59.599
        spiral.create()
        assert len(edb.modeler.rectangles) == 2
        assert len(edb.modeler.paths) == 2
        assert edb.modeler.paths[0].net.name == "IN"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_ustrip(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        MicroStripTechnologyStackup(edb)
        ustrip = MicroStripLine(edb_cell=edb, layer="METAL_TOP", net="Rf", length="2mm", freq=10e9)
        ustrip.create()
        assert ustrip.impedance == 48.7
        ustrip.width = "300um"
        assert ustrip.width == 300e-6
        assert ustrip.impedance == 37.52

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_patch_antenna(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        stackup = MicroStripTechnologyStackup(pedb=edb)
        stackup.substrate.thickness = 254e-6
        stackup.substrate.material.permittivity = 3.5
        patch_antenna = RectangularPatch(
            edb_cell=edb,
            length_feeding_line=5e-3,
            target_frequency="2.4Ghz",
            permittivity=stackup.substrate.material.permittivity,
        )
        patch_antenna.create()
        assert str(patch_antenna.estimated_frequency) == "1.928Ghz"
        assert patch_antenna.width == 0.04164
        assert patch_antenna.length == 0.03337
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_circular_patch_antenna(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        stackup = MicroStripTechnologyStackup(pedb=edb)
        stackup.substrate.thickness = 254e-6
        stackup.substrate.material.permittivity = 3.5
        patch_antenna = CircularPatch(edb_cell=edb, length_feeding_line=5e-3, target_frequency="2.4Ghz")
        patch_antenna.create()
        assert str(patch_antenna.estimated_frequency) == "2.412GHz"
        assert patch_antenna.radius == 0.0174
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="Need to check variable with grpc")
    def test_triangular_antenna(self, get_edb_examples):
        edb = get_edb_examples.create_empty_edb()
        stackup = MicroStripTechnologyStackup(pedb=edb)
        stackup.substrate.thickness = 254e-6
        stackup.substrate.material.permittivity = 3.5
        patch_antenna = TriangularPatch(edb_cell=edb, length_feeding_line=5e-3, target_frequency="2.4Ghz")
        patch_antenna.create()
        assert str(patch_antenna.estimated_frequency) == "2.43GHz"
        assert patch_antenna.side == 0.039201
        edb.close(terminate_rpc_session=False)

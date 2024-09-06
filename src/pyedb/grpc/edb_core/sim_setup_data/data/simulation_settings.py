# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list


class BaseSimulationSettings:
    def __init__(self, pedb, sim_setup, edb_object):
        self._pedb = pedb
        self._sim_setup = sim_setup
        self._edb_object = edb_object
        self._t_sim_setup_type = {
            "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
            "kPEM": None,
            "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }

    @property
    def enabled(self):
        return self._edb_object.Enabled

    @enabled.setter
    def enabled(self, value):
        self._edb_object.Enabled = value


class SimulationSettings(BaseSimulationSettings):
    def __init__(self, pedb, sim_setup, edb_object):
        super().__init__(pedb, sim_setup, edb_object)


class HFSSSimulationSettings(SimulationSettings):
    def __init__(self, pedb, sim_setup, edb_object):
        super().__init__(pedb, sim_setup, edb_object)

    @property
    def mesh_operations(self):
        return self._edb_object.MeshOperations


class HFSSPISimulationSettings(SimulationSettings):
    def __init__(self, pedb, sim_setup, edb_object):
        super().__init__(pedb, sim_setup, edb_object)

    @property
    def auto_select_nets_for_simulation(self):
        """Auto select nets for simulation.

        Returns
        -------
            bool
        """
        return self._edb_object.AutoSelectNetsForSimulation

    @auto_select_nets_for_simulation.setter
    def auto_select_nets_for_simulation(self, value: bool):
        self._edb_object.AutoSelectNetsForSimulation = value

    @property
    def ignore_dummy_nets_for_selected_nets(self):
        """Auto select Nets for simulation

        Returns
        -------
            bool
        """
        return self._edb_object.IgnoreDummyNetsForSelectedNets

    @ignore_dummy_nets_for_selected_nets.setter
    def ignore_dummy_nets_for_selected_nets(self, value):
        self._edb_object.IgnoreDummyNetsForSelectedNets = value

    @property
    def ignore_small_holes(self):
        """Ignore small holes choice.

        Returns
        -------
            bool
        """
        return self._edb_object.IgnoreSmallHoles

    @ignore_small_holes.setter
    def ignore_small_holes(self, value: bool):
        self._edb_object.IgnoreSmallHoles = value

    @property
    def ignore_small_holes_min_diameter(self):
        """Min diameter to ignore small holes.

        Returns
        -------
            str
        """
        value = self._edb_object.IgnoreSmallHolesMinDiameter
        return float(value) if value else value

    @ignore_small_holes_min_diameter.setter
    def ignore_small_holes_min_diameter(self, value):
        self._edb_object.IgnoreSmallHolesMinDiameter = self._pedb.edb_value(value).ToString()

    @property
    def improved_loss_model(self):
        """Improved Loss Model on power ground nets option.
        1: Level 1
        2: Level 2
        3: Level 3
        """
        levels = {"Level 1": 1, "Level 2": 2, "Level 3": 3}
        return levels[self._edb_object.ImprovedLossModel]

    @improved_loss_model.setter
    def improved_loss_model(self, value: int):
        levels = {1: "Level 1", 2: "Level 2", 3: "Level 3"}
        self._edb_object.ImprovedLossModel = levels[value]

    @property
    def include_enhanced_bond_wire_modeling(self):
        """Enhance Bond wire modeling.

        Returns
        -------
            bool
        """
        return self._edb_object.IncludeEnhancedBondWireModeling

    @include_enhanced_bond_wire_modeling.setter
    def include_enhanced_bond_wire_modeling(self, value: bool):
        self._edb_object.IncludeEnhancedBondWireModeling = value

    @property
    def include_nets(self):
        """Add Additional Nets for simulation.

        Returns
        -------
            [str]
            List of net name.
        """
        return list(self._edb_object.IncludeNets)

    @include_nets.setter
    def include_nets(self, value):
        value = value if isinstance(value, list) else [value]
        self._edb_object.IncludeNets = convert_py_list_to_net_list(value)

    @property
    def min_plane_area_to_mesh(self):
        """The minimum area below which geometry is ignored.

        Returns
        -------
            str
        """
        return self._edb_object.MinPlaneAreaToMesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        self._edb_object.MinPlaneAreaToMesh = self._pedb.edb_value(value).ToString()

    @property
    def min_void_area_to_mesh(self):
        """The minimum area below which voids are ignored.

        Returns
        -------
            str
        """
        return self._edb_object.MinVoidAreaToMesh

    @min_void_area_to_mesh.setter
    def min_void_area_to_mesh(self, value):
        self._edb_object.MinVoidAreaToMesh = self._pedb.edb_value(value).ToString()

    @property
    def model_type(self):
        """Model Type setting.

        0: RDL,
        1: Package
        2: PCB

        Returns
        -------
            int

        """
        return self._edb_object.ModelType

    @model_type.setter
    def model_type(self, value: int):
        self._edb_object.ModelType = value

    @property
    def perform_erc(self):
        """Perform ERC

        Returns
        -------
            bool
        """
        return self._edb_object.PerformERC

    @perform_erc.setter
    def perform_erc(self, value: bool):
        self._edb_object.PerformERC = value

    @property
    def pi_slider_pos(self):
        """The Simulation Preference Slider setting
        Model type: ``0``= balanced, ``1``=Accuracy.
        Returns
        -------
            int
        """
        return self._edb_object.PISliderPos

    @pi_slider_pos.setter
    def pi_slider_pos(self, value):
        self._edb_object.PISliderPos = value

    @property
    def rms_surface_roughness(self):
        """RMS Surface Roughness setting

        Returns
        -------
            str
        """
        return self._edb_object.RMSSurfaceRoughness

    @rms_surface_roughness.setter
    def rms_surface_roughness(self, value):
        self._edb_object.RMSSurfaceRoughness = self._pedb.edb_value(value).ToString()

    @property
    def signal_nets_conductor_modeling(self) -> int:
        """Conductor Modeling.
        0: MeshInside,
        1: ImpedanceBoundary
        """
        modelling_type = {
            "Mesh Inside": 0,
            "Impedance Boundary": 1,
        }

        return modelling_type[self._edb_object.SignalNetsConductorModeling]

    @signal_nets_conductor_modeling.setter
    def signal_nets_conductor_modeling(self, value: int):
        modelling_type = {
            0: "Mesh Inside",
            1: "Impedance Boundary",
        }
        self._edb_object.SignalNetsConductorModeling = modelling_type[value]

    @property
    def signal_nets_error_tolerance(self):
        """Error Tolerance

        Returns
        -------
            str
        Value between 0.02 and 1.
        """
        value = self._edb_object.SignalNetsErrorTolerance
        return "default" if value == "Default" else float(value)

    @signal_nets_error_tolerance.setter
    def signal_nets_error_tolerance(self, value):
        self._edb_object.SignalNetsErrorTolerance = self._pedb.edb_value(value).ToString()

    @property
    def signal_nets_include_improved_dielectric_fill_refinement(self):
        return self._edb_object.SignalNetsIncludeImprovedDielectricFillRefinement

    @signal_nets_include_improved_dielectric_fill_refinement.setter
    def signal_nets_include_improved_dielectric_fill_refinement(self, value: bool):
        self._edb_object.SignalNetsIncludeImprovedDielectricFillRefinement = value

    @property
    def signal_nets_include_improved_loss_handling(self):
        """Improved Dielectric Fill Refinement choice.

        Returns
        -------
            bool
        """
        return self._edb_object.SignalNetsIncludeImprovedLossHandling

    @signal_nets_include_improved_loss_handling.setter
    def signal_nets_include_improved_loss_handling(self, value: bool):
        self._edb_object.SignalNetsIncludeImprovedLossHandling = value

    @property
    def snap_length_threshold(self):
        return self._edb_object.SnapLengthThreshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        self._edb_object.SnapLengthThreshold = self._pedb.edb_value(value).ToString()

    @property
    def surface_roughness_model(self):
        """Chosen Model setting
        Model allowed, ``"None"``, ``"Exponential"`` or ``"Hammerstad"``.

        Returns
        -------
            str

        """
        model = {
            "None": 0,
            "Exponential": 1,
            "Hammerstad": 2,
        }
        return model[self._edb_object.SurfaceRoughnessModel]

    @surface_roughness_model.setter
    def surface_roughness_model(self, value):
        model = {
            0: "None",
            1: "Exponential",
            2: "Hammerstad",
        }
        self._edb_object.SurfaceRoughnessModel = model[value]

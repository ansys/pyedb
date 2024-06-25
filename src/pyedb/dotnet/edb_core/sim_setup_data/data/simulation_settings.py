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


class BaseSimulationSettings:
    def __init__(self, pedb, sim_setup, edb_object):
        self._pedb = pedb
        self.sim_setup = sim_setup
        self._edb_object = edb_object
        self.t_sim_setup_type = {
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
    def __init__(self, edb_setup_info, pedb, edb_object):
        super().__init__(pedb, edb_setup_info, edb_object)
        self._pedb = pedb
        self.logger = self._pedb.logger
        self._edb_setup_info = edb_setup_info
        self._simulation_settings = edb_setup_info.SimulationSettings

    @property
    def auto_select_nets_for_simulation(self):
        """Auto select nets for simulation.

        Returns
        -------
            bool
        """
        return self._simulation_settings.AutoSelectNetsForSimulation

    @auto_select_nets_for_simulation.setter
    def auto_select_nets_for_simulation(self, value):
        if isinstance(value, bool):
            self._simulation_settings.AutoSelectNetsForSimulation = value
        else:
            self.logger.error(
                "Property auto_select_nets_for_simulation expects a boolean "
                f"value while the provided value is {value}."
            )

    @property
    def enabled(self):
        return self._simulation_settings.Enabled

    @enabled.setter
    def enabled(self, value):
        if isinstance(value, bool):
            self._simulation_settings.Enabled = value
        else:
            self.logger.error(f"Property enabled expects a boolean value while the provided value is {value}.")

    @property
    def ignore_dummy_nets_for_selected_nets(self):
        """Auto select Nets for simulation

        Returns
        -------
            bool
        """
        return self._simulation_settings.IgnoreDummyNetsForSelectedNets

    @ignore_dummy_nets_for_selected_nets.setter
    def ignore_dummy_nets_for_selected_nets(self, value):
        if isinstance(value, bool):
            self._simulation_settings.IgnoreDummyNetsForSelectedNets = value
        else:
            self.logger.error(
                "Property ignore_dummy_nets_for_selected_nets expects a boolean "
                f"value while the provided value is {value}."
            )

    @property
    def ignore_small_holes(self):
        """Ignore small holes choice.

        Returns
        -------
            bool
        """
        return self._simulation_settings.IgnoreSmallHoles

    @ignore_small_holes.setter
    def ignore_small_holes(self, value):
        if isinstance(value, bool):
            self._simulation_settings.IgnoreSmallHoles = value
        else:
            self.logger.error(
                f"Property ignore_small_holes expects a boolean value while the provided value is {value}."
            )

    @property
    def ignore_small_holes_min_diameter(self):
        """Min diameter to ignore small holes.

        Returns
        -------
            str
        """
        return self._simulation_settings.IgnoreSmallHolesMinDiameter

    @ignore_small_holes_min_diameter.setter
    def ignore_small_holes_min_diameter(self, value):
        self._simulation_settings.IgnoreSmallHolesMinDiameter = self._pedb.edb_value(value).ToString()

    @property
    def improved_loss_model(self):
        """Improved Loss Model on power ground nets option.

        Returns
        -------
            str
            ``Level1``, ``Level2``, ``Level3``
        """
        return self._simulation_settings.ImprovedLossModel

    @improved_loss_model.setter
    def improved_loss_model(self, value):
        expected_values = ["Level1", "Level2", "Level3"]
        if isinstance(value, str) and value in expected_values:
            self._simulation_settings.ImprovedLossModel = value
        else:
            self.logger.error(
                "Property improved_loss_model expects a string value among "
                f"'Level1', 'Level2' or 'Level3' while the provided value is {value}."
            )

    @property
    def include_enhanced_bond_wire_modeling(self):
        """Enhance Bond wire modeling.

        Returns
        -------
            bool
        """
        return self._simulation_settings.IncludeEnhancedBondWireModeling

    @include_enhanced_bond_wire_modeling.setter
    def include_enhanced_bond_wire_modeling(self, value):
        if isinstance(value, bool):
            self._simulation_settings.IncludeEnhancedBondWireModeling = value
        else:
            self.logger.error(
                "Property include_enhanced_bond_wire_modeling expects a "
                f"boolean value while the provided value is {value}."
            )

    @property
    def include_nets(self):
        """Add Additional Nets for simulation.

        Returns
        -------
            [str]
            List of net name.
        """
        return list(self._simulation_settings.IncludeNets)

    @include_nets.setter
    def include_nets(self, value):
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            self._simulation_settings.IncludeNets = convert_py_list_to_net_list(value)
        else:
            self.logger.error(
                f"Property include_nets expects a string or list of string while the provided value is {value}."
            )

    @property
    def min_plane_area_to_mesh(self):
        """The minimum area below which geometry is ignored.

        Returns
        -------
            str
        """
        return self._simulation_settings.MinPlaneAreaToMesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        self._simulation_settings.MinPlaneAreaToMesh = self._pedb.edb_value(value).ToString()

    @property
    def min_void_area_to_mesh(self):
        """The minimum area below which voids are ignored.

        Returns
        -------
            str
        """
        return self._simulation_settings.MinVoidAreaToMesh

    @min_void_area_to_mesh.setter
    def min_void_area_to_mesh(self, value):
        self._simulation_settings.MinVoidAreaToMesh = self._pedb.edb_value(value).ToString()

    @property
    def model_type(self):
        """Model Type setting.

        Returns
        -------
            int
        Model type: ``0``=RDL, ``1``=Package, ``2``=PCB
        """
        return self._simulation_settings.ModelType

    @model_type.setter
    def model_type(self, value):
        if isinstance(value, int) and value in range(3):
            self._simulation_settings.ModelType = value
        else:
            self.logger.error(
                f"Property model_type expects an integer value among 0, 1 or 2 while the provided value is {value}."
            )

    @property
    def perform_erc(self):
        """Perform ERC

        Returns
        -------
            bool
        """
        return self._simulation_settings.PerformERC

    @perform_erc.setter
    def perform_erc(self, value):
        if isinstance(value, bool):
            self._simulation_settings.PerformERC = value
        else:
            self.logger.error(f"Property perform_erc expects a boolean value while the provided value is {value}.")

    @property
    def pi_slider_pos(self):
        """The Simulation Preference Slider setting

        Returns
        -------
            int
        Model type: ``0``= balanced, ``1``=Accuracy.
        """
        return self._simulation_settings.PISliderPos

    @pi_slider_pos.setter
    def pi_slider_pos(self, value):
        if isinstance(value, int) and value in range(2):
            self._simulation_settings.PISliderPos = value
        else:
            self.logger.error(
                f"Property pi_slider_pos expects an integer value among 0 or 1 while the provided value is {value}."
            )

    @property
    def rms_surface_roughness(self):
        """RMS Surface Roughness setting

        Returns
        -------
            str
        """
        return self._simulation_settings.RMSSurfaceRoughness

    @rms_surface_roughness.setter
    def rms_surface_roughness(self, value):
        self._simulation_settings.RMSSurfaceRoughness = self._pedb.edb_value(value).ToString()

    @property
    def signal_nets_conductor_modeling(self):
        """Conductor Modeling

        Returns
        -------
            str
        Value: ``"MeshInside"`` or ``"ImpedanceBoundary"``.
        """
        return self._simulation_settings.SignalNetsConductorModeling

    @signal_nets_conductor_modeling.setter
    def signal_nets_conductor_modeling(self, value):
        expected_values = ["MeshInside", "ImpedanceBoundary"]
        if isinstance(value, str) and value in expected_values:
            self._simulation_settings.SignalNetsConductorModeling = value
        else:
            self.logger.error(
                "Property signal_nets_conductor_modeling expects a string value among "
                f"'MeshInside' or 'ImpedanceBoundary' while the provided value is {value}."
            )

    @property
    def signal_nets_error_tolerance(self):
        """Error Tolerance

        Returns
        -------
            str
        Value between 0.02 and 1.
        """
        return self._simulation_settings.SignalNetsErrorTolerance

    @signal_nets_error_tolerance.setter
    def signal_nets_error_tolerance(self, value):
        self._simulation_settings.SignalNetsErrorTolerance = self._pedb.edb_value(value).ToString()

    @property
    def signal_nets_include_improved_dielectric_fill_refinement(self):
        return self._simulation_settings.SignalNetsIncludeImprovedDielectricFillRefinement

    @signal_nets_include_improved_dielectric_fill_refinement.setter
    def signal_nets_include_improved_dielectric_fill_refinement(self, value):
        if isinstance(value, bool):
            self._simulation_settings.SignalNetsIncludeImprovedDielectricFillRefinement = value
        else:
            self.logger.error(
                "Property signal_nets_include_improved_dielectric_fill_refinement "
                f"expects a boolean value while the provided value is {value}."
            )

    @property
    def signal_nets_include_improved_loss_handling(self):
        """Improved Dielectric Fill Refinement choice.

        Returns
        -------
            bool
        """
        return self._simulation_settings.SignalNetsIncludeImprovedLossHandling

    @signal_nets_include_improved_loss_handling.setter
    def signal_nets_include_improved_loss_handling(self, value):
        if isinstance(value, bool):
            self._simulation_settings.SignalNetsIncludeImprovedLossHandling = value
        else:
            self.logger.error(
                "Property signal_nets_include_improved_loss_handling "
                f"expects a boolean value while the provided value is {value}."
            )

    @property
    def snap_length_threshold(self):
        return self._simulation_settings.SnapLengthThreshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        self._simulation_settings.SnapLengthThreshold = self._pedb.edb_value(value).ToString()

    @property
    def surface_roughness_model(self):
        """Chosen Model setting

        Returns
        -------
            str
        Model allowed, ``"None"``, ``"Exponential"`` or ``"Hammerstad"``.
        """
        return self._simulation_settings.SurfaceRoughnessModel

    @surface_roughness_model.setter
    def surface_roughness_model(self, value):
        expected_values = ["None", "Exponential", "Hammerstad"]
        if isinstance(value, str) and value in expected_values:
            self._simulation_settings.SurfaceRoughnessModel = value
        else:
            self.logger.error(
                "Property surface_roughness_model expects a string value among "
                f"'None', 'Exponential' or 'Hammerstad' while the provided value is {value}."
            )

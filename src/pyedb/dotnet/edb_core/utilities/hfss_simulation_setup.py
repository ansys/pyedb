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


from pyedb.dotnet.edb_core.sim_setup_data.data.mesh_operation import (
    LengthMeshOperation,
    SkinDepthMeshOperation,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.settings import (
    AdaptiveSettings,
    AdvancedMeshSettings,
    CurveApproxSettings,
    DcrSettings,
    DefeatureSettings,
    HfssPortSettings,
    HfssSolverSettings,
    ViaSettings,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.sim_setup_info import SimSetupInfo
from pyedb.dotnet.edb_core.utilities.simulation_setup import SimulationSetup
from pyedb.generic.general_methods import generate_unique_name


class HfssSimulationSetup(SimulationSetup):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, pedb, edb_object=None, name: str = None):
        super().__init__(pedb, edb_object)
        self._simulation_setup_builder = self._pedb._edb.Utility.HFSSSimulationSetup
        if edb_object is None:
            self._name = name

            sim_setup_info = SimSetupInfo(self._pedb, sim_setup=self, setup_type="kHFSS", name=name)
            self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)
            self._update_setup()

    @property
    def solver_slider_type(self):
        """Solver slider type.
        Options are:
        1 - ``Fast``.
        2 - ``Medium``.
        3 - ``Accurate``.

        Returns
        -------
        int
        """
        solver_types = {
            "kFast": 0,
            "kMedium": 1,
            "kAccurate": 2,
            "kNumSliderTypes": 3,
        }
        return solver_types[self.sim_setup_info.simulation_settings.SolveSliderType.ToString()]

    @solver_slider_type.setter
    def solver_slider_type(self, value):
        """Set solver slider type."""
        solver_types = {
            0: self.sim_setup_info.simulation_settings.TSolveSliderType.kFast,
            1: self.sim_setup_info.simulation_settings.TSolveSliderType.kMedium,
            2: self.sim_setup_info.simulation_settings.TSolveSliderType.kAccurate,
            3: self.sim_setup_info.simulation_settings.TSolveSliderType.kNumSliderTypes,
        }
        self.sim_setup_info.simulation_settings.SolveSliderType = solver_types[value]
        self._update_setup()

    @property
    def is_auto_setup(self):
        """Flag indicating if automatic setup is enabled."""
        return self.get_sim_setup_info.SimulationSettings.IsAutoSetup

    @is_auto_setup.setter
    def is_auto_setup(self, value):
        self.get_sim_setup_info.SimulationSettings.IsAutoSetup = value
        self._update_setup()

    @property
    def hfss_solver_settings(self):
        """Manages EDB methods for HFSS solver settings.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.HfssSolverSettings`

        """
        return HfssSolverSettings(self)

    @property
    def adaptive_settings(self):
        """Adaptive Settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveSettings`

        """
        return AdaptiveSettings(self)

    @property
    def defeature_settings(self):
        """Defeature settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.DefeatureSettings`

        """
        return DefeatureSettings(self)

    @property
    def via_settings(self):
        """Via settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.ViaSettings`

        """
        return ViaSettings(self)

    @property
    def advanced_mesh_settings(self):
        """Advanced mesh settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.AdvancedMeshSettings`

        """
        return AdvancedMeshSettings(self)

    @property
    def curve_approx_settings(self):
        """Curve approximation settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.CurveApproxSettings`

        """
        return CurveApproxSettings(self)

    @property
    def dcr_settings(self):
        """Dcr settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.DcrSettings`

        """
        return DcrSettings(self)

    @property
    def hfss_port_settings(self):
        """HFSS port settings Class.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.HfssPortSettings`

        """
        return HfssPortSettings(self)

    @property
    def mesh_operations(self):
        """Mesh operations settings Class.

        Returns
        -------
        List of :class:`dotnet.edb_core.edb_data.hfss_simulation_setup_data.MeshOperation`

        """
        settings = self.sim_setup_info.simulation_settings.MeshOperations
        mesh_operations = {}
        for i in list(settings):
            if i.MeshOpType == i.TMeshOpType.kMeshSetupLength:
                mesh_operations[i.Name] = LengthMeshOperation(self, i)
            elif i.MeshOpType == i.TMeshOpType.kMeshSetupSkinDepth:
                mesh_operations[i.Name] = SkinDepthMeshOperation(self, i)
            elif i.MeshOpType == i.TMeshOpType.kMeshSetupBase:
                mesh_operations[i.Name] = SkinDepthMeshOperation(self, i)

        return mesh_operations

    def add_length_mesh_operation(
        self,
        net_layer_list,
        name=None,
        max_elements=1000,
        max_length="1mm",
        restrict_elements=True,
        restrict_length=True,
        refine_inside=False,
        mesh_region=None,
    ):
        """Add a mesh operation to the setup.

        Parameters
        ----------
        net_layer_list : dict
            Dictionary containing nets and layers on which enable Mesh operation. Example ``{"A0_N": ["TOP", "PWR"]}``.
        name : str, optional
            Mesh operation name.
        max_elements : int, optional
            Maximum number of elements. Default is ``1000``.
        max_length : str, optional
            Maximum length of elements. Default is ``1mm``.
        restrict_elements : bool, optional
            Whether to restrict number of elements. Default is ``True``.
        restrict_length : bool, optional
            Whether to restrict length of elements. Default is ``True``.
        mesh_region : str, optional
            Mesh region name.
        refine_inside : bool, optional
            Whether to refine inside or not.  Default is ``False``.

        Returns
        -------
        :class:`dotnet.edb_core.edb_data.hfss_simulation_setup_data.LengthMeshOperation`
        """
        if not name:
            name = generate_unique_name("skin")
        mop = LengthMeshOperation(self, self._pedb.simsetupdata.LengthMeshOperation())
        mop.mesh_region = mesh_region
        mop.name = name
        mop.nets_layers_list = net_layer_list
        mop.refine_inside = refine_inside
        mop.max_elements = max_elements
        mop.max_length = max_length
        mop.restrict_length = restrict_length
        mop.restrict_max_elements = restrict_elements
        self.sim_setup_info.simulation_settings.MeshOperations.Add(mop._edb_object)
        self._update_setup()
        return mop

    def add_skin_depth_mesh_operation(
        self,
        net_layer_list,
        name=None,
        max_elements=1000,
        skin_depth="1um",
        restrict_elements=True,
        surface_triangle_length="1mm",
        number_of_layers=2,
        refine_inside=False,
        mesh_region=None,
    ):
        """Add a mesh operation to the setup.

        Parameters
        ----------
        net_layer_list : dict
            Dictionary containing nets and layers on which enable Mesh operation. Example ``{"A0_N": ["TOP", "PWR"]}``.
        name : str, optional
            Mesh operation name.
        max_elements : int, optional
            Maximum number of elements. Default is ``1000``.
        skin_depth : str, optional
            Skin Depth. Default is ``1um``.
        restrict_elements : bool, optional
            Whether to restrict number of elements. Default is ``True``.
        surface_triangle_length : bool, optional
            Surface Triangle length. Default is ``1mm``.
        number_of_layers : int, str, optional
            Number of layers. Default is ``2``.
        mesh_region : str, optional
            Mesh region name.
        refine_inside : bool, optional
            Whether to refine inside or not.  Default is ``False``.

        Returns
        -------
        :class:`dotnet.edb_core.edb_data.hfss_simulation_setup_data.LengthMeshOperation`
        """
        if not name:
            name = generate_unique_name("length")
        mesh_operation = SkinDepthMeshOperation(self, self._pedb.simsetupdata.SkinDepthMeshOperation())
        mesh_operation.mesh_region = mesh_region
        mesh_operation.name = name
        mesh_operation.nets_layers_list = net_layer_list
        mesh_operation.refine_inside = refine_inside
        mesh_operation.max_elements = max_elements
        mesh_operation.skin_depth = skin_depth
        mesh_operation.number_of_layer_elements = number_of_layers
        mesh_operation.surface_triangle_length = surface_triangle_length
        mesh_operation.restrict_max_elements = restrict_elements
        self.sim_setup_info.simulation_settings.MeshOperations.Add(mesh_operation._edb_object)
        self._update_setup()
        return mesh_operation

    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s=0.02):
        """Set single-frequency solution.

        Parameters
        ----------
        frequency : str, float, optional
            Adaptive frequency. The default is ``5GHz``.
        max_num_passes : int, optional
            Maximum number of passes. The default is ``10``.
        max_delta_s : float, optional
            Maximum delta S. The default is ``0.02``.

        Returns
        -------
        bool

        """
        self.adaptive_settings.adapt_type = "kSingle"
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        return self.adaptive_settings.add_adaptive_frequency_data(frequency, max_num_passes, max_delta_s)

    def set_solution_multi_frequencies(self, frequencies=("5GHz", "10GHz"), max_num_passes=10, max_delta_s="0.02"):
        """Set multi-frequency solution.

        Parameters
        ----------
        frequencies : list, tuple, optional
            List or tuple of adaptive frequencies. The default is ``5GHz``.
        max_num_passes : int, optional
            Maximum number of passes. Default is ``10``.
        max_delta_s : float, optional
            Maximum delta S. The default is ``0.02``.

        Returns
        -------
        bool

        """
        self.adaptive_settings.adapt_type = "kMultiFrequencies"
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        for i in frequencies:
            if not self.adaptive_settings.add_adaptive_frequency_data(i, max_num_passes, max_delta_s):
                return False
        return True

    def set_solution_broadband(
        self, low_frequency="5GHz", high_frequency="10GHz", max_num_passes=10, max_delta_s="0.02"
    ):
        """Set broadband solution.

        Parameters
        ----------
        low_frequency : str, float, optional
            Low frequency. The default is ``5GHz``.
        high_frequency : str, float, optional
            High frequency. The default is ``10GHz``.
        max_num_passes : int, optional
            Maximum number of passes. The default is ``10``.
        max_delta_s : float, optional
            Maximum Delta S. Default is ``0.02``.

        Returns
        -------
        bool
        """
        self.adaptive_settings.adapt_type = "kBroadband"
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        if not self.adaptive_settings.add_broadband_adaptive_frequency_data(
            low_frequency, high_frequency, max_num_passes, max_delta_s
        ):  # pragma no cover
            return False
        return True


class HFSSPISimulationSetup(SimulationSetup):
    """Manages EDB methods for HFSSPI simulation setup."""

    def __init__(self, pedb, edb_object=None, name: str = None):
        super().__init__(pedb, edb_object)

        self._simulation_setup_builder = self._pedb._edb.Utility.HFSSPISimulationSetup
        if edb_object is None:
            self._name = name
            sim_setup_info = SimSetupInfo(self._pedb, sim_setup=self, setup_type="kHFSSPI", name=name)
            self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)
            self._update_setup()

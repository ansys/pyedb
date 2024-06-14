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


import warnings

from pyedb.dotnet.edb_core.general import (
    convert_netdict_to_pydict,
    convert_pydict_to_netdict,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.mesh_operation import (
    MeshOperationLength,
    MeshOperationSkinDepth,
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
from pyedb.dotnet.edb_core.sim_setup_data.data.siw_dc_ir_settings import (
    SiwaveDCIRSettings,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.sweep_data import SweepData
from pyedb.dotnet.edb_core.sim_setup_data.io.siwave import (
    AdvancedSettings,
    DCAdvancedSettings,
    DCSettings,
)
from pyedb.generic.general_methods import generate_unique_name, is_linux


def _parse_value(v):
    """Parse value in C sharp format."""
    #  duck typing parse of the value 'v'
    if v is None or v == "":
        pv = v
    elif v == "true":
        pv = True
    elif v == "false":
        pv = False
    else:
        try:
            pv = int(v)
        except ValueError:
            try:
                pv = float(v)
            except ValueError:
                if isinstance(v, str) and v[0] == v[-1] == "'":
                    pv = v[1:-1]
                else:
                    pv = v
    return pv


class AdaptiveType(object):
    (SingleFrequency, MultiFrequency, BroadBand) = range(0, 3)


class SimulationSetup(object):
    """Provide base simulation setup.

    Parameters
    ----------
    pedb : :class:`pyedb.dotnet.edb.Edb`
        Inherited object.
    edb_object : :class:`Ansys.Ansoft.Edb.Utility.SIWaveSimulationSetup`,
    :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`,
    :class:`Ansys.Ansoft.Edb.Utility.HFSSSimulationSettings`
        EDB object.
    """

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object
        self._setup_type = ""
        self._setup_type_mapping = {
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

        if float(self._pedb.edbversion) >= 2024.2:
            self._setup_type_mapping.update(
                {
                    "kRaptorX": self._pedb.simsetupdata.RaptorX.RaptorXSimulationSettings,
                    "kHFSSPI": self._pedb.simsetupdata.HFSSPISimulationSettings,
                }
            )
        if self._edb_object:
            self._name = self._edb_object.GetName()

        self._sweep_list = {}

    def _create(self, name=None):
        """Create a simulation setup."""
        if not name:
            name = generate_unique_name(self.setup_type)
            self._name = name

        setup_type = self._setup_type_mapping[self._setup_type]
        edb_setup_info = self._pedb.simsetupdata.SimSetupInfo[setup_type]()
        edb_setup_info.Name = name
        if (
            edb_setup_info.get_SimSetupType().ToString() == "kRaptorX"
            or edb_setup_info.get_SimSetupType().ToString() == "kHFSSPI"
        ):
            self._edb_setup_info = edb_setup_info
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    def _set_edb_setup_info(self, edb_setup_info):
        """Create a setup object from a setup information object."""
        utility = self._pedb._edb.Utility
        setup_type_mapping = {
            "kHFSS": utility.HFSSSimulationSetup,
            "kPEM": None,
            "kSIwave": utility.SIWaveSimulationSetup,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": utility.SIWaveDCIRSimulationSetup,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }

        version = self._pedb.edbversion.split(".")
        if int(version[0]) == 2024 and int(version[1]) == 2 or int(version[0]) > 2024:
            setup_type_mapping["kRaptorX"] = utility.RaptorXSimulationSetup
        setup_utility = setup_type_mapping[self._setup_type]
        return setup_utility(edb_setup_info)

    def _update_setup(self):
        """Update setup in EDB."""
        if self._setup_type == "kHFSS":
            mesh_operations = self.get_sim_setup_info.SimulationSettings.MeshOperations
            mesh_operations.Clear()
            for mop in self.mesh_operations.values():
                mesh_operations.Add(mop.mesh_operation)

        if self._name in self._pedb.setups:
            self._pedb.layout.cell.DeleteSimulationSetup(self._name)
        if not self._pedb.layout.cell.AddSimulationSetup(self._edb_object):
            raise Exception("Updating setup {} failed.".format(self._name))
        else:
            return True

    @property
    def enabled(self):
        """Flag indicating if the setup is enabled."""
        return self.get_sim_setup_info.SimulationSettings.Enabled

    @enabled.setter
    def enabled(self, value):
        self.get_sim_setup_info.SimulationSettings.Enabled = value
        self._edb_object = self._set_edb_setup_info(self.get_sim_setup_info)
        self._update_setup()

    @property
    def name(self):
        """Name of the setup."""
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        self._pedb.layout.cell.DeleteSimulationSetup(self.name)
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.Name = value
        self._name = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def position(self):
        """Position in the setup list."""
        return self.get_sim_setup_info.Position

    @position.setter
    def position(self, value):
        edb_setup_info = self.get_sim_setup_info.SimulationSettings
        edb_setup_info.Position = value
        self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def setup_type(self):
        """Type of the setup."""
        return self.get_sim_setup_info.SimSetupType.ToString()

    @property
    def frequency_sweeps(self):
        """List of frequency sweeps."""
        temp = {}
        if self.setup_type in ("kRaptorX", "kHFSSPI"):
            sweep_data_list = self._edb_setup_info.SweepDataList
        else:
            sweep_data_list = self.get_sim_setup_info.SweepDataList
        for i in list(sweep_data_list):
            temp[i.Name] = SweepData(self, None, i.Name, i)
        return temp

    def _add_frequency_sweep(self, sweep_data):
        """Add a frequency sweep.

        Parameters
        ----------
        sweep_data: SweepData
        """
        self._sweep_list[sweep_data.name] = sweep_data
        if self.setup_type in ["kRaptorX", "kHFSSPI"]:
            edb_setup_info = self._edb_setup_info
        else:
            edb_setup_info = self.get_sim_setup_info

        if self._setup_type in ["kSIwave", "kHFSS", "kRaptorX", "kHFSSPI"]:
            for _, v in self._sweep_list.items():
                edb_setup_info.SweepDataList.Add(v._edb_object)

        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    def delete_frequency_sweep(self, sweep_data):
        """Delete a frequency sweep.

        Parameters
        ----------
            sweep_data : EdbFrequencySweep.
        """
        name = sweep_data.name
        if name in self._sweep_list:
            self._sweep_list.pop(name)

        fsweep = []
        if self.frequency_sweeps:
            fsweep = [val for key, val in self.frequency_sweeps.items() if not key == name]
            self.get_sim_setup_info.SweepDataList.Clear()
            for i in fsweep:
                self.get_sim_setup_info.SweepDataList.Add(i._edb_object)
            self._update_setup()
            return True if name in self.frequency_sweeps else False

    def add_frequency_sweep(self, name=None, frequency_sweep=None):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep. The default is ``None``.
        frequency_sweep : list, optional
            List of frequency points. The default is ``None``.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.simulation_setup_data.EdbFrequencySweep`

        Examples
        --------
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_frequency_sweep(frequency_sweep=[
        ...     ["linear count", "0", "1kHz", 1],
        ...     ["log scale", "1kHz", "0.1GHz", 10],
        ...     ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...     ])
        """
        if name in self.frequency_sweeps:
            return False

        if not frequency_sweep:
            frequency_sweep = [["linear scale", "0.1GHz", "10GHz", "0.1GHz"]]
        elif not isinstance(frequency_sweep[0], list):
            frequency_sweep = [frequency_sweep]

        if not name:
            name = generate_unique_name("sweep")
        sweep = SweepData(self, frequency_sweep, name)
        self._add_frequency_sweep(sweep)
        self._update_setup()
        return sweep


class HfssSimulationSetup(SimulationSetup):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._setup_type = "kHFSS"
        self._mesh_operations = {}

    def create(self, name=None):
        """Create an HFSS setup."""
        self._name = name
        self._create(name)
        return self

    @property
    def get_sim_setup_info(self):
        """Get simulation setup information."""
        return self._edb_object.GetSimSetupInfo()

    @property
    def solver_slider_type(self):
        """Solver slider type.
        Options are:
        1 - ``kFast``.
        2 - ``kMedium``.
        3 - ``kAccurate``.
        4 - ``kNumSliderTypes``.

        Returns
        -------
        str
        """
        return self.get_sim_setup_info.SimulationSettings.TSolveSliderType.ToString()

    @solver_slider_type.setter
    def solver_slider_type(self, value):
        """Set solver slider type."""
        solver_types = {
            "kFast": self.get_sim_setup_info.SimulationSettings.TSolveSliderType.k25DViaWirebond,
            "kMedium": self.get_sim_setup_info.SimulationSettings.TSolveSliderType.k25DViaRibbon,
            "kAccurate": self.get_sim_setup_info.SimulationSettings.TSolveSliderType.k25DViaMesh,
            "kNumSliderTypes": self.get_sim_setup_info.SimulationSettings.TSolveSliderType.k25DViaField,
        }
        self.get_sim_setup_info.SimulationSettings.TSolveSliderType = solver_types[value]
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
        if self._mesh_operations:
            return self._mesh_operations
        settings = self.get_sim_setup_info.SimulationSettings.MeshOperations
        self._mesh_operations = {}
        for i in list(settings):
            if i.MeshOpType == i.TMeshOpType.kMeshSetupLength:
                self._mesh_operations[i.Name] = MeshOperationLength(self, i)
            elif i.MeshOpType == i.TMeshOpType.kMeshSetupSkinDepth:
                self._mesh_operations[i.Name] = MeshOperationSkinDepth(self, i)
            elif i.MeshOpType == i.TMeshOpType.kMeshSetupBase:
                self._mesh_operations[i.Name] = MeshOperationSkinDepth(self, i)

        return self._mesh_operations

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
        mesh_operation = MeshOperationLength(self, self._pedb.simsetupdata.LengthMeshOperation())
        mesh_operation.mesh_region = mesh_region
        mesh_operation.name = name
        mesh_operation.nets_layers_list = net_layer_list
        mesh_operation.refine_inside = refine_inside
        mesh_operation.max_elements = str(max_elements)
        mesh_operation.max_length = max_length
        mesh_operation.restrict_length = restrict_length
        mesh_operation.restrict_max_elements = restrict_elements
        self.mesh_operations[name] = mesh_operation
        return mesh_operation if self._update_setup() else False

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
        mesh_operation = MeshOperationSkinDepth(self, self._pedb.simsetupdata.SkinDepthMeshOperation())
        mesh_operation.mesh_region = mesh_region
        mesh_operation.name = name
        mesh_operation.nets_layers_list = net_layer_list
        mesh_operation.refine_inside = refine_inside
        mesh_operation.max_elements = max_elements
        mesh_operation.skin_depth = skin_depth
        mesh_operation.number_of_layer_elements = number_of_layers
        mesh_operation.surface_triangle_length = surface_triangle_length
        mesh_operation.restrict_max_elements = restrict_elements
        self.mesh_operations[name] = mesh_operation
        return mesh_operation if self._update_setup() else False

    def add_frequency_sweep(self, name=None, frequency_sweep=None):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep.
        frequency_sweep : list, optional
            List of frequency points.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.simulation_setup.EdbFrequencySweep`

        Examples
        --------
        >>> setup1 = edbapp.create_hfss_setup("setup1")
        >>> setup1.add_frequency_sweep(frequency_sweep=[
        ...                           ["linear count", "0", "1kHz", 1],
        ...                           ["log scale", "1kHz", "0.1GHz", 10],
        ...                           ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...                           ])
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return SweepData(self, frequency_sweep, name)

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


class SiwaveSYZSimulationSetup(SimulationSetup):
    """Manages EDB methods for SIwave simulation setup.

    Parameters
    ----------
    pedb : :class:`pyedb.dotnet.edb.Edb`
        Inherited AEDT object.
    edb_setup : :class:`Ansys.Ansoft.Edb.Utility.SIWaveSimulationSetup`
        Edb object.
    """

    def __init__(self, pedb, edb_setup=None):
        super().__init__(pedb, edb_setup)
        self._edb = self._pedb
        self._setup_type = "kSIwave"
        self._sim_setup_info = None

    def create(self, name=None):
        """Create a SIwave SYZ setup.

        Returns
        -------
        :class:`SiwaveDCSimulationSetup`
        """
        self._name = name
        self._create(name)
        self.si_slider_position = 1

        return self

    def get_configurations(self):
        """Get SIwave SYZ simulation settings.

        Returns
        -------
        dict
            Dictionary of SIwave SYZ simulation settings.
        """
        return {
            "pi_slider_position": self.pi_slider_position,
            "si_slider_position": self.si_slider_position,
            "use_custom_settings": self.use_si_settings,
            "use_si_settings": self.use_si_settings,
            "advanced_settings": self.advanced_settings.get_configurations(),
        }

    @property
    def advanced_settings(self):
        """SIwave advanced settings."""
        return AdvancedSettings(self)

    @property
    def get_sim_setup_info(self):
        """Get simulation information from the setup."""
        if self._sim_setup_info:
            return self._sim_setup_info

        edb_setup = self._edb_object
        edb_sim_setup_info = self._pedb.simsetupdata.SimSetupInfo[self._setup_type_mapping[self._setup_type]]()
        edb_sim_setup_info.Name = edb_setup.GetName()

        string = edb_setup.ToString().replace("\t", "").split("\r\n")

        if is_linux:
            string = string[0].split("\n")
        keys = [i.split("=")[0] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
        values = [i.split("=")[1] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
        for val in string:
            if "SourceTermsToGround()" in val:
                break
            elif "SourceTermsToGround" in val:
                sources = {}
                val = val.replace("SourceTermsToGround(", "").replace(")", "").split(",")
                for v in val:
                    source = v.split("=")
                    sources[source[0]] = int(source[1].replace("'", ""))
                edb_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
                    sources
                )
                break
        for k in keys:
            value = _parse_value(values[keys.index(k)])
            setter = None
            if k in dir(edb_sim_setup_info.SimulationSettings):
                setter = edb_sim_setup_info.SimulationSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings

            elif k in dir(edb_sim_setup_info.SimulationSettings.DCAdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.DCAdvancedSettings
            elif "DCIRSettings" in dir(edb_sim_setup_info.SimulationSettings) and k in dir(
                edb_sim_setup_info.SimulationSettings.DCIRSettings
            ):
                setter = edb_sim_setup_info.SimulationSettings.DCIRSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.DCSettings):
                setter = edb_sim_setup_info.SimulationSettings.DCSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings
            if setter:
                try:
                    setter.__setattr__(k, value)
                except TypeError:
                    try:
                        setter.__setattr__(k, str(value))
                    except:
                        pass

        return edb_sim_setup_info

    def set_pi_slider(self, value):
        """Set SIwave PI simulation accuracy level.
        Options are:
        - ``0``: Optimal speed
        - ``1``:  Balanced
        - ``2``: Optimal accuracy

        .. deprecated:: 0.7.5
           Use :property:`pi_slider_position` property instead.

        """
        warnings.warn("`set_pi_slider` is deprecated. Use `pi_slider_position` property instead.", DeprecationWarning)
        self.pi_slider_position = value

    def set_si_slider(self, value):
        """Set SIwave SI simulation accuracy level.

        Options are:
        - ``0``: Optimal speed;
        - ``1``:  Balanced;
        - ``2``: Optimal accuracy```.
        """
        self.use_si_settings = True
        self.use_custom_settings = False
        self.si_slider_position = value
        self.advanced_settings.set_si_slider(value)

    @property
    def pi_slider_position(self):
        """PI solider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.SimulationSettings.PISliderPos

    @pi_slider_position.setter
    def pi_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.PISliderPos = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

        self.use_si_settings = False
        self.use_custom_settings = False
        self.advanced_settings.set_pi_slider(value)

    @property
    def si_slider_position(self):
        """SI slider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.SimulationSettings.SISliderPos

    @si_slider_position.setter
    def si_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.SISliderPos = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

        self.use_si_settings = True
        self.use_custom_settings = False
        self.advanced_settings.set_si_slider(value)

    @property
    def use_custom_settings(self):
        """Custom settings to use.

        Returns
        -------
        bool
        """
        return self.get_sim_setup_info.SimulationSettings.UseCustomSettings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.UseCustomSettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def use_si_settings(self):
        """Whether to use SI Settings.

        Returns
        -------
        bool
        """
        return self.get_sim_setup_info.SimulationSettings.UseSISettings

    @use_si_settings.setter
    def use_si_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.UseSISettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()


class SiwaveDCSimulationSetup(SiwaveSYZSimulationSetup):
    """Manages EDB methods for SIwave DC simulation setup.

    Parameters
    ----------
    pedb : :class:`pyedb.dotnet.edb.Edb`
        Inherited AEDT object.
    edb_setup : Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings
        EDB object. The default is ``None``.
    """

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._setup_type = "kSIwaveDCIR"
        self._edb = pedb
        self._mesh_operations = {}

    def create(self, name=None):
        """Create a SIwave DCIR setup.

        Returns
        -------
        :class:`SiwaveDCSimulationSetup`
        """
        self._name = name
        self._create(name)
        self.set_dc_slider(1)
        return self

    @property
    def dc_ir_settings(self):
        """DC IR settings."""
        return SiwaveDCIRSettings(self)

    def get_configurations(self):
        """Get SIwave DC simulation settings.

        Returns
        -------
        dict
            Dictionary of SIwave DC simulation settings.
        """
        return {
            "dc_settings": self.dc_settings.get_configurations(),
            "dc_advanced_settings": self.dc_advanced_settings.get_configurations(),
        }

    def set_dc_slider(self, value):
        """Set DC simulation accuracy level.

        Options are:

        - ``0``: Optimal speed
        - ``1``: Balanced
        - ``2``: Optimal accuracy
        """
        self.use_custom_settings = False
        self.dc_settings.dc_slider_position = value
        self.dc_advanced_settings.set_dc_slider(value)

    @property
    def dc_settings(self):
        """SIwave DC setting."""
        return DCSettings(self)

    @property
    def dc_advanced_settings(self):
        """Siwave DC advanced settings.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return DCAdvancedSettings(self)

    @property
    def source_terms_to_ground(self):
        """Dictionary of grounded terminals.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return convert_netdict_to_pydict(self.get_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround)

    def add_source_terminal_to_ground(self, source_name, terminal=0):
        """Add a source terminal to ground.

        Parameters
        ----------
        source_name : str,
            Source name.
        terminal : int, optional
            Terminal to assign. Options are:

             - 0=Unspecified
             - 1=Negative node
             - 2=Positive none

        Returns
        -------
        bool

        """
        terminals = self.source_terms_to_ground
        terminals[source_name] = terminal
        self.get_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
            terminals
        )
        return self._update_setup()

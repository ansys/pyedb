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


from enum import Enum
import warnings

from pyedb.dotnet.edb_core.sim_setup_data.data.sim_setup_info import SimSetupInfo
from pyedb.dotnet.edb_core.sim_setup_data.data.sweep_data import SweepData
from pyedb.generic.general_methods import generate_unique_name


class SimulationSetupType(Enum):
    kHFSS = "hfss"
    kPEM = None
    kSIwave = "siwave_ac"
    kLNA = "lna"
    kTransient = "transient"
    kQEye = "quick_eye"
    kVEye = "verif_eye"
    kAMI = "ami"
    kAnalysisOption = "analysis_option"
    kSIwaveDCIR = "siwave_dc"
    kSIwaveEMI = "siwave_emi"
    kHFSSPI = "hfss_pi"
    kDDRwizard = "ddrwizard"
    kQ3D = "q3d"


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
        self._simulation_setup_builder = None
        self._simulation_setup_type = {
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
            self._simulation_setup_type.update(
                {
                    "kRaptorX": self._pedb.simsetupdata.RaptorX.RaptorXSimulationSettings,
                    "kHFSSPI": self._pedb.simsetupdata.HFSSPISimulationSettings,
                }
            )
        if self._edb_object:
            self._name = self._edb_object.GetName()

        self._sweep_list = {}

    @property
    def sim_setup_info(self):
        return SimSetupInfo(self._pedb, sim_setup=self, edb_object=self._edb_object.GetSimSetupInfo())

    def set_sim_setup_info(self, sim_setup_info):
        self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)

    @property
    def get_sim_setup_info(self):
        """Get simulation setup information."""
        warnings.warn("Use new property :func:`sim_setup_info` instead.", DeprecationWarning)
        return self.sim_setup_info._edb_object

    def get_simulation_settings(self):
        sim_settings = self.sim_setup_info.simulation_settings
        properties = {}
        for k in dir(sim_settings):
            if not k.startswith("_"):
                properties[k] = getattr(sim_settings, k)
        return properties

    def set_simulation_settings(self, sim_settings: dict):
        for k, v in sim_settings.items():
            if k == "enabled":
                continue
            if k in self.get_simulation_settings():
                setattr(self.sim_setup_info.simulation_settings, k, v)
        self._update_setup()

    @property
    def setup_type(self):
        return self.sim_setup_info.sim_setup_type

    @property
    def type(self):
        return SimulationSetupType[self.setup_type].value

    def _create(self, name=None, simulation_setup_type=""):
        """Create a simulation setup."""
        if not name:
            name = generate_unique_name(self.setup_type)
            self._name = name

        edb_setup_info = self._pedb.simsetupdata.SimSetupInfo[self._simulation_setup_type[simulation_setup_type]]()
        edb_setup_info.Name = name
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
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }

        if float(self._pedb.edbversion) >= 2024.2:
            setup_type_mapping["kRaptorX"] = utility.RaptorXSimulationSetup
            setup_type_mapping["kHFSSPI"] = utility.HFSSPISimulationSetup
        sim_setup_type = self.sim_setup_info.sim_setup_type
        setup_utility = setup_type_mapping[sim_setup_type]
        return setup_utility(edb_setup_info._edb_object)

    @property
    def mesh_operations(self):
        return {}

    def _update_setup(self):
        """Update setup in EDB."""
        # Update sweep

        # Replace setup
        if self._name in self._pedb.setups:
            self._pedb.layout.cell.DeleteSimulationSetup(self._name)
        if not self._pedb.layout.cell.AddSimulationSetup(self._edb_object):
            raise Exception("Updating setup {} failed.".format(self._name))
        else:
            return True

    @property
    def enabled(self):
        """Flag indicating if the setup is enabled."""
        return self.get_simulation_settings()["enabled"]

    @enabled.setter
    def enabled(self, value: bool):
        self.set_simulation_settings({"enabled": value})

    @property
    def name(self):
        """Name of the setup."""
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        self._pedb.layout.cell.DeleteSimulationSetup(self.name)
        edb_setup_info = self.sim_setup_info
        edb_setup_info.name = value
        self._name = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def position(self):
        """Position in the setup list."""
        return self.sim_setup_info.position

    @position.setter
    def position(self, value):
        edb_setup_info = self.sim_setup_info.simulation_settings
        edb_setup_info.position = value
        self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def setup_type(self):
        """Type of the setup."""
        return self.sim_setup_info.sim_setup_type

    @property
    def frequency_sweeps(self):
        warnings.warn("Use new property :func:`sweeps` instead.", DeprecationWarning)
        return self.sweeps

    @property
    def sweeps(self):
        """List of frequency sweeps."""
        return {i.name: i for i in self.sim_setup_info.sweep_data_list}

    def add_sweep(self, name, frequency_set: list = None, **kwargs):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep. The default is ``None``.
        frequency_set : list, optional
            List of frequency points. The default is ``None``.

        Returns
        -------

        Examples
        --------
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_sweep(name="sw1", frequency_set=["linear count", "1MHz", "100MHz", 10])
        """
        name = generate_unique_name("sweep") if not name else name
        if name in self.sweeps:
            raise ValueError("Sweep {} already exists.".format(name))

        sweep_data = SweepData(self._pedb, name=name, sim_setup=self)
        for k, v in kwargs.items():
            if k in dir(sweep_data):
                setattr(sweep_data, k, v)

        if frequency_set is None:
            sweep_type = "linear_scale"
            start, stop, increment = "50MHz", "5GHz", "50MHz"
            sweep_data.add(sweep_type, start, stop, increment)
        elif len(frequency_set) == 0:
            pass
        else:
            if not isinstance(frequency_set[0], list):
                frequency_set = [frequency_set]
            for fs in frequency_set:
                sweep_data.add(*fs)

        ss_info = self.sim_setup_info
        ss_info.add_sweep_data(sweep_data)
        self.set_sim_setup_info(ss_info)
        self._update_setup()
        return sweep_data

    def _add_frequency_sweep(self, sweep_data):
        """Add a frequency sweep.

        Parameters
        ----------
        sweep_data: SweepData
        """
        warnings.warn("Use new property :func:`add_sweep_data` instead.", DeprecationWarning)
        self._sweep_list[sweep_data.name] = sweep_data
        edb_setup_info = self.sim_setup_info

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
            self.sim_setup_info._edb_object.SweepDataList.Clear()
            for i in fsweep:
                self.sim_setup_info._edb_object.SweepDataList.Add(i._edb_object)
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
        warnings.warn("`create_component_from_pins` is deprecated. Use `add_sweep` method instead.", DeprecationWarning)
        return self.add_sweep(name, frequency_sweep)

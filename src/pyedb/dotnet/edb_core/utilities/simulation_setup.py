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

from pyedb.dotnet.edb_core.sim_setup_data.data.sim_setup_info import SimSetupInfo
from pyedb.dotnet.edb_core.sim_setup_data.data.sweep_data import SweepData
from pyedb.generic.general_methods import generate_unique_name


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

    @sim_setup_info.setter
    def sim_setup_info(self, sim_setup_info):
        self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)

    @property
    def setup_type(self):
        return self.sim_setup_info.sim_setup_type

    def _create(self, name=None, simulation_setup_type=""):
        """Create a simulation setup."""
        if not name:
            name = generate_unique_name(self.setup_type)
            self._name = name

        edb_setup_info = self._pedb.simsetupdata.SimSetupInfo[self._simulation_setup_type[simulation_setup_type]]()
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
            setup_type_mapping["kHFSSPI"] = utility.HFSSPISimulationSetup
        sim_setup_type = self.sim_setup_info.sim_setup_type
        setup_utility = setup_type_mapping[sim_setup_type.ToString()]
        return setup_utility(edb_setup_info)

    def _update_setup(self):
        """Update setup in EDB."""
        # Update mesh operation
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
        warnings.warn("Use new property :func:`sweeps` instead.", DeprecationWarning)
        return self.sweeps

    @property
    def sweeps(self):
        """List of frequency sweeps."""
        temp = {}
        if self.setup_type in ("kRaptorX", "kHFSSPI"):
            sweep_data_list = self._edb_setup_info.SweepDataList
            for i in list(sweep_data_list):
                temp[i.Name] = SweepData(self, None, i.Name, i)
            return temp
        else:
            return {i.name: i for i in self.sim_setup_info.sweep_data_list}

    def add_sweep(self, name, frequency_set: list = None):
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
        if frequency_set is None:
            sweep_type = "linear_scale"
            start, stop, increment = "50MHz", "5GHz", "50MHz"
            sweep_data.add(sweep_type, start, stop, increment)
        else:
            if not isinstance(frequency_set[0], list):
                frequency_set = [frequency_set]
            for fs in frequency_set:
                sweep_data.add(*fs)

        ss_info = self.sim_setup_info
        ss_info.add_sweep_data(sweep_data)
        self.sim_setup_info = ss_info
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
        warnings.warn("`create_component_from_pins` is deprecated. Use `add_sweep` method instead.", DeprecationWarning)
        return self.add_sweep(name, frequency_sweep)

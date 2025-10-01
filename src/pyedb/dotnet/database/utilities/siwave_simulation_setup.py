# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pyedb.dotnet.database.general import (
    convert_netdict_to_pydict,
    convert_pydict_to_netdict,
)
from pyedb.dotnet.database.sim_setup_data.data.sim_setup_info import SimSetupInfo
from pyedb.dotnet.database.sim_setup_data.data.siw_dc_ir_settings import (
    SiwaveDCIRSettings,
)
from pyedb.dotnet.database.sim_setup_data.io.siwave import (
    AdvancedSettings,
    DCAdvancedSettings,
    DCSettings,
)
from pyedb.dotnet.database.utilities.simulation_setup import SimulationSetup
from pyedb.generic.general_methods import is_linux
from pyedb.generic.settings import settings


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


def clone_edb_sim_setup_info(source, target):
    string = source.ToString().replace("\t", "").split("\r\n")
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
            target.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(sources)
            break
    for k in keys:
        value = _parse_value(values[keys.index(k)])
        setter = None
        if k in dir(target.SimulationSettings):
            setter = target.SimulationSettings
        elif k in dir(target.SimulationSettings.AdvancedSettings):
            setter = target.SimulationSettings.AdvancedSettings

        elif k in dir(target.SimulationSettings.DCAdvancedSettings):
            setter = target.SimulationSettings.DCAdvancedSettings
        elif "DCIRSettings" in dir(target.SimulationSettings) and k in dir(target.SimulationSettings.DCIRSettings):
            setter = target.SimulationSettings.DCIRSettings
        elif k in dir(target.SimulationSettings.DCSettings):
            setter = target.SimulationSettings.DCSettings
        elif k in dir(target.SimulationSettings.AdvancedSettings):
            setter = target.SimulationSettings.AdvancedSettings
        if setter:
            try:
                setter.__setattr__(k, value)
            except TypeError:
                try:
                    setter.__setattr__(k, str(value))
                except Exception as e:
                    settings.logger.warning(
                        f"Failed to update attribute {k} with value {value} - {type(e).__name__}: {str(e)}"
                    )


class SiwaveSimulationSetup(SimulationSetup):
    """Manages EDB methods for SIwave simulation setup."""

    def __init__(self, pedb, edb_object=None, name: str = None):
        super().__init__(pedb, edb_object)
        self._simulation_setup_builder = self._pedb._edb.Utility.SIWaveSimulationSetup
        if edb_object is None:
            self._name = name
            sim_setup_info = SimSetupInfo(self._pedb, sim_setup=self, setup_type="kSIwave", name=name)
            self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)
            self._update_setup()

        self._siwave_sweeps_list = []

    def create(self, name=None):
        """Create a SIwave SYZ setup.

        Returns
        -------
        :class:`SiwaveDCSimulationSetup`
        """
        self._name = name
        self._create(name, simulation_setup_type="kSIwave")
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
    def sim_setup_info(self):
        """Overrides the default sim_setup_info object."""
        return self.get_sim_setup_info

    @sim_setup_info.setter
    def sim_setup_info(self, sim_setup_info):
        self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)

    @property
    def get_sim_setup_info(self):  # todo remove after refactoring
        """Get simulation information from the setup."""

        sim_setup_info = SimSetupInfo(self._pedb, sim_setup=self, setup_type="kSIwave", name=self._edb_object.GetName())
        clone_edb_sim_setup_info(source=self._edb_object, target=sim_setup_info._edb_object)
        return sim_setup_info

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
    def enabled(self):
        """Flag indicating if the setup is enabled."""
        return self.sim_setup_info.simulation_settings.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Set the enabled flag for the setup."""
        self.sim_setup_info.simulation_settings.Enabled = value

    @property
    def pi_slider_position(self):
        """PI solider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.simulation_settings.PISliderPos

    @pi_slider_position.setter
    def pi_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.simulation_settings.PISliderPos = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

        self.use_si_settings = False
        self.use_custom_settings = False
        self.advanced_settings.set_pi_slider(value)

    @property
    def si_slider_position(self):
        """SI slider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.simulation_settings.SISliderPos

    @si_slider_position.setter
    def si_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.simulation_settings.SISliderPos = value
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
        return self.get_sim_setup_info.simulation_settings.UseCustomSettings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.simulation_settings.UseCustomSettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def use_si_settings(self):
        """Whether to use SI Settings.

        Returns
        -------
        bool
        """
        return self.get_sim_setup_info.simulation_settings.UseSISettings

    @use_si_settings.setter
    def use_si_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.simulation_settings.UseSISettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    def add_sweep(self, name: str = None, frequency_set: list = None, sweep_type: str = "interpolation", **kwargs):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep. The default is ``None``.
        frequency_set : list, optional
            List of frequency points. The default is ``None``.
        sweep_type : str, optional
            Sweep type. The default is ``"interpolation"``. Options are ``"discrete"``,"discrete"``.
        Returns
        -------

        Examples
        --------
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_sweep(name="sw1", frequency_set=["linear count", "1MHz", "100MHz", 10])
        """
        sweep_data = SimulationSetup.add_sweep(
            self, name=name, frequency_set=frequency_set, sweep_type=sweep_type, **kwargs
        )
        self._siwave_sweeps_list.append(sweep_data)
        return sweep_data

    @property
    def sweeps(self):
        """List of frequency sweeps."""
        return {i.name: i for i in self._siwave_sweeps_list}

    @property
    def dc_settings(self):
        """SIwave DC setting."""
        return DCSettings(self)

    @property
    def dc_advanced_settings(self):
        """Siwave DC advanced settings.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return DCAdvancedSettings(self)


class SiwaveDCSimulationSetup(SimulationSetup):
    """Manages EDB methods for SIwave DC simulation setup."""

    def __init__(self, pedb, edb_object=None, name: str = None):
        super().__init__(pedb, edb_object)
        self._simulation_setup_builder = self._pedb._edb.Utility.SIWaveDCIRSimulationSetup
        self._mesh_operations = {}
        if edb_object is None:
            self._name = name
            sim_setup_info = SimSetupInfo(self._pedb, sim_setup=self, setup_type="kSIwaveDCIR", name=name)
            self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)
            self._update_setup()

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
    def enabled(self):
        """Flag indicating if the setup is enabled.

        .. deprecated:: 0.57.0
            Use :property:`settings.enabled` property instead.

        Returns
        -------
        bool
        """

        warnings.warn("`enabled` property is deprecated. Use `settings.enabled` property instead.", DeprecationWarning)
        return self.settings.enabled

    @property
    def sim_setup_info(self):
        """Overrides the default sim_setup_info object."""
        return SimSetupInfo(self._pedb, sim_setup=self, edb_object=self.get_sim_setup_info._edb_object)

    @sim_setup_info.setter
    def sim_setup_info(self, sim_setup_info):
        self._edb_object = self._simulation_setup_builder(sim_setup_info._edb_object)

    @property
    def get_sim_setup_info(self):  # todo remove after refactoring
        """Get simulation information from the setup."""
        warnings.warn("Use new property :func:`sim_setup_info` instead.", DeprecationWarning)
        sim_setup_info = SimSetupInfo(
            self._pedb, sim_setup=self, setup_type="kSIwaveDCIR", name=self._edb_object.GetName()
        )
        clone_edb_sim_setup_info(source=self._edb_object, target=sim_setup_info._edb_object)
        return sim_setup_info

    @property
    def dc_ir_settings(self):
        """DC IR settings."""
        return self.settings

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
        self.settings.use_custom_settings = False
        self.settings.dc.dc_slider_position = value
        self.settings.dc_advanced.set_dc_slider(value)

    @property
    def dc_settings(self):
        """SIwave DC setting.

        deprecated:: 0.57.0
              Use :property:`settings` property instead.

        """
        warnings.warn("`dc_settings` is deprecated. Use `settings.dc` property instead.", DeprecationWarning)
        return self.settings.dc

    @property
    def settings(self):
        """Get the settings interface for SIwave DC simulation.

        Returns
        -------
        Settings
            An instance of the Settings class providing access to SIwave DC simulation settings.
        """
        return Settings(self, self.sim_setup_info)

    @property
    def dc_advanced_settings(self):
        """Siwave DC advanced settings.

        .. deprecated :: 0.57.0
                Use :property:`settings` property instead.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        warnings.warn(
            "`dc_advanced_settings` is deprecated. Use `settings.dc_advanced` property instead.", DeprecationWarning
        )
        return self.settings.dc_advanced

    @property
    def source_terms_to_ground(self):
        """Dictionary of grounded terminals.

        .. deprecated:: 0.57.0
            Use :property:`settings.source_terms_to_ground` property instead.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        warnings.warn(
            "`source_terms_to_ground` is deprecated. Use `settings.source_terms_to_ground` property instead.",
            DeprecationWarning,
        )
        return self.settings.source_terms_to_ground

    def add_source_terminal_to_ground(self, source_name, terminal=0):
        """Add a source terminal to ground.

        .. deprecated:: 0.57.0
            Use :method:`settings.add_source_terminal_to_ground` method instead.

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
        warnings.warn(
            "`add_source_terminal_to_ground` is deprecated. Use "
            "`settings.add_source_terminal_to_ground` method instead.",
            DeprecationWarning,
        )
        return self.settings.add_source_terminal_to_ground(source_name, terminal)


class General:
    """Class to manage global settings for the Siwave simulation setup module.
    Added to be compliant with ansys-edbe-core settings structure."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def pi_slider_pos(self):
        return self._parent.dc_slider_position

    @property
    def si_slider_pos(self):
        return self._parent.si_slider_position

    @property
    def use_custom_settings(self):
        return self._parent.use_dc_custom_settings

    @property
    def use_si_settings(self):
        return self._parent.use_si_settings


class SIwaveSParameterSettings:
    def __init__(self, parent):
        self._parent = parent

    @property
    def dc_behavior(self):
        return

    @property
    def extrapolation(self):
        return

    @property
    def interpolation(self):
        return

    @property
    def use_state_space(self):
        return True


class Settings(SimulationSetup, SiwaveDCIRSettings):
    """Class to manage global settings for the Siwave simulation setup module.
    Added to be compliant with ansys-edbe-core settings structure."""

    def __init__(self, parent, sim_setup_info):
        SimulationSetup.__init__(self, pedb=parent._pedb, edb_object=parent._edb_object)
        SiwaveDCIRSettings.__init__(self, parent)
        self._parent = parent
        self._sim_setup_info = sim_setup_info

    @property
    def advanced(self):
        return True

    @property
    def dc(self):
        return DCSettings(self._parent)

    @property
    def dc_advanced(self):
        return DCAdvancedSettings(self._parent)

    @property
    def general(self):
        return DCSettings(self._parent)

    @property
    def dc_report_config_file(self) -> str:
        """Path to the DC report configuration file."""
        # return self._sim_setup_info._edb_object.SimulationSettings.DCIRSettings.DCReportConfigFile
        return super().dc_report_config_file

    @dc_report_config_file.setter
    def dc_report_config_file(self, value: str):
        SiwaveDCIRSettings.dc_report_config_file = value

    @property
    def dc_report_show_active_devices(self) -> bool:
        """Flag to show active devices in the DC report."""
        return super().dc_report_show_active_devices

    @dc_report_show_active_devices.setter
    def dc_report_show_active_devices(self, value: bool):
        SiwaveDCIRSettings.dc_report_show_active_devices = value

    @property
    def enabled(self) -> bool:
        """Flag indicating if the setup is enabled."""
        return self._sim_setup_info.simulation_settings.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._sim_setup_info.simulation_settings.Enabled = value

    @property
    def export_dc_thermal_data(self) -> bool:
        """Flag to export DC thermal data."""
        return SiwaveDCIRSettings.export_dc_thermal_data

    @export_dc_thermal_data.setter
    def export_dc_thermal_data(self, value: bool):
        SiwaveDCIRSettings.export_dc_thermal_data = value

    @property
    def full_dc_report_path(self) -> str:
        """Full path to the DC report."""
        return SiwaveDCIRSettings.full_dc_report_path

    @full_dc_report_path.setter
    def full_dc_report_path(self, value: str):
        SiwaveDCIRSettings.full_dc_report_path = value

    @property
    def icepak_temp_file_path(self) -> str:
        """Path to the Icepak temporary file."""
        return SiwaveDCIRSettings.icepak_temp_file_path

    @icepak_temp_file_path.setter
    def icepak_temp_file_path(self, value: str):
        SiwaveDCIRSettings.icepak_temp_file_path = value

    @property
    def import_thermal_data(self) -> bool:
        """Flag to import thermal data."""
        return super().import_thermal_data

    @import_thermal_data.setter
    def import_thermal_data(self, value: bool):
        SiwaveDCIRSettings.import_thermal_data = value

    @property
    def s_parameter(self) -> SIwaveSParameterSettings:
        """S-parameter settings."""
        return SIwaveSParameterSettings(self._parent)

    @property
    def source_terms_to_ground(self) -> dict[str, int]:
        """Dictionary of grounded terminals.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return convert_netdict_to_pydict(super().source_terms_to_ground)

    @source_terms_to_ground.setter
    def source_terms_to_ground(self, value: dict[str, int]):
        SiwaveDCIRSettings.source_terms_to_ground = convert_pydict_to_netdict(value)

    @property
    def use_loop_res_for_per_pin(self):
        """Flag to use loop resistance for per-pin calculations."""
        return super().use_loop_res_for_per_pin

    @use_loop_res_for_per_pin.setter
    def use_loop_res_for_per_pin(self, value: bool):
        SiwaveDCIRSettings.use_loop_res_for_per_pin = value

    @property
    def via_report_path(self) -> str:
        """Path to the via report."""
        return super().via_report_path

    @via_report_path.setter
    def via_report_path(self, value: str):
        SiwaveDCIRSettings.via_report_path = value

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
        self._sim_setup_info.simulation_settings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(terminals)
        return self._update_setup()

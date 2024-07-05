import warnings

from pyedb.dotnet.edb_core.general import (
    convert_netdict_to_pydict,
    convert_pydict_to_netdict,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.sim_setup_info import SimSetupInfo
from pyedb.dotnet.edb_core.sim_setup_data.data.siw_dc_ir_settings import (
    SiwaveDCIRSettings,
)
from pyedb.dotnet.edb_core.sim_setup_data.io.siwave import (
    AdvancedSettings,
    DCAdvancedSettings,
    DCSettings,
)
from pyedb.dotnet.edb_core.utilities.simulation_setup import SimulationSetup
from pyedb.generic.general_methods import is_linux


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
                except:
                    pass


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
        return convert_netdict_to_pydict(self.get_sim_setup_info.simulation_settings.DCIRSettings.SourceTermsToGround)

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
        self.get_sim_setup_info.simulation_settings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
            terminals
        )
        return self._update_setup()

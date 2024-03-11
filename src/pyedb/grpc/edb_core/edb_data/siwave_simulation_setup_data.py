from pyedb.grpc.edb_core.edb_data.hfss_simulation_setup_data import EdbFrequencySweep
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import pyedb_function_handler
import ansys.edb.core.simulation_setup as simulation_setup
#from ansys.edb.simulation_setup.simulation_setup import SIWaveSimulationSetup


class SiwaveAdvancedSettings(object):
    def __init__(self, parent):
        self._parent = parent

    @property
    def simulation_setup(self):
        """EDB internal simulation setup object."""
        return self._parent._edb_simulation_setup

    @property
    def include_inter_plane_coupling(self):
        """Whether to turn on InterPlane Coupling.
        The setter will also enable custom settings.

        Returns
        -------
        bool
            ``True`` if interplane coupling is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_inter_plane_coupling

    @property
    def xtalk_threshold(self):
        """XTalk threshold.
        The setter enables custom settings.

        Returns
        -------
        str
        """
        return self.simulation_setup.settings.advanced.cross_talk_threshold

    @property
    def min_void_area(self):
        """Minimum void area to include.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.advanced.min_void_area

    @property
    def min_pad_area_to_mesh(self):
        """Minimum void pad area to mesh to include.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.advanced.min_pad_area_to_mesh

    @property
    def min_plane_area_to_mesh(self):
        """Minimum plane area to mesh to include.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.advanced.min_plane_area_to_mesh

    @property
    def snap_length_threshold(self):
        """Snapping length threshold.

        Returns
        -------
        str
        """
        return self.simulation_setup.settings.advanced.snap_length_threshold

    @property
    def return_current_distribution(self):
        """Whether to enable the return current distribution.
        This option is used to accurately model the change of the characteristic impedance
        of transmission lines caused by a discontinuous ground plane. Instead of injecting
        the return current of a trace into a single point on the ground plane,
        the return current for a high impedance trace is spread out.
        The trace return current is not distributed when all traces attached to a node
        have a characteristic impedance less than 75 ohms or if the difference between
        two connected traces is less than 25 ohms.

        Returns
        -------
        bool
            ``True`` if return current distribution is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.return_current_distribution

    @property
    def ignore_non_functional_pads(self):
        """Exclude non-functional pads.

        Returns
        -------
        bool
            `True`` if functional pads have to be ignored, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.ignore_non_functional_pads

    @property
    def include_coplane_coupling(self):
        """Whether to enable coupling between traces and adjacent plane edges.
        This option provides a model for crosstalk between signal lines and planes.
        Plane edges couple to traces when they are parallel.
        Traces and coplanar edges that are oblique to each other do not overlap
        and cannot be considered for coupling.


        Returns
        -------
        bool
            ``True`` if coplane coupling is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_co_plane_coupling

    @property
    def include_fringe_coupling(self):
        """Whether to include the effect of fringe field coupling between stacked cavities.


        Returns
        -------
        bool
            ``True`` if fringe coupling is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_fringe_coupling

    @property
    def include_split_plane_coupling(self):
        """Whether to account for coupling between adjacent parallel plane edges.
        Primarily, two different cases are being considered:
        - Plane edges that form a split.
        - Plane edges that form a narrow trace-like plane.
        The former leads to crosstalk between adjacent planes for which
        a specific coupling model is applied. For the latter, fringing effects
        are considered to model accurately the propagation characteristics
        of trace-like cavities. Further, the coupling between narrow planes is
        also modeled by enabling this feature.

        Returns
        -------
        bool
            ``True`` if split plane coupling is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_split_plane_coupling

    @property
    def include_infinite_ground(self):
        """Whether to Include a ground plane to serve as a voltage reference for traces and planes
        if they are not defined in the layout.

        Returns
        -------
        bool
            ``True`` if infinite ground is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_inf_gnd

    @property
    def include_trace_coupling(self):
        """Whether to model coupling between adjacent traces.
        Coupling is considered for parallel and almost parallel trace segments.

        Returns
        -------
        bool
            ``True`` if trace coupling is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_trace_coupling

    @property
    def include_vi_sources(self):
        """Whether to include the effect of parasitic elements from voltage and
        current sources.

        Returns
        -------
        bool
            ``True`` if vi sources is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.include_vi_sources

    @property
    def infinite_ground_location(self):
        """Elevation of the infinite unconnected ground plane placed under the design.

        Returns
        -------
        str
        """
        return self.simulation_setup.settings.advanced.inf_gnd_location

    @property
    def max_coupled_lines(self):
        """Maximum number of coupled lines to build the new coupled transmission line model.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.advanced.max_coupled_lines

    @property
    def automatic_mesh(self):
        """Whether to automatically pick a suitable mesh refinement frequency,
        depending on drawing size, number of modes, and/or maximum sweep
        frequency.

        Returns
        -------
        bool
            ``True`` if automatic mesh is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.advanced.mesh_automatic

    @property
    def perform_erc(self):
        """Whether to perform an electrical rule check while generating the solver input.
        In some designs, the same net may be divided into multiple nets with separate names.
        These nets are connected at a "star" point. To simulate these nets, the error checking
        for DC shorts must be turned off. All overlapping nets are then internally united
        during simulation.

        Returns
        -------
        bool
            ``True`` if perform erc is used, ``False`` otherwise.
        """
        return self.simulation_setup._settings.advanced.perform_erc

    @property
    def mesh_frequency(self):
        """Mesh size based on the effective wavelength at the specified frequency.

        Returns
        -------
        str
        """
        return self.simulation_setup.settings.advanced.mesh_frequency

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_inter_plane_coupling = value
            self._parent._update_setup()

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.cross_talk_threshold = value
            self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        self.simulation_setup.settings.advanced.min_void_area = value
        self._parent._update_setup()

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):
        self.simulation_setup.settings.advanced.min_pad_area_to_mesh = value
        self._parent._update_setup()

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        self.simulation_setup.settings.advanced.min_plane_area_to_mesh = value
        self._parent._update_setup()

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        self.simulation_setup.settings.advanced.snap_length_threshold = value
        self._parent._update_setup()

    @return_current_distribution.setter
    def return_current_distribution(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.advanced.return_current_distribution = value
            self._parent._update_setup()

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.advanced.ignore_non_functional_pads = value
            self._parent._update_setup()

    @include_coplane_coupling.setter
    def include_coplane_coupling(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_co_plane_coupling = value
            self._parent._update_setup()

    @include_fringe_coupling.setter
    def include_fringe_coupling(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_customer_settings = True
            self.simulation_setup.settings.advanced.include_fringe_coupling = value
            self._parent._update_setup()

    @include_split_plane_coupling.setter
    def include_split_plane_coupling(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_split_plane_coupling = value
            self._parent._update_setup()

    @include_infinite_ground.setter
    def include_infinite_ground(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_inf_gnd = value
            self._parent._update_setup()

    @include_trace_coupling.setter
    def include_trace_coupling(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_trace_coupling = value
            self._parent._update_setup()

    @include_vi_sources.setter
    def include_vi_sources(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.include_vi_sources = value
            self._parent._update_setup()

    @infinite_ground_location.setter
    def infinite_ground_location(self, value):
        self.simulation_setup.settings.general.use_custom_settings = True
        self.simulation_setup.settings.advanced.inf_gnd_location = value
        self._parent._update_setup()

    @max_coupled_lines.setter
    def max_coupled_lines(self, value):
        self.simulation_setup.settings.general.use_custom_settings = True
        self.simulation_setup.settings.advanced.max_coupled_lines = value
        self._parent._update_setup()

    @automatic_mesh.setter
    def automatic_mesh(self, value):
        self.simulation_setup.settings.general.use_custom_settings = True
        self.simulation_setup.settings.advanced.mesh_automatic = value
        self._parent._update_setup()

    @perform_erc.setter
    def perform_erc(self, value):
        self.simulation_setup.settings.advanced.perform_erc = value
        self._parent._update_setup()

    @mesh_frequency.setter
    def mesh_frequency(self, value):
        if isinstance(value, bool):
            self.simulation_setup.settings.general.use_custom_settings = True
            self.simulation_setup.settings.advanced.mesh_frequency = value
            self._parent._update_setup()


class SiwaveDCAdvancedSettings(object):
    def __init__(self, parent):
        self._parent = parent

    @property
    def simulation_setup(self):
        """EDB internal simulation setup object."""

        return self._parent._edb_simulation_setup

    @property
    def min_void_area(self):
        """Minimum area below which voids are ignored.

        Returns
        -------
        float
        """
        return self.simulation_setup.settings.dc_advanced.dc_min_void_area_to_mesh

    @property
    def min_plane_area(self):
        """Minimum area below which geometry is ignored.

        Returns
        -------
        float
        """
        return self.simulation_setup.settings.dc_advanced.dc_min_plane_area_to_mesh

    @property
    def energy_error(self):
        """Energy error.

        Returns
        -------
        float
        """
        return self.simulation_setup.settings.dc_advanced.energy_error

    @property
    def max_init_mesh_edge_length(self):
        """Initial mesh maximum edge length.

        Returns
        -------
        float
        """
        return self.simulation_setup.settings.dc_advanced.max_init_mesh_edge_length

    @property
    def max_num_pass(self):
        """Maximum number of passes.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.dc_advanced.max_num_passes

    @property
    def min_num_pass(self):
        """Minimum number of passes.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.dc_advanced.min_num_passes

    @property
    def mesh_bondwires(self):
        """Mesh bondwires.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.dc_advanced.mesh_bws

    @property
    def mesh_vias(self):
        """Mesh vias.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.dc_advanced.mesh_vias

    @property
    def num_bondwire_sides(self):
        """Number of bondwire sides.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.dc_advanced.num_bw_sides

    @property
    def num_via_sides(self):
        """Number of via sides.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.dc_advanced.num_via_sides

    @property
    def percent_local_refinement(self):
        """Percentage of local refinement.

        Returns
        -------
        float
        """
        return self.simulation_setup.settings.dc_advanced.percent_local_refinement

    @property
    def perform_adaptive_refinement(self):
        """Whether to perform adaptive mesh refinement.

        Returns
        -------
        bool
            ``True`` if adaptive refinement is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.dc_advanced.perform_adaptive_refinement

    @property
    def refine_bondwires(self):
        """Whether to refine mesh along bondwires.

        Returns
        -------
        bool
            ``True`` if refine bondwires is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.dc_advanced.refine_bws

    @property
    def refine_vias(self):
        """Whether to refine mesh along vias.

        Returns
        -------
        bool
            ``True`` if via refinement is used, ``False`` otherwise.

        """
        return self.simulation_setup.settings.dc_advanced.refine_vias

    @property
    def compute_inductance(self):
        """Whether to compute Inductance.

        Returns
        -------
        bool
            ``True`` if inductances will be computed, ``False`` otherwise.
        """
        return self.simulation_setup.settings.dc.compute_inductance

    @property
    def contact_radius(self):
        """Circuit element contact radius.

        Returns
        -------
        str
        """
        return self.simulation_setup.settings.dc.contact_radius

    @property
    def dc_slider_position(self):
        """Slider position for DC.

        Returns
        -------
        int
        """
        return self.simulation_setup.settings.dc.dc_slider_pos

    @property
    def use_dc_custom_settings(self):
        """Whether to use DC custom settings.
        This setting is automatically enabled by other properties when needed.

        Returns
        -------
        bool
            ``True`` if custom dc settings are used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.dc.use_dc_custom_settings

    @property
    def plot_jv(self):
        """Plot JV.

        Returns
        -------
        bool
            ``True`` if plot JV is used, ``False`` otherwise.
        """
        return self.simulation_setup.settings.dc.plot_jv

    @plot_jv.setter
    def plot_jv(self, value):
        self.simulation_setup.settings.dc.plot_jv = value
        self._parent._update_setup()

    @compute_inductance.setter
    def compute_inductance(self, value):
        self.simulation_setup.settings.dc.compute_inductance = value
        self._parent._update_setup()

    @contact_radius.setter
    def contact_radius(self, value):
        self.simulation_setup.settings.dc.contact_radius = value
        self._parent._update_setup()

    @dc_slider_position.setter
    def dc_slider_position(self, value):
        """DC simulation accuracy level slider position.
        Options:
        0- ``optimal speed``
        1- ``balanced``
        2- ``optimal accuracy``.
        """
        self.simulation_setup.settings.dc.use_dc_custom_settings = False
        self.simulation_setup.settings.dc.dc_slider_pos = value
        self._parent._update_setup()

    @use_dc_custom_settings.setter
    def use_dc_custom_settings(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = value
        self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        self.simulation_setup.settings.dc_advanced.dc_min_void_area_to_mesh = value
        self._parent._update_setup()

    @min_plane_area.setter
    def min_plane_area(self, value):
        self.simulation_setup.settings.dc_advanced.dc_min_plane_area_to_mesh = value
        self._parent._update_setup()

    @energy_error.setter
    def energy_error(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.energy_error = value
        self._parent._update_setup()

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.max_init_mesh_edge_length = value
        self._parent._update_setup()

    @max_num_pass.setter
    def max_num_pass(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.max_num_passes = value
        self._parent._update_setup()

    @min_num_pass.setter
    def min_num_pass(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.min_num_passes = value
        self._parent._update_setup()

    @mesh_bondwires.setter
    def mesh_bondwires(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.mesh_bws = value
        self._parent._update_setup()

    @mesh_vias.setter
    def mesh_vias(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.mesh_vias = value
        self._parent._update_setup()

    @num_bondwire_sides.setter
    def num_bondwire_sides(self, value):
        self.simulation_setup.settings.dc_advanced.mesh_bws = True
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.num_bw_sides = value
        self._parent._update_setup()

    @num_via_sides.setter
    def num_via_sides(self, value):
        self.simulation_setup.settings.dc_advanced.mesh_vias = True
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.num_via_sides = value
        self._parent._update_setup()

    @percent_local_refinement.setter
    def percent_local_refinement(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.percent_local_refinement = value
        self._parent._update_setup()

    @perform_adaptive_refinement.setter
    def perform_adaptive_refinement(self, value):
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.perform_adaptive_refinement = value
        self._parent._update_setup()

    @refine_bondwires.setter
    def refine_bondwires(self, value):
        self.simulation_setup.settings.dc_advanced.mesh_bws = True
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup.settings.dc_advanced.refine_bws = value
        self._parent._update_setup()

    @refine_vias.setter
    def refine_vias(self, value):
        self.simulation_setup.settings.dc_advanced.mesh_vias = True
        self.simulation_setup.settings.dc.use_dc_custom_settings = True
        self.simulation_setup._settings.dc_advanced.refine_vias = value
        self._parent._update_setup()


class SiwaveSYZSimulationSetup(SiwaveAdvancedSettings, object):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, edb, name=None, simulation_configuration=None):
        self._edb = edb
        self._sweep_data = []
        if not name and not simulation_configuration:
            name = generate_unique_name("siwave")
        self._edb_simulation_setup = simulation_setup.SIWaveSimulationSetup.create(self._edb.active_cell, name)
        if simulation_configuration:
            _get_edb_setup_info(simulation_configuration, self.edb_simulation_setup)
        #self._update_setup()
        self.setup_type = "SIWave"
        SiwaveAdvancedSettings.__init__(self, self)

    @property
    def edb_simulation_setup(self):
        """EDB internal simulation setup object."""
        return self._edb_simulation_setup

    @pyedb_function_handler()
    def _update_setup(self):
        if self.edb_simulation_setup.name in self._edb.setups:
            self._edb.layout.cell.delete_simulation_setup(self.name)
        self._edb.layout.cell.add_simulation_setup(self._edb_simulation_setup)
        return True

    @property
    def dc_settings(self):
        """Siwave DC settings.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return SiwaveDCAdvancedSettings(self)

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        if self._sweep_data:
            return self._sweep_data
        self._sweep_data = {}
        for i in self.simulation_setup.sweep_data:
            self._sweep_data[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
        return self._sweep_data

    @property
    def name(self):
        """Setup name."""
        return self.simulation_setup.name

    @name.setter
    def name(self, value):
        """Set name of the setup."""
        legacy_name = self.simulation_setup.Name
        self.simulation_setup.name = value
        self._update_setup()
        if legacy_name in self._edb.setups:
            del self._edb._setups[legacy_name]

    @property
    def enabled(self):
        """Whether the setup is enabled."""
        return self.simulation_setup.settings.enabled

    @enabled.setter
    def enabled(self, value):
        self.simulation_setup.settings.enabled = value
        self._update_setup()

    @property
    def pi_slider_postion(self):
        """PI solider position. Values are from ``1`` to ``3``."""
        return self.simulation_setup.settings.general.pi_slider_pos

    @pi_slider_postion.setter
    def pi_slider_postion(self, value):
        self.simulation_setup.settings.general.use_custom_settings = False
        self.simulation_setup.settings.general.pi_slider_pos = value
        #self._update_setup()

    @property
    def si_slider_postion(self):
        """SI solider position. Values are from ``1`` to ``3``."""
        return self.simulation_setup.settings.general.si_slider_pos

    @si_slider_postion.setter
    def si_slider_postion(self, value):
        self.simulation_setup.settings.general.use_custom_settings = False
        self.simulation_setup.settings.general.si_slider_pos = value
        #self._update_setup()

    @property
    def use_custom_settings(self):
        """Whether to use custom settings.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.general.use_custom_settings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        self.simulation_setup.settings.general.use_custom_settings = value
        self._update_setup()

    @property
    def use_si_settings(self):
        """Whether to use SI Settings.

        Returns
        -------
        bool
        """
        return self.simulation_setup.settings.general.use_si_settings

    @use_si_settings.setter
    def use_si_settings(self, value):
        self.simulation_setup.settings.general.use_custom_settings = False
        self.simulation_setup.settings.general.use_si_settings = value
        self._update_setup()

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.EdbFrequencySweep`

        Examples
        --------
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_frequency_sweep(frequency_sweep=[
        ...                           ["linear count", "0", "1kHz", 1],
        ...                           ["log scale", "1kHz", "0.1GHz", 10],
        ...                           ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...                           ])
        """
        if name in self.frequency_sweeps:
            return False
        else:
            name = generate_unique_name("sweep")
        sweep = EdbFrequencySweep(self, frequency_sweep, name)
        self._sweep_data[name] = sweep
        return sweep


def _parse_value(v):
    """

    Parameters
    ----------
    v :


    Returns
    -------

    """
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


@pyedb_function_handler()
def _get_edb_setup_info(edb_siwave_sim_setup, edb_sim_setup_info):
    string = str(edb_siwave_sim_setup).replace("\t", "").split("\r\n")
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
                sources[source[0]] = source[1]
            edb_sim_setup_info.simulation_settings.dc_ir_settings.source_terms_to_ground = sources
            break
    for k in keys:
        value = _parse_value(values[keys.index(k)])
        setter = None
        if k in dir(edb_sim_setup_info.simulation_settings):
            setter = edb_sim_setup_info.simulation_settings
        elif k in dir(edb_sim_setup_info.simulation_settings.advanced_settings):
            setter = edb_sim_setup_info.simulation_settings.advanced_settings

        elif k in dir(edb_sim_setup_info.simulation_settings.dc_advanced_settings):
            setter = edb_sim_setup_info.simulation_settings.dc_advanced_settings
        elif "DCIRSettings" in dir(edb_sim_setup_info.simulation_settings) and k in dir(
            edb_sim_setup_info.simulation_settings.dc_ir_settings
        ):
            setter = edb_sim_setup_info.simulation_settings.dc_ir_settings
        elif k in dir(edb_sim_setup_info.simulation_settings.dc_settings):
            setter = edb_sim_setup_info.simulation_settings.dc_settings
        elif k in dir(edb_sim_setup_info.simulation_settings.advanced_settings):
            setter = edb_sim_setup_info.simulation_settings.advanced_settings
        if setter:
            try:
                setter.__setattr__(k, value)
            except TypeError:
                try:
                    setter.__setattr__(k, str(value))
                except:
                    pass


class SiwaveDCSimulationSetup(SiwaveDCAdvancedSettings, object):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, edb, name=None, edb_siwave_sim_setup=None):
        self._edb = edb
        self._mesh_operations = {}
        self._edb_sim_setup_info = SiwaveDCSimulationSetup()
        if edb_siwave_sim_setup:
            _get_edb_setup_info(edb_siwave_sim_setup, self.simulation_setup)

        else:
            if not name:
                self._edb_sim_setup_info.name = generate_unique_name("siwave")
            else:
                self._edb_sim_setup_info.name = name
            self._update_setup()
        self.setup_type = "kSIWaveDCIR"

        SiwaveDCAdvancedSettings.__init__(self, self)

    @property
    def edb_sim_setup_info(self):
        """EDB internal simulation setup object."""
        return self._edb_sim_setup_info

    @pyedb_function_handler()
    def _update_setup(self):
        edb_sim_setup = SiwaveDCSimulationSetup(self._edb_sim_setup_info)
        if self.name in self._edb.setups:
            self._edb.layout.cell.delete_simulation_setupSetup(self.name)
        self._edb.active_cell.add_simulation_setup(edb_sim_setup)
        return True

    @property
    def name(self):
        """Setup name."""
        return self.simulation_setup.name

    @name.setter
    def name(self, value):
        """Set name of the setup."""
        legacy_name = self._edb_sim_setup_info.name
        self._edb_sim_setup_info.name = value
        self._update_setup()
        if legacy_name in self._edb.setups:
            del self._edb._setups[legacy_name]

    @property
    def enabled(self):
        """Whether setup is enabled."""
        return self.simulation_setup.settings.general.enabled

    @enabled.setter
    def enabled(self, value):
        self.simulation_setup.settings.general.enabled = value
        self._update_setup()

    @property
    def source_terms_to_ground(self):
        """Dictionary of grounded terminals.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return self.simulation_setup.settings.dc.source_terms_to_ground

    @pyedb_function_handler()
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
        self.simulation_setup.settings.dc.source_terms_to_ground = terminals
        return self._update_setup()

from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import pyedb_function_handler
from ansys.edb.simulation_setup import SweepData
import ansys.edb.utility as utility
import ansys.edb.simulation_setup as simulation_setup


class EdbFrequencySweep(object):
    """Manages EDB methods for frequency sweep."""

    def __init__(self, parent, edb_sweep_data=None):
        self._edb_sim_setup = parent.edb_sim_setup
        if edb_sweep_data:
            self._edb_sweep_data = edb_sweep_data
            self._name = self._edb_sweep_data.name

    @pyedb_function_handler()
    def _update_sweep(self):
        """Update sweep."""
        pass

    @property
    def edb_sweep_data(self):
        return self._edb_sim_setup.sweep_data

    @property
    def name(self):
        """Name of the sweep."""
        return self._edb_sweep_data.name

    @name.setter
    def name(self, value):
        """Set name of this sweep"""
        if isinstance(value, str):
            self._edb_sweep_data.name = value

    @property
    def sweep_type(self):
        """Sweep type."""
        return [sweep.distribution for sweep in self.edb_sweep_data]

    @property
    def frequencies(self):
        """List of frequencies points."""
        return self.edb_sweep_data.frequencies

    @property
    def adaptive_sampling(self):
        """Whether adaptive sampling is used.

        Returns
        -------
        bool
            ``True`` if adaptive sampling is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.adaptive_sampling
        pass

    @property
    def adv_dc_extrapolation(self):
        """Whether to turn on advanced DC Extrapolation.

        Returns
        -------
        bool
            ``True`` if advanced DC Extrapolation is used, ``False`` otherwise.

        """
        return self._edb_sim_setup.settings.option.enhanced_low_frequency_accuracy

    @adv_dc_extrapolation.setter
    def adv_dc_extrapolation(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.option.enhanced_low_frequency_accuracy = value

    @property
    def auto_s_mat_only_solve(self):
        """Whether to turn on Auto/Manual SMatrix only solve.

        Returns
        -------
        bool
            ``True`` if Auto/Manual SMatrix only solve is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.auto_s_mat_only_solve

    @property
    def enforce_causality(self):
        """Whether to enforce causality during interpolating sweep.

        Returns
        -------
        bool
            ``True`` if enforce causality is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.enforce_causality
        pass

    @property
    def enforce_dc_and_causality(self):
        """Whether to enforce DC point and causality.

        Returns
        -------
        bool
            ``True`` if enforce dc point and causality is used, ``False`` otherwise.

        """
        # return self._edb_sweep_data.enforce_dc_and_causality
        pass

    @property
    def enforce_passivity(self):
        """Whether to enforce passivity during interpolating sweep.

        Returns
        -------
        bool
            ``True`` if enforce passivity is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.enforce_passivity
        pass

    @property
    def freq_sweep_type(self):
        """Sweep type.
        Options are:
        - ``kInterpolatingSweep``.
        - ``kDiscreteSweep``.
        - ``kBroadbandFastSweep``.

        Returns
        -------
        str
        """
        pass
        # return self._edb_sweep_data.freq_sweeptype

    @property
    def interp_use_full_basis(self):
        """Whether to use Full basis elements.

        Returns
        -------
        bool
            ``True`` if full basis interpolation is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.interp_use_full_basis
        pass

    @property
    def interp_use_port_impedance(self):
        """Whether to turn on the port impedance interpolation.

        Returns
        -------
        bool
            ``True`` if port impedance is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.interp_use_port_impedance
        pass

    @property
    def interp_use_prop_const(self):
        """Whether to use propagation constants.

        Returns
        -------
        bool
            ``True`` if propagation constants are used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.interp_use_prop_const
        pass

    @property
    def interp_use_s_matrix(self):
        """Whether to use S matrix.

        Returns
        -------
        bool
            ``True`` if S matrix are used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.interp_use_s_matrix
        pass

    @property
    def max_solutions(self):
        """Number of aximum solutions.

        Returns
        -------
        int
        """
        # return self._edb_sweep_data.max_solutions
        pass

    @property
    def min_freq_s_mat_only_solve(self):
        """Minimum frequency SMatrix only solve.

        Returns
        -------
        str
            Frequency with units.
        """
        # return self._edb_sweep_data.min_freq_s_mat_only_solve
        pass

    @property
    def min_solved_freq(self):
        """Minimum solved frequency.

        Returns
        -------
        str
            Frequency with units.
        """
        # return self._edb_sweep_data.min_solved_freq
        pass

    @property
    def passivity_tolerance(self):
        """Tolerance for passivity enforcement.

        Returns
        -------
        float
        """
        # return self._edb_sweep_data.passivity_tolerance
        pass

    @property
    def relative_s_error(self):
        """Specify S-parameter error tolerance for interpolating sweep.

        Returns
        -------
        float
        """
        # return self._edb_sweep_data.relative_s_error
        pass

    @property
    def save_fields(self):
        """Whether to turn on or off the extraction of surface current data.

        Returns
        -------
        bool
            ``True`` if save fields is enabled, ``False`` otherwise.
        """
        # return self._edb_sweep_data.save_fields
        pass

    @property
    def save_rad_fields_only(self):
        """Whether to turn on save radiated fields only.

        Returns
        -------
        bool
            ``True`` if save radiated field only is used, ``False`` otherwise.

        """
        # return self._edb_sweep_data.save_rad_fields_only
        pass

    @property
    def use_q3d_for_dc(self):
        """Whether to enable Q3D solver for DC point extraction .

        Returns
        -------
        bool
            ``True`` if Q3d for DC point is used, ``False`` otherwise.
        """
        # return self._edb_sweep_data.use_q3d_for_dc
        pass

    @adaptive_sampling.setter
    def adaptive_sampling(self, value):
        # self._edb_sweep_data.adaptive_sampling = value
        pass

    @auto_s_mat_only_solve.setter
    def auto_s_mat_only_solve(self, value):
        # self._edb_sweep_data.auto_s_mat_only_solve = value
        pass

    @enforce_causality.setter
    def enforce_causality(self, value):
        # self._edb_sweep_data.enforce_causality = value
        pass

    @enforce_dc_and_causality.setter
    def enforce_dc_and_causality(self, value):
        # self._edb_sweep_data.enforce_dc_and_causality = value
        pass

    @enforce_passivity.setter
    def enforce_passivity(self, value):
        # self._edb_sweep_data.enforce_passivity = value
        pass

    @freq_sweep_type.setter
    def freq_sweep_type(self, value):
        # edb_freq_sweep_type = self._edb_sweep_data.t_freq_sweep_type
        # if value in [0, "InterpolatingSweep"]:
        #     self._edb_sweep_data.freq_sweep_type = edb_freq_sweep_type.interpolating_sweep
        # elif value in [1, "DiscreteSweep"]:
        #     self._edb_sweep_data.freq_sweep_type = edb_freq_sweep_type.discrete_sweep
        # elif value in [2, "BroadbandFastSweep"]:
        #     self._edb_sweep_data.freq_sweep_type = edb_freq_sweep_type.broadband_fast_sweep
        # elif value in [3, "NumSweepTypes"]:
        #     self._edb_sweep_data.freq_sweep_type = edb_freq_sweep_type.num_sweep_types
        pass

    @interp_use_full_basis.setter
    def interp_use_full_basis(self, value):
        # self._edb_sweep_data.interp_use_full_basis = value
        pass

    @interp_use_port_impedance.setter
    def interp_use_port_impedance(self, value):
        # self._edb_sweep_data.interp_use_port_impedance = value
        pass

    @interp_use_prop_const.setter
    def interp_use_prop_const(self, value):
        # self._edb_sweep_data.interp_use_prop_const = value
        pass

    @interp_use_s_matrix.setter
    def interp_use_s_matrix(self, value):
        # self._edb_sweep_data.interp_use_s_matrix = value
        pass

    @max_solutions.setter
    def max_solutions(self, value):
        # self._edb_sweep_data.max_solutions = value
        pass

    @min_freq_s_mat_only_solve.setter
    def min_freq_s_mat_only_solve(self, value):
        # self._edb_sweep_data.min_freq_s_mat_only_solve = value
        pass

    @min_solved_freq.setter
    def min_solved_freq(self, value):
        # self._edb_sweep_data.min_solved_freq = value
        pass

    @passivity_tolerance.setter
    def passivity_tolerance(self, value):
        # self._edb_sweep_data.passivity_tolerance = value
        pass

    @relative_s_error.setter
    def relative_s_error(self, value):
        # self._edb_sweep_data.relative_s_error = value
        pass

    @save_fields.setter
    def save_fields(self, value):
        # self._edb_sweep_data.save_fields = value
        pass

    @save_rad_fields_only.setter
    def save_rad_fields_only(self, value):
        # self._edb_sweep_data.save_rad_fields_only = value
        pass

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value):
        # self._edb_sweep_data.use_q3d_for_dc = value
        pass

    @pyedb_function_handler()
    def _set_frequencies(self, freq_sweep_string="Linear Step: 0GHz to 20GHz, step=0.05GHz"):
        self.edb_sweep_data.frequency_string = freq_sweep_string

    @pyedb_function_handler()
    def set_frequencies_linear_scale(self, start="0.1GHz", stop="20GHz", step="50MHz"):
        """Set a linear scale frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        step : str, float
            Step frequency.

        Returns
        -------
        str
            String representing the frequency sweep data.

        """
        if not self.edb_sweep_data:
            sweep_name = generate_unique_name("pyedb_sweep")
        else:
            sweep_name = self.edb_sweep_data.name
        self.edb_sweep_data = simulation_setup.SweepData(name=sweep_name,
                                                         distribution="LIN",
                                                         start_f=start,
                                                         end_f=stop,
                                                         step=step,
                                                         fast_sweep=False)
        return self.edb_sweep_data.frequency_string

    @pyedb_function_handler()
    def set_frequencies_linear_count(self, start="1kHz", stop="0.1GHz", count=10):
        """Set a linear count frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        count : int
            Step frequency.

        Returns
        -------
        str
            String representing the frequency sweep data.

        """
        if not self.edb_sweep_data:
            sweep_name = generate_unique_name("pyedb_sweep")
        else:
            sweep_name = self.edb_sweep_data.name
        self.edb_sweep_data = simulation_setup.SweepData(name=sweep_name,
                                                         distribution="LINC",
                                                         start_f=start,
                                                         end_f=stop,
                                                         step=count,
                                                         fast_sweep=False)
        return self.edb_sweep_data.frequency_string

    @pyedb_function_handler()
    def set_frequencies_log_scale(self, start="1kHz", stop="0.1GHz", samples=10):
        """Set a log count frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        samples : int
            Step frequency.

        Returns
        -------
        bool
            ``True`` if correctly executed, ``False`` otherwise.
        """
        if not self.edb_sweep_data:
            sweep_name = generate_unique_name("pyedb_sweep")
        else:
            sweep_name = self.edb_sweep_data.name
        self.edb_sweep_data = simulation_setup.SweepData(name=sweep_name,
                                                         distribution="DEC",
                                                         start_f=start,
                                                         end_f=stop,
                                                         step=samples,
                                                         fast_sweep=False)
        return self.edb_sweep_data.frequency_string

    # @pyedb_function_handler()
    # def set_frequencies(self, frequency_list=None):
    #     """Set frequency list to the sweep frequencies.
    #
    #     Parameters
    #     ----------
    #     frequency_list : list, optional
    #         List of lists with four elements. Each list must contain:
    #
    #           1- frequency type (``"linear count"``, ``"log scale"`` or ``"linear scale"``)
    #           2- start frequency
    #           3- stop frequency
    #           4- step frequency or count
    #
    #     Returns
    #     -------
    #     bool
    #         ``True`` if correctly executed, ``False`` otherwise.
    #
    #     """
    #     if not frequency_list:
    #         frequency_list = [
    #             ["linear count", "0", "1kHz", 1],
    #             ["log scale", "1kHz", "0.1GHz", 10],
    #             ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
    #         ]
    #     temp = []
    #     for i in frequency_list:
    #         if i[0] == "linear count":
    #             temp.extend(list(self._edb_sweep_data.SetFrequencies(i[1], i[2], i[3])))
    #         elif i[0] == "linear scale":
    #             temp.extend(list(self._edb_sweep_data.SetFrequencies(i[1], i[2], i[3])))
    #         elif i[0] == "log scale":
    #             temp.extend(list(self._edb_sweep_data.SetLogFrequencies(i[1], i[2], i[3])))
    #         else:
    #             return False
    #     self._edb_sweep_data.Frequencies.Clear()
    #     for i in temp:
    #         self._edb_sweep_data.Frequencies.Add(i)
    #     return self._update_sweep()


class MeshOperation(object):
    """Mesh Operation Class."""

    def __init__(self, parent, edb_mesh_operation):
        self._edb_mesh_operation = edb_mesh_operation
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def mesh_operation_object(self):
        """
        0- ``MeshSetupBase``
        1- ``MeshSetupLength``
        2- ``MeshSetupSkinDepth``
        Returns
        -------

        """
        if self.mesh_operation_type == 0:
            return self
        elif self.mesh_operation_type == 1:
            return MeshOperationLength(self._edb_mesh_operation)
        elif self.mesh_operation_type == 2:
            return MeshOperationSkinDepth(self._edb_mesh_operation)

    @property
    def enabled(self):
        """Whether if mesh operation is enabled.

        Returns
        -------
        bool
            ``True`` if mesh operation is used, ``False`` otherwise.
        """
        return self._edb_mesh_operation.enabled

    @enabled.setter
    def enabled(self, value):
        if isinstance(value, bool):
            self._edb_mesh_operation.enabled = value

    @property
    def mesh_operation_type(self):
        """Mesh operation type.
        Options:
        0- ``MeshSetupBase``
        1- ``MeshSetupLength``
        2- ``MeshSetupSkinDepth``

        Returns
        -------
        int
        """
        if isinstance(self._edb_mesh_operation, simulation_setup.MeshOperation):
            return 0
        elif isinstance(self._edb_mesh_operation, simulation_setup.LengthMeshOperation):
            return 1
        elif isinstance(self._edb_mesh_operation, simulation_setup.SkinDepthMeshOperation):
            return 2
        else:
            return None

    @property
    def mesh_region(self):
        """Mesh region name.

        Returns
        -------
        str
            Name of the mesh region.
        """
        return self._edb_mesh_operation.mesh_region

    @property
    def name(self):
        """Mesh operation name.

        Returns
        -------
        str
        """
        return self._edb_mesh_operation.name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._edb_mesh_operation.name = value

    @property
    def nets_layers(self):
        """List of nets and layers.

        Returns
        -------
        list
           List of lists with three elements. Each list must contain:
           1- net name
           2- layer name
           3- bool.
           Third element is represents whether if the mesh operation is sheet or not.

        """
        return self._edb_mesh_operation.net_layer_info

    @nets_layers.setter
    def nets_layers(self, values):
        temp = []
        for net, layers in values.items():
            for layer in layers:
                temp.append(net, layer, True)
        self._edb_mesh_operation.net_layer_info = temp

    @property
    def refine_inside(self):
        """Whether to turn on refine inside objects.

        Returns
        -------
        bool
            ``True`` if refine inside objects is used, ``False`` otherwise.

        """
        return self._edb_mesh_operation.refine_inside

    @refine_inside.setter
    def refine_inside(self, value):
        if isinstance(value, bool):
            self._edb_mesh_operation.refine_inside = value


class MeshOperationLength(MeshOperation):
    """Mesh operation Length class.
    This class is accessible from Hfss Setup in EDB and add_length_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_length_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, edb_mesh_operation):
        MeshOperation.__init__(self, edb_mesh_operation)
        self._edb_mesh_operation = edb_mesh_operation

    @property
    def max_length(self):
        """Maximum length of elements.

        Returns
        -------
        str
        """
        return self._edb_mesh_operation.max_length

    @max_length.setter
    def max_length(self, value):
        self._edb_mesh_operation.max_length = str(utility.Value(value))

    @property
    def restrict_max_length(self):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        return self._edb_mesh_operation.restrict_max_length

    @restrict_max_length.setter
    def restrict_max_length(self, value):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        if isinstance(value, bool):
            self._edb_mesh_operation.restrict_max_length = value

    @property
    def max_elements(self):
        return self._edb_mesh_operation.max_elements

    @max_elements.setter
    def max_elements(self, value):
        self._edb_mesh_operation.max_elements = str(utility.Value(value))

    @property
    def restrict_max_elements(self):
        return self._edb_mesh_operation.restrict_max_elements

    @restrict_max_elements.setter
    def restrict_max_elements(self, value):
        if isinstance(value, bool):
            self._edb_mesh_operation.restrict_max_elements = value


class MeshOperationSkinDepth(MeshOperation):
    """Mesh operation Skin Depth class.
    This class is accessible from Hfss Setup in EDB and assign_skin_depth_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_skin_depth_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, parent, edb_mesh_operation):
        MeshOperation.__init__(self, edb_mesh_operation)
        self._edb_mesh_operation = edb_mesh_operation

    @property
    def max_elements(self):
        return self._edb_mesh_operation.max_elements

    @max_elements.setter
    def max_elements(self, value):
        self._edb_mesh_operation.max_elements = value

    @property
    def restrict_max_elements(self):
        return self._edb_mesh_operation.restrict_max_elements

    @restrict_max_elements.setter
    def restrict_max_elements(self, value):
        if isinstance(value, bool):
            self._edb_mesh_operation.restrict_max_elements = value

    @property
    def number_of_layers(self):
        return self._edb_mesh_operation.number_of_layers

    @number_of_layers.setter
    def number_of_layers(self, value):
        self._edb_mesh_operation.number_of_layers = value

    @property
    def refine_inside(self):
        return self._edb_mesh_operation.refine_inside

    @refine_inside.setter
    def refine_inside(self, value):
        self._edb_mesh_operation.refine_inside = value

    @property
    def skin_depth(self):
        """Skin depth value.

        Returns
        -------
        str
        """
        return self._edb_mesh_operation.skin_depth

    @skin_depth.setter
    def skin_depth(self, value):
        self._edb_mesh_operation.skin_depth = value

    @property
    def surface_triangle_length(self):
        """Surface triangle length value.

        Returns
        -------
        str
        """
        return self._edb_mesh_operation.surface_triangle_length

    @surface_triangle_length.setter
    def surface_triangle_length(self, value):
        self._edb_mesh_operation.surface_triangle_length = value


class HfssPortSettings(object):
    """Manages EDB methods for HFSS port settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def _hfss_port_settings(self):
        return self._edb_sim_setup.settings.solver

    @property
    def max_delta_z0(self):
        """Maximum change to Z0 in successive passes.

        Returns
        -------
        float
        """
        return self._hfss_port_settings.max_delta_z0

    @max_delta_z0.setter
    def max_delta_z0(self, value):
        self._hfss_port_settings.max_delta_z0 = value

    @property
    def max_triangles_for_wave_port(self):
        """Maximum number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.max_triangles_for_wave_port

    @max_triangles_for_wave_port.setter
    def max_triangles_for_wave_port(self, value):
        self._hfss_port_settings.max_triangles_for_wave_port = value

    @property
    def min_triangles_for_wave_port(self):
        """Minimum number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.min_triangles_for_wave_port

    @min_triangles_for_wave_port.setter
    def min_triangles_for_wave_port(self, value):
        self._hfss_port_settings.min_triangles_for_wave_port = value

    @property
    def set_triangles_for_wave_port(self):
        """Whether to enable setting of minimum and maximum mesh limits for wave ports.

        Returns
        -------
        bool
            ``True`` if triangles wave port  is used, ``False`` otherwise.
        """
        return self._hfss_port_settings.set_triangles_for_wave_port

    @set_triangles_for_wave_port.setter
    def set_triangles_for_wave_port(self, value):
        if isinstance(value, bool):
            self._hfss_port_settings.set_triangles_for_wave_port = value


class HfssSolverSettings(object):
    """Manages EDB methods for HFSS solver settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def enhanced_low_freq_accuracy(self):
        """Whether to enable legacy low-frequency sampling.

        Returns
        -------
        bool
            ``True`` if low frequency accuracy is used, ``False`` otherwise.
        """
        return self._edb_sim_setup.settings.options.enhanced_low_frequency_accuracy

    @enhanced_low_freq_accuracy.setter
    def enhanced_low_freq_accuracy(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.options.enhanced_low_frequency_accuracy = value

    @property
    def order_basis(self):
        """Order of the basic functions for HFSS.
        - 0=Zero.
        - 1=1st order.
        - 2=2nd order.
        - 3=Mixed.

        Returns
        -------
        int
            Integer value according to the description."""
        mapping = {0: "zero", 1: "first", 2: "second", 3: "mixed"}
        return mapping[self._edb_sim_setup.settings.options.order_basis.value]

    @order_basis.setter
    def order_basis(self, value):
        mapping = {"zero": 0, "first": 1, "second": 2, "mixed": 3}
        self._edb_sim_setup.settings.options.order_basis = simulation_setup.BasisFunctionOrder(mapping[value])

    @property
    def relative_residual(self):
        """Residual for use by the iterative solver.

        Returns
        -------
        float
        """
        return self._edb_sim_setup.settings.options.relative_residual

    @relative_residual.setter
    def relative_residual(self, value):
        self._edb_sim_setup.settings.options.relative_residual = value

    @property
    def solver_type(self):
        """Get solver type to use (Direct/Iterative/Auto) for HFSS.
        Options:
        0- ``AutoSolver``.
        1- ``DirectSolver``.
        2- ``IterativeSolver``.

        Returns
        -------
        str
        """
        mapping = {0: "auto", 1: "direct", 2: "iterative"}
        return mapping[self._edb_sim_setup.settings.options.solver_type.value]

    @solver_type.setter
    def solver_type(self, value):
        mapping = {"direct": simulation_setup.SolverType.DIRECT_SOLVER,
                   "iterative": simulation_setup.SolverType.ITERATIVE_SOLVER}
        self._edb_sim_setup.settings.options.solver_type = mapping[value]

    @property
    def use_shell_elements(self):
        """Whether to enable use of shell elements.

        Returns
        -------
        bool
            ``True`` if shall elements are used, ``False`` otherwise.
        """
        # return self._hfss_solver_settings.use_shell_elements
        return False

    @use_shell_elements.setter
    def use_shell_elements(self, value):
        # self._hfss_solver_settings.use_shell_elements = value
        # self._parent._update_setup()
        pass


class AdaptiveFrequencyData(object):
    """Manages EDB methods for adaptive frequency data."""

    def __init__(self, adaptive_frequency_data):
        self._adaptive_frequency_data = adaptive_frequency_data

    @property
    def adaptive_frequency(self):
        """Adaptive frequency for the setup.

        Returns
        -------
        str
            Frequency with units.
        """
        return self._adaptive_frequency_data.adaptive_frequency

    @adaptive_frequency.setter
    def adaptive_frequency(self, value):
        self._adaptive_frequency_data.adaptive_frequency = value

    @property
    def max_delta(self):
        """Maximum change of S-parameters between two consecutive passes, which serves as
        a stopping criterion.

        Returns
        -------
        str
        """
        return self._adaptive_frequency_data.max_delta

    @max_delta.setter
    def max_delta(self, value):
        self._adaptive_frequency_data.max_delta = str(value)

    @property
    def max_passes(self):
        """Maximum allowed number of mesh refinement cycles.

        Returns
        -------
        int
        """
        return self._adaptive_frequency_data.max_passes

    @max_passes.setter
    def max_passes(self, value):
        self._adaptive_frequency_data.max_passes = value


class AdaptiveSettings(object):
    """Manages EDB methods for adaptive settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def adapt_type(self):
        """Adaptive type.
        Options:
        1- ``SINGLE``.
        2- ``MULTI_FREQUENCIES``.
        3- ``BROADBAND``.

        Returns
        -------
        str
        """
        return self._edb_sim_setup.settings.general.adaptive_solution_type.name

    @adapt_type.setter
    def adapt_type(self, value):
        adapt_solution_type = simulation_setup.AdaptType(value)
        self._edb_sim_setup.settings.general.adaptive_solution_type = adapt_solution_type

    @property
    def adaptive_frequency_data_list(self):
        """List of all adaptive frequency data.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveFrequencyData`
        """
        if self.adapt_type == "SINGLE":
            return [AdaptiveFrequencyData(self._edb_sim_setup.settings.general.single_frequency_adaptive_solution)]
        elif self.adapt_type == "MULTI_FREQUENCIES":
            return [AdaptiveFrequencyData(i) for i in
                    self._edb_sim_setup.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies]

    @property
    def do_adaptive(self):
        """Whether if adpative mesh is on.

        Returns
        -------
        bool
            ``True`` if adaptive is used, ``False`` otherwise.

        """
        # return self.adaptive_settings.do_adaptive
        return True

    @property
    def max_refine_per_pass(self):
        """Maximum number of mesh elementat that can be added during an adaptive pass.

        Returns
        -------
        int
        """
        return self._edb_sim_setup.settings.options.max_refinement_per_pass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value):
        if isinstance(value, int):
            self._edb_sim_setup.settings.options.max_refinement_per_pass = value

    @property
    def use_max_refinement(self):
        return self._edb_sim_setup.settings.options.use_max_refinement

    @use_max_refinement.setter
    def use_max_refinement(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.options.use_max_refinement = value

    @property
    def min_passes(self):
        """Minimum number of passes.

        Returns
        -------
        int
        """
        return self._edb_sim_setup.settings.options.min_passes

    @min_passes.setter
    def min_passes(self, value):
        if isinstance(value, int):
            self._edb_sim_setup.settings.options.min_passes = value

    @property
    def save_fields(self):
        """Whether to turn on save fields.

        Returns
        -------
        bool
            ``True`` if save fields is used, ``False`` otherwise.
        """
        return self._edb_sim_setup.settings.general.save_fields

    @save_fields.setter
    def save_fields(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.general.save_fields = value

    @property
    def save_rad_field_only(self):
        """Whether to turn on save radiated fields only.

        Returns
        -------
        bool
            ``True`` if save radiated field only is used, ``False`` otherwise.

        """
        return self._edb_sim_setup.settings.general.save_rad_fields_only

    @save_rad_field_only.setter
    def save_rad_field_only(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.general.save_rad_fields_only = value

    @property
    def use_max_refinement(self):
        """Whether to turn on maximum refinement.

        Returns
        -------
        bool
            ``True`` if maximum refinement is used, ``False`` otherwise.
        """
        return self._edb_sim_setup.settings.options.use_max_refinement

    @use_max_refinement.setter
    def use_max_refinement(self, value):
        if isinstance(value, bool):
            self._edb_sim_setup.settings.options.use_max_refinement = value

    @pyedb_function_handler()
    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s=0.02):
        """Set single frequency solution.

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
        self.adapt_type = 0
        single_adapt_solution = self._edb_sim_setup.settings.general.single_frequency_adaptive_solution
        single_adapt_solution.adaptive_frequency = frequency
        single_adapt_solution.max_delta = str(max_delta_s)
        single_adapt_solution.max_passes = max_num_passes
        self._edb_sim_setup.settings.general.single_frequency_adaptive_solution = single_adapt_solution
        return True

    @pyedb_function_handler()
    def set_solution_multi_frequencies(self, frequencies=("5GHz", "10GHz"),
                                       max_delta_s=(0.02, 0.01), max_passes=30, output_variables=None):
        self.adapt_type = 1
        multi_freq_adapt_freqs = self._edb_sim_setup.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies
        multi_freq_adapt_freqs = []
        for i in range(len(frequencies)):
            if not output_variables:
                edb_adpt_freq = simulation_setup.AdaptiveFrequency(adaptive_frequency=frequencies[i],
                                                                   max_delta=max_delta_s[i])
                multi_freq_adapt_freqs.append(edb_adpt_freq)
            else:
                output_variable = output_variables[i]
                edb_adpt_freq = simulation_setup.AdaptiveFrequency(adaptive_frequency=frequencies[i],
                                                                   max_delta=max_delta_s[i],
                                                                   output_variables=output_variable)
                multi_freq_adapt_freqs.append(edb_adpt_freq)
        self._edb_sim_setup.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies = multi_freq_adapt_freqs
        self._edb_sim_setup.settings.general.multi_frequency_adaptive_solution.max_passes = max_passes
        return True

    @pyedb_function_handler()
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
        self.adapt_type = 2
        broadband_adapt_solution = self._edb_sim_setup.settings.general.broadband_adaptive_solution
        broadband_adapt_solution.low_frequency = str(utility.Value(low_frequency))
        broadband_adapt_solution.high_frequency = str(utility.Value(high_frequency))
        broadband_adapt_solution.max_num_passes = max_num_passes
        broadband_adapt_solution.max_delta = str(max_delta_s)
        self._edb_sim_setup.settings.general.broadband_adaptive_solution = broadband_adapt_solution
        return True

    @pyedb_function_handler()
    def add_adaptive_frequency_data(self, frequency=0, max_num_passes=10, max_delta_s=0.02, output_variable=None):
        """Add adaptive frequency point. Supports all setup types (Single, Multi-frequency)

        Parameters
        ----------
        frequency : str, float
            Frequency with units or float frequency (in Hz).
        max_num_passes : int, optional
            Maximum number of passes. The default is ``10``.
        max_delta_s : float, optional
            Maximum delta S. The default is ``0.02``.
        output_variable : dict { str : str }: Map of output variable name to maximum delta S.
            Optional.

        Returns
        -------
        bool
            ``True`` if method is successful, ``False`` otherwise.
        """
        if self.adapt_type == "SINGLE":
            adapt_solution = self._edb_sim_setup.settings.general.single_frequency_adaptive_solution
            adapt_solution.adaptive_frequency = str(utility.Value(frequency))
            adapt_solution.max_passes = max_num_passes
            adapt_solution.max_delta = str(max_delta_s)
            self._edb_sim_setup.settings.general.single_frequency_adaptive_solution = adapt_solution
            return True
        elif self.adapt_type == "MULTI_FREQUENCIES":
            multi_freq_solution = self._edb_sim_setup.settings.general.multi_frequency_adaptive_solution
            adaptive_frequencies = multi_freq_solution.adaptive_frequencies
            adaptive_frequencies = []
            adapt_freq = simulation_setup.AdaptiveFrequency(adaptive_frequency=frequency, max_delta=max_delta_s)
            if output_variable:
                adapt_freq.output_variables = output_variable
            adaptive_frequencies.append(adapt_freq)
            multi_freq_solution.adaptive_frequencies = adaptive_frequencies
            self._edb_sim_setup.settings.options.multi_frequency_adaptive_solution = multi_freq_solution
            return True
        return False

    @pyedb_function_handler()
    def add_broadband_adaptive_frequency_data(
            self, low_frequency=0, high_frequency=10e9, max_num_passes=10, max_delta_s=0.02
    ):
        """Add a setup for frequency data.

        Parameters
        ----------
        low_frequency : str, float
            Frequency with units or float frequency (in Hz).
        high_frequency : str, float
            Frequency with units or float frequency (in Hz).
        max_num_passes : int, optional
            Maximum number of passes. The default is ``10``.
        max_delta_s : float, optional
            Maximum delta S. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` if method is successful, ``False`` otherwise.
        """
        broad_band_adaptive_setup = simulation_setup.BroadbandAdaptiveSolution(low_frequency=low_frequency,
                                                                               high_frequency=high_frequency,
                                                                               max_delta=max_delta_s,
                                                                               max_num_passes=max_num_passes)
        self._edb_sim_setup.settings.general.broadband_adaptive_solution = broad_band_adaptive_setup
        return True


class DefeatureSettings(object):
    """Manages EDB methods for defeature settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def _defeature_settings(self):
        return self._edb_sim_setup.settings.advanced

    @property
    def defeature_absolute_length(self):
        """Absolute length for polygon defeaturing.

        Returns
        -------
        str
        """
        return self._defeature_settings.defeature_absolute_length

    @defeature_absolute_length.setter
    def defeature_absolute_length(self, value):
        self._defeature_settings.defeature_absolute_length = value

    @property
    def defeature_ratio(self):
        """Defeature ratio.

        Returns
        -------
        float
        """
        return self._defeature_settings.defeature_ratio

    @defeature_ratio.setter
    def defeature_ratio(self, value):
        self._defeature_settings.defeature_ratio = value

    @property
    def healing_option(self):
        """Whether to turn on healing of mis-aligned points and edges.
        Options are:
        0- Turn off.
        1- Turn on.

        Returns
        -------
        int
        """
        # return self._defeature_settings.healing_option
        return 0

    @healing_option.setter
    def healing_option(self, value):
        # self._defeature_settings.healing_option = value
        pass

    @property
    def auto_ic_mode_resolution(self):
        """Enable auto IC mode.

        Returns
        -------
        bool
        """
        return self._defeature_settings.ic_mode_auto_resolution

    @auto_ic_mode_resolution.setter
    def auto_ic_mode_resolution(self, value):
        if isinstance(value, bool):
            self._defeature_settings.ic_mode_auto_resolution = value

    @property
    def ic_mode_length(self):
        return self._defeature_settings.ic_mode_length

    @ic_mode_length.setter
    def ic_mode_length(self, value):
        self._defeature_settings.ic_mode_length = str(utility.Value(value).value)

    @property
    def remove_floating_geometry(self):
        """Whether to remove floating geometries.

        Returns
        -------
        bool
            ``True`` if floating geometry removal is used, ``False`` otherwise.
        """
        return self._defeature_settings.remove_floating_geometry

    @remove_floating_geometry.setter
    def remove_floating_geometry(self, value):
        if isinstance(value, bool):
            self._defeature_settings.remove_floating_geometry = value

    @property
    def small_void_area(self):
        """Small voids to remove area.

        Returns
        -------
        float
        """
        return self._defeature_settings.small_void_area

    @small_void_area.setter
    def small_void_area(self, value):
        self._defeature_settings.small_void_area = utility.Value(value).value

    @property
    def union_polygons(self):
        """Whether to turn on the union of polygons before meshing.

        Returns
        -------
        bool
            ``True`` if union polygons is used, ``False`` otherwise.
        """
        return self._defeature_settings.union_polygons

    @union_polygons.setter
    def union_polygons(self, value):
        if isinstance(value, bool):
            self._defeature_settings.union_polygons = value

    @property
    def use_defeature(self):
        """Whether to turn on the defeature.

        Returns
        -------
        bool
            ``True`` if defeature is used, ``False`` otherwise.
        """
        return self._defeature_settings.use_defeature

    @use_defeature.setter
    def use_defeature(self, value):
        if isinstance(value, bool):
            self._defeature_settings.use_defeature = value

    @property
    def use_defeature_absolute_length(self):
        """Whether to turn on the defeature absolute length.

        Returns
        -------
        bool
            ``True`` if defeature absolute length is used, ``False`` otherwise.

        """
        return self._defeature_settings.use_defeature_absolute_length

    @use_defeature_absolute_length.setter
    def use_defeature_absolute_length(self, value):
        if isinstance(value, bool):
            self._defeature_settings.use_defeature_absolute_length = value


class ViaSettings(object):
    """Manages EDB methods for via settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

        self._via_style_mapping = {
            0: "WIREBOND",
            1: "RIBBON",
            2: "MESH",
            3: "FIELD",
            4: "NUM_VIA_STYLE",
        }

    @property
    def _via_settings(self):
        return self._edb_sim_setup.settings.advanced

    @property
    def via_density(self):
        """Via density.

        Returns
        -------
        float
        """
        return self._via_settings.num_via_density

    @via_density.setter
    def via_density(self, value):
        self._via_settings.num_via_density = utility.Value(value).value

    @property
    def via_material(self):
        """Via material.

        Returns
        -------
        str
        """
        return self._via_settings.via_material

    @via_material.setter
    def via_material(self, value):
        self._via_settings.via_material = value

    @property
    def via_num_sides(self):
        """Via number of sides.

        Returns
        -------
        int
        """
        return self._via_settings.num_via_sides

    @via_num_sides.setter
    def via_num_sides(self, value):
        self._via_settings.num_via_sides = value

    @property
    def via_style(self):
        """Via style.
        Options:
        0- ``WIREBOND``.
        1- ``RIBBON``.
        2- ``MESH``.
        3- ``FIELD``.
        4- ``NUM_VIA_STYLE``.

        Returns
        -------
        str
        """
        return self._via_settings.via_model_type.name

    @via_style.setter
    def via_style(self, value):
        via_style = None
        if isinstance(value, int):
            via_style = simulation_setup.ViaStyle(value)
        if isinstance(value, str):
            via_style_mapping = {"WIREBOND": simulation_setup.ViaStyle.WIREBOND,
                                 "RIBBON": simulation_setup.ViaStyle.RIBBON,
                                 "MESH": simulation_setup.ViaStyle.MESH,
                                 "FIELD": simulation_setup.ViaStyle.FIELD,
                                 "NUM_VIA_STYLE": simulation_setup.ViaStyle.NUM_VIA_STYLE}
            try:
                via_style =via_style_mapping[value]
            except:
                pass
        if via_style:
            self._via_settings.via_model_type = via_style


class AdvancedMeshSettings(object):
    """Manages EDB methods for advanced mesh settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def _advanced_mesh_settings(self):
        return self._edb_sim_setup.settings.advanced_meshing

    @property
    def layer_snap_tol(self):
        """Layer snap tolerance. Attempt to align independent stackups in the mesher.

        Returns
        -------
        str

        """
        return self._advanced_mesh_settings.layer_snap_tol

    @layer_snap_tol.setter
    def layer_snap_tol(self, value):
        self._advanced_mesh_settings.layer_snap_tol = value


class CurveApproxSettings(object):
    """Manages EDB methods for curve approximate settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def _curve_approx_settings(self):
        return self._edb_sim_setup.settings.advanced_meshing

    @property
    def arc_angle(self):
        """Step-size to be used for arc faceting.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.arc_step_size

    @arc_angle.setter
    def arc_angle(self, value):
        self._curve_approx_settings.arc_step_size = value

    @property
    def arc_to_chord_error(self):
        """Maximum tolerated error between straight edge (chord) and faceted arc.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):
        self._curve_approx_settings.arc_to_chord_error = value

    @property
    def max_arc_points(self):
        """Maximum number of mesh points for arc segments.

        Returns
        -------
        int
        """
        return self._curve_approx_settings.max_num_arc_points

    @max_arc_points.setter
    def max_arc_points(self, value):
        self._curve_approx_settings.max_num_arc_points = value

    @property
    def start_azimuth(self):
        """Azimuth angle for first mesh point of the arc.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.circle_start_azimuth

    @start_azimuth.setter
    def start_azimuth(self, value):
        self._curve_approx_settings.circle_start_azimuth = value

    @property
    def use_arc_to_chord_error(self):
        """Whether to turn on the arc-to-chord error setting for arc faceting.

        Returns
        -------
            ``True`` if arc-to-chord error is used, ``False`` otherwise.
        """
        return self._curve_approx_settings.use_arc_chord_error_approx

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):
        if isinstance(value, bool):
            self._curve_approx_settings.use_arc_chord_error_approx = value


class DcrSettings(object):
    """Manages EDB methods for DCR settings."""

    def __init__(self, parent):
        self._edb_sim_setup = parent.edb_sim_setup

    @property
    def _dcr_settings(self):
        return self._edb_sim_setup.settings.dcr

    @property
    def max_passes(self):
        """Conduction maximum number of passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.max_passes

    @max_passes.setter
    def max_passes(self, value):
        self._dcr_settings.max_passes = value

    @property
    def min_converged_passes(self):
        """Conduction minimum number of converged passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value):
        self._dcr_settings.min_converged_passes = value

    @property
    def min_passes(self):
        """Conduction minimum number of passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.min_passes

    @min_passes.setter
    def min_passes(self, value):
        self._dcr_settings.min_passes = value

    @property
    def percent_error(self):
        """WConduction error percentage.

        Returns
        -------
        float
        """
        return self._dcr_settings.percent_error

    @percent_error.setter
    def percent_error(self, value):
        self._dcr_settings.percent_error = value

    @property
    def percent_refinement_per_pass(self):
        """Conduction refinement.

        Returns
        -------
        float
        """
        return self._dcr_settings.percent_refinement_per_pass

    @percent_refinement_per_pass.setter
    def percent_refinement_per_pass(self, value):
        self._dcr_settings.percent_refinement_per_pass = value


class HfssSimulationSetup(object):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, edb, name=None, edb_hfss_sim_setup=None):
        self._edb = edb
        self._name = None
        self._mesh_operations = {}

        if edb_hfss_sim_setup:
            self._edb_sim_setup = edb_hfss_sim_setup
            self._name = edb_hfss_sim_setup.name
        else:
            if not name:
                self._name = generate_unique_name("hfss")
            else:
                self._name = name
            self._edb_sim_setup = simulation_setup.HfssSimulationSetup.create(self._edb.active_cell, "test")
            pass

    @property
    def edb_sim_setup(self):
        """EDB internal simulation setup object."""
        return self._edb_sim_setup

    @property
    def frequency_sweeps(self):
        """Frequency sweep list.

        Returns
        -------
        List of :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.EdbFrequencySweep`
        """
        sweep_data_list = {}
        for i in self.edb_sim_setup.sweep_data:
            sweep_data_list[i.name] = EdbFrequencySweep(self, i)
        return sweep_data_list

    @property
    def name(self):
        """Name of the setup."""
        return self.edb_sim_setup.name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.edb_sim_setup.name = value

    @property
    def setup_type(self):
        """Setup type."""
        return self.edb_sim_setup.type

    @property
    def hfss_solver_settings(self):
        """Manages EDB methods for HFSS solver settings.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.HfssSolverSettings`

        """
        return HfssSolverSettings(self)

    @property
    def adaptive_settings(self):
        """Adaptive Settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveSettings`

        """
        return AdaptiveSettings(self)

    @property
    def defeature_settings(self):
        """Defeature settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.DefeatureSettings`

        """
        return DefeatureSettings(self)

    @property
    def via_settings(self):
        """Via settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.ViaSettings`

        """
        return ViaSettings(self)

    @property
    def advanced_mesh_settings(self):
        """Advanced mesh settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.AdvancedMeshSettings`

        """
        return AdvancedMeshSettings(self)

    @property
    def curve_approx_settings(self):
        """Curve approximation settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.CurveApproxSettings`

        """
        return CurveApproxSettings(self)

    @property
    def dcr_settings(self):
        """Dcr settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.DcrSettings`

        """
        return DcrSettings(self)

    @property
    def hfss_port_settings(self):
        """HFSS port settings Class.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.HfssPortSettings`

        """
        return HfssPortSettings(self)

    @property
    def mesh_operations(self):
        """Mesh operations settings Class.

        Returns
        -------
        List of :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.MeshOperation`

        """

        mesh_op_list = {}
        for i in self.edb_sim_setup.mesh_operations:
            mesh_op_list[i.name] = MeshOperation(self, i)
        return mesh_op_list

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.LengthMeshOperation`
        """
        if not name:
            name = generate_unique_name("skin")
        edb_mesh_op = simulation_setup.LengthMeshOperation(name=name,
                                                           net_layer_info=net_layer_list,
                                                           enabled=True,
                                                           refine_inside=refine_inside,
                                                           mesh_region=mesh_region,
                                                           max_length=max_length,
                                                           restrict_max_length=restrict_length,
                                                           max_elements=max_elements,
                                                           restrict_max_elements=restrict_elements)
        mesh_operation = MeshOperationLength(self, edb_mesh_op)
        setup_mesh_op = self.edb_sim_setup.mesh_operations
        setup_mesh_op.append(edb_mesh_op)
        self.edb_sim_setup.mesh_operations = setup_mesh_op
        self.mesh_operations[name] = mesh_operation

    @pyedb_function_handler()
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
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.LengthMeshOperation`
        """
        if not name:
            name = generate_unique_name("length")
        mesh_operation = MeshOperationSkinDepth(self, self._edb.simsetupdata.SkinDepthMeshOperation())
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

    @pyedb_function_handler()
    def add_frequency_sweep(self, name="sweep1",
                            distribution="LIN",
                            start_frequency="0GHz",
                            stop_frequency="10GHz",
                            step_frequency="10MHz"):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep.
        frequency_sweep : list, optional
            List of frequency points.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.EdbFrequencySweep`

        Examples
        --------
        """
        if name in [freq_data.name for freq_data in self.edb_sim_setup.sweep_data]:
            return False
        sweep_data = simulation_setup.SweepData(name=name, distribution=distribution, start_f=start_frequency,
                                                end_f=stop_frequency, step=step_frequency)
        sweep_data_list = self._edb_sim_setup.sweep_data
        sweep_data_list.append(sweep_data)
        self._edb_sim_setup.sweep_data = sweep_data_list
        if [freq_data.name for freq_data in self.edb_sim_setup.sweep_data]:
            return True
        return False




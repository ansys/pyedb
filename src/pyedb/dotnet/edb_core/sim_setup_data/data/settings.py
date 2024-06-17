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

from pyedb.dotnet.edb_core.sim_setup_data.data.adaptive_frequency_data import (
    AdaptiveFrequencyData,
)


class AdaptiveSettings(object):
    """Manages EDB methods for adaptive settings."""

    def __init__(self, parent):
        self._parent = parent
        self._adapt_type_mapping = {
            "kSingle": self.adaptive_settings.AdaptType.kSingle,
            "kMultiFrequencies": self.adaptive_settings.AdaptType.kMultiFrequencies,
            "kBroadband": self.adaptive_settings.AdaptType.kBroadband,
            "kNumAdaptTypes": self.adaptive_settings.AdaptType.kNumAdaptTypes,
        }

    @property
    def adaptive_settings(self):
        """Adaptive EDB settings.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveSettings`
        """
        return self._parent.sim_setup_info.simulation_settings.AdaptiveSettings

    @property
    def adaptive_frequency_data_list(self):
        """List of all adaptive frequency data.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveFrequencyData`
        """
        return [AdaptiveFrequencyData(i) for i in list(self.adaptive_settings.AdaptiveFrequencyDataList)]

    @property
    def adapt_type(self):
        """Adaptive type.
        Options:
        1- ``kSingle``.
        2- ``kMultiFrequencies``.
        3- ``kBroadband``.
        4- ``kNumAdaptTypes``.

        Returns
        -------
        str
        """
        return self.adaptive_settings.AdaptType.ToString()

    @adapt_type.setter
    def adapt_type(self, value):
        self.adaptive_settings.AdaptType = self._adapt_type_mapping[value]
        self._parent._update_setup()

    @property
    def basic(self):
        """Whether if turn on basic adaptive.

        Returns
        -------
            ``True`` if basic adaptive is used, ``False`` otherwise.
        """
        return self.adaptive_settings.Basic

    @basic.setter
    def basic(self, value):
        self.adaptive_settings.Basic = value
        self._parent._update_setup()

    @property
    def do_adaptive(self):
        """Whether if adaptive mesh is on.

        Returns
        -------
        bool
            ``True`` if adaptive is used, ``False`` otherwise.

        """
        return self.adaptive_settings.DoAdaptive

    @property
    def max_refinement(self):
        """Maximum number of mesh elements to be added per pass.

        Returns
        -------
        int
        """
        return self.adaptive_settings.MaxRefinement

    @max_refinement.setter
    def max_refinement(self, value):
        self.adaptive_settings.MaxRefinement = value
        self._parent._update_setup()

    @property
    def max_refine_per_pass(self):
        """Maximum number of mesh elementat that can be added during an adaptive pass.

        Returns
        -------
        int
        """
        return self.adaptive_settings.MaxRefinePerPass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value):
        self.adaptive_settings.MaxRefinePerPass = value
        self._parent._update_setup()

    @property
    def min_passes(self):
        """Minimum number of passes.

        Returns
        -------
        int
        """
        return self.adaptive_settings.MinPasses

    @min_passes.setter
    def min_passes(self, value):
        self.adaptive_settings.MinPasses = value
        self._parent._update_setup()

    @property
    def save_fields(self):
        """Whether to turn on save fields.

        Returns
        -------
        bool
            ``True`` if save fields is used, ``False`` otherwise.
        """
        return self.adaptive_settings.SaveFields

    @save_fields.setter
    def save_fields(self, value):
        self.adaptive_settings.SaveFields = value
        self._parent._update_setup()

    @property
    def save_rad_field_only(self):
        """Flag indicating if the saving of only radiated fields is turned on.

        Returns
        -------
        bool
            ``True`` if save radiated field only is used, ``False`` otherwise.

        """
        return self.adaptive_settings.SaveRadFieldsOnly

    @save_rad_field_only.setter
    def save_rad_field_only(self, value):
        self.adaptive_settings.SaveRadFieldsOnly = value
        self._parent._update_setup()

    @property
    def use_convergence_matrix(self):
        """Whether to turn on the convergence matrix.

        Returns
        -------
        bool
            ``True`` if convergence matrix is used, ``False`` otherwise.

        """
        return self.adaptive_settings.UseConvergenceMatrix

    @use_convergence_matrix.setter
    def use_convergence_matrix(self, value):
        self.adaptive_settings.UseConvergenceMatrix = value
        self._parent._update_setup()

    @property
    def use_max_refinement(self):
        """Whether to turn on maximum refinement.

        Returns
        -------
        bool
            ``True`` if maximum refinement is used, ``False`` otherwise.
        """
        return self.adaptive_settings.UseMaxRefinement

    @use_max_refinement.setter
    def use_max_refinement(self, value):
        self.adaptive_settings.UseMaxRefinement = value
        self._parent._update_setup()

    def add_adaptive_frequency_data(self, frequency=0, max_num_passes=10, max_delta_s=0.02):
        """Add a setup for frequency data.

        Parameters
        ----------
        frequency : str, float
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
        low_freq_adapt_data = self._parent._pedb.simsetupdata.AdaptiveFrequencyData()
        low_freq_adapt_data.MaxDelta = self._parent._pedb.edb_value(max_delta_s).ToString()
        low_freq_adapt_data.MaxPasses = max_num_passes
        low_freq_adapt_data.AdaptiveFrequency = self._parent._pedb.edb_value(frequency).ToString()
        self.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        self.adaptive_settings.AdaptiveFrequencyDataList.Add(low_freq_adapt_data)
        return self._parent._update_setup()

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
        low_freq_adapt_data = self._parent._pedb.simsetupdata.AdaptiveFrequencyData()
        low_freq_adapt_data.MaxDelta = self._parent._pedb.edb_value(max_delta_s).ToString()
        low_freq_adapt_data.MaxPasses = max_num_passes
        low_freq_adapt_data.AdaptiveFrequency = self._parent._pedb.edb_value(low_frequency).ToString()
        high_freq_adapt_data = self._parent._pedb.simsetupdata.AdaptiveFrequencyData()
        high_freq_adapt_data.MaxDelta = self._parent._pedb.edb_value(max_delta_s).ToString()
        high_freq_adapt_data.MaxPasses = max_num_passes
        high_freq_adapt_data.AdaptiveFrequency = self._parent._pedb.edb_value(high_frequency).ToString()
        self.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        self.adaptive_settings.AdaptiveFrequencyDataList.Add(low_freq_adapt_data)
        self.adaptive_settings.AdaptiveFrequencyDataList.Add(high_freq_adapt_data)
        return self._parent._update_setup()


class DefeatureSettings(object):
    """Manages EDB methods for defeature settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _defeature_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.DefeatureSettings

    @property
    def defeature_abs_length(self):
        """Absolute length for polygon defeaturing.

        Returns
        -------
        str
        """
        return self._defeature_settings.DefeatureAbsLength

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):
        self._defeature_settings.DefeatureAbsLength = value
        self._parent._update_setup()

    @property
    def defeature_ratio(self):
        """Defeature ratio.

        Returns
        -------
        float
        """
        return self._defeature_settings.DefeatureRatio

    @defeature_ratio.setter
    def defeature_ratio(self, value):
        self._defeature_settings.DefeatureRatio = value
        self._parent._update_setup()

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
        return self._defeature_settings.HealingOption

    @healing_option.setter
    def healing_option(self, value):
        self._defeature_settings.HealingOption = value
        self._parent._update_setup()

    @property
    def model_type(self):
        """Model type.
        Options:
        0- General.
        1- IC.

        Returns
        -------
        int
        """
        return self._defeature_settings.ModelType

    @model_type.setter
    def model_type(self, value):
        """Model type (General 0 or IC 1)."""
        self._defeature_settings.ModelType = value
        self._parent._update_setup()

    @property
    def remove_floating_geometry(self):
        """Whether to remove floating geometries.

        Returns
        -------
        bool
            ``True`` if floating geometry removal is used, ``False`` otherwise.
        """
        return self._defeature_settings.RemoveFloatingGeometry

    @remove_floating_geometry.setter
    def remove_floating_geometry(self, value):
        self._defeature_settings.RemoveFloatingGeometry = value
        self._parent._update_setup()

    @property
    def small_void_area(self):
        """Small voids to remove area.

        Returns
        -------
        float
        """
        return self._defeature_settings.SmallVoidArea

    @small_void_area.setter
    def small_void_area(self, value):
        self._defeature_settings.SmallVoidArea = value
        self._parent._update_setup()

    @property
    def union_polygons(self):
        """Whether to turn on the union of polygons before meshing.

        Returns
        -------
        bool
            ``True`` if union polygons is used, ``False`` otherwise.
        """
        return self._defeature_settings.UnionPolygons

    @union_polygons.setter
    def union_polygons(self, value):
        self._defeature_settings.UnionPolygons = value
        self._parent._update_setup()

    @property
    def use_defeature(self):
        """Whether to turn on the defeature.

        Returns
        -------
        bool
            ``True`` if defeature is used, ``False`` otherwise.
        """
        return self._defeature_settings.UseDefeature

    @use_defeature.setter
    def use_defeature(self, value):
        self._defeature_settings.UseDefeature = value
        self._parent._update_setup()

    @property
    def use_defeature_abs_length(self):
        """Whether to turn on the defeature absolute length.

        Returns
        -------
        bool
            ``True`` if defeature absolute length is used, ``False`` otherwise.

        """
        return self._defeature_settings.UseDefeatureAbsLength

    @use_defeature_abs_length.setter
    def use_defeature_abs_length(self, value):
        self._defeature_settings.UseDefeatureAbsLength = value
        self._parent._update_setup()


class AdvancedMeshSettings(object):
    """Manages EDB methods for advanced mesh settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _advanced_mesh_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.AdvancedMeshSettings

    @property
    def layer_snap_tol(self):
        """Layer snap tolerance. Attempt to align independent stackups in the mesher.

        Returns
        -------
        str

        """
        return self._advanced_mesh_settings.LayerSnapTol

    @layer_snap_tol.setter
    def layer_snap_tol(self, value):
        self._advanced_mesh_settings.LayerSnapTol = value
        self._parent._update_setup()

    @property
    def mesh_display_attributes(self):
        """Mesh display attributes. Set color for mesh display (i.e. ``"#000000"``).

        Returns
        -------
        str
        """
        return self._advanced_mesh_settings.MeshDisplayAttributes

    @mesh_display_attributes.setter
    def mesh_display_attributes(self, value):
        self._advanced_mesh_settings.MeshDisplayAttributes = value
        self._parent._update_setup()

    @property
    def replace_3d_triangles(self):
        """Whether to turn on replace 3D triangles.

        Returns
        -------
        bool
            ``True`` if replace 3D triangles is used, ``False`` otherwise.

        """
        return self._advanced_mesh_settings.Replace3DTriangles

    @replace_3d_triangles.setter
    def replace_3d_triangles(self, value):
        self._advanced_mesh_settings.Replace3DTriangles = value
        self._parent._update_setup()


class ViaSettings(object):
    """Manages EDB methods for via settings."""

    def __init__(
        self,
        parent,
    ):
        self._parent = parent
        self._via_style_mapping = {
            "k25DViaWirebond": self._via_settings.T25DViaStyle.k25DViaWirebond,
            "k25DViaRibbon": self._via_settings.T25DViaStyle.k25DViaRibbon,
            "k25DViaMesh": self._via_settings.T25DViaStyle.k25DViaMesh,
            "k25DViaField": self._via_settings.T25DViaStyle.k25DViaField,
            "kNum25DViaStyle": self._via_settings.T25DViaStyle.kNum25DViaStyle,
        }

    @property
    def _via_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.ViaSettings

    @property
    def via_density(self):
        """Via density.

        Returns
        -------
        float
        """
        return self._via_settings.ViaDensity

    @via_density.setter
    def via_density(self, value):
        self._via_settings.ViaDensity = value
        self._parent._update_setup()

    @property
    def via_mesh_plating(self):
        """Via mesh plating.

        Returns
        -------
        bool
        """
        if float(self._parent._pedb.edbversion) < 2024.1:
            self._parent._pedb.logger.error("Property only supported on Ansys release 2024R1 and later")
            return False
        return self._via_settings.ViaMeshPlating

    @via_mesh_plating.setter
    def via_mesh_plating(self, value):
        if float(self._parent._pedb.edbversion) < 2024.1:
            self._parent._pedb.logger.error("Property only supported on Ansys release 2024R1 and later")
        else:
            self._via_settings.ViaMeshPlating = value
            self._parent._update_setup()

    @property
    def via_material(self):
        """Via material.

        Returns
        -------
        str
        """
        return self._via_settings.ViaMaterial

    @via_material.setter
    def via_material(self, value):
        self._via_settings.ViaMaterial = value
        self._parent._update_setup()

    @property
    def via_num_sides(self):
        """Via number of sides.

        Returns
        -------
        int
        """
        return self._via_settings.ViaNumSides

    @via_num_sides.setter
    def via_num_sides(self, value):
        self._via_settings.ViaNumSides = value
        self._parent._update_setup()

    @property
    def via_style(self):
        """Via style.
        Options:
        1- ``k25DViaWirebond``.
        2- ``k25DViaRibbon``.
        3- ``k25DViaMesh``.
        4- ``k25DViaField``.
        5- ``kNum25DViaStyle``.

        Returns
        -------
        str
        """
        return self._via_settings.ViaStyle.ToString()

    @via_style.setter
    def via_style(self, value):
        self._via_settings.ViaStyle = self._via_style_mapping[value]
        self._parent._update_setup()


class CurveApproxSettings(object):
    """Manages EDB methods for curve approximate settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _curve_approx_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.CurveApproxSettings

    @property
    def arc_angle(self):
        """Step-size to be used for arc faceting.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.ArcAngle

    @arc_angle.setter
    def arc_angle(self, value):
        self._curve_approx_settings.ArcAngle = value
        self._parent._update_setup()

    @property
    def arc_to_chord_error(self):
        """Maximum tolerated error between straight edge (chord) and faceted arc.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.ArcToChordError

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):
        self._curve_approx_settings.ArcToChordError = value
        self._parent._update_setup()

    @property
    def max_arc_points(self):
        """Maximum number of mesh points for arc segments.

        Returns
        -------
        int
        """
        return self._curve_approx_settings.MaxArcPoints

    @max_arc_points.setter
    def max_arc_points(self, value):
        self._curve_approx_settings.MaxArcPoints = value
        self._parent._update_setup()

    @property
    def start_azimuth(self):
        """Azimuth angle for first mesh point of the arc.

        Returns
        -------
        str
        """
        return self._curve_approx_settings.StartAzimuth

    @start_azimuth.setter
    def start_azimuth(self, value):
        self._curve_approx_settings.StartAzimuth = value
        self._parent._update_setup()

    @property
    def use_arc_to_chord_error(self):
        """Whether to turn on the arc-to-chord error setting for arc faceting.

        Returns
        -------
            ``True`` if arc-to-chord error is used, ``False`` otherwise.
        """
        return self._curve_approx_settings.UseArcToChordError

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):
        self._curve_approx_settings.UseArcToChordError = value
        self._parent._update_setup()


class DcrSettings(object):
    """Manages EDB methods for DCR settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _dcr_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.DCRSettings

    @property
    def conduction_max_passes(self):
        """Conduction maximum number of passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMaxPasses

    @conduction_max_passes.setter
    def conduction_max_passes(self, value):
        self._dcr_settings.ConductionMaxPasses = value
        self._parent._update_setup()

    @property
    def conduction_min_converged_passes(self):
        """Conduction minimum number of converged passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMinConvergedPasses

    @conduction_min_converged_passes.setter
    def conduction_min_converged_passes(self, value):
        self._dcr_settings.ConductionMinConvergedPasses = value
        self._parent._update_setup()

    @property
    def conduction_min_passes(self):
        """Conduction minimum number of passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMinPasses

    @conduction_min_passes.setter
    def conduction_min_passes(self, value):
        self._dcr_settings.ConductionMinPasses = value
        self._parent._update_setup()

    @property
    def conduction_per_error(self):
        """WConduction error percentage.

        Returns
        -------
        float
        """
        return self._dcr_settings.ConductionPerError

    @conduction_per_error.setter
    def conduction_per_error(self, value):
        self._dcr_settings.ConductionPerError = value
        self._parent._update_setup()

    @property
    def conduction_per_refine(self):
        """Conduction refinement.

        Returns
        -------
        float
        """
        return self._dcr_settings.ConductionPerRefine

    @conduction_per_refine.setter
    def conduction_per_refine(self, value):
        self._dcr_settings.ConductionPerRefine = value
        self._parent._update_setup()


class HfssPortSettings(object):
    """Manages EDB methods for HFSS port settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _hfss_port_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.HFSSPortSettings

    @property
    def max_delta_z0(self):
        """Maximum change to Z0 in successive passes.

        Returns
        -------
        float
        """
        return self._hfss_port_settings.MaxDeltaZ0

    @max_delta_z0.setter
    def max_delta_z0(self, value):
        self._hfss_port_settings.MaxDeltaZ0 = value
        self._parent._update_setup()

    @property
    def max_triangles_wave_port(self):
        """Maximum number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.MaxTrianglesWavePort

    @max_triangles_wave_port.setter
    def max_triangles_wave_port(self, value):
        self._hfss_port_settings.MaxTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def min_triangles_wave_port(self):
        """Minimum number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.MinTrianglesWavePort

    @min_triangles_wave_port.setter
    def min_triangles_wave_port(self, value):
        self._hfss_port_settings.MinTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def enable_set_triangles_wave_port(self):
        """Whether to enable setting of minimum and maximum mesh limits for wave ports.

        Returns
        -------
        bool
            ``True`` if triangles wave port  is used, ``False`` otherwise.
        """
        return self._hfss_port_settings.SetTrianglesWavePort

    @enable_set_triangles_wave_port.setter
    def enable_set_triangles_wave_port(self, value):
        self._hfss_port_settings.SetTrianglesWavePort = value
        self._parent._update_setup()


class HfssSolverSettings(object):
    """Manages EDB methods for HFSS solver settings."""

    def __init__(self, sim_setup):
        self._parent = sim_setup

    @property
    def _hfss_solver_settings(self):
        return self._parent.get_sim_setup_info.SimulationSettings.HFSSSolverSettings

    @property
    def enhanced_low_freq_accuracy(self):
        """Whether to enable legacy low-frequency sampling.

        Returns
        -------
        bool
            ``True`` if low frequency accuracy is used, ``False`` otherwise.
        """
        return self._hfss_solver_settings.EnhancedLowFreqAccuracy

    @enhanced_low_freq_accuracy.setter
    def enhanced_low_freq_accuracy(self, value):
        self._hfss_solver_settings.EnhancedLowFreqAccuracy = value
        self._parent._update_setup()

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
        return mapping[self._hfss_solver_settings.OrderBasis]

    @order_basis.setter
    def order_basis(self, value):
        mapping = {"zero": 0, "first": 1, "second": 2, "mixed": 3}
        self._hfss_solver_settings.OrderBasis = mapping[value]
        self._parent._update_setup()

    @property
    def relative_residual(self):
        """Residual for use by the iterative solver.

        Returns
        -------
        float
        """
        return self._hfss_solver_settings.RelativeResidual

    @relative_residual.setter
    def relative_residual(self, value):
        self._hfss_solver_settings.RelativeResidual = value
        self._parent._update_setup()

    @property
    def solver_type(self):
        """Get solver type to use (Direct/Iterative/Auto) for HFSS.
        Options:
        1- ``kAutoSolver``.
        2- ``kDirectSolver``.
        3- ``kIterativeSolver``.
        4- ``kNumSolverTypes``.

        Returns
        -------
        str
        """
        mapping = {"kAutoSolver": "auto", "kDirectSolver": "direct", "kIterativeSolver": "iterative"}
        solver_type = self._hfss_solver_settings.SolverType.ToString()
        return mapping[solver_type]

    @solver_type.setter
    def solver_type(self, value):
        mapping = {
            "auto": self._hfss_solver_settings.SolverType.kAutoSolver,
            "direct": self._hfss_solver_settings.SolverType.kDirectSolver,
            "iterative": self._hfss_solver_settings.SolverType.kIterativeSolver,
        }
        self._hfss_solver_settings.SolverType = mapping[value]
        self._parent._update_setup()

    @property
    def use_shell_elements(self):
        """Whether to enable use of shell elements.

        Returns
        -------
        bool
            ``True`` if shall elements are used, ``False`` otherwise.
        """
        return self._hfss_solver_settings.UseShellElements

    @use_shell_elements.setter
    def use_shell_elements(self, value):
        self._hfss_solver_settings.UseShellElements = value
        self._parent._update_setup()

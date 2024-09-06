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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.dotnet.edb_core.sim_setup_data.data.sweep_data import SweepData
from pyedb.dotnet.edb_core.utilities.simulation_setup import SimulationSetup
from pyedb.generic.general_methods import generate_unique_name


class RaptorXSimulationSetup(SimulationSetup):
    """Manages EDB methods for RaptorX simulation setup."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._pedb = pedb
        self._setup_type = "kRaptorX"
        self._edb_setup_info = None
        self.logger = self._pedb.logger

    def create(self, name=None):
        """Create an HFSS setup."""
        self._name = name
        self._create(name, simulation_setup_type=self._setup_type)
        return self

    @property
    def setup_type(self):
        return self._setup_type

    @property
    def settings(self):
        return RaptorXSimulationSettings(self._edb_setup_info, self._pedb)

    @property
    def enabled(self):
        return self.settings.enabled

    @enabled.setter
    def enabled(self, value):
        self.settings.enabled = value

    @property
    def position(self):
        return self._edb_setup_info.Position

    @position.setter
    def position(self, value):
        if isinstance(value, int):
            self._edb_setup_info.Position = value
        else:
            self.logger.error(f"RaptorX setup position input setter must be an integer. Provided value {value}")

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


class RaptorXSimulationSettings(object):
    def __init__(self, edb_setup_info, pedb):
        self._pedb = pedb
        self.logger = self._pedb.logger
        self._edb_setup_info = edb_setup_info
        self._simulation_settings = edb_setup_info.SimulationSettings
        self._general_settings = RaptorXGeneralSettings(self._edb_setup_info, self._pedb)
        self._advanced_settings = RaptorXSimulationAdvancedSettings(self._edb_setup_info, self._pedb)
        self._simulation_settings = self._edb_setup_info.SimulationSettings

    @property
    def general_settings(self):
        return self._general_settings

    @property
    def advanced_settings(self):
        return self._advanced_settings

    @property
    def enabled(self):
        return self._simulation_settings.Enabled

    @enabled.setter
    def enabled(self, value):
        if isinstance(value, bool):
            self._simulation_settings.Enabled = value
        else:
            self.logger.error(f"RaptorX setup enabled setter input must be a boolean. Provided value {value}")


class RaptorXGeneralSettings(object):
    def __init__(self, edb_setup_info, pedb):
        self._general_settings = edb_setup_info.SimulationSettings.GeneralSettings
        self._pedb = pedb
        self.logger = self._pedb.logger

    @property
    def global_temperature(self):
        """The simulation temperature. Units: C"""
        return self._general_settings.GlobalTemperature

    @global_temperature.setter
    def global_temperature(self, value):
        self._general_settings.GlobalTemperature = self._pedb.edb_value(value).ToDouble()

    @property
    def max_frequency(self):
        return self._general_settings.MaxFrequency

    @max_frequency.setter
    def max_frequency(self, value):
        """This allows user to specify the maximum simulation frequency, a parameter which controls how tight the model
        mesh will be. User can override the default meshing frequency as defined by Max Frequency using the Advanced
        settings > MeshFrequency. Example: "10GHz".
        """
        self._general_settings.MaxFrequency = self._pedb.edb_value(value).ToString()


class RaptorXSimulationAdvancedSettings(object):
    def __init__(self, edb_setup_info, pedb):
        self._edb_setup_info = edb_setup_info
        self._advanced_settings = edb_setup_info.SimulationSettings.AdvancedSettings
        self._pedb = pedb
        self.logger = self._pedb.logger

    @property
    def auto_removal_sliver_poly(self):
        return self._advanced_settings.AutoRemovalSliverPoly

    @auto_removal_sliver_poly.setter
    def auto_removal_sliver_poly(self, value):
        self._advanced_settings.AutoRemovalSliverPoly = self._pedb.edb_value(value).ToDouble()

    @property
    def cell_per_wave_length(self):
        """This setting describes the number of cells that fit under each wavelength. The wavelength is
        calculated according to the Max Frequency or the Mesh Frequency, unless specified by user through
        this setting. E.g. Setting Cells/Wavelength to 20 means that an object will be divided into 10 cells
        if its width or length is 1/2 wavelengths.
        Units: unitless.
        """
        return self._advanced_settings.CellsPerWavelength

    @cell_per_wave_length.setter
    def cell_per_wave_length(self, value):
        if isinstance(value, int):
            self._advanced_settings.CellsPerWavelength = value
        else:
            self.logger.error(f"RaptorX cell_per_wave_length setter input must be an integer, value provided {value}")

    @property
    def edge_mesh(self):
        """This option controls both, the thickness and the width of the exterior conductor filament.
        When specified, it prevails over the Mesh Frequency or Max Frequency during mesh calculation.
        Example: "0.8um".
        """
        return self._advanced_settings.EdgeMesh

    @edge_mesh.setter
    def edge_mesh(self, value):
        self._advanced_settings.EdgeMesh = self._pedb.edb_value(value).ToString()

    @property
    def eliminate_slit_per_hole(self):
        """This is a setting that internally simplifies layouts with strain relief or thermal relief slits and
        holes. It will examine each hole separately against the whole polygon it belongs to.
        If the area of the hole is below the threshold defined in this setting, then the hole will be filled.
        Units: unitless.
        """
        return self._advanced_settings.EliminateSlitPerHoles

    @eliminate_slit_per_hole.setter
    def eliminate_slit_per_hole(self, value):
        self._advanced_settings.EliminateSlitPerHoles = self._pedb.edb_value(value).ToDouble()

    @property
    def mesh_frequency(self):
        """User can override the default meshing applied by setting a custom frequency for mesh generation.
        Example: "1GHz".
        """
        return self._advanced_settings.MeshFrequency

    @mesh_frequency.setter
    def mesh_frequency(self, value):
        self._advanced_settings.MeshFrequency = self._pedb.edb_value(value).ToString()

    @property
    def net_settings_options(self):
        """A list of Name, Value pairs that stores advanced option."""
        return [val for val in list(self._advanced_settings.NetSettingsOptions)]

    @net_settings_options.setter
    def net_settings_options(self, value):
        if isinstance(value, list):
            self._advanced_settings.NetSettingsOptions = convert_py_list_to_net_list(value)
        else:
            self.logger.error(
                f"RaptorX setup net_settings_options input setter must be a list. " f"Provided value {value}"
            )

    @property
    def override_shrink_fac(self):
        """Set the shrink factor explicitly, that is, review what-if scenarios of migrating to half-node
        technologies.
        Units: unitless.
        """
        return self._advanced_settings.OverrideShrinkFac

    @override_shrink_fac.setter
    def override_shrink_fac(self, value):
        self._advanced_settings.OverrideShrinkFac = self._pedb.edb_value(value).ToDouble()

    @property
    def plane_projection_factor(self):
        """To eliminate unnecessary mesh complexity of "large" metal planes and improve overall extraction time,
        user can define the mesh of certain planes using a combination of the Plane Projection Factor and
        settings of the Nets Advanced Options.
        Units: unitless.
        """
        return self._advanced_settings.PlaneProjectionFactor

    @plane_projection_factor.setter
    def plane_projection_factor(self, value):
        self._advanced_settings.PlaneProjectionFactor = self._pedb.edb_value(value).ToDouble()

    @property
    def use_accelerate_via_extraction(self):
        """Setting this option will simplify/merge neighboring vias before sending the layout for processing
        to the mesh engine and to the EM engine.
        """
        return self._advanced_settings.UseAccelerateViaExtraction

    @use_accelerate_via_extraction.setter
    def use_accelerate_via_extraction(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseAccelerateViaExtraction = value
        else:
            self.logger.error(
                "RaptorX setup use_accelerate_via_extraction setter input must be boolean." f"Provided value {value}"
            )

    @property
    def use_auto_removal_sliver_poly(self):
        """Setting this option simplifies layouts by aligning slightly misaligned overlapping polygons."""
        return self._advanced_settings.UseAutoRemovalSliverPoly

    @use_auto_removal_sliver_poly.setter
    def use_auto_removal_sliver_poly(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseAutoRemovalSliverPoly = value
        else:
            self.logger.error(
                f"RaptorX setup use_auto_removal_sliver_poly setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_cells_per_wavelength(self):
        """This setting describes the number of cells that fit under each wavelength. The wavelength is calculated
        according to the Max Frequency or the Mesh Frequency, unless specified by user through this setting.
        """
        return self._advanced_settings.UseCellsPerWavelength

    @use_cells_per_wavelength.setter
    def use_cells_per_wavelength(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseCellsPerWavelength = value
        else:
            self.logger.error(f"RaptorX setup use_cells_per_wavelength setter must be boolean. Provided value {value}")

    @property
    def use_edge_mesh(self):
        """This option controls both, the thickness and the width of the exterior conductor filament.
        When checked, it prevails over the Mesh Frequency or Max Frequency during mesh calculation.
        """
        return self._advanced_settings.UseEdgeMesh

    @use_edge_mesh.setter
    def use_edge_mesh(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEdgeMesh = value
        else:
            self.logger.error(f"RaptorX setup use_edge_mesh setter must be a boolean. Provided value {value}")

    @property
    def use_eliminate_slit_per_holes(self):
        """This is a setting that internally simplifies layouts with strain relief or thermal relief slits and
        holes.
        """
        return self._advanced_settings.UseEliminateSlitPerHoles

    @use_eliminate_slit_per_holes.setter
    def use_eliminate_slit_per_holes(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEliminateSlitPerHoles = value
        else:
            self.logger.error(
                f"RaptorX setup use_eliminate_slit_per_holes setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_enable_advanced_cap_effects(self):
        """Applies all the capacitance related effects such as Conformal Dielectrics, Loading Effect,
        Dielectric Damage.
        """
        return self._advanced_settings.UseEnableAdvancedCapEffects

    @use_enable_advanced_cap_effects.setter
    def use_enable_advanced_cap_effects(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEnableAdvancedCapEffects = value
        else:
            self.logger.error(
                f"RaptorX setup use_enable_advanced_cap_effects setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_enable_etch_transform(self):
        """Pre-distorts the layout based on the foundry rules, applying the conductor's bias (positive/negative –
        deflation/inflation) at the conductor edges due to unavoidable optical effects in the manufacturing process.
        """
        return self._advanced_settings.UseEnableEtchTransform

    @use_enable_etch_transform.setter
    def use_enable_etch_transform(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEnableEtchTransform = value
        else:
            self.logger.error(
                f"RaptorX setup use_enable_etch_transform setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_enable_hybrid_extraction(self):
        """This setting allows the modelling engine to separate the layout into two parts in an attempt to
        decrease the complexity of EM modelling.
        """
        return self._edb_setup_info.UseEnableHybridExtraction

    @use_enable_hybrid_extraction.setter
    def use_enable_hybrid_extraction(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEnableHybridExtraction = value
        else:
            self.logger.error(
                f"RaptorX setup use_enable_hybrid_extraction setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_enable_substrate_network_extraction(self):
        """This setting models substrate coupling effects using an equivalent distributed RC network."""
        return self._advanced_settings.UseEnableSubstrateNetworkExtraction

    @use_enable_substrate_network_extraction.setter
    def use_enable_substrate_network_extraction(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseEnableSubstrateNetworkExtraction = value
        else:
            self.logger.error(
                f"RaptorX setup use_enable_substrate_network_extraction setter must be a boolean. "
                f"Provided value {value}"
            )

    @property
    def use_extract_floating_metals_dummy(self):
        """Enables modeling of floating metals as dummy fills. Captures the effect of dummy fill by extracting
        the effective capacitance between any pairs of metal segments in the design, in the presence of each
        individual dummy metal islands. This setting cannot be used with UseExtractFloatingMetalsFloating.
        """
        return self._advanced_settings.UseExtractFloatingMetalsDummy

    @use_extract_floating_metals_dummy.setter
    def use_extract_floating_metals_dummy(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseExtractFloatingMetalsDummy = value
        else:
            self.logger.error(
                f"RaptorX setup use_extract_floating_metals_dummy setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_extract_floating_metals_floating(self):
        """Enables modeling of floating metals as floating nets. Floating metal are grouped into a single entity
        and treated as an independent net. This setting cannot be used with UseExtractFloatingMetalsDummy.
        """
        return self._advanced_settings.UseExtractFloatingMetalsFloating

    @use_extract_floating_metals_floating.setter
    def use_extract_floating_metals_floating(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseExtractFloatingMetalsFloating = value
        else:
            self.logger.error(
                f"RaptorX setup use_extract_floating_metals_floating setter must be a boolean. "
                f"Provided value {value}"
            )

    @property
    def use_lde(self):
        """
        Takes into account the variation of resistivity as a function of a conductor’s drawn width and spacing to
        its neighbors or as a function of its local density, due to dishing, slotting, cladding thickness, and so
        on.
        """
        return self._advanced_settings.UseLDE

    @use_lde.setter
    def use_lde(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseLDE = value
        else:
            self.logger.error(f"RaptorX setup use_lde setter must be a boolean. Provided value {value}")

    @property
    def use_mesh_frequency(self):
        """
        User can override the default meshing applied by the mesh engine by checking this option and setting a
        custom frequency for mesh generation.
        """
        return self._advanced_settings.UseMeshFrequency

    @use_mesh_frequency.setter
    def use_mesh_frequency(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseMeshFrequency = value
        else:
            self.logger.error(f"RaptorX setup use_mesh_frequency setter must be a boolean. Provided value {value}")

    @property
    def use_override_shrink_fac(self):
        """Set the shrink factor explicitly, that is, review what-if scenarios of migrating to half-node
        technologies.
        """
        return self._advanced_settings.UseOverrideShrinkFac

    @use_override_shrink_fac.setter
    def use_override_shrink_fac(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseOverrideShrinkFac = value
        else:
            self.logger.error(f"RaptorX setup use_override_shrink_fac setter must be a boolean. Provided value {value}")

    @property
    def use_plane_projection_factor(self):
        """To eliminate unnecessary mesh complexity of "large" metal planes and improve overall
        extraction time, user can define the mesh of certain planes using a combination of the Plane Projection
        Factor and settings of the Nets Advanced Options.
        """
        return self._advanced_settings.UsePlaneProjectionFactor

    @use_plane_projection_factor.setter
    def use_plane_projection_factor(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UsePlaneProjectionFactor = value
        else:
            self.logger.error(
                f"RaptorX setup use_plane_projection_factor setter must be a boolean. " f"Provided value {value}"
            )

    @property
    def use_relaxed_z_axis(self):
        """Enabling this option provides a simplified mesh along the z-axis."""
        return self._advanced_settings.UseRelaxedZAxis

    @use_relaxed_z_axis.setter
    def use_relaxed_z_axis(self, value):
        if isinstance(value, bool):
            self._advanced_settings.UseRelaxedZAxis = value
        else:
            self.logger.error(f"RaptorX setup use_relaxed_z_axis setter must be a boolean. " f"Provided value {value}")

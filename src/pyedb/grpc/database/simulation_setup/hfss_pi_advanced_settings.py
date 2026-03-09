# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

# Try to import the ANSYS 2026.1 gRPC package
try:
    from ansys.edb.core.simulation_setup.hfss_pi_simulation_settings import (
        HFSSPIAdvancedSettings as CoreHFSSPIAdvancedSettings,
    )
except ImportError as e:
    print(
        f"HFSSPiAdvancedSettings is available on with ANSYS release 2026.1 and latest pyedb-core: {e}."
        f"Please upgrade to access this class."
    )


class HFSSPIAdvancedSettings:
    """HFSS PI simulation advanced settings class."""

    def __init__(self, pedb, core: "CoreHFSSPIAdvancedSettings"):
        self._pedb = pedb
        self._core = core

    @property
    def arc_to_chord_error(self) -> str:
        """Arc to chord error value.

        Returns
        -------
        str
            Arc to chord error value.
        """
        return self._core.arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value: str):
        """Set arc to chord error value.

        Parameters
        ----------
        value : str
            Arc to chord error value.
        """
        self._core.arc_to_chord_error = value

    @property
    def auto_model_resolution(self) -> bool:
        """Flag indicating if model resolution is automatically calculated.

        Returns
        -------
        bool
            Auto model resolution value.
        """
        return self._core.auto_model_resolution

    @auto_model_resolution.setter
    def auto_model_resolution(self, value: bool):
        """Set auto model resolution value.

        Parameters
        ----------
        value : bool
            Auto model resolution value.
        """
        self._core.auto_model_resolution = value

    @property
    def max_num_arc_points(self) -> str:
        """Maximum number of points used to approximate arcs.

        Returns
        -------
        str
            Maximum number of arc points.
        """
        return self._core.max_num_arc_points

    @max_num_arc_points.setter
    def max_num_arc_points(self, value: str):
        """Set maximum number of arc points.

        Parameters
        ----------
        value : str
            Maximum number of arc points.
        """
        self._core.max_num_arc_points = value

    @property
    def mesh_for_via_plating(self) -> bool:
        """Flag indicating if meshing for via plating is enabled.

        Returns
        -------
        bool
            Mesh for via plating value.
        """
        return self._core.mesh_for_via_plating

    @mesh_for_via_plating.setter
    def mesh_for_via_plating(self, value: bool):
        """Set mesh for via plating value.

        Parameters
        ----------
        value : bool
            Mesh for via plating value.
        """
        self._core.mesh_for_via_plating = value

    @property
    def model_resolution_length(self) -> str:
        """Model resolution to use when manually setting the model resolution.

        Returns
        -------
        str
            Model resolution length value.
        """
        return self._core.model_resolution_length

    @model_resolution_length.setter
    def model_resolution_length(self, value: str):
        """Set model resolution length value.

        Parameters
        ----------
        value : str
            Model resolution length value.
        """
        self._core.model_resolution_length = value

    @property
    def num_via_sides(self) -> int:
        """Number of sides a via is considered to have.

        Returns
        -------
        int
            Number of via sides.
        """
        return self._core.num_via_sides

    @num_via_sides.setter
    def num_via_sides(self, value: int):
        """Set number of via sides.

        Parameters
        ----------
        value : int
            Number of via sides.
        """
        self._core.num_via_sides = value

    @property
    def remove_floating_geometry(self) -> bool:
        """Flag indicating if a geometry not connected to any other geometry is removed.

        Returns
        -------
        bool
            Remove floating geometry value.
        """
        return self._core.remove_floating_geometry

    @remove_floating_geometry.setter
    def remove_floating_geometry(self, value: bool):
        """Set remove floating geometry value.

        Parameters
        ----------
        value : bool
            Remove floating geometry value.
        """
        self._core.remove_floating_geometry = value

    @property
    def small_plane_area(self) -> str:
        """Planes with an area smaller than this value are ignored during simulation.

        Returns
        -------
        str
            Small plane area value.
        """
        return self._core.small_plane_area

    @small_plane_area.setter
    def small_plane_area(self, value: str):
        """Set small plane area value.

        Parameters
        ----------
        value : str
            Small plane area value.
        """
        self._core.small_plane_area = value

    @property
    def small_void_area(self) -> float:
        """Voids with an area smaller than this value are ignored during simulation.

        Returns
        -------
        float
            Small void area value.
        """
        return self._core.small_void_area

    @small_void_area.setter
    def small_void_area(self, value: float):
        """Set small void area value.

        Parameters
        ----------
        value : float
            Small void area value.
        """
        self._core.small_void_area = value

    @property
    def use_arc_chord_error_approx(self) -> bool:
        """Flag indicating if arc chord error approximation is used.

        Returns
        -------
        bool
            Use arc to chord error approximation value.
        """
        return self._core.use_arc_chord_error_approx

    @use_arc_chord_error_approx.setter
    def use_arc_chord_error_approx(self, value: bool):
        """Set use arc to chord error approximation value.

        Parameters
        ----------
        value : bool
            Use arc to chord error approximation value.
        """
        self._core.use_arc_chord_error_approx = value

    @property
    def via_material(self) -> str:
        """Default via material.

        Returns
        -------
        str
            Via material name.
        """
        return self._core.via_material

    @via_material.setter
    def via_material(self, value: str):
        """Set via material.

        Parameters
        ----------
        value : str
            Via material name.
        """
        self._core.via_material = value

    @property
    def zero_metal_layer_thickness(self) -> str:
        """Pwr/Gnd layers with a thickness smaller than this value are simplified during simulation.

        Returns
        -------
        str
            Zero metal layer thickness value.
        """
        return self._core.zero_metal_layer_thickness

    @zero_metal_layer_thickness.setter
    def zero_metal_layer_thickness(self, value: str):
        """Set zero metal layer thickness value.

        Parameters
        ----------
        value : str
            Zero metal layer thickness value.
        """
        self._core.zero_metal_layer_thickness = value

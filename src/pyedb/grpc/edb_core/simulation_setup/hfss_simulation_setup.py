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


from ansys.edb.core.simulation_setup.adaptive_solutions import (
    AdaptiveFrequency as GrpcAdaptiveFrequency,
)
from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    AdaptType as GrpcAdaptType,
)
from ansys.edb.core.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup as GrpcHfssSimulationSetup,
)

from pyedb.generic.general_methods import generate_unique_name


class HfssSimulationSetup(GrpcHfssSimulationSetup):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, pedb, edb_object, name: str = None):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._name = name

    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s=0.02):
        """Set HFSS single frequency solution.
        Parameters
        ----------
        frequency : str, optional
            Adaptive frequency.
        max_num_passes : int, optional
            Maxmímum passes number. Default value `10`.
        max_delta_s : float, optional
            Maximum delta S value. Default value `0.02`,

        Returns
        -------
         bool
        """
        try:
            self.settings.general.adaptive_solution_type = GrpcAdaptType.SINGLE
            self.settings.general.single_frequency_adaptive_solution.adaptive_frequency = frequency
            self.settings.general.single_frequency_adaptive_solution.max_passes = max_num_passes
            self.settings.general.single_frequency_adaptive_solution.max_delta = str(max_delta_s)
            return True
        except:
            return False

    def set_solution_multi_frequencies(self, frequencies="5GHz", max_delta_s=0.02):
        """Set HFSS setup multi frequencies adaptive.

        Parameters
        ----------
        frequencies : str, List[str].
            Adaptive frequencies.
        max_delta_s : float, List[float].
            Max delta S values.

        Returns
        -------
            bool.
        """
        try:
            self.settings.general.adaptive_solution_type = GrpcAdaptType.MULTI_FREQUENCIES
            if not isinstance(frequencies, list):
                frequencies = [frequencies]
            if not isinstance(max_delta_s, list):
                max_delta_s = [max_delta_s]
                if len(max_delta_s) < len(frequencies):
                    for _ in frequencies[len(max_delta_s) :]:
                        max_delta_s.append(max_delta_s[-1])
            adapt_frequencies = [
                GrpcAdaptiveFrequency(frequencies[ind], str(max_delta_s[ind])) for ind in range(len(frequencies))
            ]
            self.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies = adapt_frequencies
            return True
        except:
            return False

    def set_solution_broadband(self, low_frequency="1GHz", high_frequency="10GHz", max_delta_s=0.02, max_num_passes=10):
        try:
            self.settings.general.adaptive_solution_type = GrpcAdaptType.BROADBAND
            self.settings.general.broadband_adaptive_solution.low_frequency = low_frequency
            self.settings.general.broadband_adaptive_solution.high_frequency = high_frequency
            self.settings.general.broadband_adaptive_solution.max_delta = str(max_delta_s)
            self.settings.general.broadband_adaptive_solution.max_num_passes = max_num_passes
            return True
        except:
            return False

    def add_adaptive_frequency_data(self, frequency="5GHz", max_delta_s="0.01"):
        try:
            adapt_frequencies = self.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies
            adapt_frequencies.append(GrpcAdaptiveFrequency(frequency, str(max_delta_s)))
            self.settings.general.multi_frequency_adaptive_solution.adaptive_frequencies = adapt_frequencies
            return True
        except:
            return False

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
        from ansys.edb.core.simulation_setup.mesh_operation import (
            LengthMeshOperation as GrpcLengthMeshOperation,
        )

        if not name:
            name = generate_unique_name("skin")
        net_layer_op = []
        if net_layer_list:
            for net, layers in net_layer_list.items():
                if not isinstance(layers, list):
                    layers = [layers]
                for layer in layers:
                    net_layer_op.append((net, layer, True))

        mop = GrpcLengthMeshOperation(
            name=name,
            net_layer_info=net_layer_op,
            refine_inside=refine_inside,
            mesh_region=mesh_region,
            max_length=max_length,
            restrict_max_length=restrict_length,
            restrict_max_elements=restrict_elements,
            max_elements=max_elements,
        )
        self.mesh_operations.append(mop)
        return mop

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
        net_layer_op = []
        if net_layer_list:
            for net, layers in net_layer_list.items():
                if not isinstance(layers, list):
                    layers = [layers]
                for layer in layers:
                    net_layer_op.append((net, layer, True))
        from ansys.edb.core.simulation_setup.mesh_operation import (
            SkinDepthMeshOperation as GrpcSkinDepthMeshOperation,
        )

        mesh_operation = GrpcSkinDepthMeshOperation(
            name=name,
            net_layer_info=net_layer_op,
            refine_inside=refine_inside,
            mesh_region=mesh_region,
            skin_depth=skin_depth,
            surface_triangle_length=surface_triangle_length,
            restrict_max_elements=restrict_elements,
            max_elements=max_elements,
            num_layers=str(number_of_layers),
        )
        self.mesh_operations.append(mesh_operation)
        return mesh_operation

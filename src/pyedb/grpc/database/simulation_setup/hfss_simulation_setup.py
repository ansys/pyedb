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


from ansys.edb.core.simulation_setup.adaptive_solutions import (
    AdaptiveFrequency as GrpcAdaptiveFrequency,
)
from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    AdaptType as GrpcAdaptType,
)
from ansys.edb.core.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup as GrpcHfssSimulationSetup,
)
from ansys.edb.core.simulation_setup.mesh_operation import LengthMeshOperation as GrpcLengthMeshOperation

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.simulation_setup.sweep_data import SweepData


class HfssSimulationSetup(GrpcHfssSimulationSetup):
    """HFSS simulation setup class."""

    def __init__(self, pedb, edb_object, name: str = None):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._name = name

    @property
    def hfss_solver_settings(self):
        """Legacy compatibility to settings properties."""
        return self.settings.options

    @property
    def adaptive_settings(self):
        """Legacy compatibility to general settings."""
        return self.settings.general

    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s=0.02) -> bool:
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
        bool.

        """
        try:
            self.settings.general.adaptive_solution_type = GrpcAdaptType.SINGLE
            sfs = self.settings.general.single_frequency_adaptive_solution
            sfs.adaptive_frequency = frequency
            sfs.max_passes = max_num_passes
            sfs.max_delta = str(max_delta_s)
            self.settings.general.single_frequency_adaptive_solution = sfs
            return True
        except:
            return False

    def set_solution_multi_frequencies(self, frequencies="5GHz", max_delta_s=0.02) -> bool:
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
        """Set solution to broadband.

        Parameters
        ----------
        low_frequency : str
            Low frequency value.
        high_frequency : str
            High frequency value.
        max_delta_s : float
            Max delta S value.
        max_num_passes : int
            Maximum number of passes.

        Returns
        -------
        bool.

        """
        try:
            self.settings.general.adaptive_solution_type = GrpcAdaptType.BROADBAND
            bfs = self.settings.general.broadband_adaptive_solution
            bfs.low_frequency = low_frequency
            bfs.high_frequency = high_frequency
            bfs.max_delta = str(max_delta_s)
            bfs.max_num_passes = max_num_passes
            self.settings.general.broadband_adaptive_solution = bfs
            return True
        except:
            return False

    def add_adaptive_frequency_data(self, frequency="5GHz", max_delta_s="0.01"):
        """Add adaptive frequency data to simulation setup.

        Parameters
        ----------
        frequency : str
            Adaptive frequency value.

        max_delta_s : str
            Maximum delta S value.

        Returns
        -------
        bool.

        """
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
        :class:`LengthMeshOperation <ansys.edb.core.simulation_setup.mesh_operation.LengthMeshOperation>`

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
            mesh_region=str(net_layer_op),
            max_length=str(max_length),
            restrict_max_length=restrict_length,
            restrict_max_elements=restrict_elements,
            max_elements=str(max_elements),
        )
        mesh_ops = self.mesh_operations
        mesh_ops.append(mop)
        self.mesh_operations = mesh_ops
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
        :class:`LengthMeshOperation <ansys.edb.core.simulation_setup.mesh_operation.LengthMeshOperation>`

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
            skin_depth=str(skin_depth),
            surface_triangle_length=str(surface_triangle_length),
            restrict_max_elements=restrict_elements,
            max_elements=str(max_elements),
            num_layers=str(number_of_layers),
        )
        mesh_ops = self.mesh_operations
        mesh_ops.append(mesh_operation)
        self.mesh_operations = mesh_ops
        return mesh_operation

    def add_sweep(
        self,
        name=None,
        distribution="linear",
        start_freq="0GHz",
        stop_freq="20GHz",
        step="10MHz",
        discrete=False,
        frequency_set=None,
    ):
        """Add a HFSS frequency sweep.

        Parameters
        ----------
        name : str, optional
         Sweep name.
        distribution : str, optional
            Type of the sweep. The default is `"linear"`. Options are:
            - `"linear"`
            - `"linear_count"`
            - `"decade_count"`
            - `"octave_count"`
            - `"exponential"`
        start_freq : str, float, optional
            Starting frequency. The default is ``1``.
        stop_freq : str, float, optional
            Stopping frequency. The default is ``1e9``.
        step : str, float, int, optional
            Frequency step. The default is ``1e6``. or used for `"decade_count"`, "linear_count"`, "octave_count"`
            distribution. Must be integer in that case.
        discrete : bool, optional
            Whether the sweep is discrete. The default is ``False``.
        frequency_set : List, optional
            Frequency set is a list adding one or more frequency sweeps. If ``frequency_set`` is provided, the other
            arguments are ignored except ``discrete``. Default value is ``None``.
            example of frequency_set : [['linear_scale', '50MHz', '200MHz', '10MHz']].

        Returns
        -------
        bool
        """
        init_sweep_count = len(self.sweep_data)
        if frequency_set:
            for sweep in frequency_set:
                if "linear_scale" in sweep:
                    distribution = "LIN"
                elif "linear_count" in sweep:
                    distribution = "LINC"
                elif "exponential" in sweep:
                    distribution = "ESTP"
                elif "log_scale" in sweep:
                    distribution = "DEC"
                elif "octave_count" in sweep:
                    distribution = "OCT"
                else:
                    distribution = "LIN"
                start_freq = self._pedb.number_with_units(sweep[1], "Hz")
                stop_freq = self._pedb.number_with_units(sweep[2], "Hz")
                step = str(sweep[3])
                if not name:
                    name = f"sweep_{init_sweep_count + 1}"
                sweep_data = [
                    SweepData(
                        self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step
                    )
                ]
                if discrete:
                    sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
                for sweep in self.sweep_data:
                    sweep_data.append(sweep)
                self.sweep_data = sweep_data
        else:
            start_freq = self._pedb.number_with_units(start_freq, "Hz")
            stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
            step = str(step)
            if not distribution in ["LIN", "LINC", "ESTP", "DEC", "OCT"]:
                if distribution.lower() == "linear" or distribution.lower() == "linear scale":
                    distribution = "LIN"
                elif distribution.lower() == "linear_count" or distribution.lower() == "linear count":
                    distribution = "LINC"
                elif distribution.lower() == "exponential":
                    distribution = "ESTP"
                elif (
                    distribution.lower() == "decade_count"
                    or distribution.lower() == "decade count"
                    or distribution.lower()
                ) == "log scale":
                    distribution = "DEC"
                elif distribution.lower() == "octave_count" or distribution.lower() == "octave count":
                    distribution = "OCT"
                else:
                    distribution = "LIN"
            if not name:
                name = f"sweep_{init_sweep_count + 1}"
            sweep_data = [
                SweepData(
                    self._pedb, name=name, distribution=distribution, start_f=start_freq, end_f=stop_freq, step=step
                )
            ]
            if discrete:
                sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
            for sweep in self.sweep_data:
                sweep_data.append(sweep)
            self.sweep_data = sweep_data
            if len(self.sweep_data) == init_sweep_count + 1:
                return self.sweep_data[-1]
            else:
                self._pedb.logger.error("Failed to add frequency sweep data")
                return False

    def auto_mesh_operation(
        self,
        trace_ratio_seeding: float = 3,
        signal_via_side_number: int = 12,
        power_ground_via_side_number: int = 6,
    ) -> bool:
        """
        Automatically create and apply a length-based mesh operation for all nets in the design.

        The method inspects every signal net, determines the smallest trace width, and
        seeds a :class:`GrpcLengthMeshOperation` whose maximum element length is
        ``smallest_width * trace_ratio_seeding``. Signal vias (padstack instances) are
        configured with the requested number of polygon sides, while power/ground vias
        are updated through the global ``num_via_sides`` advanced setting.

        Parameters
        ----------
        trace_ratio_seeding : float, optional
            Ratio used to compute the maximum allowed element length from the
            smallest trace width found in the design.  The resulting length is
            ``min_width * trace_ratio_seeding``.  Defaults to ``3``.
        signal_via_side_number : int, optional
            Number of sides (i.e. faceting resolution) assigned to **signal**
            padstack instances that belong to the nets being meshed.
            Defaults to ``12``.
        power_ground_via_side_number : int, optional
            Number of sides assigned to **power/ground** vias via the global
            ``advanced.num_via_sides`` setting.  Defaults to ``6``.

        Returns
        -------
        bool

        Raises
        ------
        ValueError
            If the design contains no terminals, making mesh seeding impossible.

        Notes
        -----
        * Only primitives of type ``"path"`` are considered when determining the
          smallest trace width.
        * Every ``(net, layer, sheet)`` tuple required by the mesher is
          automatically populated; sheet are explicitly marked as ``False``.
        * Existing contents of :attr:`mesh_operations` are **replaced** by the
          single new operation.

        Examples
        --------
        >>> setup = edbapp.setups["my_setup"]
        >>> setup.auto_mesh_operation(trace_ratio_seeding=4, signal_via_side_number=16)
        >>> setup.mesh_operations[0].max_length
        '2.5um'
        """
        net_for_mesh_seeding = list(set([term.net.name for term in list(self._pedb.terminals.values())]))
        if not net_for_mesh_seeding:
            raise ValueError("No terminals found to seed the mesh operation.")
        meshop = GrpcLengthMeshOperation(name=f"{self.name}_AutoMeshOp")
        layer_info = []
        smallest_width = 1e3
        for net in net_for_mesh_seeding:
            traces = [prim for prim in self._pedb.modeler.primitives_by_net[net] if prim.type == "path"]
            _width = min([trace.width for trace in traces], default=1e3)
            if _width < smallest_width:
                smallest_width = _width
            layers = list(set([trace.layer.name for trace in traces]))
            for layer in layers:
                layer_info.append((net, layer, False))
            for inst in self._pedb.padstacks.instances_by_net[net]:
                inst.side_number = signal_via_side_number
        meshop.max_length = f"{round(float((smallest_width * trace_ratio_seeding)), 9) * 1e6}um"
        meshop.net_layer_info = layer_info
        self.mesh_operations = [meshop]
        self.settings.advanced.num_via_sides = power_ground_via_side_number
        if self.mesh_operations:
            return True
        return False

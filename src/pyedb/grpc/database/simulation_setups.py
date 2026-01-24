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


from typing import Union, cast

from ansys.edb.core.database import ProductIdType as GrpcProductIdType

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.simulation_setup.hfss_simulation_setup import HfssSimulationSetup
from pyedb.grpc.database.simulation_setup.q3d_simulation_setup import Q3DSimulationSetup
from pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup import RaptorXSimulationSetup
from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup as BaseSimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup import SIWaveCPASimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup import SIWaveDCIRSimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_simulation_setup import SiwaveSimulationSetup
from pyedb.siwave_core.product_properties import SIwaveProperties


class SimulationSetups:
    """Simulation setups container class."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._hfss_setups: dict[str, HfssSimulationSetup] = {}
        self._siwave_setups: dict[str, SiwaveSimulationSetup] = {}
        self._siwave_dcir_setups: dict[str, SIWaveDCIRSimulationSetup] = {}
        self._raptorx_setups: dict[str, RaptorXSimulationSetup] = {}
        self._q3d_setups: dict[str, Q3DSimulationSetup] = {}
        self._siwave_cpa_setup: dict[str, SIWaveCPASimulationSetup] = {}

    @property
    def hfss(self) -> dict[str, HfssSimulationSetup]:
        """HFSS simulation setups.

        Returns
        -------
        List[:class:`HFSSSimulationSetup <pyedb.grpc.database.simulation_setup.
        hfss_simulation_setup.HFSSSimulationSetup>`]
        """
        self._hfss_setups = {
            setup.name: HfssSimulationSetup(self._pedb, setup)
            for setup in self._pedb.active_cell.simulation_setups
            if setup.type.name.lower() == "hfss"
        }
        return self._hfss_setups

    @property
    def siwave(self) -> dict[str, SiwaveSimulationSetup]:
        """SIWave simulation setups.

        Returns
        -------
        List[:class:`SIWaveSimulationSetup <pyedb.grpc.database.simulation_setup.
        siwave_simulation_setup.SIWaveSimulationSetup>`]
        """
        self._siwave_setups = {
            setup.name: SiwaveSimulationSetup(self._pedb, setup)
            for setup in self._pedb.active_cell.simulation_setups
            if setup.type.name.lower() == "si_wave"
        }
        return self._siwave_setups

    @property
    def siwave_dcir(self) -> dict[str, SIWaveDCIRSimulationSetup]:
        """SIWave DCIR simulation setups.

        Returns
        -------
        List[:class:`SIWaveDCIRSimulationSetup <pyedb.grpc.database.simulation_setup.
        siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup>`]
        """
        self._siwave_dcir_setups = {
            setup.name: SIWaveDCIRSimulationSetup(self._pedb, setup)
            for setup in self._pedb.active_cell.simulation_setups
            if setup.type.name.lower() == "si_wave_dcir"
        }
        return self._siwave_dcir_setups

    @property
    def siwave_cpa(self) -> dict[str, SIWaveCPASimulationSetup]:
        """SIWave CPA simulation setups.

        Returns
        -------
        List[:class:`SIWaveCPASimulationSetup <pyedb.grpc.database.simulation_setup.
        siwave_cpa_simulation_setup.SIWaveCPASimulationSetup>`]
        """

        # cpa setup is not a real simulation setup type in EDB.
        # It is created through product interface (ProductProperty).
        # THe setup is unique per design, and is created when imported inside SIwave,
        # THe setup does not reside itself inside simulation setups collection.

        # check if cpa name exists
        cpa_setup_name = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME
        ).value
        if cpa_setup_name:
            if cpa_setup_name not in self._siwave_cpa_setup:
                # instantiate the cpa setup
                self._siwave_cpa_setup[cpa_setup_name] = SIWaveCPASimulationSetup(self._pedb, cpa_setup_name)
        return self._siwave_cpa_setup

    @property
    def raptorx(self) -> dict[str, RaptorXSimulationSetup]:
        """RaptorX simulation setups.

        Returns
        -------
        List[:class:`RaptorXSimulationSetup <pyedb.grpc.database.simulation_setup.
        raptor_x_simulation_setup.RaptorXSimulationSetup>`]
        """
        if self._raptorx_setups is None:
            self._raptorx_setups = {
                setup.name: RaptorXSimulationSetup(self._pedb, setup)
                for setup in self._pedb.active_cell.simulation_setups
                if setup.type.name.lower() == "raptor_x"
            }
        return self._raptorx_setups

    @property
    def q3d(self) -> dict[str, Q3DSimulationSetup]:
        """Q3D simulation setups.

        Returns
        -------
        List[:class:`Q3DSimulationSetup <pyedb.grpc.database.simulation_setup.
        q3d_simulation_setup.Q3DSimulationSetup>`]
        """
        if self._q3d_setups is None:
            self._q3d_setups = {
                setup.name: Q3DSimulationSetup(self._pedb, setup)
                for setup in self._pedb.active_cell.simulation_setups
                if setup.type == "q3d_sim"
            }
        return self._q3d_setups

    @property
    def setups(self) -> dict[str, object]:
        """All simulation setups.

        Returns
        -------
        dict[str:setup name, :class:`SimulationSetup <pyedb.grpc.database.simulation_setup.
        simulation_setup.SimulationSetup>`]
        """
        # Merge all per-solver dicts into a single mapping
        return {**self.hfss, **self.siwave, **self.siwave_dcir, **self.siwave_cpa, **self.raptorx, **self.q3d}

    def create(
        self,
        name=None,
        solver="hfss",
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> Union[BaseSimulationSetup, None]:
        """Add HFSS analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        solver : str, optional
            Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptorx", "q3d").
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
            Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        HfssSimulationSetup
            Created setup object.

        Examples
        --------
        .. code:: python

            from pyedb import Edb

            edb = Edb("my_aedb")
            hfss_setup = edb.simulation_setups.create(
                name="MySetup",
                solver="hfss",
                distribution="linear_count",
                start_freq=1e9,
                stop_freq=10e9,
                step_freq=100,
                discrete_sweep=False,
                sweep_name="MyFrequencySweep",
            )
        """
        if not name:
            name = generate_unique_name(f"{solver}_setup")
        if name in self._pedb.setups:
            self._pedb.logger.error(f"Simulation setup {name} already defined.")
            return None
        if solver.lower() == "hfss":
            setup = HfssSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"HFSS setup {name} created.")
        elif solver.lower() == "siwave":
            setup = SiwaveSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave setup {name} created.")
        elif solver.lower() == "siwave_dcir":
            setup = SIWaveDCIRSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave DCIR setup {name} created.")
        elif solver.lower() == "raptorx":
            setup = RaptorXSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"RaptorX setup {name} created.")
        elif solver.lower() == "q3d":
            setup = Q3DSimulationSetup.create(self._pedb.active_cell, name)
            self._pedb.logger.info(f"Q3D setup {name} created.")
        else:
            setup = HfssSimulationSetup.create(self._pedb.active_cell, name)
            self._pedb.logger.info(f"HFSS setup {name} created.")
            setup.add_sweep(
                name=sweep_name,
                distribution=distribution,
                start_freq=start_freq,
                stop_freq=stop_freq,
                step=step_freq,
                discrete=discrete_sweep,
                frequency_set=None,
            )
            self._pedb.logger.info(f"Frequency sweep {sweep_name} added to simulation setup {name}.")

        for k, v in kwargs.items():
            setattr(setup, k, v)
        return setup

    def create_hfss_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> HfssSimulationSetup:
        """Add HFSS analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
        Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        HfssSimulationSetup
            Created setup object.
        """
        result = self.create(
            name=name,
            solver="hfss",
            distribution=distribution,
            start_freq=start_freq,
            stop_freq=stop_freq,
            step_freq=step_freq,
            discrete_sweep=discrete_sweep,
            sweep_name=sweep_name,
            **kwargs,
        )
        return cast(HfssSimulationSetup, result)  # casting only for IDE type checking purposes

    def create_siwave_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> SiwaveSimulationSetup:
        """Add SIWave analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
            Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        SIWaveSimulationSetup
            Created setup object.
        """
        result = self.create(
            name=name,
            solver="siwave",
            distribution=distribution,
            start_freq=start_freq,
            stop_freq=stop_freq,
            step_freq=step_freq,
            discrete_sweep=discrete_sweep,
            sweep_name=sweep_name,
            **kwargs,
        )
        return cast(SiwaveSimulationSetup, result)  # casting only for IDE type checking purposes

    def create_siwave_dcir_setup(self, name=None, **kwargs) -> SIWaveDCIRSimulationSetup:
        """Add SIWave DCIR analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).

        Returns
        -------
        SIWaveDCIRSimulationSetup
            Created setup object.
        """
        result = self.create(name=name, solver="siwave_dcir", **kwargs)
        return cast(SIWaveDCIRSimulationSetup, result)  # casting only for IDE type checking purposes

    def create_siwave_cpa_setup(self, name=None, siwave_cpa_config=None, **kwargs) -> SIWaveCPASimulationSetup:
        """Add SIWave CPA analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).

        Returns
        -------
        SIWaveCPASimulationSetup
            Created setup object.
        """
        if not name:
            name = generate_unique_name("siwave_cpa_setup")
        if name in self.siwave_cpa:
            self._pedb.logger.error(f"SIWave CPA simulation setup {name} already defined.")
            return self.siwave_cpa[name]

        # Create the CPA setup through product property interface
        cpa_setup = SIWaveCPASimulationSetup.create(self._pedb, name, siwave_cpa_config)
        self._pedb.logger.info(f"SIWave CPA setup {name} created.")

        # Store the created setup in the internal dictionary
        self._siwave_cpa_setup[name] = cpa_setup

        return cpa_setup

    def create_raptorx_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> RaptorXSimulationSetup:
        """Add RaptorX analysis setup
        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
            Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.
        Returns
        -------
        RaptorXSimulationSetup
            Created setup object.
        """

        result = self.create(
            name=name,
            solver="raptorx",
            distribution=distribution,
            start_freq=start_freq,
            stop_freq=stop_freq,
            step_freq=step_freq,
            discrete_sweep=discrete_sweep,
            sweep_name=sweep_name,
            **kwargs,
        )
        return cast(RaptorXSimulationSetup, result)  # casting only for IDE type checking purposes

    def create_q3d_setup(
        self,
        name=None,
        distribution="linear",
        start_freq=0,
        stop_freq=20e9,
        step_freq=1e6,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> Q3DSimulationSetup:
        """Add Q3D analysis setup
        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency (Hz).
        stop_freq : float, str, optional
            Stopping frequency (Hz).
        step_freq : float, str, int, optional
            Frequency step (Hz) or count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.
        Returns
        -------
        Q3DSimulationSetup
            Created setup object.
        """

        result = self.create(
            name=name,
            solver="q3d",
            distribution=distribution,
            start_freq=start_freq,
            stop_freq=stop_freq,
            step_freq=step_freq,
            discrete_sweep=discrete_sweep,
            sweep_name=sweep_name,
            **kwargs,
        )
        return cast(Q3DSimulationSetup, result)  # casting only for IDE type checking purposes

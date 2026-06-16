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


from typing import cast

from ansys.edb.core.database import ProductIdType as CoreProductIdType
from ansys.edb.core.simulation_setup.simulation_setup import SimulationSetup as CoreSimulationSetup

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.simulation_setup.hfss_pi_simulation_setup import HFSSPISimulationSetup
from pyedb.grpc.database.simulation_setup.hfss_simulation_setup import HfssSimulationSetup
from pyedb.grpc.database.simulation_setup.q3d_simulation_setup import Q3DSimulationSetup
from pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup import RaptorXSimulationSetup
from pyedb.grpc.database.simulation_setup.simulation_setup import SimulationSetup as BaseSimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup import SIWaveCPASimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup import SIWaveDCIRSimulationSetup
from pyedb.grpc.database.simulation_setup.siwave_simulation_setup import SiwaveSimulationSetup
from pyedb.misc.decorators import deprecate_argument_name
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
        self._hfss_pi_setups: dict[str, HFSSPISimulationSetup] = {}

    @staticmethod
    def _sweep_params_are_set(start_freq, stop_freq, step_freq) -> bool:
        """Return True when all sweep parameters are explicitly provided."""
        return start_freq is not None and stop_freq is not None and step_freq is not None

    def _raw_simulation_setups(self) -> list[CoreSimulationSetup]:
        """Return raw (uncast) core SimulationSetup objects from the active cell.

        This helper exists to work around a limitation in the public
        ``ansys-edb-core`` API.  ``Cell.simulation_setups`` internally calls
        ``.cast()`` on every object it returns.  The ``cast()`` implementation
        in the core library only handles a subset of solver types (HFSS,
        SI_WAVE, SI_WAVE_DCIR, RAPTOR_X) and returns ``None`` for any type it
        does not recognise — most notably ``HFSS_PI``.  Those ``None`` values
        are then silently discarded during the usual None-filtering step,
        making the ``hfss_pi`` property (and the ``setups`` aggregator) always
        return an empty dict even after a valid HFSS PI setup has been created.

        To avoid this, this method bypasses ``.cast()`` entirely: it calls the
        underlying gRPC stub (``_Cell__stub.GetSimulationSetups``) directly and
        wraps the raw protobuf messages in plain ``CoreSimulationSetup``
        objects.  The type is then read via ``setup.type.name`` inside each
        property and the correct PyEDB wrapper class is instantiated there.

        If the private stub attribute is not accessible for any reason (e.g. a
        future API refactor), the method falls back to the public
        ``active_cell.simulation_setups`` call so that HFSS, SI_WAVE and other
        already-handled types remain functional.

        Returns
        -------
        list[CoreSimulationSetup]
            All simulation setups present in the active cell, including
            ``HFSS_PI`` and any other types not covered by ``.cast()``.
        """
        try:
            # Access the private name-mangled gRPC stub on Cell directly so we
            # can call GetSimulationSetups without going through .cast(), which
            # would drop HFSS_PI setups (see docstring above).
            stub = self._pedb.active_cell._Cell__stub
            msgs = stub.GetSimulationSetups(self._pedb.active_cell.msg).items
            return [CoreSimulationSetup(msg) for msg in msgs]
        except Exception:
            # Fall back to the public API if the private stub is not accessible.
            # Note: HFSS_PI setups will be missing in this path due to the
            # .cast() issue described above, but all other solver types work.
            setups = self._pedb.active_cell.simulation_setups
            if isinstance(setups, list):
                return [s for s in setups if s is not None]
            return []

    @property
    def hfss(self) -> dict[str, HfssSimulationSetup]:
        """HFSS simulation setups.

        Returns
        -------
        List[:class:`HFSSSimulationSetup <pyedb.grpc.database.simulation_setup.
        hfss_simulation_setup.HFSSSimulationSetup>`]
        """
        self._hfss_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._hfss_setups
        self._hfss_setups = {
            setup.name: HfssSimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "hfss"
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
        self._siwave_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._siwave_setups
        self._siwave_setups = {
            setup.name: SiwaveSimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "si_wave"
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
        self._siwave_dcir_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._siwave_dcir_setups
        self._siwave_dcir_setups = {
            setup.name: SIWaveDCIRSimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "si_wave_dcir"
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
            CoreProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME
        ).value
        if cpa_setup_name:
            if cpa_setup_name not in self._siwave_cpa_setup:
                # instantiate the cpa setup
                self._siwave_cpa_setup[cpa_setup_name] = SIWaveCPASimulationSetup(self._pedb, cpa_setup_name)
        return self._siwave_cpa_setup

    @property
    def raptor_x(self) -> dict[str, RaptorXSimulationSetup]:
        """RaptorX simulation setups.

        Returns
        -------
        List[:class:`RaptorXSimulationSetup <pyedb.grpc.database.simulation_setup.
        raptor_x_simulation_setup.RaptorXSimulationSetup>`]
        """
        self._raptorx_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._raptorx_setups
        self._raptorx_setups = {
            setup.name: RaptorXSimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "raptor_x"
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
        self._q3d_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._q3d_setups
        self._q3d_setups = {
            setup.name: Q3DSimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "q3d_sim"
        }
        return self._q3d_setups

    @property
    def hfss_pi(self) -> dict[str, HFSSPISimulationSetup]:
        """HFSS PI simulation setups.

        Returns
        -------
        List[:class:`HFSSPISimulationSetup <pyedb.grpc.database.simulation_setup.
        hfss_pi_simulation_setup.HFSSPISimulationSetup>`]
        """
        self._hfss_pi_setups = {}
        setups = self._raw_simulation_setups()
        if not setups:
            return self._hfss_pi_setups
        self._hfss_pi_setups = {
            setup.name: HFSSPISimulationSetup(self._pedb, setup)
            for setup in setups
            if setup.type is not None and setup.type.name.lower() == "hfss_pi"
        }
        return self._hfss_pi_setups

    @property
    def setups(
        self,
    ) -> dict[
        str,
        HfssSimulationSetup
        | SiwaveSimulationSetup
        | SIWaveDCIRSimulationSetup
        | SIWaveCPASimulationSetup
        | RaptorXSimulationSetup
        | Q3DSimulationSetup
        | HFSSPISimulationSetup,
    ]:
        """All simulation setups.

        Returns
        -------
        dict[str:setup name, :class:`SimulationSetup <pyedb.grpc.database.simulation_setup.
        simulation_setup.SimulationSetup>`]
        """
        # Merge all per-solver dicts into a single mapping
        return {
            **self.hfss,
            **self.siwave,
            **self.siwave_dcir,
            **self.siwave_cpa,
            **self.raptor_x,
            **self.q3d,
            **self.hfss_pi,
        }

    def create(self, name=None, solver="hfss") -> BaseSimulationSetup | None:
        """Add analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        solver : str, optional
            Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptor_x", "q3d", "hfss_pi").

        Returns
        -------
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
        elif solver.lower() == "raptor_x":
            setup = RaptorXSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"RaptorX setup {name} created.")
        elif solver.lower() == "q3d":
            setup = Q3DSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"Q3D setup {name} created.")
        elif solver.lower() == "hfss_pi":
            setup = HFSSPISimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"HFSS PI setup {name} created.")
        else:
            setup = HfssSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"HFSS setup {name} created.")
        return setup

    @deprecate_argument_name({"freq_step": "step_freq"})
    def create_hfss_setup(
        self,
        name=None,
        distribution="linear",
        start_freq: float | str = None,
        stop_freq: float | str = None,
        step_freq: float | str | int = None,
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
            Starting frequency in Hz, or a unit string like ``"0Hz"``.
        stop_freq : float, str, optional
            Stopping frequency in Hz, or a unit string like ``"10GHz"``.
        step_freq : float, str, int, optional
            Frequency step in Hz, unit string (for example ``"10MHz"``),
            or point count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        HfssSimulationSetup
            Created setup object.
        """
        setup = self.create(
            name=name,
            solver="hfss",
        )
        if self._sweep_params_are_set(start_freq, stop_freq, step_freq):
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
        return cast(HfssSimulationSetup, setup)  # casting only for IDE type checking purposes

    def create_hfss_pi_setup(
        self,
        name=None,
        distribution="linear",
        start_freq: float | str = None,
        stop_freq: float | str = None,
        step_freq: float | str | int = None,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
        **kwargs,
    ) -> HFSSPISimulationSetup:
        """Add HFSS analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        distribution : str, optional
            Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
        start_freq : float, str, optional
            Starting frequency in Hz, or a unit string like ``"0Hz"``.
        stop_freq : float, str, optional
            Stopping frequency in Hz, or a unit string like ``"10GHz"``.
        step_freq : float, str, int, optional
            Frequency step in Hz, unit string (for example ``"10MHz"``),
            or point count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        HfssSimulationSetup
            Created setup object.
        """
        setup = self.create(
            name=name,
            solver="hfss_pi",
        )
        if self._sweep_params_are_set(start_freq, stop_freq, step_freq):
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
        return cast(HFSSPISimulationSetup, setup)  # casting only for IDE type checking purposes

    def create_siwave_setup(
        self,
        name=None,
        distribution="linear",
        start_freq: float | str = None,
        stop_freq: float | str = None,
        step_freq: float | str | int = None,
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
            Starting frequency in Hz, or a unit string like ``"0Hz"``.
        stop_freq : float, str, optional
            Stopping frequency in Hz, or a unit string like ``"10GHz"``.
        step_freq : float, str, int, optional
            Frequency step in Hz, unit string (for example ``"10MHz"``),
            or point count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        SIWaveSimulationSetup
            Created setup object.
        """
        setup = self.create(
            name=name,
            solver="siwave",
        )
        if self._sweep_params_are_set(start_freq, stop_freq, step_freq):
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
        return cast(SiwaveSimulationSetup, setup)  # casting only for IDE type checking purposes

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
        setup = self.create(name=name, solver="siwave_dcir")
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return cast(SIWaveDCIRSimulationSetup, setup)  # casting only for IDE type checking purposes

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
        setup = SIWaveCPASimulationSetup.create(self._pedb, name, siwave_cpa_config)
        for k, v in kwargs.items():
            setattr(setup, k, v)
        self._pedb.logger.info(f"SIWave CPA setup {name} created.")

        # Store the created setup in the internal dictionary
        self._siwave_cpa_setup[name] = setup

        return setup

    def create_raptor_x_setup(
        self,
        name=None,
        distribution="linear",
        start_freq: float | str = None,
        stop_freq: float | str = None,
        step_freq: float | str | int = None,
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
            Starting frequency in Hz, or a unit string like ``"0Hz"``.
        stop_freq : float, str, optional
            Stopping frequency in Hz, or a unit string like ``"10GHz"``.
        step_freq : float, str, int, optional
            Frequency step in Hz, unit string (for example ``"10MHz"``),
            or point count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        RaptorXSimulationSetup
            Created setup object.
        """
        setup = self.create(
            name=name,
            solver="raptor_x",
        )
        if self._sweep_params_are_set(start_freq, stop_freq, step_freq):
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
        return cast(RaptorXSimulationSetup, setup)  # casting only for IDE type checking purposes

    def create_q3d_setup(
        self,
        name=None,
        distribution="linear",
        start_freq: float | str = None,
        stop_freq: float | str = None,
        step_freq: float | str | int = None,
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
            Starting frequency in Hz, or a unit string like ``"0Hz"``.
        stop_freq : float, str, optional
            Stopping frequency in Hz, or a unit string like ``"10GHz"``.
        step_freq : float, str, int, optional
            Frequency step in Hz, unit string (for example ``"10MHz"``),
            or point count depending on distribution.
        discrete_sweep : bool, optional
            Use discrete sweep.
        sweep_name : str, optional
            Name of the frequency sweep.

        Returns
        -------
        Q3DSimulationSetup
            Created setup object.
        """
        setup = self.create(
            name=name,
            solver="q3d",
        )
        if self._sweep_params_are_set(start_freq, stop_freq, step_freq):
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
        return cast(Q3DSimulationSetup, setup)  # casting only for IDE type checking purposes

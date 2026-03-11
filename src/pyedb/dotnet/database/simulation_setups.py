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


from pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data import (
    RaptorXSimulationSetup,
)
from pyedb.dotnet.database.utilities.hfss_simulation_setup import HFSSPISimulationSetup, HfssSimulationSetup
from pyedb.dotnet.database.utilities.siwave_simulation_setup import SiwaveDCSimulationSetup, SIwaveSimulationSetup
from pyedb.generic.general_methods import generate_unique_name


class SimulationSetups:
    """Simulation setups container class."""

    def __init__(self, pedb):
        self._pedb = pedb

    def create(
        self,
        name=None,
        solver="hfss",
    ):
        """Add analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name (auto-generated if None).
        solver : str, optional
            Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptor_x", "q3d").
        """
        if not name:
            name = generate_unique_name(f"{solver}_setup")
        if name in self._pedb.setups:
            raise ValueError(f"Simulation setup {name} already defined.")
        if solver.lower() == "hfss":
            setup = HfssSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"HFSS setup {name} created.")
        elif solver.lower() == "siwave":
            setup = SIwaveSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave setup {name} created.")
        elif solver.lower() == "siwave_dcir":
            setup = SiwaveDCSimulationSetup.create(self._pedb, name)
            self._pedb.logger.info(f"SIWave DCIR setup {name} created.")
        else:
            raise ValueError(f"Unsupported solver type: {solver}.")
        return setup

    def create_hfss_setup(
        self,
        name: str = None,
        distribution="linear",
        start_freq: float = None,
        stop_freq: float = None,
        freq_step: float = None,
        discrete_sweep=False,
        sweep_name: str = "frequency_sweep",
    ) -> HfssSimulationSetup:
        """Create an HFSS simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_hfss_setup("setup1")
        >>> setup1.hfss_port_settings.max_delta_z0 = 0.5
        """
        if name in self._pedb.setups:
            raise RuntimeError("setup already exists")
        elif not name:
            name = generate_unique_name("setup")
        setup = HfssSimulationSetup.create(self._pedb, name=name)
        setup.set_solution_single_frequency("1Ghz")
        setup.add_sweep(
            name=sweep_name,
            distribution=distribution,
            start_freq=start_freq,
            stop_freq=stop_freq,
            step=freq_step,
            discrete=discrete_sweep,
        )
        return setup

    def create_hfss_pi_setup(self, name=None):
        """Create an HFSS PI simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.hfss_pi_simulation_setup_data.HFSSPISimulationSetup when succeeded, ``False``
        when failed.

        """
        if name in self._pedb.setups:
            self._pedb.logger.error("Setup name already used in the layout")
            return False
        if float(self._pedb.version) < 2024.2:
            raise (
                "Unsupported ANSYS release version for HFSS PI simulation setup. "
                "Please use Ansys release 2024R2 or higher.",
                UserWarning,
            )
            return False
        return HFSSPISimulationSetup.create(self._pedb, name=name)

    def create_raptor_x_setup(self, name=None):
        """Create an RaptorX simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationSetup`

        """
        if name in self._pedb.setups:
            raise ValueError("Setup name already used in the layout")
        version = float(self._pedb.version)
        if version < 2024.2:
            raise RuntimeError("RaptorX simulation only supported with Ansys release 2024R2 and higher")
        else:
            setup = RaptorXSimulationSetup.create(self._pedb, name=name)
            return setup

    def create_siwave_dcir_setup(self, name=None, **kwargs):
        """Create a setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_siwave_dc_setup("setup1")
        >>> setup1.mesh_bondwires = True

        """
        if not name:
            name = generate_unique_name("Siwave_DC")
        if name in self._pedb.setups:
            raise RuntimeError("setup already exists")
        setup = SiwaveDCSimulationSetup(self._pedb, name=name)
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return setup

    def create_siwave_setup(self, name=None, **kwargs):
        """Create a setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_frequency_sweep(
        ...     frequency_sweep=[
        ...         ["linear count", "0", "1kHz", 1],
        ...         ["log scale", "1kHz", "0.1GHz", 10],
        ...         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...     ]
        ... )
        """
        if not name:
            name = generate_unique_name("Siwave_SYZ")
        if name in self._pedb.setups:
            raise RuntimeError("setup already exists")
        setup = SIwaveSimulationSetup(self._pedb, name=name)
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return self._pedb.setups[name]

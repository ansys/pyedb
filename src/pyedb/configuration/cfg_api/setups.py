# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Simulation setups builder API.

Data models:
  :class:`~pyedb.configuration.cfg_setup.CfgHFSSSetup`
  :class:`~pyedb.configuration.cfg_setup.CfgSIwaveACSetup`
  :class:`~pyedb.configuration.cfg_setup.CfgSIwaveDCSetup`
  :class:`~pyedb.configuration.cfg_setup.CfgFrequencies`
  :class:`~pyedb.configuration.cfg_setup.CfgSetups`

All builder methods below delegate data storage to the root pydantic models.
``to_list()`` returns ``list[dict]`` compatible with ``CfgSetups.create()``.
"""

from __future__ import annotations

from typing import List, Literal, Optional, Union

from pyedb.configuration.cfg_setup import (
    CfgFrequencies,
    CfgHFSSSetup,
    CfgSIwaveACSetup,
    CfgSIwaveDCSetup,
    CfgSetups,
)

# Re-export root classes so users can import them from the API package
HFSSSetup = CfgHFSSSetup
SIwaveACSetup = CfgSIwaveACSetup
SIwaveDCSetup = CfgSIwaveDCSetup
FrequencySweep = CfgSetupAC = CfgSIwaveACSetup.CfgFrequencySweep if hasattr(CfgSIwaveACSetup, "CfgFrequencySweep") else None


class FrequenciesConfig:
    """Builder helper to create a :class:`~pyedb.configuration.cfg_setup.CfgFrequencies` entry.

    Parameters
    ----------
    start : float or str
        e.g. ``"1GHz"`` or ``1e9``
    stop : float or str
    distribution : str
        ``"linear_count"``, ``"log_count"``, ``"linear_scale"``, ``"log_scale"``, ``"single"``
    increment : int or str
        Step / count / sample value
    """

    def __init__(
        self,
        start: Union[float, str],
        stop: Union[float, str],
        distribution: str,
        increment: Union[int, str],
    ):
        self._model = CfgFrequencies(start=start, stop=stop, distribution=distribution, increment=increment)

    def to_dict(self) -> dict:
        return self._model.model_dump(exclude_none=True)


class SetupsConfig:
    """Fluent builder for the ``setups`` configuration list.

    Wraps :class:`~pyedb.configuration.cfg_setup.CfgSetups`.

    Examples
    --------
    >>> hfss = cfg.setups.add_hfss_setup(name="HFSS_1")
    >>> sw = hfss.add_frequency_sweep(CfgHFSSSetup.CfgFrequencySweep(
    ...     name="sweep1", type="interpolation"))
    >>> siw = cfg.setups.add_siwave_ac_setup(name="SIwave_AC_1")
    """

    def __init__(self):
        self._model = CfgSetups()

    def add_hfss_setup(self, name: str, **kwargs) -> CfgHFSSSetup:
        """Add an HFSS setup.

        Parameters
        ----------
        name : str
        **kwargs
            Any field of :class:`~pyedb.configuration.cfg_setup.CfgHFSSSetup`.

        Returns
        -------
        CfgHFSSSetup
        """
        setup = CfgHFSSSetup(name=name, **kwargs)
        self._model.setups.append(setup)
        return setup

    def add_siwave_ac_setup(self, name: str, **kwargs) -> CfgSIwaveACSetup:
        """Add a SIwave AC setup.

        Parameters
        ----------
        name : str
        **kwargs
            Any field of :class:`~pyedb.configuration.cfg_setup.CfgSIwaveACSetup`.

        Returns
        -------
        CfgSIwaveACSetup
        """
        setup = CfgSIwaveACSetup(name=name, **kwargs)
        self._model.setups.append(setup)
        return setup

    def add_siwave_dc_setup(
        self,
        name: str,
        dc_slider_position: Union[int, str] = 1,
        **kwargs,
    ) -> CfgSIwaveDCSetup:
        """Add a SIwave DC setup.

        Parameters
        ----------
        name : str
        dc_slider_position : int or str
        **kwargs
            Any field of :class:`~pyedb.configuration.cfg_setup.CfgSIwaveDCSetup`.

        Returns
        -------
        CfgSIwaveDCSetup
        """
        setup = CfgSIwaveDCSetup(name=name, dc_slider_position=dc_slider_position, **kwargs)
        self._model.setups.append(setup)
        return setup

    def to_list(self) -> List[dict]:
        """Serialise to a list of dicts compatible with ``CfgSetups.create()``."""
        return [s.model_dump(exclude_none=True) for s in self._model.setups]


# Backward-compatible / convenience aliases that __init__.py and users expect
HfssSetupConfig = CfgHFSSSetup
SIwaveACSetupConfig = CfgSIwaveACSetup
SIwaveDCSetupConfig = CfgSIwaveDCSetup
FrequencySweepConfig = CfgSIwaveACSetup.CfgFrequencySweep


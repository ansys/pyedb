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

from pyedb.dotnet.database.cell.terminal.terminal import Terminal
from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.utility.value import Value


class GapPort(EdgeTerminal):
    """Manages gap port properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.

    Examples
    --------
    This example shows how to access the ``GapPort`` class.
    >>> from pyedb import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> gap_port = edb.ports["gap_port"]
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def magnitude(self) -> float:
        """Magnitude.

        Returns
        -------
        float
            Magnitude value.
        """
        return Value(self.core.source_amplitude, self._pedb.active_cell)

    @property
    def phase(self) -> float:
        """Phase.

        Returns
        -------
        float
            Phase value.
        """
        return Value(self.core.source_phase, self._pedb.active_cell)

    @property
    def renormalize(self) -> bool:
        """Whether renormalize is active.

        Returns
        -------
        bool
        """
        return self.core.port_post_processing_prop.do_renormalize

    @property
    def deembed(self) -> bool:
        """Deembed gap port.

        Returns
        -------
        bool

        """
        return self.core.port_post_processing_prop.do_deembed

    @property
    def renormalize_z0(self) -> tuple[float, float]:
        """Renormalize Z0 value (real, imag).

        Returns
        -------
        Tuple(float, float)
            (Real value, Imaginary value).
        """
        return (
            self.core.port_post_processing_prop.renormalizion_z0[0],
            self.core.port_post_processing_prop.renormalizion_z0[1],
        )

    @property
    def terminal_type(self) -> str:
        """Returns terminal type.

        Returns
        -------
        str
        """
        return self.core.terminal_type


class CircuitPort(GapPort):
    """Manages gap port properties.
    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.
    Examples
    --------
    This example shows how to access the ``GapPort`` class.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)


class WavePort(EdgeTerminal):
    """Manages wave port properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.

    Examples
    --------
    This example shows how to access the ``WavePort`` class.

    >>> from pyedb import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> exc = edb.ports
    """

    def __init__(self, pedb, edb_terminal):
        super().__init__(pedb, edb_terminal)

    @property
    def horizontal_extent_factor(self) -> float:
        """Horizontal extent factor.

        Returns
        -------
        float
            Extent value.
        """
        return self._hfss_port_property["Horizontal Extent Factor"]

    @horizontal_extent_factor.setter
    def horizontal_extent_factor(self, value):
        p = self._hfss_port_property
        p["Horizontal Extent Factor"] = value
        self._hfss_port_property = p

    @property
    def vertical_extent_factor(self) -> float:
        """Vertical extent factor.

        Returns
        -------
        float
            Vertical extent value.

        """
        return self._hfss_port_property["Vertical Extent Factor"]

    @vertical_extent_factor.setter
    def vertical_extent_factor(self, value):
        p = self._hfss_port_property
        p["Vertical Extent Factor"] = value
        self._hfss_port_property = p

    @property
    def pec_launch_width(self) -> float:
        """Launch width for the printed electronic component (PEC).

        Returns
        -------
        float
            Pec launch width value.
        """
        return self._hfss_port_property["PEC Launch Width"]

    @pec_launch_width.setter
    def pec_launch_width(self, value):
        p = self._hfss_port_property
        p["PEC Launch Width"] = value
        self._hfss_port_property = p

    @property
    def deembed(self) -> bool:
        """Whether deembed is active.

        Returns
        -------
        bool

        """
        return self.port_post_processing_prop.do_deembed

    @deembed.setter
    def deembed(self, value):
        p = self.port_post_processing_prop
        p.do_deembed = value
        self.port_post_processing_prop = p

    @property
    def deembed_length(self) -> float:
        """Deembed Length.

        Returns
        -------
        float
            deembed value.
        """
        return Value(self.core.port_post_processing_prop.deembed_length, self._pedb.active_cell)

    @deembed_length.setter
    def deembed_length(self, value):
        p = self.core.port_post_processing_prop
        p.deembed_length = Value(value)
        self.core.port_post_processing_prop = p


class ExcitationSources(EdgeTerminal):
    """Manage sources properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.



    Examples
    --------
    This example shows how to access this class.
    >>> from pyedb import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> all_sources = edb.sources
    >>> print(all_sources["VSource1"].name)

    """

    def __init__(self, pedb, edb_terminal):
        Terminal.__init__(self, pedb, edb_terminal)


class BundleWavePort(BundleTerminal):
    """Manages bundle wave port properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
        BundleTerminal instance from EDB.

    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def _wave_port(self) -> WavePort:
        """ "Wave port.


        Returns
        -------
        :class:`WavePort <pyedb.grpc.ports.ports.WavePort>`

        """
        return WavePort(self._pedb, self.terminals[0].core)

    @property
    def horizontal_extent_factor(self) -> float:
        """Horizontal extent factor.

        Returns
        -------
        float
            Horizontal extent value.
        """
        return self._wave_port.horizontal_extent_factor

    @horizontal_extent_factor.setter
    def horizontal_extent_factor(self, value):
        self._wave_port.horizontal_extent_factor = value

    @property
    def vertical_extent_factor(self) -> float:
        """Vertical extent factor.

        Returns
        -------
        float
            Vertical extent value.
        """
        return self._wave_port.vertical_extent_factor

    @vertical_extent_factor.setter
    def vertical_extent_factor(self, value):
        self._wave_port.vertical_extent_factor = value

    @property
    def pec_launch_width(self) -> float:
        """Launch width for the printed electronic component (PEC).

        Returns
        -------
        float
            Width value.
        """
        return self._wave_port.pec_launch_width

    @pec_launch_width.setter
    def pec_launch_width(self, value):
        self._wave_port.pec_launch_width = value

    @property
    def deembed(self) -> bool:
        """Whether deembed is active.

        Returns
        -------
        bool
        """
        return self._wave_port.deembed

    @deembed.setter
    def deembed(self, value):
        self._wave_port.deembed = value

    @property
    def deembed_length(self) -> float:
        """Deembed Length.

        Returns
        -------
        float
            Length value.
        """
        return self._wave_port.deembed_length

    @deembed_length.setter
    def deembed_length(self, value):
        self._wave_port.deembed_length = value


class CoaxPort(PadstackInstanceTerminal):
    """Manages bundle wave port properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.PadstackInstanceTerminal
        PadstackInstanceTerminal instance from EDB.

    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def radial_extent_factor(self):
        """Radial extent factor.

        Returns
        -------
        float
            Radial extent value.
        """
        return self._hfss_port_property["Radial Extent Factor"]

    @radial_extent_factor.setter
    def radial_extent_factor(self, value):
        p = self._hfss_port_property
        p["Radial Extent Factor"] = value
        self._hfss_port_property = p

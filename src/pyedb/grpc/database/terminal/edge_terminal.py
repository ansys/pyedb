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

import re

from ansys.edb.core.terminal.bundle_terminal import BundleTerminal as GrpcBundleTerminal
from ansys.edb.core.terminal.edge_terminal import EdgeTerminal as GrpcEdgeTerminal


class EdgeTerminal(GrpcEdgeTerminal):
    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._edb_object = edb_object
        self._hfss_type = "Gap"

    @property
    def _edb_properties(self):
        from ansys.edb.core.database import ProductIdType as GrpcProductIdType

        try:
            p = self._edb_object.get_product_property(GrpcProductIdType.DESIGNER, 1)
        except:
            p = ""
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        from ansys.edb.core.database import ProductIdType as GrpcProductIdType

        self._edb_object.set_product_property(GrpcProductIdType.DESIGNER, 1, value)

    @property
    def is_wave_port(self):
        if self._hfss_port_property:
            return True
        return False

    @property
    def _hfss_port_property(self):
        """HFSS port property."""
        hfss_prop = re.search(r"HFSS\(.*?\)", self._edb_properties)
        p = {}
        if hfss_prop:
            hfss_type = re.search(r"'HFSS Type'='([^']+)'", hfss_prop.group())
            orientation = re.search(r"'Orientation'='([^']+)'", hfss_prop.group())
            horizontal_ef = re.search(r"'Horizontal Extent Factor'='([^']+)'", hfss_prop.group())
            vertical_ef = re.search(r"'Vertical Extent Factor'='([^']+)'", hfss_prop.group())
            radial_ef = re.search(r"'Radial Extent Factor'='([^']+)'", hfss_prop.group())
            pec_w = re.search(r"'PEC Launch Width'='([^']+)'", hfss_prop.group())

            p["HFSS Type"] = hfss_type.group(1) if hfss_type else ""
            p["Orientation"] = orientation.group(1) if orientation else ""
            p["Horizontal Extent Factor"] = float(horizontal_ef.group(1)) if horizontal_ef else ""
            p["Vertical Extent Factor"] = float(vertical_ef.group(1)) if vertical_ef else ""
            p["Radial Extent Factor"] = float(radial_ef.group(1)) if radial_ef else ""
            p["PEC Launch Width"] = pec_w.group(1) if pec_w else ""
        else:
            p["HFSS Type"] = ""
            p["Orientation"] = ""
            p["Horizontal Extent Factor"] = ""
            p["Vertical Extent Factor"] = ""
            p["Radial Extent Factor"] = ""
            p["PEC Launch Width"] = ""
        return p

    @_hfss_port_property.setter
    def _hfss_port_property(self, value):
        txt = []
        for k, v in value.items():
            txt.append("'{}'='{}'".format(k, v))
        txt = ",".join(txt)
        self._edb_properties = "HFSS({})".format(txt)

    def couple_ports(self, port):
        """Create a bundle wave port.

        Parameters
        ----------
        port : :class:`Waveport <pyedb.grpc.database.ports.ports.WavePort>`,
        :class:`GapPOrt <pyedb.grpc.database.ports.ports.GapPort>`, list, optional
            Ports to be added.

        Returns
        -------
        :class:`BundleWavePort <pyedb.grpc.database.ports.ports.BundleWavePort>`
        """
        if not isinstance(port, (list, tuple)):
            port = [port]
        temp = [self]
        temp.extend([i for i in port])
        bundle_terminal = GrpcBundleTerminal.create(temp)
        return self._pedb.ports[bundle_terminal.name]

    @property
    def is_port(self):
        return True

    @property
    def ref_terminal(self):
        """Return refeference terminal.

        ..deprecated:: 0.44.0
           Use: func:`reference_terminal` property instead.

        """
        self._pedb.logger.warning("ref_terminal is deprecated, use reference_terminal property instead.")
        return self.reference_terminal

    @ref_terminal.setter
    def ref_terminal(self, value):
        self._pedb.logger.warning("ref_terminal is deprecated, use reference_terminal property instead.")
        self.reference_terminal = value

    @property
    def hfss_type(self):
        return self._hfss_type

    @hfss_type.setter
    def hfss_type(self, value):
        self._hfss_type = value

    @property
    def terminal_type(self):
        return "EdgeTerminal"

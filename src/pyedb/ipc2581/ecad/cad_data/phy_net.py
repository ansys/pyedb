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

from pyedb.generic.general_methods import ET


class PhyNet(object):
    """Class describing an IPC2581 physical net."""

    def __init__(self):
        self._name = ""
        self._phy_net_points = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):  # pragma no cover
        if isinstance(value, str):
            self._name = value

    @property
    def phy_net_points(self):
        return self._phy_net_points

    @phy_net_points.setter
    def phy_net_points(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([net for net in value if isinstance(net, PhyNetPoint)]) == len(value):
                self._phy_net_points = value

    def add_phy_net_point(self, point=None):  # pragma no cover
        if isinstance(point, PhyNetPoint):
            self._phy_net_points.append(point)

    def write_xml(self, step):  # pragma no cover
        if step:
            phy_net = ET.SubElement(step, "PhyNet")
            for phy_net_point in self.phy_net_points:
                phy_net_point.write_xml(phy_net)


class PhyNetPoint(object):
    """Class describing an IPC2581 physical net point."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.layer_ref = ""
        self.net_node_type = ""
        self._exposure = ExposureType().Exposed
        self.via = ""
        self.standard_primitive_id = ""

    @property
    def exposure(self):
        if self._exposure == ExposureType.Exposed:
            return "EXPOSED"
        elif self._exposure == ExposureType.CoveredPrimary:
            return "COVERED_PRIMARY"
        elif self._exposure == ExposureType.CoveredSecondary:
            return "COVERED_SECONDARY"

    def write_xml(self, phynet):  # pragma no cover
        if phynet:
            phynet_point = ET.SubElement(phynet, "PhyNetPoint")
            phynet_point.set("x", self.x)
            phynet_point.set("y", self.y)
            phynet_point.set("layerRef", self.layer_ref)
            phynet_point.set("netNode", self.net_node_type)
            phynet_point.set("exposure", self.exposure)
            phynet_point.set("via", self.via)
            primitive_ref = ET.SubElement(phynet_point, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primitive_id)


class NetNodeType(object):
    (Middle, End) = range(0, 2)


class ExposureType(object):
    (CoveredPrimary, CoveredSecondary, Exposed) = range(0, 3)

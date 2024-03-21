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
from pyedb.ipc2581.ecad.cad_data.drill import Drill
from pyedb.ipc2581.ecad.cad_data.padstack_instance import PadstackInstance
from pyedb.ipc2581.ecad.cad_data.path import Path
from pyedb.ipc2581.ecad.cad_data.polygon import Polygon


class Feature(object):
    """Class describing IPC2581 features."""

    def __init__(self, ipc):
        self._ipc = ipc
        self.feature_type = FeatureType().Polygon
        self.net = ""
        self.x = 0.0
        self.y = 0.0
        self.polygon = Polygon(self._ipc)
        self._cutouts = []
        self.path = Path(self._ipc)
        # self.pad = PadstackDef()
        self.padstack_instance = PadstackInstance()
        self.drill = Drill()
        # self.via = Via()

    @property
    def cutouts(self):
        return self._cutouts

    @cutouts.setter
    def cutouts(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, Polygon)]) == len(value):
                self._cutouts = value

    def add_cutout(self, cutout=None):  # pragma no cover
        if isinstance(cutout, Polygon):
            self._cutouts.append(cutout)

    def write_xml(self, layer_feature):  # pragma no cover
        net = ET.SubElement(layer_feature, "Set")
        net.set("net", self.net)
        if self.feature_type == FeatureType.Polygon:
            self.polygon.write_xml(net)
        elif self.feature_type == FeatureType.Path:
            self.path.write_xml(net)
        elif self.feature_type == FeatureType.PadstackInstance:
            net.set("net", self.padstack_instance.net)
            self.padstack_instance.write_xml(net)
        elif self.feature_type == FeatureType.Drill:
            self.drill.write_xml(net)


class FeatureType:
    (Polygon, Path, PadstackInstance, Drill) = range(0, 4)

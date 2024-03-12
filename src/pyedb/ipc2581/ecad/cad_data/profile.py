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
from pyedb.ipc2581.ecad.cad_data.layer_feature import LayerFeature


class Profile(object):
    def __init__(self, ipc):
        self._profile = []
        self._ipc = ipc

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, LayerFeature)]) == len(value):
                self._profile = value

    def add_polygon(self, polygon):  # pragma no cover
        if isinstance(polygon, LayerFeature):
            self._profile.append(polygon)

    def xml_writer(self, step):  # pragma no cover
        profile = ET.SubElement(step, "Profile")
        for poly in self.profile:
            for feature in poly.features:
                if feature.feature_type == 0:
                    polygon = ET.SubElement(profile, "Polygon")
                    polygon_begin = ET.SubElement(polygon, "PolyBegin")
                    polygon_begin.set(
                        "x", str(self._ipc.from_meter_to_units(feature.polygon.poly_steps[0].x, self._ipc.units))
                    )
                    polygon_begin.set(
                        "y", str(self._ipc.from_meter_to_units(feature.polygon.poly_steps[0].y, self._ipc.units))
                    )
                    for poly_step in feature.polygon.poly_steps[1:]:
                        poly_step.write_xml(polygon, self._ipc)
                    for cutout in feature.polygon.cutout:
                        cutout.write_xml(profile, self._ipc)

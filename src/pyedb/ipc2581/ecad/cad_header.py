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
from pyedb.ipc2581.ecad.spec import Spec


class CadHeader(object):
    """Class describing a layer stackup."""

    def __init__(self):
        self._specs = []
        self.units = ""

    @property
    def specs(self):
        return self._specs

    def add_spec(
        self, name="", material="", layer_type="", conductivity="", dielectric_constant="", loss_tg="", embedded=""
    ):  # pragma no cover
        spec = Spec()
        spec.name = name
        spec.material = material
        spec.conductivity = conductivity
        spec.dielectric_constant = dielectric_constant
        spec.layer_type = layer_type
        spec.loss_tangent = loss_tg
        spec.embedded = embedded
        self.specs.append(spec)

    def write_xml(self, ecad):  # pragma no cover
        cad_header = ET.SubElement(ecad, "CadHeader")
        cad_header.set("units", self.units)
        for spec in self.specs:
            spec.write_xml(cad_header)

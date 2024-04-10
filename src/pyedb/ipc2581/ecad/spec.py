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


class Spec(object):
    """Class describing a layer."""

    def __init__(self):
        self.name = ""
        self.material = ""
        self.layer_type = ""
        self.conductivity = ""
        self.dielectric_constant = ""
        self.loss_tangent = ""
        self.embedded = ""

    def write_xml(self, ecad_header):  # pragma no cover
        spec = ET.SubElement(ecad_header, "Spec")
        spec.set("name", self.name)
        material = ET.SubElement(spec, "General")
        material.set("type", "MATERIAL")
        material_set = ET.SubElement(material, "Property")
        material_set.set("text", self.material)
        layer_type = ET.SubElement(spec, "General")
        layer_type.set("type", "OTHER")
        layer_type.set("comment", "LAYER_TYPE")
        layer_type_set = ET.SubElement(layer_type, "Property")
        layer_type_set.set("text", self.layer_type)
        conductivity = ET.SubElement(spec, "Conductor")
        conductivity.set("type", "CONDUCTIVITY")
        conductivity_set = ET.SubElement(conductivity, "Property")
        conductivity_set.set("value", self.conductivity)
        conductivity_set.set("unit", "MHO/CM")
        dielectric = ET.SubElement(spec, "Dielectric")
        dielectric.set("type", "DIELECTRIC_CONSTANT")
        dielectric_set = ET.SubElement(dielectric, "Property")
        dielectric_set.set("value", self.dielectric_constant)
        loss_tg = ET.SubElement(spec, "Dielectric")
        loss_tg.set("type", "LOSS_TANGENT")
        loss_tg_set = ET.SubElement(loss_tg, "Property")
        loss_tg_set.set("value", self.loss_tangent)
        if self.layer_type == "CONDUCTOR":
            embedded = ET.SubElement(spec, "General")
            embedded.set("type", "OTHER")
            embedded.set("comment", "LAYER_EMBEDDED_STATUS")
            embedded_set = ET.SubElement(embedded, "Property")
            embedded_set.set("text", self.embedded)

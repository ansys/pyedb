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
from pyedb.ipc2581.content.dictionary_color import DictionaryColor
from pyedb.ipc2581.content.dictionary_line import DictionaryLine
from pyedb.ipc2581.content.layer_ref import LayerRef
from pyedb.ipc2581.content.standard_geometries_dictionary import (
    StandardGeometriesDictionary,
)


class Content(object):
    def __init__(self, ipc):
        self.mode = self.Mode().Stackup
        self.units = ipc.units
        self.role_ref = "Owner"
        self.function_mode = self.Mode().Stackup
        self.step_ref = "Ansys_IPC2581"
        self._layer_ref = []
        self.dict_colors = DictionaryColor()
        self.dict_line = DictionaryLine(self)
        self.standard_geometries_dict = StandardGeometriesDictionary(self)

    @property
    def layer_ref(self):
        return self._layer_ref

    @layer_ref.setter
    def layer_ref(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([lay for lay in value if isinstance(lay, LayerRef)]) == len(value):
                self._layer_ref = value

    def add_layer_ref(self, layer_ref_name=None):  # pragma no cover
        if isinstance(layer_ref_name, str):
            layer_ref = LayerRef()
            layer_ref.name = layer_ref_name
            self._layer_ref.append(layer_ref)

    def write_wml(self, root=None):  # pragma no cover
        content = ET.SubElement(root, "Content")
        content.set("roleRef", "Owner")
        if self.mode == self.Mode.Stackup:
            function_mode = ET.SubElement(content, "FunctionMode")
            function_mode.set("mode", "USERDEF")
        step_ref = ET.SubElement(content, "StepRef")
        step_ref.set("name", self.step_ref)
        for lay in self.layer_ref:
            lay.write_xml(content)
        self.dict_colors.write_xml(content)
        self.dict_line.write_xml(content)
        self.standard_geometries_dict.write_xml(content)

        # skipping user defined geometries

    class Mode(object):
        (Stackup) = range(1)

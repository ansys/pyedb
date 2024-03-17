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

from dataclasses import dataclass


@dataclass
class CellShapes:
    polygons: list
    paths: list
    texts: list
    boxes: list


class ICLayoutData:
    def __init__(self, klayout, layers):
        self._klayout = klayout
        self._layers = layers

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, value):
        if isinstance(value, list):
            self._layers = value


class ICLayerData:
    def __init__(self, klayout, name, index, data_type):
        self._klayout = klayout
        self._name = name
        self._index = index
        self._data_type = data_type
        self._shapes = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            info = self._klayout.get_info(self.index)
            info.name = value
            self._klayout.set_info(self.index, info)
            self._name = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if isinstance(value, int):
            info = self._klayout.get_info(self.index)
            info.layer = value
            self._klayout.set_info(self.index, info)
            self._index = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if isinstance(value, int):
            info = self._klayout.get_info(self.index)
            info.data_type = value
            self._klayout.set_info(self.index, info)
            self._data_type = value

    @property
    def shapes(self):
        if not self._shapes:
            self._update_shapes()
        return self._shapes

    def _update_shapes(self):
        self._shapes = {}
        top_cells = [cell for cell in self._klayout.top_cells()]
        for kcell in top_cells:
            cell = CellShapes(polygons=[], paths=[], texts=[], boxes=[])
            if not kcell.name in self._shapes:
                self._shapes[kcell.name] = cell
            for layer_id in self._klayout.layer_indexes():
                shape_list = kcell.shapes(layer_id)
                for shape in shape_list.each():
                    if shape.is_polygon():
                        cell.polygons.append(shape)
                    elif shape.is_path():
                        cell.paths.append(shape)
                    elif shape.is_text():
                        cell.texts.append(shape)
                    elif shape.is_box():
                        cell.boxes.append(shape)

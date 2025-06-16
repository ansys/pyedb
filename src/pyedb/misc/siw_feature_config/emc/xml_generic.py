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

from pyedb.generic.general_methods import ET


class XmlGeneric:
    DEBUG = False
    CLS_MAPPING = {}

    def __init__(self, element):
        self._element = element
        self._cls_sub_element = None
        self.sub_elements = []

    def add_sub_element(self, kwargs, elem_type):
        self._cls_sub_element = self.CLS_MAPPING[elem_type]
        obj = self._cls_sub_element(None)
        self.sub_elements.append(obj.create(kwargs))

    def create(self, kwargs):
        for attrib, value in kwargs.items():
            if attrib in self.__dict__.keys():
                if not isinstance(value, list):
                    self.__setattr__(attrib, value)
                else:
                    for i in value:
                        kwargs = list(i.values())[0]
                        item_type = list(i.keys())[0]
                        self.add_sub_element(kwargs, item_type)
        return self

    def write_xml(self, parent):
        elem = ET.SubElement(parent, self.__class__.__name__)
        for attrib, value in self.__dict__.items():
            if attrib.startswith("_"):
                continue
            elif attrib.isupper():
                continue
            elif value is None:
                continue
            elif isinstance(value, list):
                if len(value) == 0:
                    continue
                for i in value:
                    i.write_xml(elem)
            elif isinstance(value, str):
                elem.set(attrib, value)
            else:
                raise Exception(f"{value} is Illegal")
        return parent

    def write_dict(self, parent):
        temp = {}
        for attrib, value in self.__dict__.items():
            if attrib.startswith("_"):
                continue
            elif value is None:
                continue

            if isinstance(value, list):
                if len(value) == 0:
                    continue
                new_list = []
                for i in value:
                    parent_2 = {}
                    i.write_dict(parent_2)
                    new_list.append(parent_2)
                temp[attrib] = new_list
            else:
                temp[attrib] = value

        parent[self.__class__.__name__] = temp

    def read_dict(self, data):
        for i in data["sub_elements"]:
            elem_type = list(i.keys())[0]
            kwargs = list(i.values())[0]
            obj = self.CLS_MAPPING[elem_type](None)
            self.sub_elements.append(obj.create(kwargs))

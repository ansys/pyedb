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

from pyedb.misc.siw_feature_config.emc.xml_generic import XmlGeneric


class Net(XmlGeneric):
    """Manages net."""

    def __init__(self, element=None):
        super().__init__(element)

        if element is not None:
            self.isBus = self._element.attrib["isBus"]
            self.isClock = self._element.attrib["isClock"]
            self.isCritical = self._element.attrib["isCritical"]
            self.name = self._element.attrib["name"]
            self.type = self._element.attrib["type"] if "type" in self._element.attrib else None
            self.Diffmatename = self._element.attrib["Diffmatename"] if "Diffmatename" in self._element.attrib else None
        else:
            self.isBus = None
            self.isClock = None
            self.isCritical = None
            self.name = None
            self.type = None
            self.Diffmatename = None


class NetTags(XmlGeneric):
    """Manages net tag."""

    CLS_MAPPING = {"Net": Net}

    def __init__(self, element):
        super().__init__(element)

        if element:
            for el in self._element.findall("Net"):
                net = Net(el)
                self.sub_elements.append(net)

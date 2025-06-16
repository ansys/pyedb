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


class Comp(XmlGeneric):
    """Manages component tags."""

    def __init__(self, element):
        super().__init__(element)
        if element is not None:
            self.CompName = self._element.attrib["CompName"]
            self.CompValue = self._element.attrib["CompValue"]
            self.DeviceName = self._element.attrib["DeviceName"]
            self.capType = self._element.attrib["capType"] if "capType" in self._element.attrib else None
            self.isClockDriver = self._element.attrib["isClockDriver"]
            self.isHighSpeed = self._element.attrib["isHighSpeed"]
            self.isIC = self._element.attrib["isIC"]
            self.isOscillator = self._element.attrib["isOscillator"]
            self.xLoc = self._element.attrib["xLoc"]
            self.yLoc = self._element.attrib["yLoc"]
        else:
            self.CompName = None
            self.CompValue = None
            self.DeviceName = None
            self.capType = None
            self.isClockDriver = None
            self.isHighSpeed = None
            self.isIC = None
            self.isOscillator = None
            self.xLoc = None
            self.yLoc = None


class ComponentTags(XmlGeneric):
    """Manages component tags."""

    CLS_MAPPING = {"Comp": Comp}

    def __init__(self, element):
        super().__init__(element)

        if element:
            for el in self._element.findall("Comp"):
                comp = Comp(el)
                self.sub_elements.append(comp)

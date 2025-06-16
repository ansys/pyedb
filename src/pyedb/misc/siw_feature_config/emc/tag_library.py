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


class TagType(XmlGeneric):
    """Manages tag type."""

    def __init__(self, element):
        super().__init__(element)

        if element is not None:
            self.name = self._element.attrib["name"]
        else:
            self.name = None


class TagConfig(XmlGeneric):
    """Manages tag config."""

    def __init__(self, element):
        super().__init__(element)


class Tag(XmlGeneric):
    """Manages tag."""

    CLS_MAPPING = {"TagType": TagType, "TagConfig": TagConfig}

    def __init__(self, element):
        super().__init__(element)

        if element is not None:
            self.label = self._element.attrib["label"]
            self.name = self._element.attrib["name"]
            self.sub_elements = []

            for el in self._element.findall("TagType"):
                temp = TagType(el)
                self.sub_elements.append(temp)

            for el in self._element.findall("TagConfig"):
                temp = TagConfig(el)
                self.sub_elements.append(temp)
        else:
            self.label = None
            self.name = None
            self.sub_elements = []


class TagLibrary(XmlGeneric):
    """Manages tag library."""

    CLS_MAPPING = {
        "Tag": Tag,
    }

    def __init__(self, element):
        super().__init__(element)
        self._element = element

        if element:
            for el in self._element.findall("Tag"):
                tag = Tag(el)
                self.sub_elements.append(tag)

# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
    """
    Manages tag type configuration.

    This class handles individual tag type definitions within the tag library.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.tag_library import TagType
    >>> tag_type = TagType(None)
    >>> tag_type.name = "ClockNet"

    """

    def __init__(self, element) -> None:
        """
        Initialize tag type.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)

        if element is not None:
            self.name: str = self._element.attrib["name"]
        else:
            self.name: str | None = None


class TagConfig(XmlGeneric):
    """
    Manages tag configuration settings.

    This class handles configuration parameters for tags within the tag library.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.tag_library import TagConfig
    >>> tag_config = TagConfig(None)

    """

    def __init__(self, element) -> None:
        """
        Initialize tag configuration.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)


class Tag(XmlGeneric):
    """
    Manages individual tags with their types and configurations.

    This class represents a complete tag with its associated tag types and configurations.

    Attributes
    ----------
    CLS_MAPPING : dict
        Mapping of element types to their corresponding classes.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.tag_library import Tag
    >>> tag = Tag(None)
    >>> tag.label = "Clock"
    >>> tag.name = "CLK_TAG"

    """

    CLS_MAPPING: dict = {"TagType": TagType, "TagConfig": TagConfig}

    def __init__(self, element) -> None:
        """
        Initialize tag.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)

        if element is not None:
            self.label: str = self._element.attrib["label"]
            self.name: str = self._element.attrib["name"]
            self.sub_elements: list = []

            for el in self._element.findall("TagType"):
                temp = TagType(el)
                self.sub_elements.append(temp)

            for el in self._element.findall("TagConfig"):
                temp = TagConfig(el)
                self.sub_elements.append(temp)
        else:
            self.label: str | None = None
            self.name: str | None = None
            self.sub_elements: list = []


class TagLibrary(XmlGeneric):
    """
    Manages the complete tag library collection.

    This class handles the top-level tag library containing all tag definitions
    with their types and configurations.

    Attributes
    ----------
    CLS_MAPPING : dict
        Mapping of element types to their corresponding classes.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.tag_library import TagLibrary
    >>> tag_library = TagLibrary(None)
    >>> # Tag library ready to use

    """

    CLS_MAPPING: dict = {
        "Tag": Tag,
    }

    def __init__(self, element) -> None:
        """
        Initialize tag library.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)
        self._element = element

        if element:
            for el in self._element.findall("Tag"):
                tag = Tag(el)
                self.sub_elements.append(tag)

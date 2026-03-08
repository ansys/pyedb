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


class Net(XmlGeneric):
    """Manages individual net configuration and properties.

    This class handles net-specific attributes including bus status, clock signals,
    criticality, and differential pair configurations.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None, optional
        XML element to initialize from.
        The default is ``None``.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.net_tags import Net
    >>> net = Net()
    >>> net.name = "DDR_DQ0"
    >>> net.isClock = "0"
    >>> net.isBus = "1"
    >>> net.isCritical = "1"
    >>> net.type = "Single-Ended"

    """

    def __init__(self, element=None) -> None:
        """Initialize net configuration.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None, optional
            XML element to initialize from.
            The default is ``None``.

        """
        super().__init__(element)

        if element is not None:
            self.isBus: str = self._element.attrib["isBus"]
            self.isClock: str = self._element.attrib["isClock"]
            self.isCritical: str = self._element.attrib["isCritical"]
            self.name: str = self._element.attrib["name"]
            self.type: str | None = self._element.attrib["type"] if "type" in self._element.attrib else None
            self.Diffmatename: str | None = (
                self._element.attrib["Diffmatename"] if "Diffmatename" in self._element.attrib else None
            )
        else:
            self.isBus: str | None = None
            self.isClock: str | None = None
            self.isCritical: str | None = None
            self.name: str | None = None
            self.type: str | None = None
            self.Diffmatename: str | None = None


class NetTags(XmlGeneric):
    """Manages collection of net tags.

    This class handles the complete collection of net configurations, providing
    a container for multiple Net objects within the EMC configuration.

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
    >>> from pyedb.misc.siw_feature_config.emc.net_tags import NetTags
    >>> net_tags = NetTags(None)
    >>> # NetTags ready to store multiple Net objects

    """

    CLS_MAPPING: dict = {"Net": Net}

    def __init__(self, element) -> None:
        """Initialize net tags collection.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)

        if element:
            for el in self._element.findall("Net"):
                net = Net(el)
                self.sub_elements.append(net)

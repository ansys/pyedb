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


class Comp(XmlGeneric):
    """
    Manages individual component configuration and properties.

    This class handles component-specific attributes including component name, value,
    device type, capacitor type, and physical location information. It also tracks
    component characteristics such as clock driver, high-speed, IC, and oscillator status.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.component_tags import Comp
    >>> comp = Comp(None)
    >>> comp.CompName = "U1"
    >>> comp.CompValue = "FPGA"
    >>> comp.DeviceName = "XC7A35T"
    >>> comp.isIC = "1"
    >>> comp.isHighSpeed = "1"
    >>> comp.xLoc = "10.5"
    >>> comp.yLoc = "20.3"

    """

    def __init__(self, element) -> None:
        """
        Initialize component configuration.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)
        if element is not None:
            self.CompName: str = self._element.attrib["CompName"]
            self.CompValue: str = self._element.attrib["CompValue"]
            self.DeviceName: str = self._element.attrib["DeviceName"]
            self.capType: str | None = self._element.attrib["capType"] if "capType" in self._element.attrib else None
            self.isClockDriver: str = self._element.attrib["isClockDriver"]
            self.isHighSpeed: str = self._element.attrib["isHighSpeed"]
            self.isIC: str = self._element.attrib["isIC"]
            self.isOscillator: str = self._element.attrib["isOscillator"]
            self.xLoc: str = self._element.attrib["xLoc"]
            self.yLoc: str = self._element.attrib["yLoc"]
        else:
            self.CompName: str | None = None
            self.CompValue: str | None = None
            self.DeviceName: str | None = None
            self.capType: str | None = None
            self.isClockDriver: str | None = None
            self.isHighSpeed: str | None = None
            self.isIC: str | None = None
            self.isOscillator: str | None = None
            self.xLoc: str | None = None
            self.yLoc: str | None = None


class ComponentTags(XmlGeneric):
    """
    Manages collection of component tags.

    This class handles the complete collection of component configurations, providing
    a container for multiple Comp objects within the EMC configuration. It serves as
    the top-level container for all component-related tag information.

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
    >>> from pyedb.misc.siw_feature_config.emc.component_tags import ComponentTags
    >>> component_tags = ComponentTags(None)
    >>> # ComponentTags ready to store multiple Comp objects

    """

    CLS_MAPPING: dict = {"Comp": Comp}

    def __init__(self, element) -> None:
        """
        Initialize component tags collection.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        super().__init__(element)

        if element:
            for el in self._element.findall("Comp"):
                comp = Comp(el)
                self.sub_elements.append(comp)

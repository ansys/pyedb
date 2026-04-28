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

from pyedb.generic.general_methods import ET


class XmlGeneric:
    """
    Generic XML handler for EMC configuration.

    This class provides a generic interface for creating, reading, and writing
    XML configurations. It supports nested elements and automatic attribute mapping.

    Attributes
    ----------
    DEBUG : bool
        Debug flag for additional logging.
    CLS_MAPPING : dict
        Mapping of element types to their corresponding classes.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element or None
        XML element to initialize from.

    Examples
    --------
    >>> from pyedb.misc.siw_feature_config.emc.xml_generic import XmlGeneric
    >>> element = None
    >>> xml_obj = XmlGeneric(element)
    >>> kwargs = {"name": "test", "value": "123"}
    >>> xml_obj.create(kwargs)

    """

    DEBUG: bool = False
    CLS_MAPPING: dict = {}

    def __init__(self, element) -> None:
        """
        Initialize XML generic handler.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            XML element to initialize from.

        """
        self._element = element
        self._cls_sub_element = None
        self.sub_elements: list = []

    def add_sub_element(self, kwargs: dict, elem_type: str) -> None:
        """
        Add a sub-element to the XML structure.

        Parameters
        ----------
        kwargs : dict
            Dictionary of keyword arguments for the sub-element.
        elem_type : str
            Type of the element to add.

        Examples
        --------
        >>> xml_obj = XmlGeneric(None)
        >>> kwargs = {"name": "component1", "value": "100"}
        >>> xml_obj.add_sub_element(kwargs, "Component")

        """
        self._cls_sub_element = self.CLS_MAPPING[elem_type]
        obj = self._cls_sub_element(None)
        self.sub_elements.append(obj.create(kwargs))

    def create(self, kwargs: dict):
        """
        Create XML object from keyword arguments.

        Parameters
        ----------
        kwargs : dict
            Dictionary of keyword arguments to populate the object.

        Returns
        -------
        XmlGeneric
            Self reference for method chaining.

        Examples
        --------
        >>> xml_obj = XmlGeneric(None)
        >>> kwargs = {"name": "net1", "impedance": "50"}
        >>> xml_obj.create(kwargs)

        """
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
        """
        Write object to XML element tree.

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            Parent XML element to write to.

        Returns
        -------
        xml.etree.ElementTree.Element
            Parent element with added content.

        Examples
        --------
        >>> import xml.etree.ElementTree as ET
        >>> parent = ET.Element("Root")
        >>> xml_obj = XmlGeneric(None)
        >>> xml_obj.write_xml(parent)

        """
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

    def write_dict(self, parent: dict) -> None:
        """
        Write object to dictionary format.

        Parameters
        ----------
        parent : dict
            Parent dictionary to write to.

        Examples
        --------
        >>> xml_obj = XmlGeneric(None)
        >>> output = {}
        >>> xml_obj.write_dict(output)
        >>> print(output)

        """
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

    def read_dict(self, data: dict) -> None:
        """
        Read object from dictionary format.

        Parameters
        ----------
        data : dict
            Dictionary containing configuration data.

        Examples
        --------
        >>> xml_obj = XmlGeneric(None)
        >>> data = {"sub_elements": [{"Component": {"name": "C1", "value": "10uF"}}]}
        >>> xml_obj.read_dict(data)

        """
        for i in data["sub_elements"]:
            elem_type = list(i.keys())[0]
            kwargs = list(i.values())[0]
            obj = self.CLS_MAPPING[elem_type](None)
            self.sub_elements.append(obj.create(kwargs))

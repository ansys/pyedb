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

"""XML parser module for handling EDB XML configuration files."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
import xmltodict

from pyedb.xml_parser.xml_stackup import XmlStackup


class XmlNet(BaseModel):
    """Represents a net configuration in the XML file.

    Parameters
    ----------
    name : str
        Name of the net.
    pins_become_ports : bool, optional
        Whether pins in this net should become ports. The default is ``None``.
    """

    name: str = Field(alias="@Name")
    pins_become_ports: Optional[bool] = Field(None, alias="@PinsBecomePorts")

    model_config = dict(populate_by_name=True)


class XmlImportOptions(BaseModel):
    """Represents import options for the XML configuration.

    Parameters
    ----------
    enable_default_component_values : bool, optional
        Whether to enable default component values during import. The default is ``None``.
    flatten : bool, optional
        Whether to flatten the design hierarchy during import. The default is ``None``.
    """

    enable_default_component_values: Optional[bool] = Field(None, alias="EnableDefaultComponentValues")
    flatten: Optional[bool] = Field(None, alias="Flatten")

    model_config = dict(populate_by_name=True)


class XmlParser(BaseModel):
    """Main parser for EDB XML configuration files.

    This class provides methods to load, parse, and export XML configuration files
    used in EDB designs. It supports stackup definitions, import options, and net
    configurations.

    Parameters
    ----------
    stackup : XmlStackup, optional
        Stackup configuration object. The default is ``None``.
    import_options : XmlImportOptions, optional
        Import options configuration. The default is ``None``.
    nets : dict, optional
        Dictionary of net configurations. The default is ``None``.
    schema_version : str, optional
        Version of the XML schema. The default is ``None``.

    Examples
    --------
    >>> from pyedb.xml_parser.xml_parser import XmlParser
    >>> parser = XmlParser.load_xml_file("config.xml")
    >>> parser.to_xml_file("output.xml")
    """

    stackup: Optional[XmlStackup] = Field(default=None, alias="Stackup")
    import_options: Optional[XmlImportOptions] = Field(default=None, alias="ImportOptions")
    nets: Optional[dict] = Field(default=None, alias="Nets")
    schema_version: Optional[str] = Field(default=None, alias="schemaVersion")

    model_config = dict(populate_by_name=True)

    def add_stackup(self) -> XmlStackup:
        """Add a stackup configuration to the parser.

        Returns
        -------
        XmlStackup
            The newly created stackup object.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_parser import XmlParser
        >>> parser = XmlParser()
        >>> stackup = parser.add_stackup()
        """
        self.stackup = XmlStackup()
        return self.stackup

    @classmethod
    def load_xml_file(cls, path: str | Path) -> "XmlParser":
        """Load and parse an XML configuration file.

        Parameters
        ----------
        path : str or pathlib.Path
            Path to the XML file to load.

        Returns
        -------
        XmlParser
            The parsed XML configuration as an XmlParser instance.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_parser import XmlParser
        >>> parser = XmlParser.load_xml_file("config.xml")
        >>> print(parser.stackup)
        """
        with open(path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        data_dict = xmltodict.parse(xml_data)

        control_dict = list(data_dict.values())[0]

        return cls.model_validate(control_dict)

    def to_xml(self, root_name: str = "c:Control", pretty: bool = True) -> str:
        """Convert the parser configuration to XML string.

        Parameters
        ----------
        root_name : str, optional
            Name of the root XML tag. The default is ``"c:Control"``.
        pretty : bool, optional
            Whether to format the XML output with indentation. The default is ``True``.

        Returns
        -------
        str
            XML string representation of the configuration.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_parser import XmlParser
        >>> parser = XmlParser()
        >>> xml_string = parser.to_xml()
        """
        root = self.model_dump(by_alias=True, exclude_none=True)

        # Ensure the desired root tag attributes exist
        root["@xmlns:c"] = "http://www.ansys.com/control"
        root.setdefault("@schemaVersion", "1.0")
        stackup = root.get("Stackup")
        stackup.setdefault("@schemaVersion", "1.0")

        d = {root_name: root}
        return xmltodict.unparse(d, pretty=pretty)

    def to_xml_file(self, file_path: str | Path) -> str:
        """Write the parser configuration to an XML file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            Path to the output XML file.

        Returns
        -------
        str
            Path to the written XML file.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_parser import XmlParser
        >>> parser = XmlParser()
        >>> output_path = parser.to_xml_file("output.xml")
        """
        xml_out = self.to_xml()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_out)
        return str(file_path)

    def to_dict(self) -> dict:
        """Convert the parser configuration to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the configuration containing stackup information.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_parser import XmlParser
        >>> parser = XmlParser()
        >>> config_dict = parser.to_dict()
        """
        stackup_dict = self.stackup.to_dict()
        return {"stackup": stackup_dict}

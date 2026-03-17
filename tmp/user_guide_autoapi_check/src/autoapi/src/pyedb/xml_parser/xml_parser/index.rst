src.pyedb.xml_parser.xml_parser
===============================

.. py:module:: src.pyedb.xml_parser.xml_parser

.. autoapi-nested-parse::

   XML parser module for handling EDB XML configuration files.



Classes
-------

.. autoapisummary::

   src.pyedb.xml_parser.xml_parser.XmlNet
   src.pyedb.xml_parser.xml_parser.XmlImportOptions
   src.pyedb.xml_parser.xml_parser.XmlParser


Module Contents
---------------

.. py:class:: XmlNet(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a net configuration in the XML file.

   Parameters
   ----------
   name : str
       Name of the net.
   pins_become_ports : bool, optional
       Whether pins in this net should become ports. The default is ``None``.


   .. py:attribute:: name
      :type:  str
      :value: None



   .. py:attribute:: pins_become_ports
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: XmlImportOptions(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents import options for the XML configuration.

   Parameters
   ----------
   enable_default_component_values : bool, optional
       Whether to enable default component values during import. The default is ``None``.
   flatten : bool, optional
       Whether to flatten the design hierarchy during import. The default is ``None``.


   .. py:attribute:: enable_default_component_values
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: flatten
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: XmlParser(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Main parser for EDB XML configuration files.

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


   .. py:attribute:: stackup
      :type:  Optional[pyedb.xml_parser.xml_stackup.XmlStackup]
      :value: None



   .. py:attribute:: import_options
      :type:  Optional[XmlImportOptions]
      :value: None



   .. py:attribute:: nets
      :type:  Optional[dict]
      :value: None



   .. py:attribute:: schema_version
      :type:  Optional[str]
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:method:: add_stackup() -> pyedb.xml_parser.xml_stackup.XmlStackup

      Add a stackup configuration to the parser.

      Returns
      -------
      XmlStackup
          The newly created stackup object.

      Examples
      --------
      >>> from pyedb.xml_parser.xml_parser import XmlParser
      >>> parser = XmlParser()
      >>> stackup = parser.add_stackup()



   .. py:method:: load_xml_file(path: str | pathlib.Path) -> XmlParser
      :classmethod:


      Load and parse an XML configuration file.

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



   .. py:method:: to_xml(root_name: str = 'c:Control', pretty: bool = True) -> str

      Convert the parser configuration to XML string.

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



   .. py:method:: to_xml_file(file_path: str | pathlib.Path) -> str

      Write the parser configuration to an XML file.

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



   .. py:method:: to_dict() -> dict

      Convert the parser configuration to a dictionary.

      Returns
      -------
      dict
          Dictionary representation of the configuration containing stackup information.

      Examples
      --------
      >>> from pyedb.xml_parser.xml_parser import XmlParser
      >>> parser = XmlParser()
      >>> config_dict = parser.to_dict()




src.pyedb.misc.siw_feature_config.emc.xml_generic
=================================================

.. py:module:: src.pyedb.misc.siw_feature_config.emc.xml_generic


Classes
-------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric


Module Contents
---------------

.. py:class:: XmlGeneric(element)

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



   .. py:attribute:: DEBUG
      :type:  bool
      :value: False



   .. py:attribute:: CLS_MAPPING
      :type:  dict


   .. py:attribute:: sub_elements
      :type:  list
      :value: []



   .. py:method:: add_sub_element(kwargs: dict, elem_type: str) -> None

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




   .. py:method:: create(kwargs: dict)

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




   .. py:method:: write_xml(parent)

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




   .. py:method:: write_dict(parent: dict) -> None

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




   .. py:method:: read_dict(data: dict) -> None

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





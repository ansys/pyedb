src.pyedb.misc.siw_feature_config.emc.tag_library
=================================================

.. py:module:: src.pyedb.misc.siw_feature_config.emc.tag_library


Classes
-------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc.tag_library.TagType
   src.pyedb.misc.siw_feature_config.emc.tag_library.TagConfig
   src.pyedb.misc.siw_feature_config.emc.tag_library.Tag
   src.pyedb.misc.siw_feature_config.emc.tag_library.TagLibrary


Module Contents
---------------

.. py:class:: TagType(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



.. py:class:: TagConfig(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



.. py:class:: Tag(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



   .. py:attribute:: CLS_MAPPING
      :type:  dict


.. py:class:: TagLibrary(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



   .. py:attribute:: CLS_MAPPING
      :type:  dict



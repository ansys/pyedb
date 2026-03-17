src.pyedb.misc.siw_feature_config.emc.net_tags
==============================================

.. py:module:: src.pyedb.misc.siw_feature_config.emc.net_tags


Classes
-------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc.net_tags.Net
   src.pyedb.misc.siw_feature_config.emc.net_tags.NetTags


Module Contents
---------------

.. py:class:: Net(element=None)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


   Manages individual net configuration and properties.

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



.. py:class:: NetTags(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


   Manages collection of net tags.

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



   .. py:attribute:: CLS_MAPPING
      :type:  dict



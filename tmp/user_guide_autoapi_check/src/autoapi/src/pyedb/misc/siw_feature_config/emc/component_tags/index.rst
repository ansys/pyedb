src.pyedb.misc.siw_feature_config.emc.component_tags
====================================================

.. py:module:: src.pyedb.misc.siw_feature_config.emc.component_tags


Classes
-------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc.component_tags.Comp
   src.pyedb.misc.siw_feature_config.emc.component_tags.ComponentTags


Module Contents
---------------

.. py:class:: Comp(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



.. py:class:: ComponentTags(element)

   Bases: :py:obj:`pyedb.misc.siw_feature_config.emc.xml_generic.XmlGeneric`


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



   .. py:attribute:: CLS_MAPPING
      :type:  dict



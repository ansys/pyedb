import xml.etree.ElementTree as ET

from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.tag_library import TagLibrary
from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.net_tags import NetTags
from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.component_tags import ComponentTags


class SIWEMIScannerTags:
    def __init__(self):
        self.tag_library = ""
        self.net_tags = ""
        self.component_tags = ""

    def read_xml(self):
        tree = ET.parse(r"D:\to_delete\emi_scanner_tags.xml")

        root = tree.getroot()

        self.tag_library = TagLibrary(root.find("TagLibrary"))
        self.net_tags = NetTags(root.find("NetTags"))
        self.component_tags = ComponentTags(root.find("ComponentTags"))


emi_scanner = SIWEMIScannerTags()
emi_scanner.read_xml()

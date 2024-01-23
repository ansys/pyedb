import json
import xml.etree.ElementTree as ET

from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.tag_library import TagLibrary
from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.net_tags import NetTags
from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.component_tags import ComponentTags
from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.xml_generic import XmlGeneric


class SIWEMIScannerTags:
    def __init__(self):
        self.version = "1.0"
        self.encoding = "UTF-8"
        self.standalone = "no"

        self.tag_library = TagLibrary(None)
        self.net_tags = NetTags(None)
        self.component_tags = ComponentTags(None)

    def read_xml(self, fpath):
        tree = ET.parse(fpath)
        root = tree.getroot()

        self.tag_library = self.tag_library.read_element(root.find("TagLibrary"))
        self.net_tags = self.net_tags.read_element(root.find("NetTags"))
        self.component_tags = self.component_tags.read_element(root.find("ComponentTags"))

    def write_xml(self, fpath):
        root = ET.Element("EMCRuleCheckerSettings")

        if self.tag_library:
            self.tag_library.write_xml(root)
        if self.net_tags:
            self.net_tags.write_xml(root)
        if self.component_tags:
            self.component_tags.write_xml(root)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        tree.write(fpath, encoding=self.encoding, xml_declaration=True)

    def write_json(self, fpath):
        data = {}
        self.tag_library.write_dict(data)
        self.net_tags.write_dict(data)
        self.component_tags.write_dict(data)

        with open(fpath, "w") as f:
            json.dump(data, f, indent=4)

    def read_json(self, fpath):
        self.tag_library = TagLibrary(None)
        self.net_tags = NetTags(None)
        self.component_tags = ComponentTags(None)

        with open(fpath) as f:
            data = json.load(f)

        tag_library = data["TagLibrary"] if "TagLibrary" in data else None
        if tag_library:
            self.tag_library.read_dict(tag_library)

        net_tags = data["NetTags"] if "NetTags" in data else None
        if net_tags:
            self.net_tags.read_dict(net_tags)

        component_tags = data["ComponentTags"] if "ComponentTags" in data else None
        if component_tags:
            self.component_tags.read_dict(component_tags)


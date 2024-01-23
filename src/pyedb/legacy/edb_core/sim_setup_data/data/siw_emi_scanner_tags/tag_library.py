from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.xml_generic import XmlGeneric


class TagType(XmlGeneric):
    def __init__(self, element):
        self._element = element

        if element is not None:
            self.name = self._element.attrib["name"]
        else:
            self.name = None


class TagConfig(XmlGeneric):
    def __init__(self, element):
        self._element = element


class Tag(XmlGeneric):
    def __init__(self, element):
        self._element = element

        if element is not None:
            self.label = self._element.attrib["label"]
            self.name = self._element.attrib["name"]
            self.tag_type = []

            for el in self._element.findall("TagType"):
                temp = TagType(el)
                self.tag_type.append(temp)

            for el in self._element.findall("TagConfig"):
                temp = TagConfig(el)
                self.tag_type.append(temp)
        else:
            self.label = None
            self.name = None
            self.tag_type = []

    def add_items(self, item_type, kwargs):
        if item_type == "TagType":
            temp = TagType(None)
            self.tag_type.append(temp.create(kwargs))
        elif item_type == "TagConfig":
            temp = TagConfig(None)
            self.tag_type.append(temp.create(kwargs))


class TagLibrary(XmlGeneric):
    def __init__(self, element):
        self._element = element
        self.tags = []

        if element:
            for el in self._element.findall("Tag"):
                tag = Tag(el)
                self.tags.append(tag)

    @staticmethod
    def read_element(element):
        return TagLibrary(element)

    def read_dict(self, data):
        for i in data["tags"]:
            tag = Tag(None)
            self.tags.append(tag.create(i["Tag"]))


class TagType:
    def __init__(self, element):
        self._element = element
        self.name = self._element.attrib["name"]


class TagConfig:
    def __init__(self, element):
        self._element = element


class Tag:
    def __init__(self, element):
        self._element = element
        self.label = self._element.attrib["label"]
        self.name = self._element.attrib["name"]
        self._tag_type = TagType(self._element.find("TagType"))
        self._tag_config = TagConfig(self._element.find("TagConfig"))

    @property
    def tag_type(self):
        return self._tag_type

    @property
    def tag_config(self):
        return self._tag_config


class TagLibrary:
    def __init__(self, element):
        self._element = element
        self._tags = []

        for el in self._element.findall("Tag"):
            tag = Tag(el)
            self.tags.append(tag)

    @property
    def tags(self):
        return self._tags

    def write_to_xml(self):
        pass

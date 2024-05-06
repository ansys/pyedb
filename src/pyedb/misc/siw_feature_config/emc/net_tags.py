from pyedb.misc.siw_feature_config.emc.xml_generic import XmlGeneric


class Net(XmlGeneric):
    """Manages net."""

    def __init__(self, element=None):
        super().__init__(element)

        if element is not None:
            self.isBus = self._element.attrib["isBus"]
            self.isClock = self._element.attrib["isClock"]
            self.isCritical = self._element.attrib["isCritical"]
            self.name = self._element.attrib["name"]
            self.type = self._element.attrib["type"] if "type" in self._element.attrib else None
            self.Diffmatename = self._element.attrib["Diffmatename"] if "Diffmatename" in self._element.attrib else None
        else:
            self.isBus = None
            self.isClock = None
            self.isCritical = None
            self.name = None
            self.type = None
            self.Diffmatename = None


class NetTags(XmlGeneric):
    """Manages net tag."""

    CLS_MAPPING = {"Net": Net}

    def __init__(self, element):
        super().__init__(element)

        if element:
            for el in self._element.findall("Net"):
                net = Net(el)
                self.sub_elements.append(net)

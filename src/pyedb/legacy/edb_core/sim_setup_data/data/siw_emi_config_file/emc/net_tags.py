from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_config_file.emc.xml_generic import XmlGeneric


class Net(XmlGeneric):
    def __init__(self, element=None):
        super().__init__(element)

        if element is not None:
            self.isBus = self._element.attrib["isBus"]
            self.isClock = self._element.attrib["isClock"]
            self.isCritical = self._element.attrib["isCritical"]
            self.name = self._element.attrib["name"]
            self.type = self._element.attrib["type"] if "type" in self._element.attrib else None
        else:
            self.isBus = None
            self.isClock = None
            self.isCritical = None
            self.name = None
            self.type = None


class NetTags(XmlGeneric):
    CLS_MAPPING = {
        "Net": Net
    }

    def __init__(self, element):
        super().__init__(element)

        if element:
            for el in self._element.findall("Net"):
                net = Net(el)
                self.sub_elements.append(net)

    @staticmethod
    def read_element(element):
        return NetTags(element)

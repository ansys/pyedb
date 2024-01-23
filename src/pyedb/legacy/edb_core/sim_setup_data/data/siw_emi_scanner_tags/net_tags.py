from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.xml_generic import XmlGeneric


class Net(XmlGeneric):
    def __init__(self, element):
        self._element = element

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
    def __init__(self, element):
        self._element = element
        self.nets = []

        if element:
            for el in self._element.findall("Net"):
                net = Net(el)
                self.nets.append(net)

    @staticmethod
    def read_element(element):
        return NetTags(element)

    def read_dict(self, data):
        for i in data["nets"]:
            net = Net(None)
            self.nets.append(net.create(i["Net"]))

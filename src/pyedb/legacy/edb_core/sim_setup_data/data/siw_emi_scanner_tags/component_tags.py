from pyedb.legacy.edb_core.sim_setup_data.data.siw_emi_scanner_tags.xml_generic import XmlGeneric


class Comp(XmlGeneric):

    def __init__(self, element):
        self._element = element
        if element is not None:
            self.CompName = self._element.attrib["CompName"]
            self.CompValue = self._element.attrib["CompValue"]
            self.DeviceName = self._element.attrib["DeviceName"]
            self.capType = self._element.attrib["capType"] if "capType" in self._element.attrib else None
            self.isClockDriver = self._element.attrib["isClockDriver"]
            self.isHighSpeed = self._element.attrib["isHighSpeed"]
            self.isIC = self._element.attrib["isIC"]
            self.isOscillator = self._element.attrib["isOscillator"]
            self.xLoc = self._element.attrib["xLoc"]
            self.yLoc = self._element.attrib["yLoc"]
        else:
            self.CompName = None
            self.CompValue = None
            self.DeviceName = None
            self.capType = None
            self.isClockDriver = None
            self.isHighSpeed = None
            self.isIC = None
            self.isOscillator = None
            self.xLoc = None
            self.yLoc = None


class ComponentTags(XmlGeneric):
    def __init__(self, element):
        self._element = element
        self.comps = []

        if element:
            for el in self._element.findall("Comp"):
                comp = Comp(el)
                self.comps.append(comp)

    @staticmethod
    def read_element(element):
        return ComponentTags(element)

    def read_dict(self, data):
        for i in data["comps"]:
            comp = Comp(None)
            self.comps.append(comp.create(i["Comp"]))

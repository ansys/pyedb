from pyedb.misc.siw_feature_config.emc.xml_generic import XmlGeneric


class Comp(XmlGeneric):
    """Manages component tags."""

    def __init__(self, element):
        super().__init__(element)
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
    """Manages component tags."""

    CLS_MAPPING = {"Comp": Comp}

    def __init__(self, element):
        super().__init__(element)

        if element:
            for el in self._element.findall("Comp"):
                comp = Comp(el)
                self.sub_elements.append(comp)

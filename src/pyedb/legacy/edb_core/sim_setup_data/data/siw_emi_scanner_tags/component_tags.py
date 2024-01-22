class Comp:
    def __init__(self, element):
        self._element = element
        self.comp_name = self._element.attrib["compName"]
        self.comp_value = self._element.attrib["compValue"]
        self.device_name = self._element.attrib["deviceName"]
        self.cap_type = self._element.attrib["capType"]
        self.is_clock_driver = self._element.attrib["isClockDriver"]
        self.is_high_speed = self._element.attrib["isHighSpeed"]
        self.is_IC = self._element.attrib["isIC"]
        self.is_oscillator = self._element.attrib["isOscillator"]
        self.x_loc = self._element.attrib["xLoc"]
        self.y_loc = self._element.attrib["yLoc"]


class ComponentTags:
    def __init__(self, element):
        self._element = element
        self._comps = []

        for el in self._element.findall("Comp"):
            comp = Comp(el)
            self.comps.append(comp)

    @property
    def comps(self):
        return self._comps

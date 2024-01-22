

class Net:
    def __init__(self, element):
        self._element = element
        self.is_bus = self._element.attrib["isBus"]
        self.is_clock = self._element.attrib["isClock"]
        self.is_critical = self._element.attrib["isCritical"]
        self.name = self._element.attrib["name"]
        self.type = self._element.attrib["type"]


class NetTags:
    def __init__(self, element):
        self._element = element
        self._nets = []

        for el in self._element.findall("Net"):
            net = Net(el)
            self.nets.append(net)

    @property
    def nets(self):
        return self._nets

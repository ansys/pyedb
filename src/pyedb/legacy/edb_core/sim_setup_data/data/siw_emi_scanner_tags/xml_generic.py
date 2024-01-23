import re
from pyedb.generic.general_methods import ET


class XmlGeneric:
    DEBUG = False

    def add_items(self, item_type, kwargs):
        pass

    def create(self, kwargs):
        for attrib, value in kwargs.items():
            if attrib in self.__dict__.keys():
                if not isinstance(value, list):
                    self.__setattr__(attrib, value)
                else:
                    for i in value:
                        kwargs = list(i.values())[0]
                        item_type = list(i.keys())[0]
                        self.add_items(item_type, kwargs)
        return self

    def write_xml(self, parent):
        elem = ET.SubElement(parent, self.__class__.__name__)
        for attrib, value in self.__dict__.items():
            if attrib.startswith("_"):
                continue
            elif value is None:
                continue
            elif isinstance(value, list):
                for i in value:
                    i.write_xml(elem)
            else:
                elem.set(attrib, value)
        return parent

    def write_dict(self, parent):
        temp = {}
        for attrib, value in self.__dict__.items():
            if attrib.startswith("_"):
                continue
            elif value is None:
                continue

            if isinstance(value, list):
                new_list = []
                for i in value:
                    parent_2 = {}
                    i.write_dict(parent_2)
                    new_list.append(parent_2)
                temp[attrib] = new_list
            else:
                temp[attrib] = value

        parent[self.__class__.__name__] = temp


import json
from pyedb.generic.general_methods import ET

from pyedb.misc.siw_feature_config.emc.tag_library import \
    TagLibrary
from pyedb.misc.siw_feature_config.emc.net_tags import NetTags
from pyedb.misc.siw_feature_config.emc.component_tags import \
    ComponentTags


class EMCRuleCheckerSettings:
    """Manages EMI scanner settings."""

    def __init__(self):
        self.version = "1.0"
        self.encoding = "UTF-8"
        self.standalone = "no"

        self.tag_library = TagLibrary(None)
        self.net_tags = NetTags(None)
        self.component_tags = ComponentTags(None)

    @property
    def _element_tree(self):
        """Element tree."""
        root = ET.Element("EMCRuleCheckerSettings")

        if self.tag_library:
            self.tag_library.write_xml(root)
        if self.net_tags:
            self.net_tags.write_xml(root)
        if self.component_tags:
            self.component_tags.write_xml(root)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        return tree

    def read_xml(self, fpath):
        """Read settings from a json file.

        Parameters
        ----------
        fpath: str, Path
            Path to file.
        """
        tree = ET.parse(fpath)
        root = tree.getroot()

        self.tag_library = TagLibrary(root.find("TagLibrary"))
        self.net_tags = NetTags(root.find("NetTags"))
        self.component_tags = ComponentTags(root.find("ComponentTags"))

    def write_xml(self, fpath):
        """Write settings to a file in xml format.

        Parameters
        ----------
        fpath: str, Path
            Path to file.
        """
        self._element_tree.write(fpath, encoding=self.encoding, xml_declaration=True)

    def write_json(self, fpath):
        """Write settings to a file in json format.

        Parameters
        ----------
        fpath: str, Path
            Path to file.
        """
        data = {}
        self.tag_library.write_dict(data)
        self.net_tags.write_dict(data)
        self.component_tags.write_dict(data)

        with open(fpath, "w") as f:
            json.dump(data, f, indent=4)

    def read_json(self, fpath):
        """Read settings from a json file.

        Parameters
        ----------
        fpath: str, Path
            Path to file.
        """
        self.tag_library = TagLibrary(None)
        self.net_tags = NetTags(None)
        self.component_tags = ComponentTags(None)

        with open(fpath) as f:
            data = json.load(f)

        tag_library = data["TagLibrary"] if "TagLibrary" in data else None
        if tag_library:
            self.tag_library.read_dict(tag_library)

        net_tags = data["NetTags"] if "NetTags" in data else None
        if net_tags:
            self.net_tags.read_dict(net_tags)

        component_tags = data["ComponentTags"] if "ComponentTags" in data else None
        if component_tags:
            self.component_tags.read_dict(component_tags)

    def add_net(self, is_bus, is_clock, is_critical, name, net_type):
        """Assign tags to a net.

        Parameters
        ----------
        is_bus: str
            Whether the net is a bus.
        is_clock: str
            Whether the net is a clock.
        is_critical: str
            Whether the net is critical.
        name: str
            Name of the net.
        net_type: str
            Type of the net.
        """
        kwargs = {
            "isBus": is_bus,
            "isClock": is_clock,
            "isCritical": is_critical,
            "name": name,
            "type": net_type
        }
        self.net_tags.add_sub_element(kwargs, "Net")

    def add_component(self,
                      comp_name,
                      comp_value,
                      device_name,
                      is_clock_driver,
                      is_high_speed,
                      is_ic,
                      is_oscillator,
                      x_loc,
                      y_loc,
                      cap_type=None,
                      ):
        """Assign tags to a component.

        Parameters
        ----------
        comp_name: str
            Name of the component.
        comp_value: str
            Value of the component.
        device_name: str
            Name of the device.
        is_clock_driver: str
            Whether the component is a clock driver.
        is_high_speed: str
            Whether the component is a high speed.
        is_ic: str
            Whether the component is a IC.
        is_oscillator: str
            Whether the component is an oscillator.
        x_loc: str
            X coordinate.
        y_loc: str
            Y coordinate
        cap_type: str, optional
            Type of the capacitor. The default is ``"None"``. Options are ``"Decoupling"``, ``"Stitching"``.
        """
        kwargs = {"CompName": comp_name,
                  "CompValue": comp_value,
                  "DeviceName": device_name,
                  "capType": cap_type,
                  "isClockDriver": is_clock_driver,
                  "isHighSpeed": is_high_speed,
                  "isIC": is_ic,
                  "isOscillator": is_oscillator,
                  "xLoc": x_loc,
                  "yLoc": y_loc}
        self.component_tags.add_sub_element(kwargs, "Comp")

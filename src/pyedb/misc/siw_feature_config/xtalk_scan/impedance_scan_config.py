from pyedb.generic.general_methods import ET
from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet


class ImpedanceScan:
    def __init__(self):
        self.min_transmission_line_segment_length = "0.25mm"
        self.frequency = "2e9Hz"
        self.nets = {}

    def write_wml(self, parent):
        z_scan = ET.SubElement(parent, "Z0ScanConfig")
        z_scan.set("MinTlineSegmentLength", self.min_transmission_line_segment_length)
        z_scan.set("Z0Frequency", self.frequency)
        single_ended_nets = ET.SubElement(parent, "SingleEndedNets")
        for net in list(self.nets.values()):
            net.write_xml(single_ended_nets)

    def add_single_ended_net(self, name, nominal_impedance=50.0, warning_threshold=17.0, violation_threshold=32.0):
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.nominal_impedance = nominal_impedance
            net.warning_threshold = warning_threshold
            net.violation_threshold = violation_threshold
            self.nets[name] = net
        else:
            return False

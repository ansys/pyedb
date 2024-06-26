from pyedb.generic.general_methods import ET
from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet


class CrosstalkFrequency:
    def __init__(self):
        self.min_transmission_line_segment_length = "0.25mm"
        self.frequency = "2e9Hz"
        self.nets = {}

    def write_wml(self, parent):
        freq_scan = ET.SubElement(parent, "FdXtalkConfig")
        freq_scan.set("MinTlineSegmentLength", self.min_transmission_line_segment_length)
        freq_scan.set("XtalkFrequency", self.frequency)
        for net in list(self.nets.values()):
            net.write_xml(parent)

    def add_single_ended_net(
        self,
        name,
        next_warning_threshold=5.0,
        next_violation_threshold=10,
        fext_warning_threshold_warning=5.0,
        fext_violation_threshold=5.0,
    ):
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.next_warning_threshold = next_warning_threshold
            net.next_violation_threshold = next_violation_threshold
            net.fext_warning_threshold = fext_warning_threshold_warning
            net.fext_violation_threshold = fext_violation_threshold
            self.nets[name] = net
        else:
            return False

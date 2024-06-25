from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet


class Z0ScanConfig:
    def __init__(self):
        self.min_transmission_line_segment_length = "0.25mm"
        self.z0_frequency = "2e9Hz"
        self.nets = {}

    def add_single_ended_net(self, name, nominal_impedance=50.0, warning_threshold=17.0, violation_threshold=32.0):
        if name and not name in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.nominal_z0 = nominal_impedance
            net.warning_threshold = warning_threshold
            net.violation_threshold = violation_threshold
            self.nets[name] = net
        else:
            return False

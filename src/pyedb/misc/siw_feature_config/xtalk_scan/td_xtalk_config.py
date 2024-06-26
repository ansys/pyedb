from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet
from pyedb.misc.siw_feature_config.xtalk_scan.pins import DriverPin, ReceiverPin


class CrossTalkTime:
    def __init__(self):
        self.nets = {}
        self.driver_pins = []
        self.receiver_pins = []

    def add_single_ended_net(
        self,
        name,
        driver_rise_time=5.0,
        voltage=10,
        driver_impedance=5.0,
        termination_impedance=5.0,
    ):
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.driver_rise_time = driver_rise_time
            net.voltage = voltage
            net.driver_impedance = driver_impedance
            net.termination_impedance = termination_impedance
            self.nets[name] = net
        else:
            return False

    def add_driver_pins(self, name, ref_des, rise_time="100ps", voltage=1.0, impedance=50.0):
        pin = DriverPin(
            name=name, ref_des=ref_des, driver_rise_time=rise_time, voltage=voltage, driver_impedance=impedance
        )
        self.driver_pins.append(pin)

    def add_receiver_pin(self, name, ref_des, impedance):
        pin = ReceiverPin(name=name, ref_des=ref_des, receiver_impedance=impedance)
        self.receiver_pins.append(pin)

    def __write_wml(self, parent):
        pass

class Nets:
    def __init__(self, pedb, net_dict):
        self._pedb = pedb
        self._nets = net_dict
        self.power_ground_nets = self._nets["power_ground_nets"]
        self.signal_nets = self._nets["signal_nets"]

    def apply(self):
        nets = self._pedb.nets.nets
        for i in self._nets["power_ground_nets"]:
            nets[i].is_power_ground = True

        for i in self._nets["signal_nets"]:
            nets[i].is_power_ground = False

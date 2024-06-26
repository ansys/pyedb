from pyedb.generic.general_methods import ET


class SingleEndedNet:
    def __init__(self):
        self.name = None
        self.nominal_impedance = None
        self.warning_threshold = None
        self.violation_threshold = None
        self.fext_warning_threshold = None
        self.fext_violation_threshold = None
        self.next_warning_threshold = None
        self.next_violation_threshold = None
        self.driver_rise_time = None
        self.voltage = None
        self.driver_impedance = None
        self.termination_impedance = None

    def write_xml(self, parent):
        net = ET.SubElement(parent, "Net")
        if self.name is not None:
            net.set("Name", self.name)
        if self.nominal_impedance is not None:
            net.set("NominalZ0", str(self.nominal_impedance))
        if self.warning_threshold is not None:
            net.set("WarningThreshold", str(self.warning_threshold))
        if self.violation_threshold is not None:
            net.set("ViolationThreshold", str(self.violation_threshold))
        if self.fext_warning_threshold is not None:
            net.set("FEXTWarningThreshold", str(self.fext_warning_threshold))
        if self.fext_violation_threshold is not None:
            net.set("FEXTViolationThreshold", str(self.fext_violation_threshold))
        if self.next_warning_threshold is None:
            net.set("NEXTWarningThreshold", str(self.next_warning_threshold))
        if self.next_violation_threshold is not None:
            net.set("NEXTViolationThreshold", str(self.next_violation_threshold))
        if self.driver_rise_time is not None:
            net.set("DriverRiseTime", str(self.driver_rise_time))
        if self.voltage is not None:
            net.set("Voltage", str(self.voltage))
        if self.driver_impedance is not None:
            net.set("DriverImpedance", str(self.driver_impedance))
        if self.termination_impedance is not None:
            net.set("TerminationImpedance", str(self.termination_impedance))

class SingleEndedNet:
    def __init__(self):
        self.name = ""
        self.nominal_impedance = 50.0
        self.warning_threshold = 17.0
        self.violation_threshold = 32.0
        self.fext_warning_threshold = 7.0
        self.fext_violation_threshold = 20.0
        self.next_warning_threshold = 7.0
        self.next_violation_threshold = 20.0
        self.driver_rise_time = "125ps"
        self.voltage = 3
        self.driver_impedance = 50.0
        self.termination_impedance = 50.0

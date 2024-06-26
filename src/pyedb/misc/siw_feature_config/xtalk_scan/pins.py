from dataclasses import dataclass


@dataclass
class DriverPin:
    name: str
    ref_des: str
    driver_rise_time: str
    voltage: float
    driver_impedance: float


@dataclass
class ReceiverPin:
    name: str
    ref_des: str
    receiver_impedance: float

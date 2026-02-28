# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyedb.generic.general_methods import ET
from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet
from pyedb.misc.siw_feature_config.xtalk_scan.pins import DriverPin, ReceiverPin


class CrossTalkTime:
    """Time domain crosstalk configuration class handler.

    Parameters
    ----------
    pedb : object
        PyEDB instance.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb("path/to/aedb")
    >>> xtalk = CrossTalkTime(edb)
    >>> xtalk.add_single_ended_net("CLK", driver_rise_time=5.0, voltage=1.8)

    """

    def __init__(self, pedb) -> None:
        """Initialize time domain crosstalk configuration.

        Parameters
        ----------
        pedb : object
            PyEDB instance.

        """
        self._pedb = pedb
        self.nets = {}
        self.driver_pins = []
        self.receiver_pins = []

    def add_single_ended_net(
        self,
        name: str,
        driver_rise_time: float | str = 5.0,
        voltage: float | str = 10,
        driver_impedance: float | str = 5.0,
        termination_impedance: float | str = 5.0,
    ) -> bool:
        """Add single ended net.

        Parameters
        ----------
        name : str
            Net name.
        driver_rise_time : float or str, optional
            Driver rise time value.
            The default is ``5.0``.
        voltage : float or str, optional
            Voltage value.
            The default is ``10``.
        driver_impedance : float or str, optional
            Driver impedance value.
            The default is ``5.0``.
        termination_impedance : float or str, optional
            Termination impedance value.
            The default is ``5.0``.

        Returns
        -------
        bool
            ``True`` if the net was added successfully, ``False`` otherwise.

        Examples
        --------
        >>> xtalk = CrossTalkTime(pedb)
        >>> xtalk.add_single_ended_net("DDR_DQ0", driver_rise_time=2.0, voltage=1.2)
        True

        """
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.driver_rise_time = driver_rise_time
            net.voltage = voltage
            net.driver_impedance = driver_impedance
            net.termination_impedance = termination_impedance
            self.nets[name] = net
            return True
        else:
            self._pedb.logger.error(f"Net {name} already assigned.")
            return False

    def add_driver_pins(
        self, name: str, ref_des: str, rise_time: str = "100ps", voltage: float = 1.0, impedance: float = 50.0
    ) -> None:
        """Add driver pins.

        Parameters
        ----------
        name : str
            Pin name.
        ref_des : str
            Reference designator of the component.
        rise_time : str, optional
            Driver rise time.
            The default is ``"100ps"``.
        voltage : float, optional
            Voltage value.
            The default is ``1.0``.
        impedance : float, optional
            Driver impedance value.
            The default is ``50.0``.

        Examples
        --------
        >>> xtalk = CrossTalkTime(pedb)
        >>> xtalk.add_driver_pins("A1", "U1", rise_time="50ps", voltage=1.8, impedance=40.0)

        """
        pin = DriverPin()
        pin.name = name
        pin.ref_des = ref_des
        pin.driver_rise_time = rise_time
        pin.voltage = voltage
        pin.driver_impedance = impedance
        self.driver_pins.append(pin)

    def add_receiver_pin(self, name: str, ref_des: str, impedance: float) -> None:
        """Add receiver pin.

        Parameters
        ----------
        name : str
            Pin name.
        ref_des : str
            Reference designator of the component.
        impedance : float
            Receiver impedance value.

        Examples
        --------
        >>> xtalk = CrossTalkTime(pedb)
        >>> xtalk.add_receiver_pin("B1", "U2", impedance=75.0)

        """
        pin = ReceiverPin()
        pin.name = name
        pin.ref_des = ref_des
        pin.receiver_impedance = impedance
        self.receiver_pins.append(pin)

    def extend_xml(self, parent) -> None:
        """Extend XML tree with crosstalk configuration.

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            Parent XML element to extend.

        """
        time_scan = ET.SubElement(parent, "TdXtalkConfig")
        single_ended_nets = ET.SubElement(time_scan, "SingleEndedNets")
        for net in list(self.nets.values()):
            net.extend_xml(single_ended_nets)
        driver_pins = ET.SubElement(time_scan, "DriverPins")
        for pin in self.driver_pins:
            pin.extend_xml(driver_pins)
        receiver_pins = ET.SubElement(time_scan, "ReceiverPins")
        for pin in self.receiver_pins:
            pin.extend_xml(receiver_pins)

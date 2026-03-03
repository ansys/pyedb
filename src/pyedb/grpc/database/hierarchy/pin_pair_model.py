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


from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel as CorePinPairModel
from ansys.edb.core.utility.rlc import Rlc as CoreRlc

from pyedb.grpc.database.utility.value import Value


class PinPairModel:
    """Manage pin-pair model."""

    def __init__(self, edb_object):
        self.core = edb_object

    @classmethod
    def create(
        cls, r: float = None, l: float = None, c: float = None, pin1_name: str = None, pin2_name: str = None
    ) -> "PinPairModel":
        """Create pin pair model. Pin pair model is defined between two pins, and it can be used to define the RLC model
        between two pins. Adding optional RLC values will enable the RLC model for the pin pair.

        Parameters
        ----------
        r : float, optional
            Resistance value. If not provided, the default value will be used. Default value is 0.
        l : float, optional
            Inductance value. If not provided, the default value will be used. Default value is 0.
        c : float, optional
            Capacitance value. If not provided, the default value will be used. Default value is 0.
        pin1_name : str, optional
            First pin name. If not provided, the default name will be used. Default name is `1`.
        pin2_name : str, optional
            Second pin name. If not provided, the default name will be used. Default name is `2`.

        Returns
        -------
        PinPairModel
            The created pin pair model.

        """
        core = CorePinPairModel.create()
        rlc = CoreRlc()
        if r is not None:
            rlc.r_enabled = True
            rlc.r = Value(r)
        if l is not None:
            rlc.l_enabled = True
            rlc.l = Value(l)
        if c is not None:
            rlc.c_enabled = True
            rlc.c = Value(c)
        if not pin1_name:
            pin1_name = "1"
        if not pin2_name:
            pin2_name = "2"
        core.set_rlc(pin_pair=(pin1_name, pin2_name), rlc=rlc)
        return cls(core)

    @property
    def first_pin(self) -> str:
        """First pin name.
        
        This attribute is read-only since pin pair model is defined between two pins,
        and changing pin names will change the pin pair itself.

        Returns
        -------
        str
            First pin name.

        """
        pp = self.core.pin_pairs()
        return pp[0][0] if pp else None

    @property
    def second_pin(self) -> str:
        """Second pin name.
        
        This attribute is read-only since pin pair model is defined between two pins,
        and changing pin names will change the pin pair itself.

        Returns
        -------
        str
            Second pin name.

        """
        pp = self.core.pin_pairs()
        return pp[0][1] if pp else None

    @property
    def rlc_enable(self) -> tuple[bool, bool, bool]:
        """Enable model.

        Returns
        -------
        tuple[r_enabled(bool), l_enabled(bool), c_enabled(bool)].

        """
        return self.core.r_enabled, self.core.l_enabled, self.core.c_enabled

    @rlc_enable.setter
    def rlc_enable(self, value):
        self.core.r_enabled = Value(value[0])
        self.core.l_enabled = Value(value[1])
        self.core.c_enabled = Value(value[2])

    @property
    def resistance(self) -> float:
        """Resistance.

        Returns
        -------
        float
            Resistance value.

        """
        return Value(self.rlc.r)

    @resistance.setter
    def resistance(self, value):
        self.rlc.r = Value(value)

    @property
    def inductance(self) -> float:
        """Inductance.

        Returns
        -------
        float
            Inductance value.

        """
        return Value(self.rlc.l)

    @inductance.setter
    def inductance(self, value):
        self.rlc.l = Value(value)

    @property
    def capacitance(self) -> float:
        """Capacitance.

        Returns
        -------
        float
            Capacitance value.

        """
        return Value(self.rlc.c)

    @capacitance.setter
    def capacitance(self, value):
        self.rlc.c = Value(value)

    @property
    def rlc_values(self) -> list[float]:
        """Rlc value.

        Returns
        -------
        List[float, float, float]
            [R value, L value, C value].

        """
        return [Value(self.rlc.r), Value(self.rlc.l), Value(self.rlc.c)]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        self.rlc.r = Value(values[0])
        self.rlc.l = Value(values[1])
        self.rlc.c = Value(values[2])

    @property
    def is_null(self) -> bool:
        """Check if the pin pair model is null.

        Returns
        -------
        bool
            True if the pin pair model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def is_parallel(self) -> bool:
        """Check if the pin pair model is parallel.

        Returns
        -------
        bool
            True if the pin pair model is parallel, False otherwise.

        """
        return self.core.is_parallel

    @is_parallel.setter
    def is_parallel(self, value):
        self.core.is_parallel = value

    def pin_pairs(self) -> list[tuple[str, str]]:
        """Get all pin pairs.

        Returns
        -------
        List[Tuple[str, str]]
            List of pin pairs.

        """
        return self.core.pin_pairs()

    @property
    def rlc(self, pin_pair: tuple[str, str] = None) -> CoreRlc | None:
        """Retrieve RLC model given pin pair. If pin pair is not provided, the first pin pair will be used by default.
        If there is no pin pair, None will be returned.

        Parameters
        ----------
        pin_pair : Tuple[str, str], optional
            Tuple of pin names (first_pin, second_pin). If not provided, the first pin pair will be used by default.
            If not provided and there is no pin pair, the first pin will be taken.

        Returns
        -------
        CoreRlc
            RLC model for the pin pair.
        """
        pp = self.core.pin_pairs()
        if not pp:
            return None
        if pin_pair:
            for p in pp:
                if p[0] == pin_pair[0] and p[1] == pin_pair[1]:
                    pin_pair = self.core.rlc(pp)
            raise ValueError(f"Pin pair {pin_pair} not found.")
        else:
            pin_pair = pp[0]
        return self.core.rlc(pin_pair)

    def set_rlc(self, pin_pair: tuple[str, str], rlc: CoreRlc):
        """Set RLC model for the pin pair.

        Parameters
        ----------
        pin_pair : Tuple[str, str]
            Tuple of pin names (first_pin, second_pin).
        rlc : CoreRlc
            RLC model to set for the pin pair.

        """
        if pin_pair in self.pin_pairs():
            self.core.set_rlc(pin_pair=pin_pair, rlc=rlc)

    def delete_rlc(self, pin_pair: tuple[str, str]):
        """Delete RLC model for the pin pair.

        Parameters
        ----------
        pin_pair : Tuple[str, str]
            Tuple of pin names (first_pin, second_pin).

        """
        if pin_pair in self.pin_pairs():
            self.core.delete_rlc(pin_pair=pin_pair)
